# api_admin/app/schemas/client_api_config.py
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class ClientApiConfigBase(BaseModel):
    api_name: str  # 'employee', 'client', 'project', etc.
    api_base_url: str  # Base URL for the API
    api_token: str  # Authentication token
    api_version: Optional[str] = 'v1'
    timeout_seconds: Optional[int] = 30
    max_retries: Optional[int] = 3
    description: Optional[str] = None
    active: Optional[int] = 1

class ClientApiConfigCreate(ClientApiConfigBase):
    client_id: str

class ClientApiConfigUpdate(BaseModel):
    api_base_url: Optional[str] = None
    api_token: Optional[str] = None
    api_version: Optional[str] = None
    timeout_seconds: Optional[int] = None
    max_retries: Optional[int] = None
    description: Optional[str] = None
    active: Optional[int] = None

class ClientApiConfig(ClientApiConfigBase):
    id: str
    client_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ClientWithApiConfigs(BaseModel):
    """Client model with their API configurations"""
    id: str
    name: str
    api_key: str
    active: int
    description: Optional[str] = None
    created_at: datetime
    api_configs: list[ClientApiConfig] = []

    class Config:
        from_attributes = True