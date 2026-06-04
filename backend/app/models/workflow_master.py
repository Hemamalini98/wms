from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.init_db import Base


class WorkflowMaster(Base):
    __tablename__ = "workflow_master"

    id             = Column(Integer,  primary_key=True, autoincrement=True)
    workflow_name  = Column(String(255), nullable=False, index=True)
    stage_name     = Column(String(255), nullable=False)
    previous_stage = Column(String(255), nullable=True)
    next_stage     = Column(String(255), nullable=True)
    description    = Column(String(500), nullable=True)
    active_status  = Column(Boolean,  nullable=False, default=True)
    created_at     = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at     = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
