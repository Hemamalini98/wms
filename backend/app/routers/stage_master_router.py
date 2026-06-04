from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud import stage_master_crud
from app.init_db import get_db
from app.schemas.stage_master_schema import StageMasterCreate, StageMasterResponse, StageMasterUpdate

router = APIRouter(prefix="/stages", tags=["Stage Master"])


class StatusUpdate(BaseModel):
    active_status: bool


@router.post("/", response_model=StageMasterResponse, status_code=status.HTTP_201_CREATED)
def create_stage(stage: StageMasterCreate, db: Session = Depends(get_db)):
    if stage_master_crud.get_stage_by_name(db, stage.stage_name):
        raise HTTPException(status_code=400, detail="Stage name already exists")
    return stage_master_crud.create_stage(db, stage)


@router.get("/", response_model=List[StageMasterResponse])
def list_stages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return stage_master_crud.get_stages(db, skip=skip, limit=limit)


@router.get("/active", response_model=List[StageMasterResponse])
def list_active_stages(db: Session = Depends(get_db)):
    return stage_master_crud.get_active_stages(db)


@router.get("/{stage_name}", response_model=StageMasterResponse)
def get_stage(stage_name: str, db: Session = Depends(get_db)):
    stage = stage_master_crud.get_stage_by_name(db, stage_name)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    return stage


@router.put("/{stage_name}", response_model=StageMasterResponse)
def update_stage(stage_name: str, data: StageMasterUpdate, db: Session = Depends(get_db)):
    updated = stage_master_crud.update_stage(db, stage_name, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Stage not found")
    return updated


@router.patch("/{stage_name}/status", response_model=StageMasterResponse)
def set_stage_status(stage_name: str, body: StatusUpdate, db: Session = Depends(get_db)):
    updated = stage_master_crud.set_stage_active_status(db, stage_name, body.active_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Stage not found")
    return updated
