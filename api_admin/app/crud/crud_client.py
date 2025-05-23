from typing import List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.client import Client

async def create_client(session: AsyncSession, name: str) -> Client:
    api_key = str(uuid.uuid4())
    client = Client(
        id=str(uuid.uuid4()),
        name=name,
        api_key=api_key
    )
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client

async def get_clients(session: AsyncSession) -> List[Client]:
    try:
        print("Executing query to get all clients")
        query = select(Client)
        print("Query:", query)
        result = await session.execute(query)
        clients = result.scalars().all()
        print("Query result:", clients)
        return clients
    except Exception as e:
        import traceback
        print("Error in get_clients:", str(e))
        print("Traceback:")
        print(traceback.format_exc())
        raise

async def get_client(session: AsyncSession, client_id: str) -> Optional[Client]:
    result = await session.execute(select(Client).where(Client.id == client_id))
    return result.scalar_one_or_none()

async def update_client(session: AsyncSession, client_id: str, name: str, active: int) -> Optional[Client]:
    client = await get_client(session, client_id)
    if client:
        client.name = name
        client.active = active
        await session.commit()
        await session.refresh(client)
    return client

async def delete_client(session: AsyncSession, client_id: str) -> bool:
    client = await get_client(session, client_id)
    if client:
        await session.delete(client)
        await session.commit()
        return True
    return False
