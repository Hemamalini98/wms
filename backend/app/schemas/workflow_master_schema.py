from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class StageEntry(BaseModel):
    stage_name:     str
    previous_stage: Optional[str] = None
    next_stage:     Optional[str] = None


class WorkflowCreate(BaseModel):
    workflow_name: str
    description:   Optional[str] = None
    active_status: bool = True
    stages:        List[StageEntry]


class WorkflowUpdate(BaseModel):
    workflow_name: Optional[str] = None   # supply to rename
    description:   Optional[str] = None
    active_status: Optional[bool] = None
    stages:        List[StageEntry]


class WorkflowStageUpdate(BaseModel):
    stage_name:     Optional[str] = None
    previous_stage: Optional[str] = None
    next_stage:     Optional[str] = None
    active_status:  Optional[bool] = None


class WorkflowStageResponse(BaseModel):
    id:             int
    workflow_name:  str
    stage_name:     str
    previous_stage: Optional[str]
    next_stage:     Optional[str]
    description:    Optional[str]
    active_status:  bool
    created_at:     datetime
    updated_at:     datetime

    model_config = {"from_attributes": True}
