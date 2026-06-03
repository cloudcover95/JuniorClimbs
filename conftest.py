# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base
from backend.routers.pos import get_db as pos_get_db
from backend.routers.athletes import get_db as athletes_get_db
from backend.routers.practices import get_db as practices_get_db

# Use an in-memory SQLite database strictly for testing to ensure state isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Creates a fresh database session for a test and rolls back afterward."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Dependency override for the FastAPI test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Override dependencies for all modular routers
    app.dependency_overrides[pos_get_db] = override_get_db
    app.dependency_overrides[athletes_get_db] = override_get_db
    app.dependency_overrides[practices_get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client