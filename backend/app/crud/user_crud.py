"""
Reusable CRUD operations for the User model.
Passwords must be hashed by the caller (router layer) before reaching here.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate


# ── Insert ────────────────────────────────────────────────────────────────────
def create_user(db: Session, user_data: UserCreate) -> User:
    """Insert a new user row (password must already be hashed)."""
    db_user = User(**user_data.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ── Fetch single ──────────────────────────────────────────────────────────────
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Return a single user by primary key, or None."""
    stmt = select(User).where(User.id == user_id)
    return db.execute(stmt).scalars().first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Return a single user by email address, or None."""
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalars().first()


def get_user_by_username(db: Session, user_name: str) -> Optional[User]:
    """Return a single user by username, or None."""
    stmt = select(User).where(User.user_name == user_name)
    return db.execute(stmt).scalars().first()


# ── Fetch all ─────────────────────────────────────────────────────────────────
def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Return a paginated list of all users."""
    stmt = select(User).offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


# ── Update by id ──────────────────────────────────────────────────────────────
def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """Patch an existing user (looked up by id) with only the supplied fields."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


# ── Active / Inactive ─────────────────────────────────────────────────────────
def set_user_active_status(db: Session, user_id: int, active_status: bool) -> Optional[User]:
    """Set active_status for the user identified by id. Returns None if not found."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db_user.active_status = active_status
    db.commit()
    db.refresh(db_user)
    return db_user
