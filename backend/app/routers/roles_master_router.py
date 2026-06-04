"""
RolesMaster endpoints — CRUD via /roles prefix.
Single-record operations use numeric id; duplicates are checked on (role_name, team).
DELETE replaced by PATCH /{role_id}/status for soft activate / deactivate.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud import roles_master_crud
from app.init_db import get_db
from app.schemas.roles_master_schema import (
    RolesMasterCreate,
    RolesMasterResponse,
    RolesMasterUpdate,
)

router = APIRouter(prefix="/roles", tags=["Roles Master"])


class StatusUpdate(BaseModel):
    active_status: bool


# ── Create ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=RolesMasterResponse, status_code=status.HTTP_201_CREATED)
def create_role(role: RolesMasterCreate, db: Session = Depends(get_db)):
    """Create a new role. Returns 400 if (role_name, team) already exists."""
    if roles_master_crud.get_role_by_name_and_team(db, role.role_name, role.team):
        raise HTTPException(status_code=400, detail="Role already exists in this team")
    return roles_master_crud.create_role(db, role)


# ── Read all ──────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[RolesMasterResponse])
def list_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return roles_master_crud.get_roles(db, skip=skip, limit=limit)


@router.get("/active", response_model=List[RolesMasterResponse])
def list_active_roles(db: Session = Depends(get_db)):
    return roles_master_crud.get_active_roles(db)


# ── Read / Update / Status by id ──────────────────────────────────────────────
@router.get("/{role_id}", response_model=RolesMasterResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = roles_master_crud.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/{role_id}", response_model=RolesMasterResponse)
def update_role(role_id: int, role_data: RolesMasterUpdate, db: Session = Depends(get_db)):
    """Partially update a role. Returns 409 if the new (role_name, team) pair already exists."""
    existing = roles_master_crud.get_role(db, role_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Role not found")
    new_name = role_data.role_name or existing.role_name
    new_team = role_data.team or existing.team
    if (new_name, new_team) != (existing.role_name, existing.team):
        conflict = roles_master_crud.get_role_by_name_and_team(db, new_name, new_team)
        if conflict:
            raise HTTPException(status_code=409, detail="Role already exists in this team")
    updated = roles_master_crud.update_role(db, role_id, role_data)
    return updated


@router.patch("/{role_id}/status", response_model=RolesMasterResponse)
def set_role_status(role_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    updated = roles_master_crud.set_role_active_status(db, role_id, body.active_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Role not found")
    return updated


# ── Delete ────────────────────────────────────────────────────────────────────
@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """Permanently delete a role by ID."""
    role = roles_master_crud.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    roles_master_crud.delete_role(db, role_id)
