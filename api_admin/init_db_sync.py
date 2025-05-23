# api_admin/init_db_sync.py
import os
import sys
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create database directory if it doesn't exist
db_dir = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_dir, exist_ok=True)

# Create a synchronous engine
db_path = os.path.join(db_dir, 'api_middleware.sqlite')
engine = create_engine(f"sqlite:///{db_path}")

print(f"Database will be created at: {db_path}")

# Import models after engine creation to avoid circular imports
from app.database import Base
from app.models.user import User
from app.models.client import Client
from app.models.setting import Setting

# Create all tables
print("Dropping existing tables...")
Base.metadata.drop_all(bind=engine)
print("Creating new tables...")
Base.metadata.create_all(bind=engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Create admin user with bcrypt password hash
    print("Creating admin user...")
    password = "admin123"  # Changed from "admin" to "admin123"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    admin = User(
        username="admin",
        password_hash=password_hash,
        is_admin=True
    )
    session.add(admin)
    
    # Create default settings
    print("Creating default settings...")
    default_settings = [
        ("jwt_token_expire_minutes", "30", "JWT token expiration time in minutes"),
        ("max_clients_per_page", "10", "Maximum number of clients to show per page"),
        ("api_rate_limit", "100", "Maximum API calls per minute per client")
    ]
    
    for key, value, description in default_settings:
        setting = Setting(key=key, value=value, description=description)
        session.add(setting)
    
    # Create sample client
    print("Creating sample client...")
    import uuid
    sample_client = Client(
        name="Sample API Client",
        description="A sample client for testing",
        api_key=str(uuid.uuid4()),
        active=1
    )
    session.add(sample_client)
    
    session.commit()
    print("✅ Database initialized successfully!")
    
except Exception as e:
    session.rollback()
    print(f"❌ Error: {e}")
    raise
finally:
    session.close()

print("\n🎉 Database initialization completed!")
print(f"📍 Database location: {db_path}")
print("👤 Admin credentials:")
print("   Username: admin")
print("   Password: admin123")
print("\n⚠️  Remember to change the admin password after first login!")