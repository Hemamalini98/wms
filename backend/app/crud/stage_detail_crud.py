from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models.stage_detail import StageDetail
from app.schemas.stage_detail_schema import BulkPlannedCreate, StageDetailCreate, StageDetailUpdate


def _calc_hours(start: Optional[datetime], end: Optional[datetime]) -> Optional[float]:
    if start and end and end >= start:
        return round((end - start).total_seconds() / 3600, 2)
    return None


def _open_row(db: Session, project: str, chapters: str, stage_name: str) -> Optional[StageDetail]:
    """Return the most recent row for this (project, chapters, stage_name) that has no actual_end_date."""
    return db.execute(
        select(StageDetail)
        .where(
            and_(
                StageDetail.project      == project,
                StageDetail.chapters     == chapters,
                StageDetail.stage_name   == stage_name,
                StageDetail.actual_end_date.is_(None),
            )
        )
        .order_by(StageDetail.created_at.desc())
    ).scalars().first()


def _any_row(db: Session, project: str, chapters: str, stage_name: str) -> Optional[StageDetail]:
    """Return the most recent row for this combo regardless of open/closed state."""
    return db.execute(
        select(StageDetail)
        .where(
            and_(
                StageDetail.project    == project,
                StageDetail.chapters   == chapters,
                StageDetail.stage_name == stage_name,
            )
        )
        .order_by(StageDetail.created_at.desc())
    ).scalars().first()


def _close_row(row: StageDetail, now: datetime) -> None:
    """Close a row: stamp actual_end_date, compute hours, mark Completed, flag delay days."""
    row.actual_end_date       = now
    row.total_time_taken      = _calc_hours(row.actual_start_date, now)
    row.stage_status          = "Completed"
    row.stage_activity_status = "Completed"
    if row.planned_end_date and now.date() > row.planned_end_date.date():
        row.delayed    = True
        row.delay_days = (now.date() - row.planned_end_date.date()).days


# ── Basic CRUD ──────────────────────────────────────────────────────────────────

