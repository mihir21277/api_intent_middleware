# api_admin/scripts/migrate_client_api_configs.py
import sys
import asyncio
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine, AsyncSessionLocal
from app.models.client import Client
from app.models.client_api_config import ClientApiConfig
from app.crud.crud_client_api_config import create_client_api_config
from sqlalchemy import select

async def migrate_client_api_configs():
    """Create the new client_api_configs table and add sample configurations"""
    
    print("🔄 Starting Client API Configuration migration...")
    
    # Create the new table
    async with engine.begin() as conn:
        from app.database import Base
        # This will create the client_api_configs table
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Created client_api_configs table")
    
    # Add sample API configurations for existing clients
    async with AsyncSessionLocal() as session:
        try:
            # Get all existing clients
            result = await session.execute(select(Client).where(Client.active == 1))
            clients = result.scalars().all()
            
            print(f"📋 Found {len(clients)} active clients")
            
            for client in clients:
                print(f"\n🔧 Setting up API configs for client: {client.name}")
                
                # Create sample API configurations for each client
                api_configs = [
                    {
                        "api_name": "employee",
                        "api_base_url": f"https://{client.name.lower().replace(' ', '-')}.employee-api.com",
                        "api_token": f"emp_token_{client.id[:8]}",
                        "description": f"Employee API for {client.name}"
                    },
                    {
                        "api_name": "client", 
                        "api_base_url": f"https://{client.name.lower().replace(' ', '-')}.client-api.com",
                        "api_token": f"client_token_{client.id[:8]}",
                        "description": f"Client API for {client.name}"
                    },
                    {
                        "api_name": "project",
                        "api_base_url": f"https://{client.name.lower().replace(' ', '-')}.project-api.com", 
                        "api_token": f"project_token_{client.id[:8]}",
                        "description": f"Project API for {client.name}"
                    }
                ]
                
                for config_data in api_configs:
                    try:
                        config = await create_client_api_config(
                            session=session,
                            client_id=client.id,
                            **config_data
                        )
                        print(f"   ✅ Added {config_data['api_name']} API config")
                    except Exception as e:
                        print(f"   ❌ Error adding {config_data['api_name']} config: {e}")
            
            print(f"\n🎉 Migration completed successfully!")
            print(f"📊 Total clients processed: {len(clients)}")
            print(f"📊 API configurations per client: 3 (employee, client, project)")
            print(f"📊 Total API configurations created: {len(clients) * 3}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error during migration: {e}")
            import traceback
            print("Traceback:")
            print(traceback.format_exc())
            raise

async def show_client_api_configs():
    """Show all client API configurations"""
    print("\n📋 Current Client API Configurations:")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Client, ClientApiConfig)
                .join(ClientApiConfig, Client.id == ClientApiConfig.client_id)
                .where(Client.active == 1)
                .order_by(Client.name, ClientApiConfig.api_name)
            )
            
            current_client = None
            for client, config in result:
                if current_client != client.name:
                    current_client = client.name
                    print(f"\n🏢 Client: {client.name}")
                    print(f"   🔑 API Key: {client.api_key}")
                
                print(f"   📡 {config.api_name.upper()} API:")
                print(f"      URL: {config.api_base_url}")
                print(f"      Token: {config.api_token}")
                print(f"      Status: {'Active' if config.active else 'Inactive'}")
                
        except Exception as e:
            print(f"❌ Error showing configurations: {e}")

def main():
    """Main function with user choice"""
    print("🔧 Client API Configuration Migration Tool")
    print("=" * 50)
    
    choice = input("\nWhat would you like to do?\n1. Run migration (create table + sample data)\n2. Show current configurations\n3. Both\n\nChoice (1-3): ")
    
    if choice == "1":
        asyncio.run(migrate_client_api_configs())
    elif choice == "2":
        asyncio.run(show_client_api_configs())
    elif choice == "3":
        asyncio.run(migrate_client_api_configs())
        asyncio.run(show_client_api_configs())
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()