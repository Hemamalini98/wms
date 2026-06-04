"""
Application entry point.
Run with:  uvicorn main:app --reload   (from the backend/ directory)
"""

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
            print("[startup] Default admin user created  (admin / admin123)")
        else:
            print("[startup] Admin user already exists — skipped")
    except Exception as exc:
        db.rollback()
        print(f"[startup] Warning: could not ensure admin user — {exc}")
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
