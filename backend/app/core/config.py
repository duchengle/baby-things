from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Baby Things API"
    secret_key: str = Field(default="change-me-in-production")
    access_token_expire_minutes: int = 60 * 24
    sqlite_url: str = f"sqlite:///{(BASE_DIR / 'baby_things.db').as_posix()}"

    # Admin bootstrapping
    bootstrap_admin_username: str | None = None
    bootstrap_admin_password: str | None = None

    # OSS settings (optional during local dev)
    oss_endpoint: str | None = None
    oss_bucket: str | None = None
    oss_region: str | None = None


settings = Settings()
