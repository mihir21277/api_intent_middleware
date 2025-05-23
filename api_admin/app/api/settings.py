from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_async_session
from ..crud import crud_setting
from ..schemas.setting import Setting, SettingCreate, SettingUpdate
from ..core.auth import get_current_user
from ..models.user import User
from ..core.config import settings

router = APIRouter()

@router.get("/api/settings", response_model=List[Setting])
async def get_settings(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Get all settings"""
    return await crud_setting.get_all_settings(session)

@router.get("/api/settings/{key}", response_model=Setting)
async def get_setting(
    key: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific setting by key"""
    setting = await crud_setting.get_setting(session, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.post("/api/settings", response_model=Setting)
async def create_setting(
    setting: SettingCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new setting"""
    existing = await crud_setting.get_setting(session, setting.key)
    if existing:
        raise HTTPException(status_code=400, detail="Setting already exists")
    result = await crud_setting.create_setting(
        session, setting.key, setting.value, setting.description
    )
    
    # Update config if jwt_token_expire_minutes is changed
    if setting.key == 'jwt_token_expire_minutes':
        try:
            settings.ACCESS_TOKEN_EXPIRE_MINUTES = int(setting.value)
        except (ValueError, TypeError):
            print("Invalid jwt_token_expire_minutes value")
            settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30  # fallback to default
    
    return result

@router.put("/api/settings/{key}", response_model=Setting)
async def update_setting(
    key: str,
    setting: SettingUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Update a setting"""
    result = await crud_setting.update_setting(
        session, key, setting.value, setting.description
    )
    
    # Update config if jwt_token_expire_minutes is changed
    if key == 'jwt_token_expire_minutes':
        try:
            settings.ACCESS_TOKEN_EXPIRE_MINUTES = int(setting.value)
        except (ValueError, TypeError):
            print("Invalid jwt_token_expire_minutes value")
            settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30  # fallback to default
    
    if not result:
        raise HTTPException(status_code=404, detail="Setting not found")
    return result

@router.delete("/api/settings/{key}")
async def delete_setting(
    key: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a setting"""
    if await crud_setting.delete_setting(session, key):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Setting not found")
