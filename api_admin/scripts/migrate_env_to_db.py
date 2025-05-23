# api_admin/scripts/migrate_env_to_db.py
import sys
import asyncio
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.append(str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.setting import Setting
from sqlalchemy import select

# Environment variables to migrate to database
ENV_SETTINGS = {
    # Server Configuration
    "api_host": {
        "value": "0.0.0.0",
        "description": "API server host address"
    },
    "api_port": {
        "value": "8000", 
        "description": "API server port number"
    },
    "api_debug": {
        "value": "true",
        "description": "Enable debug mode for API server"
    },
    
    # OpenAI Configuration
    "openai_api_key": {
        "value": "sk-proj-xxxxxx",
        "description": "OpenAI API key for AI services (replace with actual key)"
    },
    "openai_model": {
        "value": "gpt-3.5-turbo",
        "description": "OpenAI model to use for intent recognition"
    },
    
    # Backend API Configuration - Employee Service
    "employee_api_base_url": {
        "value": "http://localhost:8001",
        "description": "Base URL for Employee API service"
    },
    "employee_api_token": {
        "value": "dev_token_123",
        "description": "Authentication token for Employee API"
    },
    
    # Backend API Configuration - Client Service  
    "client_api_base_url": {
        "value": "http://localhost:8002",
        "description": "Base URL for Client API service"
    },
    "client_api_token": {
        "value": "dev_token_456", 
        "description": "Authentication token for Client API"
    },
    
    # Backend API Configuration - Project Service
    "project_api_base_url": {
        "value": "http://localhost:8003",
        "description": "Base URL for Project API service"
    },
    "project_api_token": {
        "value": "dev_token_789",
        "description": "Authentication token for Project API"
    },
    
    # Logging Configuration
    "log_level": {
        "value": "DEBUG",
        "description": "Logging level (DEBUG, INFO, WARNING, ERROR)"
    },
    "log_format": {
        "value": "text",
        "description": "Log output format (text, json)"
    },
    
    # Environment Configuration
    "environment": {
        "value": "development",
        "description": "Current environment (development, staging, production)"
    }
}

async def migrate_env_settings():
    """Migrate environment variables to database settings"""
    
    print("🔄 Starting migration of environment variables to database...")
    
    async with AsyncSessionLocal() as session:
        try:
            added_count = 0
            updated_count = 0
            skipped_count = 0
            
            for key, data in ENV_SETTINGS.items():
                # Check if setting already exists
                result = await session.execute(select(Setting).where(Setting.key == key))
                existing_setting = result.scalar_one_or_none()
                
                if existing_setting:
                    # Ask user if they want to update existing setting
                    print(f"⚠️  Setting '{key}' already exists with value: '{existing_setting.value}'")
                    response = input(f"   Update to '{data['value']}'? (y/N): ")
                    
                    if response.lower() == 'y':
                        existing_setting.value = data["value"]
                        existing_setting.description = data["description"]
                        updated_count += 1
                        print(f"✅ Updated: {key}")
                    else:
                        skipped_count += 1
                        print(f"⏭️  Skipped: {key}")
                else:
                    # Add new setting
                    new_setting = Setting(
                        key=key,
                        value=data["value"],
                        description=data["description"]
                    )
                    session.add(new_setting)
                    added_count += 1
                    print(f"➕ Added: {key}")
            
            await session.commit()
            
            print(f"\n🎉 Migration completed!")
            print(f"   ➕ Added: {added_count} settings")
            print(f"   ✅ Updated: {updated_count} settings") 
            print(f"   ⏭️  Skipped: {skipped_count} settings")
            print(f"\n📝 Total settings in database: {added_count + updated_count + skipped_count}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error during migration: {e}")
            import traceback
            print("Traceback:")
            print(traceback.format_exc())
            raise

async def list_all_settings():
    """List all current settings in database"""
    print("\n📋 Current settings in database:")
    
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Setting))
            settings = result.scalars().all()
            
            if not settings:
                print("   No settings found in database.")
                return
                
            for setting in settings:
                print(f"   🔧 {setting.key}: {setting.value}")
                if setting.description:
                    print(f"      📝 {setting.description}")
                print()
                
        except Exception as e:
            print(f"❌ Error listing settings: {e}")

def main():
    """Main function"""
    print("🔧 Environment Variables to Database Migration Tool")
    print("=" * 50)
    
    choice = input("\nWhat would you like to do?\n1. Migrate env vars to database\n2. List current database settings\n3. Both\n\nChoice (1-3): ")
    
    if choice == "1":
        asyncio.run(migrate_env_settings())
    elif choice == "2":
        asyncio.run(list_all_settings())
    elif choice == "3":
        asyncio.run(list_all_settings())
        print("\n" + "="*50)
        asyncio.run(migrate_env_settings())
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()