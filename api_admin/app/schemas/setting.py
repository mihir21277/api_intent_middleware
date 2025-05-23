from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class SettingCreate(SettingBase):
    pass

class SettingUpdate(BaseModel):
    value: str
    description: Optional[str] = None

class Setting(SettingBase):
    updated_at: datetime

    class Config:
        from_attributes = True
