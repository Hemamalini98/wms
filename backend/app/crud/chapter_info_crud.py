from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chapter_info import ChapterInfo
from app.schemas.chapter_info_schema import ChapterInfoCreate, ChapterInfoUpdate


def create_chapter(db: Session, data: ChapterInfoCreate) -> ChapterInfo:
    row = ChapterInfo(**data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_chapter(db: Session, chapter_id: int) -> Optional[ChapterInfo]:
    return db.execute(select(ChapterInfo).where(ChapterInfo.id == chapter_id)).scalars().first()


def get_chapters(db: Session, skip: int = 0, limit: int = 100) -> List[ChapterInfo]:
    return list(db.execute(select(ChapterInfo).offset(skip).limit(limit)).scalars().all())


def get_chapters_by_project(db: Session, project: str) -> List[ChapterInfo]:
    return list(db.execute(select(ChapterInfo).where(ChapterInfo.project == project)).scalars().all())


def get_chapters_by_client(db: Session, client: str) -> List[ChapterInfo]:
    return list(db.execute(select(ChapterInfo).where(ChapterInfo.client == client)).scalars().all())


def bulk_update_priority_by_project(db: Session, project: str, priority: str) -> int:
    rows = db.execute(
        select(ChapterInfo).where(ChapterInfo.project == project)
    ).scalars().all()
    for row in rows:
        row.priority = priority
    db.commit()
    return len(rows)


def bulk_update_status_by_project(db: Session, project: str, status: str) -> int:
    rows = db.execute(
        select(ChapterInfo).where(ChapterInfo.project == project)
    ).scalars().all()
    for row in rows:
        row.status = status
    db.commit()
    return len(rows)


def update_chapter(db: Session, chapter_id: int, data: ChapterInfoUpdate) -> Optional[ChapterInfo]:
    row = get_chapter(db, chapter_id)
    if not row:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row
