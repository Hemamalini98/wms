from datetime import date, datetime
from typing import Any, Optional
from pydantic import BaseModel

from app.enums import ComplexityLevel, ProjectPriority, ProjectStatus


class ProjectBase(BaseModel):
    client_id:        Optional[int] = None
    project_code:     Optional[str] = None
    customer_name:    Optional[str] = None
    division_code:    Optional[str] = None
    customer_contact: Optional[str] = None
    category:         Optional[str] = None
    composition:      Optional[ComplexityLevel] = None
    workflow_name:    Optional[str] = None
    status:           Optional[ProjectStatus] = None
    project_manager:  Optional[str] = None
    sales_person:     Optional[str] = None
    priority:         Optional[ProjectPriority] = None
    project_title:    Optional[str] = None
    edition:          Optional[str] = None
    color:            Optional[str] = None
    trim_size:        Optional[str] = None
    copyright_year:   Optional[int] = None
    manuscript_pages: Optional[int] = None
    estimated_pages:  Optional[int] = None
    actual_pages:     int = 0
    chapter_count:    Optional[int] = None
    isbn_no:          Optional[str] = None
    billing_location: Optional[str] = None
    due_date:         Optional[date] = None
    file_details:     Optional[Any] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    client_id:        Optional[int] = None
    project_code:     Optional[str] = None
    customer_name:    Optional[str] = None
    division_code:    Optional[str] = None
    customer_contact: Optional[str] = None
    category:         Optional[str] = None
    composition:      Optional[ComplexityLevel] = None
    workflow_name:    Optional[str] = None
    status:           Optional[ProjectStatus] = None
    project_manager:  Optional[str] = None
    sales_person:     Optional[str] = None
    priority:         Optional[ProjectPriority] = None
    project_title:    Optional[str] = None
    edition:          Optional[str] = None
    color:            Optional[str] = None
    trim_size:        Optional[str] = None
    copyright_year:   Optional[int] = None
    manuscript_pages: Optional[int] = None
    estimated_pages:  Optional[int] = None
    actual_pages:     Optional[int] = None
    chapter_count:    Optional[int] = None
    isbn_no:          Optional[str] = None
    billing_location: Optional[str] = None
    due_date:         Optional[date] = None
    file_details:     Optional[Any] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
