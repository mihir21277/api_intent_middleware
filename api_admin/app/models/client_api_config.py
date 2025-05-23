# api_admin/app/models/client_api_config.py
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import uuid

class ClientApiConfig(Base):
    """API configuration for each client - allows per-client API endpoints"""
    __tablename__ = "client_api_configs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, ForeignKey('clients.id'), nullable=False)
    
    # API Service Information
    api_name = Column(String, nullable=False)
    api_base_url = Column(String, nullable=False)
    api_token = Column(String, nullable=False)
    
    # Optional configuration
    api_version = Column(String, default='v1')
    timeout_seconds = Column(Integer, default=30)
    max_retries = Column(Integer, default=3)
    
    # Status and metadata
    active = Column(Integer, default=1)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships with lazy loading
    client = relationship(
        "Client", 
        back_populates="api_configs",
        lazy="select"
    )
    parameter_templates = relationship(
        "ClientApiParameter", 
        back_populates="api_config", 
        cascade="all, delete-orphan",
        lazy="select"
    )