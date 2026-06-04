from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.init_db import Base


class StageDetail(Base):
    __tablename__ = "stages_details"

    __table_args__ = (
        CheckConstraint("planned_end_date IS NULL OR planned_start_date IS NULL OR planned_end_date >= planned_start_date", name="ck_stage_detail_planned_end_after_start"),
        CheckConstraint("actual_end_date IS NULL OR actual_start_date IS NULL OR actual_end_date >= actual_start_date",     name="ck_stage_detail_actual_end_after_start"),
        CheckConstraint("sla >= 0",         name="ck_stage_detail_sla_non_negative"),
        CheckConstraint("stage_level >= 0", name="ck_stage_detail_level_non_negative"),
    )

    id                    = Column(BigInteger,  primary_key=True, autoincrement=True)
    client                = Column(String(150), nullable=False)
    project               = Column(String(200), nullable=False)
    chapters              = Column(String(100), nullable=False)
    project_manager_name  = Column(String(150), ForeignKey("users.user_name",                          ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    assignee_name         = Column(String(150), ForeignKey("users.user_name",                          ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    planned_start_date    = Column(DateTime(timezone=True), nullable=True)
    planned_end_date      = Column(DateTime(timezone=True), nullable=True)
    actual_start_date     = Column(DateTime(timezone=True), nullable=True)
    actual_end_date       = Column(DateTime(timezone=True), nullable=True)
    stage_name            = Column(String(100), ForeignKey("stage_master.stage_name",                  ondelete="RESTRICT",  onupdate="CASCADE"), nullable=False)
    stage_activity        = Column(String(100), ForeignKey("stage_activity_master.stage_activity_name", ondelete="RESTRICT", onupdate="CASCADE"), nullable=True)
    total_time_taken      = Column(Float,       nullable=True)
    workflow              = Column(Text,        nullable=False, default="Workflow1")
    complexity_level      = Column(String(20),  nullable=True)
    stage_level           = Column(Integer,     nullable=True)
    sla                   = Column(Integer,     nullable=True)
    stage_status          = Column(String(20),  nullable=False, default="In-progress")
    stage_activity_status = Column(String(20),  nullable=False, default="In-progress")
    delayed               = Column(Boolean,     nullable=False, default=False)
    delay_days            = Column(Integer,     nullable=True)
    remarks               = Column(Text,        nullable=True)
    created_at            = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at            = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
