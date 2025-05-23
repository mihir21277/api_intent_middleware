from typing import List, Optional, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.setting import Setting

async def get_setting(session: AsyncSession, key: str) -> Optional[Setting]:
    result = await session.execute(select(Setting).where(Setting.key == key))
    return result.scalar_one_or_none()

async def get_all_settings(session: AsyncSession) -> List[Setting]:
    result = await session.execute(select(Setting))
    return result.scalars().all()

async def create_setting(session: AsyncSession, key: str, value: str, description: Optional[str] = None) -> Setting:
    setting = Setting(key=key, value=value, description=description)
    session.add(setting)
    await session.commit()
    await session.refresh(setting)
    return setting

async def update_setting(session: AsyncSession, key: str, value: str, description: Optional[str] = None) -> Optional[Setting]:
    setting = await get_setting(session, key)
    if setting:
        setting.value = value
        if description is not None:
            setting.description = description
        await session.commit()
        await session.refresh(setting)
    return setting

async def delete_setting(session: AsyncSession, key: str) -> bool:
    setting = await get_setting(session, key)
    if setting:
        await session.delete(setting)
        await session.commit()
        return True
    return False

# Default settings with their descriptions
DEFAULT_SETTINGS = {
    "jwt_token_expire_minutes": {
        "value": "30",
        "description": "JWT token expiration time in minutes"
    },
    "max_clients_per_page": {
        "value": "10",
        "description": "Maximum number of clients to show per page"
    },
    "api_rate_limit": {
        "value": "100",
        "description": "Maximum API calls per minute per client"
    }
}

async def initialize_settings(session: AsyncSession):
    """Initialize default settings if they don't exist"""
    for key, data in DEFAULT_SETTINGS.items():
        existing = await get_setting(session, key)
        if not existing:
            await create_setting(session, key, data["value"], data["description"])

async def get_settings_dict(session: AsyncSession) -> Dict[str, str]:
    """Get all settings as a dictionary"""
    settings = await get_all_settings(session)
    return {setting.key: setting.value for setting in settings}
