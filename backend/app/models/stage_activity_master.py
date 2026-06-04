from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, Text
from sqlalchemy.sql import func

from app.init_db import Base


class StageActivityMaster(Base):
    __tablename__ = "stage_activity_master"

    id                  = Column(BigInteger, primary_key=True, autoincrement=True)
    stage_activity_name = Column(String(150), unique=True, nullable=False, index=True)
    description         = Column(Text, nullable=True)
    active_status       = Column(Boolean, nullable=False, default=True)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
