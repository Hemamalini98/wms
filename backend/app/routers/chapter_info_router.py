from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud import chapter_info_crud
from app.init_db import get_db
from app.schemas.chapter_info_schema import ChapterInfoCreate, ChapterInfoResponse, ChapterInfoUpdate

router = APIRouter(prefix="/chapters", tags=["Chapters"])


@router.post("/", response_model=ChapterInfoResponse, status_code=status.HTTP_201_CREATED)
def create_chapter(data: ChapterInfoCreate, db: Session = Depends(get_db)):
    return chapter_info_crud.create_chapter(db, data)


@router.get("/", response_model=List[ChapterInfoResponse])
def list_chapters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return chapter_info_crud.get_chapters(db, skip=skip, limit=limit)


@router.get("/project/{project}", response_model=List[ChapterInfoResponse])
def list_chapters_by_project(project: str, db: Session = Depends(get_db)):
    return chapter_info_crud.get_chapters_by_project(db, project)


@router.get("/client/{client}", response_model=List[ChapterInfoResponse])
def list_chapters_by_client(client: str, db: Session = Depends(get_db)):
    return chapter_info_crud.get_chapters_by_client(db, client)


@router.get("/{chapter_id}", response_model=ChapterInfoResponse)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    row = chapter_info_crud.get_chapter(db, chapter_id)
    if not row:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return row


class _PriorityBody(BaseModel):
    priority: str


@router.put("/project/{project}/priority")
def bulk_update_priority(project: str, data: _PriorityBody, db: Session = Depends(get_db)):
    count = chapter_info_crud.bulk_update_priority_by_project(db, project, data.priority)
    return {"updated": count}


class _StatusBody(BaseModel):
    status: str


@router.put("/project/{project}/status")
def bulk_update_status(project: str, data: _StatusBody, db: Session = Depends(get_db)):
    count = chapter_info_crud.bulk_update_status_by_project(db, project, data.status)
    return {"updated": count}


@router.put("/{chapter_id}", response_model=ChapterInfoResponse)
def update_chapter(chapter_id: int, data: ChapterInfoUpdate, db: Session = Depends(get_db)):
    updated = chapter_info_crud.update_chapter(db, chapter_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return updated
