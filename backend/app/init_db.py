"""
Database engine, session factory, declarative base, and table initialisation.
All other modules import Base and get_db from here — never from SQLAlchemy directly.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# ── Connection ────────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/workflow_db",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # reconnect silently after idle-disconnect
    echo=False,            # set True to log generated SQL during development
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Declarative base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Shared base class for all ORM models."""
    pass


# ── Dependency injection ──────────────────────────────────────────────────────
def get_db():
    """
    FastAPI dependency that yields a scoped database session.
    The session is closed automatically when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Table creation ────────────────────────────────────────────────────────────
def create_tables() -> None:
    """
    Import every model so SQLAlchemy registers them with Base.metadata,
    then create any missing tables.  Safe to call on every startup.
    """
    from app.models import roles_master, user, client, project  # noqa: F401  (roles_master first — users.role FK depends on it)
    from app.models import stage_master, stage_activity_master  # noqa: F401
    from app.models import chapter_info                         # noqa: F401
    from app.models import stage_detail                         # noqa: F401
    Base.metadata.create_all(bind=engine)
