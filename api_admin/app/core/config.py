# api_admin/app/core/config.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os

class Settings(BaseModel):
    # Core security settings (keep these hardcoded for security)
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    
    # Database configuration (keep these hardcoded)
    DATABASE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database')
    DATABASE_FILE: str = "api_middleware.sqlite"
    
    @property
    def DATABASE_PATH(self) -> str:
        return os.path.join(self.DATABASE_DIR, self.DATABASE_FILE)
    
    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite+aiosqlite:///{self.DATABASE_PATH}"
    
    # Dynamic settings loaded from database
    _db_settings: Dict[str, str] = {}
    
    # Default values for database settings
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = None
    
    def ensure_database_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(self.DATABASE_DIR, exist_ok=True)
    
    def load_database_settings(self, db_settings: Dict[str, str]):
        """Load settings from database"""
        self._db_settings = db_settings
        
        # Update specific settings
        if 'jwt_token_expire_minutes' in db_settings:
            try:
                self.ACCESS_TOKEN_EXPIRE_MINUTES = int(db_settings['jwt_token_expire_minutes'])
            except (ValueError, TypeError):
                self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    def get_token_expire_minutes(self) -> int:
        if self.ACCESS_TOKEN_EXPIRE_MINUTES is None:
            return 30
        return self.ACCESS_TOKEN_EXPIRE_MINUTES
    
    # Helper methods to get database settings with defaults
    def get_api_host(self) -> str:
        return self._db_settings.get('api_host', '0.0.0.0')
    
    def get_api_port(self) -> int:
        try:
            return int(self._db_settings.get('api_port', '8000'))
        except (ValueError, TypeError):
            return 8000
    
    def get_api_debug(self) -> bool:
        return self._db_settings.get('api_debug', 'false').lower() == 'true'
    
    def get_openai_api_key(self) -> str:
        return self._db_settings.get('openai_api_key', '')
    
    def get_openai_model(self) -> str:
        return self._db_settings.get('openai_model', 'gpt-3.5-turbo')
    
    def get_employee_api_base_url(self) -> str:
        return self._db_settings.get('employee_api_base_url', 'http://localhost:8001')
    
    def get_employee_api_token(self) -> str:
        return self._db_settings.get('employee_api_token', '')
    
    def get_client_api_base_url(self) -> str:
        return self._db_settings.get('client_api_base_url', 'http://localhost:8002')
    
    def get_client_api_token(self) -> str:
        return self._db_settings.get('client_api_token', '')
    
    def get_project_api_base_url(self) -> str:
        return self._db_settings.get('project_api_base_url', 'http://localhost:8003')
    
    def get_project_api_token(self) -> str:
        return self._db_settings.get('project_api_token', '')
    
    def get_log_level(self) -> str:
        return self._db_settings.get('log_level', 'INFO')
    
    def get_log_format(self) -> str:
        return self._db_settings.get('log_format', 'text')
    
    def get_environment(self) -> str:
        return self._db_settings.get('environment', 'development')
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get any setting from database with optional default"""
        return self._db_settings.get(key, default)
    
    def all_settings(self) -> Dict[str, str]:
        """Get all database settings"""
        return self._db_settings.copy()

settings = Settings()
# Ensure database directory exists when config is loaded
settings.ensure_database_directory()