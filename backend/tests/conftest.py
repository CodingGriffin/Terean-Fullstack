"""
Pytest configuration and shared fixtures for all tests.
"""
import os
import sys
import pytest
import tempfile
from typing import Generator
from datetime import datetime, timedelta
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from models.user_model import UserDBModel
from models.project_model import ProjectDBModel
from models.sgy_file_model import SgyFileDBModel
from models.file_model import FileDBModel
from models.client_model import ClientDBModel
from models.contact_model import ContactDBModel
from crud.user_crud import create_user
from schemas.user_schema import UserCreate
from utils.authentication import get_password_hash


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test function."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator:
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db: Session) -> UserDBModel:
    """Create a test user."""
    user_data = UserCreate(
        username="testuser",
        password="testpassword123",
        email="test@example.com",
        full_name="Test User",
        disabled=False,
        auth_level=1,
        expiration=datetime.utcnow() + timedelta(days=30)
    )
    return create_user(db=test_db, user=user_data)


@pytest.fixture
def admin_user(test_db: Session) -> UserDBModel:
    """Create an admin test user."""
    user_data = UserCreate(
        username="adminuser",
        password="adminpassword123",
        email="admin@example.com",
        full_name="Admin User",
        disabled=False,
        auth_level=3,
        expiration=datetime.utcnow() + timedelta(days=30)
    )
    return create_user(db=test_db, user=user_data)


@pytest.fixture
def auth_headers(client: TestClient, test_user: UserDBModel) -> dict:
    """Get authentication headers for a regular user."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client: TestClient, admin_user: UserDBModel) -> dict:
    """Get authentication headers for an admin user."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "adminuser",
            "password": "adminpassword123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    env_vars = {
        "MQ_SAVE_DIR": "/tmp/test_data",
        "YOUR_GOOGLE_EMAIL": "test@gmail.com",
        "YOUR_GOOGLE_EMAIL_APP_PASSWORD": "test_password",
        "SECRET_KEY": "test-secret-key-for-jwt",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "A test project for unit testing",
        "status": "active",
        "created_date": datetime.utcnow(),
        "modified_date": datetime.utcnow(),
    }


@pytest.fixture
def sample_sgy_file_data():
    """Sample SGY file data for testing."""
    return {
        "filename": "test_file.sgy",
        "file_path": "/tmp/test_file.sgy",
        "file_size": 1024000,
        "upload_date": datetime.utcnow(),
        "status": "uploaded",
        "metadata": {"traces": 100, "samples": 1000}
    }


@pytest.fixture
def sample_client_data():
    """Sample client data for testing."""
    return {
        "name": "Test Client",
        "email": "client@example.com",
        "phone": "+1234567890",
        "company": "Test Company Inc.",
        "address": "123 Test Street, Test City, TC 12345"
    }


@pytest.fixture
def mock_velocity_model_file(temp_dir):
    """Create a mock velocity model file."""
    file_path = os.path.join(temp_dir, "velocity_model.txt")
    with open(file_path, 'w') as f:
        f.write("# Velocity Model Test Data\n")
        f.write("0.0 1500.0\n")
        f.write("10.0 1600.0\n")
        f.write("20.0 1700.0\n")
        f.write("30.0 1800.0\n")
    return file_path


# Async fixtures
@pytest.fixture
async def async_client(test_db: Session):
    """Create an async test client."""
    from httpx import AsyncClient
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# Helper functions for tests
def create_test_file(directory: str, filename: str, content: str = "test content") -> str:
    """Helper to create a test file."""
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path 