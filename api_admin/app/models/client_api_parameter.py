# api_admin/app/models/client_api_parameter.py
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import uuid

class ClientApiParameter(Base):
    """API parameter templates for different client API endpoints"""
    __tablename__ = "client_api_parameters"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_api_config_id = Column(String, ForeignKey('client_api_configs.id'), nullable=False)
    
    # Parameter Template Information
    template_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # HTTP Method and Endpoint
    http_method = Column(String, default='GET')
    endpoint_path = Column(String, nullable=False)
    
    # Parameter Configuration (JSON)
    parameter_template = Column(JSON, nullable=False)
    
    # Response Configuration
    response_mapping = Column(JSON, nullable=True)
    
    # Metadata
    active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship with lazy loading
    api_config = relationship(
        "ClientApiConfig", 
        back_populates="parameter_templates",
        lazy="select"
    )