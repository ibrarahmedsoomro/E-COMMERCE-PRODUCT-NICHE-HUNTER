"""Database connection and session factory for SQLite and PostgreSQL."""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Default to SQLite file in data/ directory, or Postgres from env
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'hunter.db'}")

# SQLite requires check_same_thread=False for multithreading
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    future=True
)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()


def get_db():
    """Dependency / context helper for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
