from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, model_validator

from app.enums import ChapterStatus, ComplexityLevel


class StageDetailBase(BaseModel):
    client:                str
    project:               str
    chapters:              str
    project_manager_name:  Optional[str]             = None
    assignee_name:         Optional[str]             = None
    planned_start_date:    Optional[datetime]        = None
    planned_end_date:      Optional[datetime]        = None
    actual_start_date:     Optional[datetime]        = None
    actual_end_date:       Optional[datetime]        = None
    stage_name:            str
    stage_activity:        Optional[str]             = None
    workflow:              str                       = "Workflow1"
    complexity_level:      Optional[ComplexityLevel] = None
    stage_level:           Optional[int]             = None
    sla:                   Optional[int]             = None
    stage_status:          ChapterStatus             = ChapterStatus.in_progress
    stage_activity_status: ChapterStatus             = ChapterStatus.in_progress
    delayed:               bool                      = False
    delay_days:            Optional[int]             = None
    remarks:               Optional[str]             = None

    @model_validator(mode="after")
    def validate_and_compute(self):
        if self.planned_end_date and self.planned_start_date and self.planned_end_date < self.planned_start_date:
            raise ValueError("planned_end_date must be >= planned_start_date")
        if self.actual_end_date and self.actual_start_date and self.actual_end_date < self.actual_start_date:
            raise ValueError("actual_end_date must be >= actual_start_date")
        if self.sla is not None and self.sla < 0:
            raise ValueError("sla must be >= 0")
        if self.stage_level is not None and self.stage_level < 0:
            raise ValueError("stage_level must be >= 0")
        return self


class StageDetailCreate(StageDetailBase):
    pass


class StageDetailUpdate(BaseModel):
    client:                Optional[str]             = None
    project:               Optional[str]             = None
    chapters:              Optional[str]             = None
    project_manager_name:  Optional[str]             = None
    assignee_name:         Optional[str]             = None
    planned_start_date:    Optional[datetime]        = None
    planned_end_date:      Optional[datetime]        = None
    actual_start_date:     Optional[datetime]        = None
    actual_end_date:       Optional[datetime]        = None
    stage_name:            Optional[str]             = None
    stage_activity:        Optional[str]             = None
    workflow:              Optional[str]             = None
    complexity_level:      Optional[ComplexityLevel] = None
    stage_level:           Optional[int]             = None
    sla:                   Optional[int]             = None
    stage_status:          Optional[ChapterStatus]   = None
    stage_activity_status: Optional[ChapterStatus]   = None
    delayed:               Optional[bool]            = None
    delay_days:            Optional[int]             = None
    remarks:               Optional[str]             = None

    @model_validator(mode="after")
    def validate_constraints(self):
        if self.planned_end_date and self.planned_start_date and self.planned_end_date < self.planned_start_date:
            raise ValueError("planned_end_date must be >= planned_start_date")
        if self.actual_end_date and self.actual_start_date and self.actual_end_date < self.actual_start_date:
            raise ValueError("actual_end_date must be >= actual_start_date")
        if self.sla is not None and self.sla < 0:
            raise ValueError("sla must be >= 0")
        if self.stage_level is not None and self.stage_level < 0:
            raise ValueError("stage_level must be >= 0")
        return self


class BulkPlannedItem(BaseModel):
    chapters:           str
    stage_name:         str
    planned_start_date: datetime
    planned_end_date:   datetime
    sla:                Optional[int] = None


class BulkPlannedCreate(BaseModel):
    client:               str
    project:              str
    workflow:             str
    complexity_level:     Optional[ComplexityLevel] = None
    project_manager_name: Optional[str]             = None
    items:                List[BulkPlannedItem]


class StageDetailResponse(StageDetailBase):
    id:               int
    total_time_taken: Optional[float] = None
    created_at:       datetime
    updated_at:       datetime

    model_config = {"from_attributes": True}
