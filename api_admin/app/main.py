from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from .api.auth import router as auth_router
from .api.clients import router as clients_router
from .api.settings import router as settings_router
from .database import Base, engine, AsyncSessionLocal
from .crud import crud_setting
from .core.config import settings
import asyncio

app = FastAPI(title="API Intent Recognition Middleware Admin Panel")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint - redirect to login
@app.get("/")
async def root():
    return FileResponse("templates/login.html")

# Login page
@app.get("/login")
async def login():
    return FileResponse("templates/login.html")

@app.get("/dashboard")
async def dashboard():
    return FileResponse("templates/dashboard.html")

@app.get("/clients")
async def clients():
    return FileResponse("templates/clients.html")

# Settings page
@app.get("/settings")
async def settings():
    return FileResponse("templates/settings.html")

# Include routers
app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(settings_router)

# Initialize database and settings on startup
@app.on_event("startup")
async def initialize():
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize settings
    async with AsyncSessionLocal() as session:
        # Initialize default settings
        await crud_setting.initialize_settings(session)
        
        # Load settings into config
        db_settings = await crud_setting.get_settings_dict(session)
        
        # Update token expiration from database
        if 'jwt_token_expire_minutes' in db_settings:
            try:
                settings.ACCESS_TOKEN_EXPIRE_MINUTES = int(db_settings['jwt_token_expire_minutes'])
            except (ValueError, TypeError):
                print("Invalid jwt_token_expire_minutes value in database")
                settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30  # fallback to default
    async for session in get_async_session():
        await crud_setting.initialize_settings(session)
        break
