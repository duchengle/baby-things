from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.config import get_cors_origins, settings
from app.core.security import get_password_hash
from app.db import Base, engine
from app.models import Activity, ActivityItem, User, UserRole
from app.routers import activities, admin, auth, babies

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


def _bootstrap_activity_items(db: Session) -> None:
    default_items = [
        ("feeding", "喂养", 10, True),
        ("poop", "大便", 20, True),
        ("bath", "洗澡", 30, True),
        ("navel_care", "肚脐护理", 40, False),
        ("vitamin", "维生素", 50, True),
        ("vaccine", "疫苗", 60, True),
        ("checkup", "体检", 70, True),
        ("other", "其他", 80, True),
    ]

    for code, display_name, sort_order, is_enabled in default_items:
        exists = db.query(ActivityItem).filter(ActivityItem.code == code).first()
        if not exists:
            db.add(
                ActivityItem(
                    code=code,
                    display_name=display_name,
                    sort_order=sort_order,
                    is_enabled=is_enabled,
                )
            )

    db.commit()

    item_map = {row.code: row.id for row in db.query(ActivityItem).all()}
    orphan_activities = db.query(Activity).filter(Activity.activity_item_id.is_(None)).all()
    for row in orphan_activities:
        if row.activity_type in item_map:
            row.activity_item_id = item_map[row.activity_type]
    db.commit()


def _ensure_activity_schema(db: Session) -> None:
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("activities")}
    if "activity_item_id" not in columns:
        db.execute(text("ALTER TABLE activities ADD COLUMN activity_item_id INTEGER"))
        db.commit()


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        _ensure_activity_schema(db)
        _bootstrap_activity_items(db)

        if settings.bootstrap_admin_username and settings.bootstrap_admin_password:
            exists = db.query(User).filter(User.username == settings.bootstrap_admin_username).first()
            if not exists:
                admin_user = User(
                    username=settings.bootstrap_admin_username,
                    password_hash=get_password_hash(settings.bootstrap_admin_password),
                    role=UserRole.ADMIN.value,
                    is_approved=True,
                )
                db.add(admin_user)
                db.commit()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(babies.router, prefix="/api")
app.include_router(activities.router, prefix="/api")
