from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stage_activity_master import StageActivityMaster
from app.schemas.stage_activity_master_schema import StageActivityMasterCreate, StageActivityMasterUpdate


def create_stage_activity(db: Session, data: StageActivityMasterCreate) -> StageActivityMaster:
    db_activity = StageActivityMaster(**data.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def get_stage_activity(db: Session, activity_id: int) -> Optional[StageActivityMaster]:
    return db.execute(select(StageActivityMaster).where(StageActivityMaster.id == activity_id)).scalars().first()


def get_stage_activity_by_name(db: Session, name: str) -> Optional[StageActivityMaster]:
    return db.execute(select(StageActivityMaster).where(StageActivityMaster.stage_activity_name == name)).scalars().first()


def get_stage_activities(db: Session, skip: int = 0, limit: int = 100) -> List[StageActivityMaster]:
    return list(db.execute(select(StageActivityMaster).offset(skip).limit(limit)).scalars().all())


def get_active_stage_activities(db: Session) -> List[StageActivityMaster]:
    return list(db.execute(select(StageActivityMaster).where(StageActivityMaster.active_status == True)).scalars().all())  # noqa: E712


def update_stage_activity(db: Session, name: str, data: StageActivityMasterUpdate) -> Optional[StageActivityMaster]:
    db_activity = get_stage_activity_by_name(db, name)
    if not db_activity:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_activity, field, value)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def set_stage_activity_active_status(db: Session, name: str, active_status: bool) -> Optional[StageActivityMaster]:
    db_activity = get_stage_activity_by_name(db, name)
    if not db_activity:
        return None
    db_activity.active_status = active_status
    db.commit()
    db.refresh(db_activity)
    return db_activity
