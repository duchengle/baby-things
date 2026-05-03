from pathlib import Path
import re

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Baby Things API"
    secret_key: str = Field(default="change-me-in-production")
    access_token_expire_minutes: int = 60 * 24
    sqlite_url: str = f"sqlite:///{(BASE_DIR / 'baby_things.db').as_posix()}"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,https://baby.leateen.com,http://baby.leateen.com"

    # Admin bootstrapping
    bootstrap_admin_username: str | None = None
    bootstrap_admin_password: str | None = None

    # OSS settings (optional during local dev)
    oss_endpoint: str | None = None
    oss_bucket: str | None = None
    oss_region: str | None = None


settings = Settings()


def _normalize_sqlite_url(url: str) -> str:
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return url

    raw_path = url[len(prefix):]
    if raw_path.startswith("/"):
        return url
    if re.match(r"^[A-Za-z]:[\\/]", raw_path):
        return url

    relative_path = raw_path[2:] if raw_path.startswith("./") else raw_path
    return f"sqlite:///{(BASE_DIR / relative_path).as_posix()}"


settings.sqlite_url = _normalize_sqlite_url(settings.sqlite_url)


def get_cors_origins() -> list[str]:
    return [item.strip() for item in settings.cors_origins.split(",") if item.strip()]
