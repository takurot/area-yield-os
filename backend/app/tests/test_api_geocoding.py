"""Test geocoding API endpoints"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.models.geocoding import GeocodingResult
from app.services.geocoding import GeocodingError


def test_geocode_endpoint_success(client: TestClient):
    """Test successful geocoding via API"""
    mock_result = GeocodingResult(
        lat=35.0036,
        lng=135.7736,
        formatted_address="京都府京都市東山区祇園町南側",
        prefecture="京都府",
        city="京都市東山区",
        district="祇園町南側",
    )

    with patch(
        "app.api.v1.geocoding.geocode_address", new=AsyncMock(return_value=mock_result)
    ):
        response = client.post(
            "/api/v1/geocoding/",
            json={"address": "京都府京都市東山区祇園町南側570-120"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["lat"] == 35.0036
    assert data["lng"] == 135.7736
    assert data["prefecture"] == "京都府"
    assert data["city"] == "京都市東山区"


def test_geocode_endpoint_empty_address(client: TestClient):
    """Test geocoding with empty address"""
    response = client.post(
        "/api/v1/geocoding/",
        json={"address": ""},
    )

    assert response.status_code == 422  # Validation error


def test_geocode_endpoint_invalid_address(client: TestClient):
    """Test geocoding with invalid address"""
    with patch(
        "app.api.v1.geocoding.geocode_address",
        new=AsyncMock(side_effect=ValueError("Address cannot be empty")),
    ):
        response = client.post(
            "/api/v1/geocoding/",
            json={"address": "invalid"},
        )

    assert response.status_code == 400
    assert "Invalid address" in response.json()["detail"]


def test_geocode_endpoint_not_found(client: TestClient):
    """Test geocoding when address not found"""
    with patch(
        "app.api.v1.geocoding.geocode_address",
        new=AsyncMock(side_effect=GeocodingError("No results found")),
    ):
        response = client.post(
            "/api/v1/geocoding/",
            json={"address": "無効な住所12345"},
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_geocode_endpoint_rate_limit(client: TestClient):
    """Test geocoding rate limit error"""
    with patch(
        "app.api.v1.geocoding.geocode_address",
        new=AsyncMock(side_effect=GeocodingError("Rate limit exceeded")),
    ):
        response = client.post(
            "/api/v1/geocoding/",
            json={"address": "京都府京都市"},
        )

    assert response.status_code == 429
    assert "rate limit" in response.json()["detail"].lower()


def test_geocode_endpoint_server_error(client: TestClient):
    """Test geocoding server error"""
    with patch(
        "app.api.v1.geocoding.geocode_address",
        new=AsyncMock(side_effect=GeocodingError("API key invalid")),
    ):
        response = client.post(
            "/api/v1/geocoding/",
            json={"address": "京都府京都市"},
        )

    assert response.status_code == 500
    assert "failed" in response.json()["detail"].lower()


def test_geocode_endpoint_unexpected_error(client: TestClient):
    """Test geocoding unexpected error"""
    with patch(
        "app.api.v1.geocoding.geocode_address",
        new=AsyncMock(side_effect=Exception("Unexpected error")),
    ):
        response = client.post(
            "/api/v1/geocoding/",
            json={"address": "京都府京都市"},
        )

    assert response.status_code == 500
    assert "unexpected" in response.json()["detail"].lower()
