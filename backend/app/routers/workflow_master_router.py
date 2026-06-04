from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import workflow_master_crud
from app.init_db import get_db
from app.schemas.workflow_master_schema import (
    WorkflowCreate,
    WorkflowStageResponse,
    WorkflowStageUpdate,
    WorkflowUpdate,
)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


# ── Workflow-level ─────────────────────────────────────────────────────────────

@router.get("/", response_model=List[str])
def list_workflow_names(db: Session = Depends(get_db)):
    return workflow_master_crud.list_workflow_names(db)


@router.get("/all", response_model=List[WorkflowStageResponse])
def get_all_stages(db: Session = Depends(get_db)):
    return workflow_master_crud.get_all_stages(db)


@router.post("/", response_model=List[WorkflowStageResponse], status_code=status.HTTP_201_CREATED)
def create_workflow(data: WorkflowCreate, db: Session = Depends(get_db)):
    if not data.stages:
        raise HTTPException(status_code=400, detail="Workflow must have at least one stage")
    return workflow_master_crud.save_workflow(
        db, data.workflow_name.strip(), data.stages,
        description=data.description, active_status=data.active_status,
    )


@router.get("/{workflow_name}", response_model=List[WorkflowStageResponse])
def get_workflow(workflow_name: str, db: Session = Depends(get_db)):
    stages = workflow_master_crud.get_workflow_stages(db, workflow_name)
    if not stages:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return stages


@router.put("/{workflow_name}", response_model=List[WorkflowStageResponse])
def update_workflow(workflow_name: str, data: WorkflowUpdate, db: Session = Depends(get_db)):
    target_name = (data.workflow_name or workflow_name).strip()
    if not data.stages:
        raise HTTPException(status_code=400, detail="Workflow must have at least one stage")
    return workflow_master_crud.save_workflow(
        db, target_name, data.stages,
        description=data.description,
        active_status=data.active_status if data.active_status is not None else True,
    )


@router.delete("/{workflow_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(workflow_name: str, db: Session = Depends(get_db)):
    deleted = workflow_master_crud.delete_workflow(db, workflow_name)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Workflow not found")


# ── Stage-level ────────────────────────────────────────────────────────────────

@router.put("/{workflow_name}/stages/{stage_id}", response_model=WorkflowStageResponse)
def update_stage(workflow_name: str, stage_id: int, data: WorkflowStageUpdate, db: Session = Depends(get_db)):
    stage = workflow_master_crud.update_stage(db, stage_id, data)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    return stage


@router.delete("/{workflow_name}/stages/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stage(workflow_name: str, stage_id: int, db: Session = Depends(get_db)):
    if not workflow_master_crud.delete_stage(db, stage_id):
        raise HTTPException(status_code=404, detail="Stage not found")


# ── Navigation helpers ─────────────────────────────────────────────────────────

@router.get("/{workflow_name}/next/{stage_name}")
def get_next_stage(workflow_name: str, stage_name: str, db: Session = Depends(get_db)):
    return {"next_stage": workflow_master_crud.get_next_stage(db, workflow_name, stage_name)}


@router.get("/{workflow_name}/previous/{stage_name}")
def get_previous_stage(workflow_name: str, stage_name: str, db: Session = Depends(get_db)):
    return {"previous_stage": workflow_master_crud.get_previous_stage(db, workflow_name, stage_name)}
