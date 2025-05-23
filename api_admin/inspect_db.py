# api_admin/scripts/inspect_db.py
import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine, get_database_path, database_exists
from app.models.user import User
from app.models.client import Client  
from app.models.setting import Setting
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

async def inspect_database():
    """Inspect the current database contents"""
    
    db_path = get_database_path()
    print(f"Database location: {db_path}")
    
    if not database_exists():
        print("❌ Database does not exist!")
        return
    
    print("✅ Database exists")
    
    # Get file info
    import os
    from datetime import datetime
    stat = os.stat(db_path)
    print(f"📊 Database size: {stat.st_size} bytes")
    print(f"📅 Last modified: {datetime.fromtimestamp(stat.st_mtime)}")
    
    # Check database contents
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Check if tables exist
            print("\n🔍 Checking database tables...")
            
            # Check users table
            try:
                result = await session.execute(select(User))
                users = result.scalars().all()
                print(f"👥 Users table: {len(users)} users found")
                for user in users:
                    print(f"   - {user.username} (admin: {bool(user.is_admin)})")
            except Exception as e:
                print(f"❌ Users table: Error - {e}")
            
            # Check clients table
            try:
                result = await session.execute(select(Client))
                clients = result.scalars().all()
                print(f"🔑 Clients table: {len(clients)} clients found")
                for client in clients:
                    status = "Active" if client.active else "Inactive"
                    print(f"   - {client.name} ({status})")
            except Exception as e:
                print(f"❌ Clients table: Error - {e}")
            
            # Check settings table
            try:
                result = await session.execute(select(Setting))
                settings = result.scalars().all()
                print(f"⚙️  Settings table: {len(settings)} settings found")
                for setting in settings:
                    print(f"   - {setting.key}: {setting.value}")
            except Exception as e:
                print(f"❌ Settings table: Error - {e}")
            
            # Check database schema
            print("\n📋 Database schema:")
            try:
                result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
                tables = result.fetchall()
                print(f"📁 Tables found: {[table[0] for table in tables]}")
            except Exception as e:
                print(f"❌ Schema check error: {e}")
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        import traceback
        print("Traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(inspect_database())