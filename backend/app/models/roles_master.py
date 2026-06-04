"""
RolesMaster table — lookup table for all valid user roles in the system.
Unique key is (role_name, team): the same role name can exist in different teams
but not twice within the same team.
User.role is a soft string reference to role_name (no FK — role_name alone is not unique).
"""

from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.init_db import Base


class RolesMaster(Base):
    __tablename__ = "roles_master"

    __table_args__ = (
        UniqueConstraint("role_name", "team", name="uq_roles_name_team"),
    )

    id            = Column(BigInteger, primary_key=True, autoincrement=True)
    role_name     = Column(String(100), nullable=False, index=True)
    team          = Column(String(150), nullable=False)
    description   = Column(Text,        nullable=True)
    active_status = Column(Boolean,     nullable=False, default=True)
    created_at    = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
