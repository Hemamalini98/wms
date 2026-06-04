from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.workflow_master import WorkflowMaster
from app.schemas.workflow_master_schema import StageEntry, WorkflowStageUpdate


def list_workflow_names(db: Session) -> List[str]:
    rows = db.execute(select(WorkflowMaster.workflow_name).distinct()).scalars().all()
    return sorted(rows)


def get_workflow_stages(db: Session, workflow_name: str) -> List[WorkflowMaster]:
    return db.execute(
        select(WorkflowMaster).where(WorkflowMaster.workflow_name == workflow_name)
    ).scalars().all()


def get_all_stages(db: Session) -> List[WorkflowMaster]:
    return db.execute(select(WorkflowMaster)).scalars().all()


def save_workflow(
    db: Session,
    workflow_name: str,
    stages: List[StageEntry],
    description: Optional[str] = None,
    active_status: bool = True,
) -> List[WorkflowMaster]:
    """Replace all stages for the given workflow name."""
    db.execute(delete(WorkflowMaster).where(WorkflowMaster.workflow_name == workflow_name))
    rows: List[WorkflowMaster] = []
    for s in stages:
        row = WorkflowMaster(
            workflow_name=workflow_name,
            stage_name=s.stage_name,
            previous_stage=s.previous_stage or None,
            next_stage=s.next_stage or None,
            description=description,
            active_status=active_status,
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def update_stage(db: Session, stage_id: int, data: WorkflowStageUpdate) -> Optional[WorkflowMaster]:
    row = db.execute(select(WorkflowMaster).where(WorkflowMaster.id == stage_id)).scalars().first()
    if not row:
        return None
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


def delete_workflow(db: Session, workflow_name: str) -> int:
    result = db.execute(delete(WorkflowMaster).where(WorkflowMaster.workflow_name == workflow_name))
    db.commit()
    return result.rowcount


def delete_stage(db: Session, stage_id: int) -> bool:
    result = db.execute(delete(WorkflowMaster).where(WorkflowMaster.id == stage_id))
    db.commit()
    return result.rowcount > 0


def get_next_stage(db: Session, workflow_name: str, stage_name: str) -> Optional[str]:
    row = db.execute(
        select(WorkflowMaster).where(
            WorkflowMaster.workflow_name == workflow_name,
            WorkflowMaster.stage_name == stage_name,
        )
    ).scalars().first()
    return row.next_stage if row else None


def get_previous_stage(db: Session, workflow_name: str, stage_name: str) -> Optional[str]:
    row = db.execute(
        select(WorkflowMaster).where(
            WorkflowMaster.workflow_name == workflow_name,
            WorkflowMaster.stage_name == stage_name,
        )
    ).scalars().first()
    return row.previous_stage if row else None
