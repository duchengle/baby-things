from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.deps import get_approved_user, get_db
from app.models import Activity, ActivityImage, ActivityItem, BabyAccess, User
from app.schemas import ActivityCreate, ActivityItemPublic, ActivityPublic

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/activity-items", response_model=list[ActivityItemPublic])
def list_activity_items(db: Session = Depends(get_db), _user: User = Depends(get_approved_user)):
    return (
        db.query(ActivityItem)
        .filter(ActivityItem.is_enabled.is_(True))
        .order_by(ActivityItem.sort_order.asc(), ActivityItem.id.asc())
        .all()
    )


def _can_record(db: Session, user: User, baby_id: int) -> bool:
    if user.role == "admin":
        return True
    access = db.query(BabyAccess).filter(BabyAccess.baby_id == baby_id, BabyAccess.user_id == user.id).first()
    return bool(access and access.can_record)


def _can_view(db: Session, user: User, baby_id: int) -> bool:
    if user.role == "admin":
        return True
    access = db.query(BabyAccess).filter(BabyAccess.baby_id == baby_id, BabyAccess.user_id == user.id).first()
    return bool(access and access.can_view)


@router.post("", response_model=ActivityPublic)
def create_activity(payload: ActivityCreate, db: Session = Depends(get_db), user: User = Depends(get_approved_user)):
    if not _can_record(db, user, payload.baby_id):
        raise HTTPException(status_code=403, detail="No record permission")

    item = None
    if payload.activity_item_id is not None:
        item = db.query(ActivityItem).filter(ActivityItem.id == payload.activity_item_id, ActivityItem.is_enabled.is_(True)).first()
        if not item:
            raise HTTPException(status_code=400, detail="Invalid activity item")
    elif payload.activity_type:
        item = db.query(ActivityItem).filter(ActivityItem.code == payload.activity_type, ActivityItem.is_enabled.is_(True)).first()
        if not item:
            raise HTTPException(status_code=400, detail="Invalid activity type")

    activity = Activity(
        baby_id=payload.baby_id,
        created_by=user.id,
        activity_item_id=item.id if item else None,
        activity_type=item.code if item else str(payload.activity_type),
        note=payload.note,
        happened_at=payload.happened_at,
    )
    db.add(activity)
    db.flush()

    for image in payload.images:
        db.add(ActivityImage(activity_id=activity.id, object_key=image.object_key, url=image.url))

    db.commit()
    db.refresh(activity)
    return ActivityPublic(
        id=activity.id,
        baby_id=activity.baby_id,
        created_by=activity.created_by,
        activity_item_id=activity.activity_item_id,
        activity_type=activity.activity_type,
        activity_type_name=item.display_name if item else None,
        note=activity.note,
        happened_at=activity.happened_at,
        image_urls=[item.url for item in activity.images],
    )


@router.get("/timeline", response_model=list[ActivityPublic])
def list_timeline(
    baby_id: int,
    day: datetime = Query(description="Day in ISO format, e.g. 2026-05-02T00:00:00"),
    db: Session = Depends(get_db),
    user: User = Depends(get_approved_user),
):
    if not _can_view(db, user, baby_id):
        raise HTTPException(status_code=403, detail="No view permission")

    day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)

    records = (
        db.query(Activity)
        .options(joinedload(Activity.activity_item))
        .filter(and_(Activity.baby_id == baby_id, Activity.happened_at >= day_start, Activity.happened_at <= day_end))
        .order_by(Activity.happened_at.desc())
        .all()
    )

    code_name_map = {
        row.code: row.display_name
        for row in db.query(ActivityItem).all()
    }

    return [
        ActivityPublic(
            id=item.id,
            baby_id=item.baby_id,
            created_by=item.created_by,
            activity_item_id=item.activity_item_id,
            activity_type=item.activity_type,
            activity_type_name=(item.activity_item.display_name if item.activity_item else code_name_map.get(item.activity_type)),
            note=item.note,
            happened_at=item.happened_at,
            image_urls=[img.url for img in item.images],
        )
        for item in records
    ]
