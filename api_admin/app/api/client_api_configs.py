# api_admin/app/api/client_api_configs.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_async_session
from ..crud import crud_client_api_config, crud_client
from ..schemas.client_api_config import (
    ClientApiConfig,
    ClientApiConfigCreate, 
    ClientApiConfigUpdate,
    ClientWithApiConfigs
)
from ..core.auth import get_current_user
from ..models.user import User

router = APIRouter()

@router.post("/api/clients/{client_id}/api-configs", response_model=ClientApiConfig)
async def create_client_api_config(
    client_id: str,
    config: ClientApiConfigCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new API configuration for a client"""
    
    # Verify client exists
    client = await crud_client.get_client(session, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if this API type already exists for this client
    existing_config = await crud_client_api_config.get_client_api_config(
        session, client_id, config.api_name
    )
    if existing_config:
        raise HTTPException(
            status_code=400, 
            detail=f"API configuration for '{config.api_name}' already exists for this client"
        )
    
    return await crud_client_api_config.create_client_api_config(
        session=session,
        client_id=client_id,
        api_name=config.api_name,
        api_base_url=config.api_base_url,
        api_token=config.api_token,
        api_version=config.api_version,
        timeout_seconds=config.timeout_seconds,
        max_retries=config.max_retries,
        description=config.description
    )

@router.get("/api/clients/{client_id}/api-configs", response_model=List[ClientApiConfig])
async def get_client_api_configs(
    client_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Get all API configurations for a specific client"""
    
    # Verify client exists
    client = await crud_client.get_client(session, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return await crud_client_api_config.get_client_api_configs(session, client_id)

@router.get("/api/clients/{client_id}/with-configs", response_model=ClientWithApiConfigs)
async def get_client_with_api_configs(
    client_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Get client with all their API configurations"""
    
    client = await crud_client.get_client(session, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    configs = await crud_client_api_config.get_client_api_configs(session, client_id)
    
    return ClientWithApiConfigs(
        id=client.id,
        name=client.name,
        api_key=client.api_key,
        active=client.active,
        description=client.description,
        created_at=client.created_at,
        api_configs=configs
    )

@router.put("/api/client-api-configs/{config_id}", response_model=ClientApiConfig)
async def update_client_api_config(
    config_id: str,
    config_update: ClientApiConfigUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Update an API configuration"""
    
    updated_config = await crud_client_api_config.update_client_api_config(
        session=session,
        config_id=config_id,
        api_base_url=config_update.api_base_url,
        api_token=config_update.api_token,
        api_version=config_update.api_version,
        timeout_seconds=config_update.timeout_seconds,
        max_retries=config_update.max_retries,
        description=config_update.description,
        active=config_update.active
    )
    
    if not updated_config:
        raise HTTPException(status_code=404, detail="API configuration not found")
    
    return updated_config

@router.delete("/api/client-api-configs/{config_id}")
async def delete_client_api_config(
    config_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Delete an API configuration"""
    
    deleted = await crud_client_api_config.delete_client_api_config(session, config_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="API configuration not found")
    
    return {"status": "success", "message": "API configuration deleted"}

# Utility endpoint for the main API middleware
@router.get("/api/resolve-client-api/{client_api_key}/{api_name}")
async def resolve_client_api(
    client_api_key: str,
    api_name: str,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Resolve client API configuration by client API key and API name
    This endpoint is used by your main API middleware
    """
    
    config = await crud_client_api_config.get_api_config_for_request(
        session, client_api_key, api_name
    )
    
    if not config:
        raise HTTPException(
            status_code=404, 
            detail=f"No {api_name} API configuration found for client"
        )
    
    return {
        "api_base_url": config.api_base_url,
        "api_token": config.api_token,
        "api_version": config.api_version,
        "timeout_seconds": config.timeout_seconds,
        "max_retries": config.max_retries
    }