def create_stage_detail(db: Session, data: StageDetailCreate) -> StageDetail:
    row = StageDetail(**data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_stage_detail(db: Session, detail_id: int) -> Optional[StageDetail]:
    return db.execute(select(StageDetail).where(StageDetail.id == detail_id)).scalars().first()


def get_stage_details(db: Session, skip: int = 0, limit: int = 100) -> List[StageDetail]:
    return list(db.execute(select(StageDetail).offset(skip).limit(limit)).scalars().all())


def get_details_by_chapter(db: Session, project: str, chapters: str) -> List[StageDetail]:
    return list(db.execute(
        select(StageDetail).where(StageDetail.project == project, StageDetail.chapters == chapters)
    ).scalars().all())


def get_details_by_project(db: Session, project: str) -> List[StageDetail]:
    return list(db.execute(select(StageDetail).where(StageDetail.project == project)).scalars().all())


def update_stage_detail(db: Session, detail_id: int, data: StageDetailUpdate) -> Optional[StageDetail]:
    row = get_stage_detail(db, detail_id)
    if not row:
        return None
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


# ── Planning: bulk insert on approval ──────────────────────────────────────────

def create_planned_rows(db: Session, payload: BulkPlannedCreate) -> List[StageDetail]:
    """
    Called once when planning is approved.
    Inserts one row per chapter × stage with planned start/end dates.
    assignee_name is NULL (unassigned) by default.
    Each row is a history record — multiple rows per (project, chapters, stage_name)
    are intentional for activity tracking.
    """
    complexity = payload.complexity_level.value if payload.complexity_level else None
    rows: List[StageDetail] = []
    for item in payload.items:
        row = StageDetail(
            client                = payload.client,
            project               = payload.project,
            chapters              = item.chapters,
            stage_name            = item.stage_name,
            workflow              = payload.workflow,
            complexity_level      = complexity,
            project_manager_name  = payload.project_manager_name,
            assignee_name         = None,
            planned_start_date    = item.planned_start_date,
            planned_end_date      = item.planned_end_date,
            sla                   = item.sla,
            stage_status          = "In-progress",
            stage_activity_status = "In-progress",
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for r in rows:
        db.refresh(r)
    return rows


# ── Stage transition ────────────────────────────────────────────────────────────

def stage_transition(
    db: Session,
    project: str,
    chapters: str,
    from_stage: str,
    to_stage: str,
    now: datetime,
) -> Optional[StageDetail]:
    """
    Called when the chapter moves to another stage (Next or Prev button).
    - Closes the open row for from_stage (sets actual_end_date).
    - Opens the next stage: if an open planned row exists, sets actual_start_date on it;
      otherwise creates a new row copying metadata from the old stage.
    Returns the new (opened) stage row.
    """
    # 1. Close old stage
    old_row = _open_row(db, project, chapters, from_stage)
    if old_row:
        _close_row(old_row, now)

    # 2. Open new stage — snapshot metadata from old_row BEFORE commit expires it
    template = _any_row(db, project, chapters, from_stage) or old_row
    t_client   = template.client               if template else project
    t_workflow = template.workflow             if template else "Workflow1"
    t_complex  = template.complexity_level     if template else None
    t_pm       = template.project_manager_name if template else None

    new_row = _open_row(db, project, chapters, to_stage)
    if new_row:
        # Planned row already exists — just stamp actual start
        new_row.actual_start_date = now
    else:
        # No row for to_stage yet — look for planned row regardless of open/closed state
        planned = _any_row(db, project, chapters, to_stage)
        new_row = StageDetail(
            client               = t_client,
            project              = project,
            chapters             = chapters,
            stage_name           = to_stage,
            workflow             = t_workflow,
            complexity_level     = t_complex,
            project_manager_name = t_pm,
            planned_start_date   = planned.planned_start_date if planned else None,
            planned_end_date     = planned.planned_end_date   if planned else None,
            sla                  = planned.sla                if planned else None,
            actual_start_date    = now,
            stage_status         = "In-progress",
            stage_activity_status= "In-progress",
        )
        db.add(new_row)

    db.commit()
    if new_row:
        db.refresh(new_row)
    return new_row


# ── Assignee change: close current row + open new row ─────────────────────────

def assign_to_stage(
    db: Session,
    project: str,
    chapters: str,
    stage_name: str,
    new_assignee: Optional[str],
    now: datetime,
) -> Optional[StageDetail]:
    """
    Called when the assignee on a chapter card changes.
    - Closes the current open row for this (project, chapters, stage_name).
    - If new_assignee is set, creates a new row copying all metadata + planned dates,
      with actual_start_date = now and the new assignee.
    Returns the newly created row (or None if assignee was cleared).
    """
    # Single query: get the current open row; also use it as the template source
    open_row = _open_row(db, project, chapters, stage_name)
    template = open_row or _any_row(db, project, chapters, stage_name)

    # Close the current open row (in-memory; committed below)
    if open_row:
        _close_row(open_row, now)

    if not new_assignee:
        if open_row:
            db.commit()
        return None

    # Snapshot fields from template BEFORE commit (commit expires attributes)
    t_client   = template.client               if template else project
    t_workflow = template.workflow             if template else "Workflow1"
    t_complex  = template.complexity_level     if template else None
    t_pm       = template.project_manager_name if template else None
    t_ps       = template.planned_start_date   if template else None
    t_pe       = template.planned_end_date     if template else None
    t_sla      = template.sla                  if template else None

    # Create new row for the new assignee
    new_row = StageDetail(
        client               = t_client,
        project              = project,
        chapters             = chapters,
        stage_name           = stage_name,
        workflow             = t_workflow,
        complexity_level     = t_complex,
        project_manager_name = t_pm,
        planned_start_date   = t_ps,
        planned_end_date     = t_pe,
        sla                  = t_sla,
        assignee_name        = new_assignee,
        actual_start_date    = now,
        stage_status         = "In-progress",
        stage_activity_status= "In-progress",
    )
    db.add(new_row)
    db.commit()
    db.refresh(new_row)
    return new_row


# ── Cascade delay: shift planned dates for subsequent stages ───────────────────

def shift_planned_dates(
    db: Session,
    project: str,
    chapters: str,
    stage_names: List[str],
    days: int,
) -> None:
    """
    Called when a stage completes late.
    Shifts planned_start_date and planned_end_date forward by `days` calendar days
    for every stage_detail row that belongs to the given subsequent stages.
    """
    if not stage_names or days <= 0:
        return
    delta = timedelta(days=days)
    rows = db.execute(
        select(StageDetail).where(
            and_(
                StageDetail.project  == project,
                StageDetail.chapters == chapters,
                StageDetail.stage_name.in_(stage_names),
            )
        )
    ).scalars().all()
    for row in rows:
        if row.planned_start_date:
            row.planned_start_date = row.planned_start_date + delta
        if row.planned_end_date:
            row.planned_end_date   = row.planned_end_date   + delta
    db.commit()


# ── PM update for whole project ────────────────────────────────────────────────

def update_pm_for_project(db: Session, project: str, pm_name: Optional[str]) -> int:
    rows = list(db.execute(select(StageDetail).where(StageDetail.project == project)).scalars().all())
    for r in rows:
        r.project_manager_name = pm_name
    db.commit()
    return len(rows)
