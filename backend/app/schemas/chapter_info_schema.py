from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, field_validator

from app.enums import ChapterStatus, ComplexityLevel, ProjectPriority, PublishedStatus


class ChapterInfoBase(BaseModel):
    client:                 str
    project:                str
    chapters:               str
    chapter_title:          Optional[str]            = None
    project_manager_name:   Optional[str]            = None
    due_date:               Optional[date]           = None
    stage_name:             Optional[str]            = None
    current_stage_activity: Optional[str]            = None
    current_assignee_name:  Optional[str]            = None
    status:                 ChapterStatus            = ChapterStatus.in_progress
    complexity_level:       ComplexityLevel          = ComplexityLevel.medium
    stage_level:            int                      = 1
    workflow:               str                      = "Workflow1"
    published_status:       PublishedStatus          = PublishedStatus.draft
    remarks:                Optional[str]            = None
    manuscript_pages:       Optional[int]            = None
    priority:               ProjectPriority          = ProjectPriority.normal
    delayed_stages:         Optional[Dict[str, int]]  = None

    @field_validator("delayed_stages", mode="before")
    @classmethod
    def coerce_delayed_stages(cls, v: Any) -> Optional[Dict[str, int]]:
        """Convert old array format ['Stage1','Stage2'] → {'Stage1':0,'Stage2':0}."""
        if isinstance(v, list):
            return {s: 0 for s in v if isinstance(s, str)}
        return v


class ChapterInfoCreate(ChapterInfoBase):
    pass


class ChapterInfoUpdate(BaseModel):
    client:                 Optional[str]            = None
    project:                Optional[str]            = None
    chapters:               Optional[str]            = None
    chapter_title:          Optional[str]            = None
    project_manager_name:   Optional[str]            = None
    due_date:               Optional[date]           = None
    stage_name:             Optional[str]            = None
    current_stage_activity: Optional[str]            = None
    current_assignee_name:  Optional[str]            = None
    status:                 Optional[ChapterStatus]  = None
    complexity_level:       Optional[ComplexityLevel]= None
    stage_level:            Optional[int]            = None
    workflow:               Optional[str]            = None
    published_status:       Optional[PublishedStatus]= None
    remarks:                Optional[str]            = None
    manuscript_pages:       Optional[int]            = None
    priority:               Optional[ProjectPriority]= None
    delayed_stages:         Optional[Dict[str, int]]  = None


class ChapterInfoResponse(ChapterInfoBase):
    id:         int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
