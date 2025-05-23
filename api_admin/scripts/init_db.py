import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import uuid
from sqlalchemy import select, delete
from app.core.security import get_password_hash
from app.database import engine
from app.models.user import Base, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async def init_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create admin user
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # Delete existing admin user
        await session.execute(delete(User).where(User.username == 'admin'))
        await session.commit()
        
        # Create new admin user
        password_hash = get_password_hash("admin123")
        print(f"Generated password hash: {password_hash}")
        
        admin_user = User(
            id=str(uuid.uuid4()),
            username="admin",
            password_hash=password_hash,
            is_admin=1
        )
        session.add(admin_user)
        await session.commit()
        print("Admin user recreated successfully!")
        
        # Verify the user was created
        result = await session.execute(select(User).where(User.username == 'admin'))
        admin = result.scalar_one_or_none()
        if admin:
            print(f"Verified admin user exists with hash: {admin.password_hash}")
        else:
            print("Error: Admin user not found after creation!")

if __name__ == "__main__":
    asyncio.run(init_db())
