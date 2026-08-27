from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import get_db
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user