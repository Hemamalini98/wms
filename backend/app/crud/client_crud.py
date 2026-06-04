from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate


def create_client(db: Session, data: ClientCreate) -> Client:
    db_client = Client(**data.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def get_client(db: Session, client_id: int) -> Optional[Client]:
    return db.execute(select(Client).where(Client.id == client_id)).scalars().first()


def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[Client]:
    return list(db.execute(select(Client).offset(skip).limit(limit)).scalars().all())


def get_active_clients(db: Session) -> List[Client]:
    return list(db.execute(select(Client).where(Client.active_status == True)).scalars().all())  # noqa: E712


def update_client(db: Session, client_id: int, data: ClientUpdate) -> Optional[Client]:
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_client, field, value)
    db.commit()
    db.refresh(db_client)
    return db_client


def set_client_active_status(db: Session, client_id: int, active_status: bool) -> Optional[Client]:
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    db_client.active_status = active_status
    db.commit()
    db.refresh(db_client)
    return db_client
