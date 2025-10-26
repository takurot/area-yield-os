"""Test authentication"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


def test_get_current_user_without_token(client: TestClient):
    """Test protected endpoint without authentication"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403  # No Authorization header


def test_get_current_user_with_invalid_token(client: TestClient):
    """Test protected endpoint with invalid token"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


@patch("app.core.auth.firebase_auth.verify_id_token")
def test_get_current_user_with_valid_firebase_token(
    mock_verify: MagicMock,
    client: TestClient
):
    """Test protected endpoint with valid Firebase token"""
    # Mock Firebase token verification
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "role": "user"
    }
    
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer valid_firebase_token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == "test123"
    assert data["email"] == "test@example.com"


def test_refresh_token_without_auth(client: TestClient):
    """Test token refresh without authentication"""
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 403


@patch("app.core.auth.firebase_auth.verify_id_token")
def test_refresh_token_with_valid_token(
    mock_verify: MagicMock,
    client: TestClient
):
    """Test token refresh with valid authentication"""
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com"
    }
    
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": "Bearer valid_token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data

