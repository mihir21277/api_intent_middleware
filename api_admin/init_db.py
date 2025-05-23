import asyncio
from app.database import Base, engine
from app.models.user import User
from app.models.client import Client
from app.models.setting import Setting
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.core.security import get_password_hash

async def init_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create admin user
    async with AsyncSession(engine) as session:
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin"),
            is_admin=True
        )
        session.add(admin)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(init_db())
    print("Database initialized with admin user (username: admin, password: admin)")
