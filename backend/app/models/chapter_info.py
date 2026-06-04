from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.init_db import Base


class ChapterInfo(Base):
    __tablename__ = "chapter_details"

    id                     = Column(BigInteger, primary_key=True, autoincrement=True)
    client                 = Column(String(150), nullable=False)
    project                = Column(String(200), nullable=False)
    chapters               = Column(String(100), nullable=False)
    chapter_title          = Column(Text,        nullable=True)
    project_manager_name   = Column(String(150), ForeignKey("users.user_name",          ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    due_date               = Column(Date,        nullable=True)
    stage_name             = Column(String(100), ForeignKey("stage_master.stage_name",  ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    current_stage_activity = Column(String(100), ForeignKey("stage_activity_master.stage_activity_name", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    current_assignee_name  = Column(String(150), ForeignKey("users.user_name",          ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    status                 = Column(String(20),  nullable=False, default="In-progress")
    complexity_level       = Column(String(20),  nullable=True,  default="Medium")
    stage_level            = Column(Integer,     nullable=True,  default=1)
    workflow               = Column(Text,        nullable=False, default="Workflow1")
    published_status       = Column(String(30),  nullable=False, default="Draft")
    remarks                = Column(Text,        nullable=True)
    manuscript_pages       = Column(Integer,     nullable=True)
    priority               = Column(String(20),  nullable=False, default="Normal")
    delayed_stages         = Column(JSON,        nullable=True,  default=list)
    created_at             = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at             = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
