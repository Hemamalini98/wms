"""
Application entry point.
Run with:  uvicorn main:app --reload   (from the backend/ directory)
"""

import logging
import logging.handlers
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.init_db import create_tables, SessionLocal
from app.routers import (
    chapter_info_router,
    client_router,
    project_router,
    roles_master_router,
    stage_activity_master_router,
    stage_detail_router,
    stage_master_router,
    upload_router,
    user_router,
    workflow_master_router,
)
from app.routers.auth_router import router as auth_router


# ── Logging configuration ─────────────────────────────────────────────────────
def _setup_logging() -> None:
    """Configure logging to console and file."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Console handler (INFO level and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (DEBUG level and above) — rotates daily and deletes logs after 1 day
    file_handler = logging.handlers.TimedRotatingFileHandler(
        "app.log",
        when="midnight",       # Rotate at midnight
        interval=1,            # Every 1 day
        backupCount=0,         # Don't keep backup files (deletes previous day's log)
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)


_setup_logging()
logger = logging.getLogger(__name__)


def _ensure_admin_user() -> None:
    """Create the default admin user on first run if it doesn't exist."""
    import bcrypt
    from sqlalchemy import select
    from app.models.user import User

    db = SessionLocal()
    try:
        exists = db.execute(
            select(User).where(User.user_name == "admin")
        ).scalars().first()
        if not exists:
            hashed = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
            db.add(User(
                user_name="admin",
                email="admin@wms.com",
                password=hashed,
                role="admin",
                team="Admin Team",
                customer_access=[],
                active_status=True,
            ))
            db.commit()
            logger.info("Default admin user created  (admin / admin123)")
        else:
            logger.info("Admin user already exists — skipped")
    except Exception as exc:
        db.rollback()
        logger.warning(f"Could not ensure admin user — {exc}")
    finally:
        db.close()


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    _ensure_admin_user()
    yield


# ── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Workflow Management System",
    description="REST API for managing internal users, external clients, and their projects.",
    version="1.0.0",
    lifespan=lifespan,
)


# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(roles_master_router.router)
app.include_router(user_router.router)
app.include_router(client_router.router)
app.include_router(project_router.router)
app.include_router(stage_master_router.router)
app.include_router(stage_activity_master_router.router)
app.include_router(chapter_info_router.router)
app.include_router(stage_detail_router.router)
app.include_router(upload_router.router)
app.include_router(workflow_master_router.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Workflow Management System"}
