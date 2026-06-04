from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stage_master import StageMaster
from app.models.stage_activity_master import StageActivityMaster
from app.schemas.stage_master_schema import StageMasterCreate, StageMasterUpdate


def _resolve_activities(db: Session, activity_ids: List[int]) -> List[StageActivityMaster]:
    """Fetch full activity objects for a list of IDs, preserving order."""
    if not activity_ids:
        return []
    rows = db.execute(select(StageActivityMaster).where(StageActivityMaster.id.in_(activity_ids))).scalars().all()
    id_map = {r.id: r for r in rows}
    return [id_map[i] for i in activity_ids if i in id_map]


def _attach_activities(db: Session, stage: StageMaster) -> StageMaster:
    """Attach resolved activity objects onto the stage instance as a transient attribute."""
    stage.stage_activities = _resolve_activities(db, stage.stage_activities or [])
    return stage


def create_stage(db: Session, data: StageMasterCreate) -> StageMaster:
    db_stage = StageMaster(
        stage_name=data.stage_name,
        description=data.description,
        stage_activities=data.stage_activities,
        sla=data.sla,
        roles=data.roles,
        active_status=data.active_status,
    )
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return _attach_activities(db, db_stage)


def get_stage(db: Session, stage_id: int) -> Optional[StageMaster]:
    stage = db.execute(select(StageMaster).where(StageMaster.id == stage_id)).scalars().first()
    return _attach_activities(db, stage) if stage else None


def get_stage_by_name(db: Session, stage_name: str) -> Optional[StageMaster]:
    stage = db.execute(select(StageMaster).where(StageMaster.stage_name == stage_name)).scalars().first()
    return _attach_activities(db, stage) if stage else None


def get_stages(db: Session, skip: int = 0, limit: int = 100) -> List[StageMaster]:
    stages = db.execute(select(StageMaster).offset(skip).limit(limit)).scalars().all()
    return [_attach_activities(db, s) for s in stages]


def get_active_stages(db: Session) -> List[StageMaster]:
    stages = db.execute(select(StageMaster).where(StageMaster.active_status == True)).scalars().all()  # noqa: E712
    return [_attach_activities(db, s) for s in stages]


def update_stage(db: Session, stage_name: str, data: StageMasterUpdate) -> Optional[StageMaster]:
    db_stage = db.execute(select(StageMaster).where(StageMaster.stage_name == stage_name)).scalars().first()
    if not db_stage:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_stage, field, value)
    db.commit()
    db.refresh(db_stage)
    return _attach_activities(db, db_stage)


def set_stage_active_status(db: Session, stage_name: str, active_status: bool) -> Optional[StageMaster]:
    db_stage = db.execute(select(StageMaster).where(StageMaster.stage_name == stage_name)).scalars().first()
    if not db_stage:
        return None
    db_stage.active_status = active_status
    db.commit()
    db.refresh(db_stage)
    return _attach_activities(db, db_stage)
