from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from ..database import get_async_session
from ..crud import crud_client
from ..core.auth import get_current_user
from ..models.user import User

router = APIRouter()

from ..schemas.client import ClientCreate, Client as ClientResponse

@router.post("/api/clients", response_model=ClientResponse)
async def create_client(
    client: ClientCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    return await crud_client.create_client(session, client.name)

@router.get("/api/clients", response_model=List[ClientResponse])
async def get_clients(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    try:
        print("Getting clients for user:", current_user.username)
        clients = await crud_client.get_clients(session)
        print("Found clients:", clients)
        return clients
    except Exception as e:
        import traceback
        print("Error getting clients:", str(e))
        print("Traceback:")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error getting clients: {str(e)}"
        )

@router.get("/api/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    client = await crud_client.get_client(session, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.put("/api/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client: ClientCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    updated_client = await crud_client.update_client(session, client_id, client.name, client.active)
    if not updated_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return updated_client

@router.delete("/api/clients/{client_id}")
async def delete_client(
    client_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    deleted = await crud_client.delete_client(session, client_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"status": "success"}
