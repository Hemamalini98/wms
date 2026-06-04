from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud import stage_activity_master_crud
from app.init_db import get_db
from app.schemas.stage_activity_master_schema import (
    StageActivityMasterCreate,
    StageActivityMasterResponse,
    StageActivityMasterUpdate,
)

router = APIRouter(prefix="/stage-activities", tags=["Stage Activity Master"])


class StatusUpdate(BaseModel):
    active_status: bool


@router.post("/", response_model=StageActivityMasterResponse, status_code=status.HTTP_201_CREATED)
def create_stage_activity(activity: StageActivityMasterCreate, db: Session = Depends(get_db)):
    if stage_activity_master_crud.get_stage_activity_by_name(db, activity.stage_activity_name):
        raise HTTPException(status_code=400, detail="Stage activity name already exists")
    return stage_activity_master_crud.create_stage_activity(db, activity)


@router.get("/", response_model=List[StageActivityMasterResponse])
def list_stage_activities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return stage_activity_master_crud.get_stage_activities(db, skip=skip, limit=limit)


@router.get("/active", response_model=List[StageActivityMasterResponse])
def list_active_stage_activities(db: Session = Depends(get_db)):
    return stage_activity_master_crud.get_active_stage_activities(db)


@router.get("/{activity_name}", response_model=StageActivityMasterResponse)
def get_stage_activity(activity_name: str, db: Session = Depends(get_db)):
    activity = stage_activity_master_crud.get_stage_activity_by_name(db, activity_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Stage activity not found")
    return activity


@router.put("/{activity_name}", response_model=StageActivityMasterResponse)
def update_stage_activity(activity_name: str, data: StageActivityMasterUpdate, db: Session = Depends(get_db)):
    updated = stage_activity_master_crud.update_stage_activity(db, activity_name, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Stage activity not found")
    return updated


@router.patch("/{activity_name}/status", response_model=StageActivityMasterResponse)
def set_stage_activity_status(activity_name: str, body: StatusUpdate, db: Session = Depends(get_db)):
    updated = stage_activity_master_crud.set_stage_activity_active_status(db, activity_name, body.active_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Stage activity not found")
    return updated
