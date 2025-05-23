from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ClientBase(BaseModel):
    name: str
    description: Optional[str] = None
    api_key: Optional[str] = None
    active: Optional[int] = 1

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
