"""Geocoding API endpoints"""

from fastapi import APIRouter, HTTPException, status
import structlog

from app.models.geocoding import GeocodingRequest, GeocodingResult
from app.services.geocoding import geocode_address, GeocodingError

router = APIRouter(prefix="/geocoding", tags=["geocoding"])
logger = structlog.get_logger()


@router.post("/", response_model=GeocodingResult)
async def geocode(request: GeocodingRequest) -> GeocodingResult:
    """
    Geocode an address to coordinates

    Args:
        request: Geocoding request with address

    Returns:
        GeocodingResult with coordinates and parsed address components

    Raises:
        HTTPException: 400 if address is invalid, 500 if geocoding fails
    """
    try:
        logger.info("geocoding_api_request", address=request.address)

        result = await geocode_address(request.address)

        logger.info(
            "geocoding_api_success",
            address=request.address,
            lat=result.lat,
            lng=result.lng,
        )

        return result

    except ValueError as e:
        logger.warning(
            "geocoding_api_invalid_input", address=request.address, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid address: {str(e)}",
        )

    except GeocodingError as e:
        logger.error("geocoding_api_error", address=request.address, error=str(e))

        # Differentiate between rate limiting and other errors
        if "rate limit" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Geocoding rate limit exceeded. Please try again later.",
            )
        elif "No results" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Address not found: {request.address}",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Geocoding failed: {str(e)}",
            )

    except Exception as e:
        logger.error(
            "geocoding_api_unexpected_error",
            address=request.address,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during geocoding",
        )
