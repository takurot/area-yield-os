"""Test geocoding service"""

import os
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.geocoding import (
    geocode_address,
    normalize_address,
    GeocodingError,
    GeocodingResult,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_geocode_address_kyoto():
    """Test geocoding a valid Kyoto address"""
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        pytest.skip("GOOGLE_MAPS_API_KEY not set, skipping integration test")

    address = "京都府京都市東山区祇園町南側570-120"

    result = await geocode_address(address)

    assert result.prefecture == "京都府"
    assert result.city == "京都市東山区"
    assert 34.0 < result.lat < 36.0
    assert 135.0 < result.lng < 136.0
    assert result.formatted_address is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_geocode_address_tokyo():
    """Test geocoding a valid Tokyo address"""
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        pytest.skip("GOOGLE_MAPS_API_KEY not set, skipping integration test")

    address = "東京都渋谷区道玄坂1-2-3"

    result = await geocode_address(address)

    assert result.prefecture == "東京都"
    assert result.city.startswith("渋谷区")
    assert 35.0 < result.lat < 36.0
    assert 139.0 < result.lng < 140.0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_geocode_address_osaka():
    """Test geocoding a valid Osaka address"""
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        pytest.skip("GOOGLE_MAPS_API_KEY not set, skipping integration test")

    address = "大阪府大阪市中央区難波5-1-60"

    result = await geocode_address(address)

    assert result.prefecture == "大阪府"
    assert result.city.startswith("大阪市")
    assert 34.0 < result.lat < 35.0
    assert 135.0 < result.lng < 136.0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_geocode_address_okinawa():
    """Test geocoding a valid Okinawa address"""
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        pytest.skip("GOOGLE_MAPS_API_KEY not set, skipping integration test")

    address = "沖縄県那覇市おもろまち1-1-1"

    result = await geocode_address(address)

    assert result.prefecture == "沖縄県"
    assert result.city.startswith("那覇市")
    assert 26.0 < result.lat < 27.0
    assert 127.0 < result.lng < 128.0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_geocode_invalid_address():
    """Test geocoding with invalid address"""
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        pytest.skip("GOOGLE_MAPS_API_KEY not set, skipping integration test")

    invalid_address = "無効な住所12345あいうえお"

    with pytest.raises(GeocodingError) as exc_info:
        await geocode_address(invalid_address)

    assert "Geocoding failed" in str(exc_info.value) or "No results" in str(
        exc_info.value
    )


@pytest.mark.asyncio
async def test_geocode_empty_address():
    """Test geocoding with empty address"""
    with pytest.raises(ValueError) as exc_info:
        await geocode_address("")

    assert "Address cannot be empty" in str(exc_info.value)


def test_normalize_address():
    """Test address normalization"""
    # Test full-width to half-width conversion
    assert normalize_address("１２３４") == "1234"

    # Test trimming whitespace
    assert normalize_address("  京都府京都市  ") == "京都府京都市"

    # Test removing special characters
    assert normalize_address("京都府・京都市") == "京都府京都市"


def test_normalize_address_empty():
    """Test normalizing empty address"""
    assert normalize_address("") == ""
    assert normalize_address("   ") == ""


@pytest.mark.asyncio
@patch("app.services.geocoding.httpx.AsyncClient")
async def test_geocode_with_rate_limiting(mock_client):
    """Test rate limiting behavior"""
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.json.return_value = {
        "status": "OVER_QUERY_LIMIT",
        "error_message": "Rate limit exceeded",
    }

    mock_instance = AsyncMock()
    mock_instance.get.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_instance

    with pytest.raises(GeocodingError) as exc_info:
        await geocode_address("京都府京都市")

    assert "rate limit" in str(exc_info.value).lower() or "OVER_QUERY_LIMIT" in str(
        exc_info.value
    )


@pytest.mark.asyncio
@patch("app.services.geocoding.httpx.AsyncClient")
async def test_geocode_network_error(mock_client):
    """Test handling network errors"""
    mock_instance = AsyncMock()
    mock_instance.get.side_effect = Exception("Network error")
    mock_client.return_value.__aenter__.return_value = mock_instance

    with pytest.raises(GeocodingError) as exc_info:
        await geocode_address("京都府京都市")

    assert "error" in str(exc_info.value).lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_geocode_result_rounding():
    """Test that coordinates are properly rounded to town level"""
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        pytest.skip("GOOGLE_MAPS_API_KEY not set, skipping integration test")

    address = "京都府京都市東山区祇園町南側570-120"

    result = await geocode_address(address)

    # Coordinates should be rounded (町丁目レベル)
    # Lat/Lng should have limited precision
    lat_str = f"{result.lat:.6f}"
    lng_str = f"{result.lng:.6f}"

    assert len(lat_str.split(".")[1]) <= 6
    assert len(lng_str.split(".")[1]) <= 6


def test_geocoding_result_model():
    """Test GeocodingResult model validation"""
    result = GeocodingResult(
        lat=35.0036,
        lng=135.7736,
        formatted_address="京都府京都市東山区祇園町南側",
        prefecture="京都府",
        city="京都市東山区",
        district="祇園町南側",
    )

    assert result.lat == 35.0036
    assert result.lng == 135.7736
    assert result.prefecture == "京都府"
    assert result.city == "京都市東山区"
