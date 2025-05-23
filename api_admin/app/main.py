# api_admin/app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api.auth import router as auth_router
from .api.clients import router as clients_router
from .api.settings import router as settings_router
from .api.client_api_configs import router as client_api_configs_router 
from .database import Base, engine, AsyncSessionLocal, database_exists, get_database_path
from .crud import crud_setting
from .core.config import settings
# Import models through __init__.py to ensure proper order
from .models import User, Setting, Client, ClientApiConfig, ClientApiParameter
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application initialization...")
    logger.info(f"Database path: {get_database_path()}")
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created/verified")
        
        # Initialize settings
        async with AsyncSessionLocal() as session:
            # Initialize default settings
            await crud_setting.initialize_settings(session)
            logger.info("✅ Default settings initialized")
            
            # Load all settings from database into config
            db_settings = await crud_setting.get_settings_dict(session)
            settings.load_database_settings(db_settings)
            
            logger.info(f"✅ Loaded {len(db_settings)} settings from database")
            logger.info(f"✅ JWT token expiration: {settings.get_token_expire_minutes()} minutes")
            logger.info(f"✅ Environment: {settings.get_environment()}")
            logger.info(f"✅ API Debug: {settings.get_api_debug()}")
        
        logger.info("🎉 Application initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during initialization: {e}")
        raise
    
    yield  # This is where the application runs
    
    # Shutdown
    logger.info("Shutting down application...")
    # Add any cleanup code here if needed
    logger.info("✅ Application shutdown completed")

# Create FastAPI app with lifespan
app = FastAPI(
    title="API Intent Recognition Middleware Admin Panel",
    description="Admin panel for managing API clients and system settings",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (create static directory if it doesn't exist)
import os
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)

try:
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc} - {request.url}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Root endpoint - redirect to login
@app.get("/")
async def root():
    return FileResponse("templates/login.html")

# Static page routes
@app.get("/login")
async def login():
    return FileResponse("templates/login.html")

@app.get("/dashboard")
async def dashboard():
    return FileResponse("templates/dashboard.html")

@app.get("/clients")
async def clients():
    return FileResponse("templates/clients.html")

@app.get("/settings")
async def settings_page():
    return FileResponse("templates/settings.html")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": {
            "exists": database_exists(),
            "path": get_database_path()
        }
    }

# Database info endpoint (for debugging)
@app.get("/api/database/info")
async def database_info():
    try:
        info = {
            "path": get_database_path(),
            "exists": database_exists(),
        }
        if database_exists():
            import os
            from datetime import datetime
            stat = os.stat(get_database_path())
            info.update({
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        return info
    except Exception as e:
        return {"error": str(e)}

# Include API routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(clients_router, tags=["Clients"])
app.include_router(settings_router, tags=["Settings"])
app.include_router(client_api_configs_router, tags=["Client API Configurations"])  