from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud import client_crud
from app.init_db import get_db
from app.schemas.client_schema import ClientCreate, ClientListResponse, ClientResponse, ClientUpdate

router = APIRouter(prefix="/clients", tags=["Clients"])


class StatusUpdate(BaseModel):
    active_status: bool


@router.post("/", response_model=ClientListResponse, status_code=status.HTTP_201_CREATED)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    return client_crud.create_client(db, client)


@router.get("/", response_model=List[ClientListResponse])
def list_clients(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    return client_crud.get_clients(db, skip=skip, limit=limit)


@router.get("/active", response_model=List[ClientListResponse])
def list_active_clients(db: Session = Depends(get_db)):
    return client_crud.get_active_clients(db)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = client_crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=ClientListResponse)
def update_client(client_id: int, data: ClientUpdate, db: Session = Depends(get_db)):
    updated = client_crud.update_client(db, client_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Client not found")
    return updated


@router.patch("/{client_id}/status", response_model=ClientListResponse)
def set_client_status(client_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    updated = client_crud.set_client_active_status(db, client_id, body.active_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Client not found")
    return updated
