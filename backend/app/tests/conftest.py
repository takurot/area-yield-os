"""Pytest configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.base import Base, engine


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create database tables for testing"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)


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
