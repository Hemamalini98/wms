"""
Pydantic schemas for the RolesMaster resource.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RolesMasterBase(BaseModel):
    role_name: str
    team: str
    description: Optional[str] = None
    active_status: bool = True


class RolesMasterCreate(RolesMasterBase):
    pass


class RolesMasterUpdate(BaseModel):
    """Partial update — only supplied fields are changed."""
    role_name: Optional[str] = None
    team: Optional[str] = None
    description: Optional[str] = None
    active_status: Optional[bool] = None


class RolesMasterResponse(RolesMasterBase):
    """Full role record returned from the API."""
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
