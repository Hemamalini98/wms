from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func

from app.init_db import Base


class StageMaster(Base):
    __tablename__ = "stage_master"

    id               = Column(BigInteger, primary_key=True, autoincrement=True)
    stage_name       = Column(String(100), unique=True, nullable=False, index=True)
    description      = Column(Text, nullable=True)
    stage_activities = Column(ARRAY(BigInteger), nullable=False, server_default="{}")  # array of stage_activity_master IDs
    sla_level1       = Column(Integer,           nullable=True)                        # SLA in days for Level 1
    sla_level2       = Column(Integer,           nullable=True)                        # SLA in days for Level 2
    sla_level3       = Column(Integer,           nullable=True)                        # SLA in days for Level 3
    roles            = Column(ARRAY(String),     nullable=False, server_default="{}")  # array of role names
    active_status    = Column(Boolean,           nullable=False, default=True)
    created_at       = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
