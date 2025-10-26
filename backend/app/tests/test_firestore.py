"""Test Firestore operations"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.services.firestore import FirestoreCache, UserProfileService


@pytest.fixture
def mock_firestore_client():
    """Mock Firestore client"""
    with patch("app.services.firestore.db") as mock_db:
        yield mock_db


@pytest.mark.asyncio
async def test_cache_set_and_get(mock_firestore_client):
    """Test cache set and get operations"""
    cache = FirestoreCache()

    # Mock document reference
    mock_doc_ref = Mock()
    mock_doc = Mock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "key": "test:key",
        "value": {"data": "test_value"},
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=1),
    }

    mock_doc_ref.get.return_value = mock_doc
    mock_firestore_client.collection.return_value.document.return_value = mock_doc_ref

    # Set cache
    result = await cache.set("test:key", {"data": "test_value"}, ttl=3600)
    assert result is True

    # Get cache
    value = await cache.get("test:key")
    assert value == {"data": "test_value"}


@pytest.mark.asyncio
async def test_cache_expiration(mock_firestore_client):
    """Test cache expiration"""
    cache = FirestoreCache()

    # Mock expired document
    mock_doc_ref = Mock()
    mock_doc = Mock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "key": "test:expire",
        "value": {"data": 1},
        "created_at": datetime.utcnow() - timedelta(hours=2),
        "expires_at": datetime.utcnow() - timedelta(hours=1),
    }

    mock_doc_ref.get.return_value = mock_doc
    mock_firestore_client.collection.return_value.document.return_value = mock_doc_ref

    # Get expired cache should return None
    value = await cache.get("test:expire")
    assert value is None

    # Document should be deleted
    mock_doc_ref.delete.assert_called_once()


@pytest.mark.asyncio
async def test_user_profile_crud(mock_firestore_client):
    """Test user profile CRUD operations"""
    service = UserProfileService()

    mock_doc_ref = Mock()
    mock_firestore_client.collection.return_value.document.return_value = mock_doc_ref

    # Create profile
    result = await service.create_profile(
        "test123", {"email": "test@example.com", "full_name": "Test User"}
    )
    assert result is True
    mock_doc_ref.set.assert_called_once()

    # Get profile
    mock_doc = Mock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "full_name": "Test User",
    }
    mock_doc_ref.get.return_value = mock_doc

    profile = await service.get_profile("test123")
    assert profile["email"] == "test@example.com"

    # Update profile
    result = await service.update_profile("test123", {"full_name": "Updated Name"})
    assert result is True
    mock_doc_ref.update.assert_called_once()

    # Delete profile
    result = await service.delete_profile("test123")
    assert result is True
    mock_doc_ref.delete.assert_called()
