"""Pytest configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.main import app
from app.db.base import Base, engine


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create database tables for testing"""
    # Try to create tables, but don't fail if database is not available
    # Some tests (like geocoding) don't require database
    try:
        Base.metadata.create_all(bind=engine)
        yield
        # Drop all tables after tests
        try:
            Base.metadata.drop_all(bind=engine)
        except OperationalError:
            # Ignore drop errors if database is not available
            pass
    except OperationalError:
        # Database not available, skip setup/teardown
        yield


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_address():
    """Sample address for testing"""
    return "京都府京都市東山区祇園町南側570-120"


@pytest.fixture
def sample_coordinates():
    """Sample coordinates for testing"""
    return {"lat": 35.0036, "lng": 135.7736}
