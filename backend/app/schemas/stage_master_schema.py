from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.schemas.stage_activity_master_schema import StageActivityMasterResponse


class StageMasterBase(BaseModel):
    stage_name:       str
    description:      Optional[str]   = None
    stage_activities: List[int]       = []
    sla_level1:       Optional[int]   = None
    sla_level2:       Optional[int]   = None
    sla_level3:       Optional[int]   = None
    roles:            List[str]       = []
    active_status:    bool            = True


class StageMasterCreate(StageMasterBase):
    pass


class StageMasterUpdate(BaseModel):
    stage_name:       Optional[str]       = None
    description:      Optional[str]       = None
    stage_activities: Optional[List[int]] = None
    sla_level1:       Optional[int]       = None
    sla_level2:       Optional[int]       = None
    sla_level3:       Optional[int]       = None
    roles:            Optional[List[str]] = None
    active_status:    Optional[bool]      = None


class StageMasterResponse(BaseModel):
    id:               int
    stage_name:       str
    description:      Optional[str]                       = None
    stage_activities: List[StageActivityMasterResponse]   = []
    sla_level1:       Optional[int]                       = None
    sla_level2:       Optional[int]                       = None
    sla_level3:       Optional[int]                       = None
    roles:            List[str]                           = []
    active_status:    bool
    created_at:       datetime

    model_config = {"from_attributes": True}
