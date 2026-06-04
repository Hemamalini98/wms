from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import project_crud
from app.init_db import get_db
from app.schemas.project_schema import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    if project.project_code and project_crud.get_project_by_code(db, project.project_code):
        raise HTTPException(status_code=400, detail="Project code already exists")
    return project_crud.create_project(db, project)


@router.get("/", response_model=List[ProjectResponse])
def list_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return project_crud.get_projects(db, skip=skip, limit=limit)


@router.get("/client/{client_id}", response_model=List[ProjectResponse])
def list_projects_by_client(client_id: int, db: Session = Depends(get_db)):
    return project_crud.get_projects_by_client(db, client_id)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = project_crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    updated = project_crud.update_project(db, project_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated
