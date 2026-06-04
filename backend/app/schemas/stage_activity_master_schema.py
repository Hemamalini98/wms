from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StageActivityMasterBase(BaseModel):
    stage_activity_name: str
    description: Optional[str] = None
    active_status: bool = True


class StageActivityMasterCreate(StageActivityMasterBase):
    pass


class StageActivityMasterUpdate(BaseModel):
    stage_activity_name: Optional[str] = None
    description: Optional[str] = None
    active_status: Optional[bool] = None


class StageActivityMasterResponse(StageActivityMasterBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
