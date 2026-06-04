from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project_schema import ProjectCreate, ProjectUpdate


def create_project(db: Session, data: ProjectCreate) -> Project:
    db_project = Project(**data.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.execute(select(Project).where(Project.id == project_id)).scalars().first()


def get_project_by_code(db: Session, project_code: str) -> Optional[Project]:
    return db.execute(select(Project).where(Project.project_code == project_code)).scalars().first()


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    return list(db.execute(select(Project).offset(skip).limit(limit)).scalars().all())


def get_projects_by_client(db: Session, client_id: int) -> List[Project]:
    return list(db.execute(select(Project).where(Project.client_id == client_id)).scalars().all())


def update_project(db: Session, project_id: int, data: ProjectUpdate) -> Optional[Project]:
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_project, field, value)
    db.commit()
    db.refresh(db_project)
    return db_project
