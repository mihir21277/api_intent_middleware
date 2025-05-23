from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.security import verify_password
from ..models.user import User
from ..database import get_async_session

async def authenticate_user(username: str, password: str, session: AsyncSession) -> Optional[User]:
    try:
        print(f"Executing query for username: {username}")
        query = select(User).where(User.username == username)
        print(f"Query: {query}")
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        print(f"Query result: {user}")
        if not user:
            print("No user found")
            return None
        print("Verifying password...")
        if not verify_password(password, user.password_hash):
            print("Invalid password")
            return None
        print("Password verified successfully")
        return user
    except Exception as e:
        import traceback
        print(f"Authentication error: {e}")
        print("Traceback:")
        print(traceback.format_exc())
        raise

async def get_user(username: str, session: AsyncSession) -> Optional[User]:
    try:
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    except Exception as e:
        print(f"Get user error: {e}")
        return None
