# api_admin/app/crud/crud_client_api_config.py
from typing import List, Optional, Dict
import uuid
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models.client_api_config import ClientApiConfig
from ..models.client import Client

async def create_client_api_config(
    session: AsyncSession, 
    client_id: str,
    api_name: str,
    api_base_url: str,
    api_token: str,
    api_version: str = 'v1',
    timeout_seconds: int = 30,
    max_retries: int = 3,
    description: str = None
) -> ClientApiConfig:
    """Create a new API configuration for a client"""
    
    config = ClientApiConfig(
        id=str(uuid.uuid4()),
        client_id=client_id,
        api_name=api_name,
        api_base_url=api_base_url,
        api_token=api_token,
        api_version=api_version,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        description=description
    )
    session.add(config)
    await session.commit()
    await session.refresh(config)
    return config

async def get_client_api_configs(session: AsyncSession, client_id: str) -> List[ClientApiConfig]:
    """Get all API configurations for a specific client"""
    result = await session.execute(
        select(ClientApiConfig)
        .where(ClientApiConfig.client_id == client_id)
        .where(ClientApiConfig.active == 1)
    )
    return result.scalars().all()

async def get_client_api_config(
    session: AsyncSession, 
    client_id: str, 
    api_name: str
) -> Optional[ClientApiConfig]:
    """Get a specific API configuration for a client"""
    result = await session.execute(
        select(ClientApiConfig)
        .where(and_(
            ClientApiConfig.client_id == client_id,
            ClientApiConfig.api_name == api_name,
            ClientApiConfig.active == 1
        ))
    )
    return result.scalar_one_or_none()

async def get_client_with_api_configs(session: AsyncSession, client_api_key: str) -> Optional[Client]:
    """Get client and all their API configurations by API key"""
    result = await session.execute(
        select(Client)
        .options(selectinload(Client.api_configs))
        .where(Client.api_key == client_api_key)
        .where(Client.active == 1)
    )
    return result.scalar_one_or_none()

async def update_client_api_config(
    session: AsyncSession,
    config_id: str,
    api_base_url: str = None,
    api_token: str = None,
    api_version: str = None,
    timeout_seconds: int = None,
    max_retries: int = None,
    description: str = None,
    active: int = None
) -> Optional[ClientApiConfig]:
    """Update an existing API configuration"""
    
    result = await session.execute(
        select(ClientApiConfig).where(ClientApiConfig.id == config_id)
    )
    config = result.scalar_one_or_none()
    
    if config:
        if api_base_url is not None:
            config.api_base_url = api_base_url
        if api_token is not None:
            config.api_token = api_token
        if api_version is not None:
            config.api_version = api_version
        if timeout_seconds is not None:
            config.timeout_seconds = timeout_seconds
        if max_retries is not None:
            config.max_retries = max_retries
        if description is not None:
            config.description = description
        if active is not None:
            config.active = active
            
        await session.commit()
        await session.refresh(config)
    
    return config

async def delete_client_api_config(session: AsyncSession, config_id: str) -> bool:
    """Delete an API configuration"""
    result = await session.execute(
        select(ClientApiConfig).where(ClientApiConfig.id == config_id)
    )
    config = result.scalar_one_or_none()
    
    if config:
        await session.delete(config)
        await session.commit()
        return True
    return False

async def get_client_api_configs_dict(session: AsyncSession, client_id: str) -> Dict[str, ClientApiConfig]:
    """Get client API configs as a dictionary keyed by api_name"""
    configs = await get_client_api_configs(session, client_id)
    return {config.api_name: config for config in configs}

# Utility function for the main API middleware
async def get_api_config_for_request(session: AsyncSession, client_api_key: str, api_name: str) -> Optional[ClientApiConfig]:
    """
    Get the API configuration for a specific client and API type
    This is what your main middleware will use
    """
    # First get the client by their API key
    result = await session.execute(
        select(Client).where(and_(Client.api_key == client_api_key, Client.active == 1))
    )
    client = result.scalar_one_or_none()
    
    if not client:
        return None
    
    # Then get their specific API configuration
    return await get_client_api_config(session, client.id, api_name)