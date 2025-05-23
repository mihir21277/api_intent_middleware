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

# Import models after engine creation to avoid circular imports
from app.database import Base
from app.models.user import User
from app.models.client import Client
from app.models.setting import Setting

# Create all tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Create admin user with bcrypt password hash
password = "admin"
password_bytes = password.encode('utf-8')
salt = bcrypt.gensalt()
password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

admin = User(
    username="admin",
    password_hash=password_hash,
    is_admin=True
)
session.add(admin)
session.commit()

print("Database initialized with admin user (username: admin, password: admin)")

