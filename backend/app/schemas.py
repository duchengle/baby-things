from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    is_approved: bool


class BabyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    birth_date: date


class BabyAccessSet(BaseModel):
    user_id: int
    can_view: bool = True
    can_record: bool = True


class BabyPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    birth_date: date
    created_by: int


class ActivityImageInput(BaseModel):
    object_key: str = Field(min_length=1, max_length=300)
    url: str = Field(min_length=1, max_length=1024)


class ActivityItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    display_name: str
    sort_order: int
    is_enabled: bool


class ActivityCreate(BaseModel):
    baby_id: int
    activity_item_id: int | None = None
    activity_type: str | None = None
    note: str | None = Field(default=None, max_length=2000)
    happened_at: datetime
    images: list[ActivityImageInput] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_activity_selector(self) -> "ActivityCreate":
        if self.activity_item_id is None and not self.activity_type:
            raise ValueError("activity_item_id or activity_type is required")
        return self

    @field_validator("images")
    @classmethod
    def validate_images_count(cls, images: list[ActivityImageInput]) -> list[ActivityImageInput]:
        if len(images) > 5:
            raise ValueError("A single activity can contain up to 5 images")
        return images


class ActivityPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    baby_id: int
    created_by: int
    activity_item_id: int | None
    activity_type: str
    activity_type_name: str | None
    note: str | None
    happened_at: datetime
    image_urls: list[str]
