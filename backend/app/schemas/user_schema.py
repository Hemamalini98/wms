"""
Pydantic schemas for the User resource.

UserCreate   — request body for POST /users  (includes password)
UserUpdate   — request body for PUT /users/{id}  (all fields optional)
UserResponse — API response shape  (password is intentionally excluded)
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    user_name: str
    email: EmailStr
    role: str
    team: str
    customer_access: List[str]                     # array of customer IDs the user can access
    active_status: bool = True


class UserCreate(UserBase):
    """All required fields to create a new user, including the plaintext password
    that the endpoint must hash before persisting."""
    password: str


class UserUpdate(BaseModel):
    """Partial update — only supplied fields are changed."""
    user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None          # will be hashed before saving
    role: Optional[str] = None
    team: Optional[str] = None
    customer_access: Optional[List[str]] = None    # optional on update; omit to leave unchanged
    active_status: Optional[bool] = None


class UserResponse(UserBase):
    """Full user record returned from the API — password is never exposed."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
