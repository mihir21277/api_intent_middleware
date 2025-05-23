from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # In production, use a secure secret key
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite+aiosqlite:///./database/api_middleware.sqlite"
    
    # Dynamic settings that can be overridden from database
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = None
    
    def get_token_expire_minutes(self) -> int:
        if self.ACCESS_TOKEN_EXPIRE_MINUTES is None:
            return 30  # Default value if not set in database
        return self.ACCESS_TOKEN_EXPIRE_MINUTES

settings = Settings()
