# api_admin/app/models/client.py
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import uuid

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    api_key = Column(String, unique=True, nullable=True)
    active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship with lazy loading
    api_configs = relationship(
        "ClientApiConfig", 
        back_populates="client", 
        cascade="all, delete-orphan",
        lazy="select"
    )