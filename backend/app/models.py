from datetime import date, datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default=UserRole.USER.value)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Baby(Base):
    __tablename__ = "babies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    birth_date: Mapped[date] = mapped_column(Date)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    access_list: Mapped[list["BabyAccess"]] = relationship(back_populates="baby", cascade="all, delete-orphan")


class BabyAccess(Base):
    __tablename__ = "baby_access"
    __table_args__ = (UniqueConstraint("baby_id", "user_id", name="uq_baby_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    baby_id: Mapped[int] = mapped_column(ForeignKey("babies.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    can_view: Mapped[bool] = mapped_column(Boolean, default=True)
    can_record: Mapped[bool] = mapped_column(Boolean, default=True)

    baby: Mapped[Baby] = relationship(back_populates="access_list")


class ActivityType(str, Enum):
    FEEDING = "feeding"
    POOP = "poop"
    BATH = "bath"
    NAVEL_CARE = "navel_care"
    VITAMIN = "vitamin"
    VACCINE = "vaccine"
    CHECKUP = "checkup"
    OTHER = "other"


class ActivityItem(Base):
    __tablename__ = "activity_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100))
    sort_order: Mapped[int] = mapped_column(Integer, default=100)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    baby_id: Mapped[int] = mapped_column(ForeignKey("babies.id"), index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    activity_item_id: Mapped[int | None] = mapped_column(ForeignKey("activity_items.id"), nullable=True, index=True)
    activity_type: Mapped[str] = mapped_column(String(30), index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    happened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    activity_item: Mapped[ActivityItem | None] = relationship()
    images: Mapped[list["ActivityImage"]] = relationship(back_populates="activity", cascade="all, delete-orphan")


class ActivityImage(Base):
    __tablename__ = "activity_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"), index=True)
    object_key: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(String(1024))

    activity: Mapped[Activity] = relationship(back_populates="images")
