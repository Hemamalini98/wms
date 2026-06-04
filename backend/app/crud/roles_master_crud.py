"""
Reusable CRUD operations for the RolesMaster model.
Unique key is (role_name, team); single-record mutations use id.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.roles_master import RolesMaster
from app.schemas.roles_master_schema import RolesMasterCreate, RolesMasterUpdate


# ── Insert ────────────────────────────────────────────────────────────────────
def create_role(db: Session, role_data: RolesMasterCreate) -> RolesMaster:
    db_role = RolesMaster(**role_data.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


# ── Fetch single ──────────────────────────────────────────────────────────────
def get_role(db: Session, role_id: int) -> Optional[RolesMaster]:
    return db.execute(select(RolesMaster).where(RolesMaster.id == role_id)).scalars().first()


def get_roles_by_name(db: Session, role_name: str) -> List[RolesMaster]:
    """Return all roles with a given name (may span multiple teams)."""
    return list(
        db.execute(select(RolesMaster).where(RolesMaster.role_name == role_name)).scalars().all()
    )


def get_role_by_name_and_team(db: Session, role_name: str, team: str) -> Optional[RolesMaster]:
    return db.execute(
        select(RolesMaster).where(
            RolesMaster.role_name == role_name,
            RolesMaster.team == team,
        )
    ).scalars().first()


# ── Fetch all ─────────────────────────────────────────────────────────────────
def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[RolesMaster]:
    stmt = select(RolesMaster).order_by(RolesMaster.team, RolesMaster.role_name).offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def get_active_roles(db: Session) -> List[RolesMaster]:
    stmt = (
        select(RolesMaster)
        .where(RolesMaster.active_status == True)  # noqa: E712
        .order_by(RolesMaster.team, RolesMaster.role_name)
    )
    return list(db.execute(stmt).scalars().all())


# ── Update ────────────────────────────────────────────────────────────────────
def update_role(db: Session, role_id: int, role_data: RolesMasterUpdate) -> Optional[RolesMaster]:
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    for field, value in role_data.model_dump(exclude_unset=True).items():
        setattr(db_role, field, value)
    db.commit()
    db.refresh(db_role)
    return db_role


# ── Delete ────────────────────────────────────────────────────────────────────
def delete_role(db: Session, role_id: int) -> None:
    db_role = get_role(db, role_id)
    if db_role:
        db.delete(db_role)
        db.commit()


# ── Active / Inactive ─────────────────────────────────────────────────────────
def set_role_active_status(db: Session, role_id: int, active_status: bool) -> Optional[RolesMaster]:
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    db_role.active_status = active_status
    db.commit()
    db.refresh(db_role)
    return db_role
