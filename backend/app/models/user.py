"""
Users table — internal system users with role-based access.
Password column stores a bcrypt hash; never store plaintext.
"""

from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.init_db import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(BigInteger, primary_key=True, autoincrement=True)
    user_name       = Column(String(150),  unique=True, nullable=False, index=True)
    email           = Column(String(255),  unique=True, nullable=False, index=True)
    password        = Column(Text,         nullable=False)                 # bcrypt hash only
    role            = Column(String(50),   nullable=False)   # soft ref to roles_master.role_name
    team            = Column(String(50),   nullable=False)
    customer_access = Column(JSONB,        nullable=False)   # stores customer-access config as JSON
    active_status   = Column(Boolean,      nullable=False, default=True)
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
