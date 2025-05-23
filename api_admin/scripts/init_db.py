# api_admin/scripts/init_db.py
import sys
import os
import asyncio
import uuid
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine, get_database_path, database_exists
from app.models.user import User
from app.models.client import Client  
from app.models.setting import Setting
from app.core.security import get_password_hash
from app.crud.crud_setting import DEFAULT_SETTINGS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete

async def init_db():
    """Initialize the database with tables and default data"""
    
    print(f"Database will be created at: {get_database_path()}")
    
    # Create all tables
    async with engine.begin() as conn:
        print("Creating database tables...")
        # Import all models to ensure they're registered
        from app.models import user, client, setting
        from app.database import Base
        
        # Drop all tables first (clean slate)
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")

    # Create session for inserting data
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Create admin user
            print("Creating admin user...")
            password_hash = get_password_hash("admin123")  # Changed from "admin" to "admin123"
            print(f"Generated password hash: {password_hash}")
            
            admin_user = User(
                id=str(uuid.uuid4()),
                username="admin",
                password_hash=password_hash,
                is_admin=1
            )
            session.add(admin_user)
            
            # Create default settings
            print("Creating default settings...")
            for key, data in DEFAULT_SETTINGS.items():
                setting = Setting(
                    key=key,
                    value=data["value"],
                    description=data["description"]
                )
                session.add(setting)
            
            # Create a sample client (optional)
            print("Creating sample client...")
            sample_client = Client(
                id=str(uuid.uuid4()),
                name="Sample API Client",
                description="A sample client for testing",
                api_key=str(uuid.uuid4()),
                active=1
            )
            session.add(sample_client)
            
            await session.commit()
            print("✅ Default data inserted successfully")
            
            # Verify the admin user was created
            result = await session.execute(select(User).where(User.username == 'admin'))
            admin = result.scalar_one_or_none()
            if admin:
                print(f"✅ Verified admin user exists with hash: {admin.password_hash}")
            else:
                print("❌ Error: Admin user not found after creation!")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error inserting data: {e}")
            import traceback
            print("Traceback:")
            print(traceback.format_exc())
            raise

    print("\n🎉 Database initialization completed!")
    print(f"📍 Database location: {get_database_path()}")
    print("👤 Admin credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n⚠️  Remember to change the admin password after first login!")

def main():
    """Main function with user confirmation"""
    if database_exists():
        print("⚠️  Database already exists!")
        response = input("Do you want to recreate it? This will delete all existing data. (y/N): ")
        if response.lower() != 'y':
            print("Database initialization cancelled.")
            return
        else:
            # Remove existing database
            os.remove(get_database_path())
            print("🗑️  Existing database removed")
    
    # Run async initialization
    asyncio.run(init_db())

if __name__ == "__main__":
    main()