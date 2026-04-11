# Database Tables (SQLAlchemy Models)
# Table for Users (Email, Hashed Password, Role) for authentication

from decimal import Clamped

import enum
from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy import Column,Integer, String, Boolean,DateTime,Enum


# Role Enum
class UserRole(str, enum.Enum):
    BORROWER = "BORROWER"
    CREDIT = "CREDIT"
    OPS = "OPS"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


