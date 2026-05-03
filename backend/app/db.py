import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

try:
    import sqlite3  # noqa: F401
except ModuleNotFoundError:
    try:
        import pysqlite3 as sqlite3  # type: ignore # noqa: F401

        # Make SQLAlchemy's sqlite dialect import fallback DBAPI successfully.
        sys.modules["sqlite3"] = sqlite3
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "sqlite3 module is unavailable in current Python runtime. "
            "Please install pysqlite3-binary or use a Python build with sqlite3 enabled."
        ) from exc


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.sqlite_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
