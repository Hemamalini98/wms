from sqlalchemy import JSON, BigInteger, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.init_db import Base


class Project(Base):
    __tablename__ = "projects"

    id               = Column(Integer,     primary_key=True, autoincrement=True)
    client_id        = Column(BigInteger,  ForeignKey("clients.id", ondelete="CASCADE"), nullable=True)
    project_code     = Column(String(100), unique=True, nullable=True, index=True)
    customer_name    = Column(String(255), nullable=True)
    division_code    = Column(String(100), nullable=True)
    customer_contact = Column(String(255), nullable=True)
    category         = Column(String(100), nullable=True)
    composition      = Column(String(50),  nullable=True)
    workflow_name    = Column(String(255), nullable=True)
    status           = Column(String(50),  nullable=True)
    project_manager  = Column(String(150), ForeignKey("users.user_name", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    sales_person     = Column(String(255), nullable=True)
    priority         = Column(String(50),  nullable=True)
    project_title    = Column(Text,        nullable=True)
    edition          = Column(String(50),  nullable=True)
    color            = Column(String(100), nullable=True)
    trim_size        = Column(String(50),  nullable=True)
    copyright_year   = Column(Integer,     nullable=True)
    manuscript_pages = Column(Integer,     nullable=True)
    estimated_pages  = Column(Integer,     nullable=True)
    actual_pages     = Column(Integer,     nullable=False, default=0)
    chapter_count    = Column(Integer,     nullable=True)
    isbn_no          = Column(String(20),  nullable=True)
    billing_location = Column(String(255), nullable=True)
    due_date         = Column(Date,        nullable=True)
    file_details     = Column(JSON,        nullable=True)
    created_at       = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="projects")
