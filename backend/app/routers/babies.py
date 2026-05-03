from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.deps import get_approved_user, get_db
from app.models import Baby, BabyAccess, User
from app.schemas import BabyAccessSet, BabyCreate, BabyPublic

router = APIRouter(prefix="/babies", tags=["babies"])


def _can_view(db: Session, user: User, baby_id: int) -> bool:
    if user.role == "admin":
        return True
    access = db.query(BabyAccess).filter(BabyAccess.baby_id == baby_id, BabyAccess.user_id == user.id).first()
    return bool(access and access.can_view)


@router.post("", response_model=BabyPublic)
def create_baby(payload: BabyCreate, db: Session = Depends(get_db), user: User = Depends(get_approved_user)):
    baby = Baby(name=payload.name, birth_date=payload.birth_date, created_by=user.id)
    db.add(baby)
    db.flush()

    db.add(BabyAccess(baby_id=baby.id, user_id=user.id, can_view=True, can_record=True))
    db.commit()
    db.refresh(baby)
    return baby


@router.get("", response_model=list[BabyPublic])
def list_babies(db: Session = Depends(get_db), user: User = Depends(get_approved_user)):
    if user.role == "admin":
        return db.query(Baby).all()

    babies = (
        db.query(Baby)
        .join(BabyAccess, Baby.id == BabyAccess.baby_id)
        .filter(BabyAccess.user_id == user.id, or_(BabyAccess.can_view.is_(True), BabyAccess.can_record.is_(True)))
        .all()
    )
    return babies


@router.post("/{baby_id}/access")
def set_baby_access(
    baby_id: int,
    payload: BabyAccessSet,
    db: Session = Depends(get_db),
    user: User = Depends(get_approved_user),
):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    if user.role != "admin" and baby.created_by != user.id:
        raise HTTPException(status_code=403, detail="Only owner or admin can manage access")

    target = db.query(User).filter(User.id == payload.user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found")

    access = db.query(BabyAccess).filter(BabyAccess.baby_id == baby_id, BabyAccess.user_id == payload.user_id).first()
    if not access:
        access = BabyAccess(baby_id=baby_id, user_id=payload.user_id)
        db.add(access)

    access.can_view = payload.can_view
    access.can_record = payload.can_record
    db.commit()
    return {"ok": True}


@router.get("/{baby_id}", response_model=BabyPublic)
def get_baby(baby_id: int, db: Session = Depends(get_db), user: User = Depends(get_approved_user)):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    if not _can_view(db, user, baby_id):
        raise HTTPException(status_code=403, detail="No permission")
    return baby
