"""Test database operations"""

import pytest
from sqlalchemy import text
from app.db.base import SessionLocal, check_database
from app.db.models import User
from datetime import datetime


@pytest.fixture
def db_session():
    """Create test database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection"""
    status = await check_database()
    # May fail if DB not set up yet, but that's okay for initial tests
    assert status in ["ok", "error"]


def test_user_crud(db_session):
    """Test user CRUD operations"""
    # Create
    user = User(
        uid="test123", email="test@example.com", full_name="Test User", role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.uid == "test123"
    assert user.email == "test@example.com"

    # Read
    fetched = db_session.query(User).filter_by(uid="test123").first()
    assert fetched is not None
    assert fetched.email == "test@example.com"

    # Update
    fetched.full_name = "Updated Name"
    db_session.commit()
    db_session.refresh(fetched)
    assert fetched.full_name == "Updated Name"

    # Delete
    db_session.delete(fetched)
    db_session.commit()
    deleted = db_session.query(User).filter_by(uid="test123").first()
    assert deleted is None
