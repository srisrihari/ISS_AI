import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.models.database import Base, get_db
from app.models.auth import UserCreate, create_user

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the tables
Base.metadata.create_all(bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Create a test client for the app."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def test_db():
    """Create a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def admin_token(client):
    """Create an admin user and get a token."""
    # Create admin user
    admin_user = UserCreate(
        username="admin_test",
        email="admin_test@example.com",
        full_name="Test Administrator",
        password="adminpassword",
        role="admin"
    )
    create_user(admin_user)
    
    # Get token
    response = client.post(
        "/api/auth/token",
        data={"username": "admin_test", "password": "adminpassword"}
    )
    return response.json()["access_token"]

@pytest.fixture
def commander_token(client):
    """Create a commander user and get a token."""
    # Create commander user
    commander_user = UserCreate(
        username="commander_test",
        email="commander_test@example.com",
        full_name="Test Commander",
        password="commanderpassword",
        role="commander"
    )
    create_user(commander_user)
    
    # Get token
    response = client.post(
        "/api/auth/token",
        data={"username": "commander_test", "password": "commanderpassword"}
    )
    return response.json()["access_token"]

@pytest.fixture
def astronaut_token(client):
    """Create an astronaut user and get a token."""
    # Create astronaut user
    astronaut_user = UserCreate(
        username="astronaut_test",
        email="astronaut_test@example.com",
        full_name="Test Astronaut",
        password="astronautpassword",
        role="astronaut"
    )
    create_user(astronaut_user)
    
    # Get token
    response = client.post(
        "/api/auth/token",
        data={"username": "astronaut_test", "password": "astronautpassword"}
    )
    return response.json()["access_token"]

@pytest.fixture
def sample_container(test_db):
    """Create a sample container for testing."""
    from app.models.database import Container
    
    container = Container(
        id="test_container",
        zone="Test Zone",
        width=100.0,
        depth=100.0,
        height=100.0
    )
    test_db.add(container)
    test_db.commit()
    
    return container

@pytest.fixture
def sample_item(test_db):
    """Create a sample item for testing."""
    from app.models.database import Item
    from datetime import datetime, timedelta
    
    item = Item(
        id="test_item",
        name="Test Item",
        width=10.0,
        depth=10.0,
        height=10.0,
        mass=5.0,
        priority=80,
        expiry_date=datetime.utcnow() + timedelta(days=30),
        usage_limit=10,
        remaining_uses=10,
        preferred_zone="Test Zone",
        is_waste=False
    )
    test_db.add(item)
    test_db.commit()
    
    return item
