from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.schemas.project_schema import ProjectResponse


class ClientBase(BaseModel):
    category_type:      str
    contact_type:       str
    first_name:         Optional[str] = None
    surname:            Optional[str] = None
    name_company:       Optional[str] = None
    company:            Optional[str] = None
    division:           Optional[str] = None
    designation:        Optional[str] = None
    department:         Optional[str] = None
    email:              Optional[str] = None
    website:            Optional[str] = None
    vendor_number:      Optional[str] = None
    address1:           Optional[str] = None
    address2:           Optional[str] = None
    city:               Optional[str] = None
    state:              Optional[str] = None
    country:            Optional[str] = None
    zip_code:           Optional[str] = None
    sub_specialisation: Optional[str] = None
    working_hours:      Optional[str] = None
    contact_hours:      Optional[str] = None
    phone_main:         Optional[str] = None
    phone_additional:   Optional[str] = None
    active_status:      bool = True
    created_by:         Optional[int] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    category_type:      Optional[str] = None
    contact_type:       Optional[str] = None
    first_name:         Optional[str] = None
    surname:            Optional[str] = None
    name_company:       Optional[str] = None
    company:            Optional[str] = None
    division:           Optional[str] = None
    designation:        Optional[str] = None
    department:         Optional[str] = None
    email:              Optional[str] = None
    website:            Optional[str] = None
    vendor_number:      Optional[str] = None
    address1:           Optional[str] = None
    address2:           Optional[str] = None
    city:               Optional[str] = None
    state:              Optional[str] = None
    country:            Optional[str] = None
    zip_code:           Optional[str] = None
    sub_specialisation: Optional[str] = None
    working_hours:      Optional[str] = None
    contact_hours:      Optional[str] = None
    phone_main:         Optional[str] = None
    phone_additional:   Optional[str] = None
    active_status:      Optional[bool] = None


class ClientListResponse(BaseModel):
    """Lightweight list response — omits nested projects to avoid N+1 queries."""
    id: int
    category_type: str
    contact_type: str
    first_name: Optional[str] = None
    surname: Optional[str] = None
    name_company: Optional[str] = None
    company: Optional[str] = None
    division: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    vendor_number: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    sub_specialisation: Optional[str] = None
    working_hours: Optional[str] = None
    contact_hours: Optional[str] = None
    phone_main: Optional[str] = None
    phone_additional: Optional[str] = None
    active_status: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClientResponse(ClientBase):
    """Full detail response including nested projects (single-record endpoints only)."""
    id: int
    created_at: datetime
    updated_at: datetime
    projects: List[ProjectResponse] = []

    model_config = {"from_attributes": True}
