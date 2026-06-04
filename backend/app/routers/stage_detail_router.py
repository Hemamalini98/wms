from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud import stage_detail_crud
from app.init_db import get_db
from app.schemas.stage_detail_schema import (
    BulkPlannedCreate,
    StageDetailCreate,
    StageDetailResponse,
    StageDetailUpdate,
)

router = APIRouter(prefix="/stage-details", tags=["Stage Details"])


# ── Planning: bulk insert on approval ──────────────────────────────────────────

@router.post("/plan", response_model=List[StageDetailResponse], status_code=status.HTTP_201_CREATED)
def create_planning_rows(payload: BulkPlannedCreate, db: Session = Depends(get_db)):
    """
    Called when planning is approved.
    Inserts one row per chapter × stage with planned dates and no assignee.
    """
    return stage_detail_crud.create_planned_rows(db, payload)


# ── Basic CRUD ─────────────────────────────────────────────────────────────────

@router.post("/", response_model=StageDetailResponse, status_code=status.HTTP_201_CREATED)
def create_stage_detail(data: StageDetailCreate, db: Session = Depends(get_db)):
    return stage_detail_crud.create_stage_detail(db, data)


@router.get("/", response_model=List[StageDetailResponse])
def list_stage_details(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return stage_detail_crud.get_stage_details(db, skip=skip, limit=limit)


@router.get("/project/{project}", response_model=List[StageDetailResponse])
def list_by_project(project: str, db: Session = Depends(get_db)):
    return stage_detail_crud.get_details_by_project(db, project)


@router.get("/project/{project}/chapter/{chapters}", response_model=List[StageDetailResponse])
def list_by_chapter(project: str, chapters: str, db: Session = Depends(get_db)):
    return stage_detail_crud.get_details_by_chapter(db, project, chapters)


@router.get("/{detail_id}", response_model=StageDetailResponse)
def get_stage_detail(detail_id: int, db: Session = Depends(get_db)):
    row = stage_detail_crud.get_stage_detail(db, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Stage detail not found")
    return row


@router.put("/{detail_id}", response_model=StageDetailResponse)
def update_stage_detail(detail_id: int, data: StageDetailUpdate, db: Session = Depends(get_db)):
    updated = stage_detail_crud.update_stage_detail(db, detail_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Stage detail not found")
    return updated


# ── Assignee change ────────────────────────────────────────────────────────────

class AssignBody(BaseModel):
    assignee_name: Optional[str] = None
    dt:            Optional[datetime] = None


@router.post("/project/{project}/chapter/{chapters}/stage/{stage_name}/assign",
             response_model=Optional[StageDetailResponse])
def assign_to_stage(project: str, chapters: str, stage_name: str,
                    body: AssignBody, db: Session = Depends(get_db)):
    """
    Close the current open row (actual_end_date=now, status=Completed) and
    create a new row for the new assignee (actual_start_date=now, status=In-progress).
    """
    now = body.dt or datetime.now(timezone.utc)
    return stage_detail_crud.assign_to_stage(db, project, chapters, stage_name, body.assignee_name, now)


# ── Stage transition ───────────────────────────────────────────────────────────

class TransitionBody(BaseModel):
    from_stage: str
    to_stage:   str
    dt:         Optional[datetime] = None


@router.post("/project/{project}/chapter/{chapters}/stage-transition",
             response_model=Optional[StageDetailResponse])
def stage_transition(project: str, chapters: str,
                     body: TransitionBody, db: Session = Depends(get_db)):
    """
    Close the old stage row (Completed) and open the new stage row (In-progress, assignee=null).
    """
    now = body.dt or datetime.now(timezone.utc)
    return stage_detail_crud.stage_transition(db, project, chapters, body.from_stage, body.to_stage, now)


# ── Cascade delay: shift planned dates for subsequent stages ───────────────────

class ShiftDatesBody(BaseModel):
    chapters:     str
    stage_names:  List[str]
    days:         int


@router.post("/project/{project}/shift-planned-dates", status_code=200)
def shift_planned_dates(project: str, body: ShiftDatesBody, db: Session = Depends(get_db)):
    """Shift planned_start_date and planned_end_date forward for subsequent stages after a delay."""
    stage_detail_crud.shift_planned_dates(db, project, body.chapters, body.stage_names, body.days)
    return {"ok": True}
