from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserProfile, UserUpdate

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user)):
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        is_verified=current_user.is_verified,
        plan=current_user.plan,
    )

@router.patch("/me", response_model=UserProfile)
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.email is not None:
        current_user.email = payload.email
    db.commit()
    db.refresh(current_user)

    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        is_verified=current_user.is_verified,
        plan=current_user.plan,
    )