from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_admin_user, get_db
from app.models import User
from app.schemas import UserPublic

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserPublic])
def list_users(db: Session = Depends(get_db), _admin: User = Depends(get_admin_user)):
    return db.query(User).order_by(User.id.asc()).all()


@router.get("/users/pending", response_model=list[UserPublic])
def list_pending_users(db: Session = Depends(get_db), _admin: User = Depends(get_admin_user)):
    return db.query(User).filter(User.is_approved.is_(False), User.role == "user").all()


@router.post("/users/{user_id}/approve", response_model=UserPublic)
def approve_user(user_id: int, db: Session = Depends(get_db), _admin: User = Depends(get_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_approved = True
    db.commit()
    db.refresh(user)
    return user
