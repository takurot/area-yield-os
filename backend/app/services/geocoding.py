"""Geocoding service using Google Maps Geocoding API"""

import re
import unicodedata
from typing import Optional
import httpx
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.core.config import settings
from app.models.geocoding import GeocodingResult

logger = structlog.get_logger()


class GeocodingError(Exception):
    """Custom exception for geocoding errors"""

    pass


def normalize_address(address: str) -> str:
    """
    Normalize address string

    Args:
        address: Raw address string

    Returns:
        Normalized address string
    """
    if not address:
        return ""

    # Convert full-width characters to half-width
    address = unicodedata.normalize("NFKC", address)

    # Remove extra whitespace
    address = " ".join(address.split())

    # Remove special characters that might interfere
    address = re.sub(r"[・･]", "", address)

    return address.strip()


def _extract_prefecture(address_components: list) -> Optional[str]:
    """Extract prefecture from address components"""
    for component in address_components:
        if "administrative_area_level_1" in component.get("types", []):
            return component.get("long_name")
    return None


def _extract_city(address_components: list) -> Optional[str]:
    """Extract city from address components"""
    # Try locality first (市区町村)
    for component in address_components:
        if "locality" in component.get("types", []):
            return component.get("long_name")

    # Fallback to sublocality_level_1 (特別区)
    for component in address_components:
        if "sublocality_level_1" in component.get("types", []):
            return component.get("long_name")

    return None


def _extract_district(address_components: list) -> Optional[str]:
    """Extract district from address components"""
    for component in address_components:
        if "sublocality_level_2" in component.get(
            "types", []
        ) or "sublocality_level_3" in component.get("types", []):
            return component.get("long_name")
    return None


def _extract_postal_code(address_components: list) -> Optional[str]:
    """Extract postal code from address components"""
    for component in address_components:
        if "postal_code" in component.get("types", []):
            return component.get("long_name")
    return None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
)
async def _call_geocoding_api(address: str) -> dict:
    """
    Call Google Maps Geocoding API with retry logic

    Args:
        address: Normalized address string

    Returns:
        API response as dict

    Raises:
        GeocodingError: If API call fails
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    if not api_key:
        raise GeocodingError("Google Maps API key not configured")

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key,
        "language": "ja",
        "region": "jp",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            status = data.get("status")

            if status == "OK":
                return data
            elif status == "ZERO_RESULTS":
                raise GeocodingError(f"No results found for address: {address}")
            elif status == "OVER_QUERY_LIMIT":
                raise GeocodingError("Google Maps API rate limit exceeded")
            elif status == "REQUEST_DENIED":
                raise GeocodingError("Google Maps API request denied (check API key)")
            elif status == "INVALID_REQUEST":
                raise GeocodingError(
                    f"Invalid geocoding request for address: {address}"
                )
            else:
                raise GeocodingError(f"Geocoding failed with status: {status}")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise GeocodingError("Rate limit exceeded") from e
        raise GeocodingError(f"HTTP error: {e.response.status_code}") from e
    except httpx.RequestError as e:
        raise GeocodingError(f"Network error: {str(e)}") from e
    except Exception as e:
        raise GeocodingError(f"Unexpected error: {str(e)}") from e


async def geocode_address(address: str) -> GeocodingResult:
    """
    Geocode an address to coordinates

    Args:
        address: Address string to geocode

    Returns:
        GeocodingResult with coordinates and parsed address

    Raises:
        ValueError: If address is empty
        GeocodingError: If geocoding fails
    """
    if not address or not address.strip():
        raise ValueError("Address cannot be empty")

    # Normalize address
    normalized_address = normalize_address(address)

    logger.info(
        "geocoding_request",
        original_address=address,
        normalized_address=normalized_address,
    )

    try:
        # Call Geocoding API
        data = await _call_geocoding_api(normalized_address)

        # Parse first result
        result = data["results"][0]
        geometry = result["geometry"]
        location = geometry["location"]

        # Round coordinates to town level (approximately 100m precision)
        # ~0.001 degree ≈ 100m
        lat = round(location["lat"], 4)
        lng = round(location["lng"], 4)

        # Extract address components
        address_components = result.get("address_components", [])
        prefecture = _extract_prefecture(address_components)
        city = _extract_city(address_components)
        district = _extract_district(address_components)
        postal_code = _extract_postal_code(address_components)

        formatted_address = result.get("formatted_address", "")

        geocoding_result = GeocodingResult(
            lat=lat,
            lng=lng,
            formatted_address=formatted_address,
            prefecture=prefecture or "",
            city=city or "",
            district=district,
            postal_code=postal_code,
        )

        logger.info(
            "geocoding_success",
            address=address,
            lat=lat,
            lng=lng,
            prefecture=prefecture,
            city=city,
        )

        return geocoding_result

    except GeocodingError:
        logger.error("geocoding_failed", address=address)
        raise
    except Exception as e:
        logger.error("geocoding_unexpected_error", address=address, error=str(e))
        raise GeocodingError(f"Unexpected geocoding error: {str(e)}") from e
