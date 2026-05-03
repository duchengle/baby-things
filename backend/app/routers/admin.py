from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_admin_user, get_db
from app.models import Activity, ActivityItem, User
from app.schemas import ActivityItemCreate, ActivityItemPublic, ActivityItemUpdate, UserPublic

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/activity-items", response_model=list[ActivityItemPublic])
def list_activity_items(db: Session = Depends(get_db), _admin: User = Depends(get_admin_user)):
    return db.query(ActivityItem).order_by(ActivityItem.sort_order.asc(), ActivityItem.id.asc()).all()


@router.post("/activity-items", response_model=ActivityItemPublic)
def create_activity_item(payload: ActivityItemCreate, db: Session = Depends(get_db), _admin: User = Depends(get_admin_user)):
    code = payload.code.strip().lower()
    exists = db.query(ActivityItem).filter(ActivityItem.code == code).first()
    if exists:
        raise HTTPException(status_code=400, detail="Activity item code already exists")

    item = ActivityItem(
        code=code,
        display_name=payload.display_name.strip(),
        sort_order=payload.sort_order,
        is_enabled=payload.is_enabled,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/activity-items/{item_id}", response_model=ActivityItemPublic)
def update_activity_item(
    item_id: int,
    payload: ActivityItemUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    item = db.query(ActivityItem).filter(ActivityItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Activity item not found")

    if payload.code is not None:
        new_code = payload.code.strip().lower()
        code_conflict = db.query(ActivityItem).filter(ActivityItem.code == new_code, ActivityItem.id != item_id).first()
        if code_conflict:
            raise HTTPException(status_code=400, detail="Activity item code already exists")
        item.code = new_code
    if payload.display_name is not None:
        item.display_name = payload.display_name.strip()
    if payload.sort_order is not None:
        item.sort_order = payload.sort_order
    if payload.is_enabled is not None:
        item.is_enabled = payload.is_enabled

    db.commit()
    db.refresh(item)
    return item


@router.delete("/activity-items/{item_id}")
def delete_activity_item(item_id: int, db: Session = Depends(get_db), _admin: User = Depends(get_admin_user)):
    item = db.query(ActivityItem).filter(ActivityItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Activity item not found")

    in_use = db.query(Activity).filter(Activity.activity_item_id == item_id).first()
    if in_use:
        raise HTTPException(status_code=400, detail="Activity item is in use and cannot be deleted")

    db.delete(item)
    db.commit()
    return {"ok": True}


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
