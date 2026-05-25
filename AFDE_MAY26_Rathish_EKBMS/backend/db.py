"""SQLAlchemy engine, session, and Base for the EKBMS backend.

Named `db.py` (not `database.py`) on purpose: avoids a name collision with
the top-level `database/` folder in the repo.
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "database" / "ekbms.db"

# Allow override via env var (useful for tests / CI / non-default deploys).
SQLALCHEMY_DATABASE_URL = os.getenv("EKBMS_DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
