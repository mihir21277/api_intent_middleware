# api_admin/app/models/__init__.py

# Import all models in the correct order to ensure relationships work
from .user import User
from .setting import Setting  
from .client import Client
from .client_api_config import ClientApiConfig
from .client_api_parameter import ClientApiParameter

# Make them available when importing from models
__all__ = ["User", "Setting", "Client", "ClientApiConfig", "ClientApiParameter"]