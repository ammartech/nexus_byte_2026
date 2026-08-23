from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse, RefreshRequest, PasswordResetRequest, PasswordResetConfirm
from app.models.password_reset_token import PasswordResetToken
from app.core.security import create_access_token, generate_refresh_token, REFRESH_TOKEN_EXPIRE_DAYS
from app.models.refresh_token import RefreshToken
from datetime import datetime, timedelta, timezone
import hashlib
import uuid

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=pwd_context.hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return RegisterResponse(id=str(user.id), email=user.email, is_verified=user.is_verified)
@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(str(user.id))
    raw_refresh_token = generate_refresh_token()
    token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
    family_id = uuid.uuid4()

    refresh_row = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        family_id=family_id,
        revoked=False,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_row)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=raw_refresh_token)
@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(payload.refresh_token.encode()).hexdigest()
    token_row = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    if not token_row:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if token_row.revoked:
        # Reuse detected: revoke the whole family
        db.query(RefreshToken).filter(RefreshToken.family_id == token_row.family_id).update({"revoked": True})
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token reuse detected; session revoked")

    if token_row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # Rotate: revoke the old token, issue a new one in the same family
    token_row.revoked = True

    new_raw_token = generate_refresh_token()
    new_token_hash = hashlib.sha256(new_raw_token.encode()).hexdigest()

    new_token_row = RefreshToken(
        user_id=token_row.user_id,
        token_hash=new_token_hash,
        family_id=token_row.family_id,
        revoked=False,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_token_row)
    db.commit()

    new_access_token = create_access_token(str(token_row.user_id))

    return TokenResponse(access_token=new_access_token, refresh_token=new_raw_token)

@router.post("/password-reset", status_code=202)
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        raw_token = generate_refresh_token()
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        reset_row = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            used=False,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db.add(reset_row)
        db.commit()
        # In production this token would be emailed, not returned.
        # Returned here only for local testing.
        return {"message": "If that email exists, a reset link was sent.", "dev_token": raw_token}

    return {"message": "If that email exists, a reset link was sent."}


@router.post("/password-reset/confirm", status_code=200)
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(payload.reset_token.encode()).hexdigest()
    token_row = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()

    if not token_row or token_row.used or token_row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.id == token_row.user_id).first()
    user.password_hash = pwd_context.hash(payload.new_password)
    token_row.used = True
    db.commit()

    return {"message": "Password updated successfully"}