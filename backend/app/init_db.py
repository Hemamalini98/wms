"""
Database engine, session factory, declarative base, and table initialisation.
All other modules import Base and get_db from here — never from SQLAlchemy directly.
"""

import logging
import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import Pool
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Connection ────────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/workflow_db",
)


def _ensure_database_exists() -> None:
    """Create the database if it doesn't exist."""
    # Parse the database URL to extract components
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL)

    db_name = parsed.path.lstrip("/")
    user = parsed.username or "postgres"
    password = parsed.password or "password"
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432

    # Connect to the default 'postgres' database to create our database
    admin_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"

    try:
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        with admin_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            ).fetchone()

            if not result:
                logger.info(f"Database '{db_name}' not found, creating...")
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"Database '{db_name}' created successfully")
            else:
                logger.debug(f"Database '{db_name}' already exists")

        admin_engine.dispose()
    except Exception as exc:
        logger.error(f"Connection failure: could not ensure database exists — {exc}")
        raise


try:
    _ensure_database_exists()

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,   # reconnect silently after idle-disconnect
        echo=False,            # set True to log generated SQL during development
    )

    @event.listens_for(Pool, "connect")
    def receive_connect(dbapi_conn, connection_record):
        logger.info("Database connected")

    @event.listens_for(Pool, "detach")
    def receive_detach(dbapi_conn, connection_record):
        logger.debug("Database connection detached")

except Exception as exc:
    logger.error(f"Connection failure: {exc}")
    raise

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
    try:
        logger.info("Creating missing tables")

        # Import all models to register them
        from app.models import roles_master, user, client, project  # noqa: F401  (roles_master first — users.role FK depends on it)
        from app.models import stage_master, stage_activity_master  # noqa: F401
        from app.models import chapter_info                         # noqa: F401
        from app.models import stage_detail                         # noqa: F401
        from app.models import workflow_master                      # noqa: F401

        logger.debug(f"Registered models: {list(Base.metadata.tables.keys())}")

        # Get existing tables from database
        with engine.connect() as conn:
            inspector_result = conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            ).fetchall()
            existing_tables = {row[0] for row in inspector_result}
            logger.debug(f"Existing tables: {existing_tables if existing_tables else 'none'}")

        # Create all tables (creates only missing ones)
        logger.info(f"Creating tables for models: {list(Base.metadata.tables.keys())}")
        Base.metadata.create_all(bind=engine)

        # Check which tables were created
        with engine.connect() as conn:
            new_inspector_result = conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            ).fetchall()
            new_tables = {row[0] for row in new_inspector_result}
            created_tables = new_tables - existing_tables

        if created_tables:
            logger.info(f"Created tables: {', '.join(sorted(created_tables))}")
        else:
            logger.info("No new tables created (all exist)")

        logger.info("Tables ready")
    except Exception as exc:
        logger.error(f"Connection failure: {exc}", exc_info=True)
        raise
