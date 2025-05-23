from sqlalchemy import Column, String, Integer, DateTime, func
from ..database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
