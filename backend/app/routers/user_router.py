"""
User endpoints — CRUD via /users prefix.
GET / PUT use email as the lookup key.
DELETE replaced by PATCH /{email}/status for soft activate / deactivate.
"""

from typing import List

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud import roles_master_crud, user_crud
from app.init_db import get_db
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


# ── Helpers ───────────────────────────────────────────────────────────────────
class StatusUpdate(BaseModel):
    active_status: bool


def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _validate_role(db, role_name: str):
    """Raise 400 if role_name does not exist or has no active entry in roles_master."""
    roles = roles_master_crud.get_roles_by_name(db, role_name)
    if not roles:
        raise HTTPException(status_code=400, detail=f"Role '{role_name}' does not exist in roles_master")
    if not any(r.active_status for r in roles):
        raise HTTPException(status_code=400, detail=f"Role '{role_name}' is inactive and cannot be assigned")


# ── Create ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user. Validates role against roles_master."""
    _validate_role(db, user.role)
    if user_crud.get_user_by_username(db, user.user_name):
        raise HTTPException(status_code=400, detail="Username already taken")
    if user_crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = user.model_copy(update={"password": _hash_password(user.password)})
    return user_crud.create_user(db, hashed)


# ── Read all ──────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Return a paginated list of all users."""
    return user_crud.get_users(db, skip=skip, limit=limit)


# ── Read by id ────────────────────────────────────────────────────────────────
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Return a single user by ID."""
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── Update by id ──────────────────────────────────────────────────────────────
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Partially update a user by ID."""
    if user_data.role:
        _validate_role(db, user_data.role)
    if user_data.password:
        user_data = user_data.model_copy(update={"password": _hash_password(user_data.password)})
    updated = user_crud.update_user(db, user_id, user_data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


# ── Activate / Deactivate ─────────────────────────────────────────────────────
@router.patch("/{user_id}/status", response_model=UserResponse)
def set_user_status(user_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    """Set a user active or inactive by ID."""
    updated = user_crud.set_user_active_status(db, user_id, body.active_status)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated
