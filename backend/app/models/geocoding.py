"""Geocoding models"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class GeocodingResult(BaseModel):
    """Geocoding result model"""

    lat: float = Field(..., description="Latitude", ge=-90, le=90)
    lng: float = Field(..., description="Longitude", ge=-180, le=180)
    formatted_address: str = Field(..., description="Formatted address")
    prefecture: str = Field(..., description="Prefecture (都道府県)")
    city: str = Field(..., description="City (市区町村)")
    district: Optional[str] = Field(None, description="District (町丁目)")
    postal_code: Optional[str] = Field(None, description="Postal code")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lat": 35.0036,
                "lng": 135.7736,
                "formatted_address": "京都府京都市東山区祇園町南側",
                "prefecture": "京都府",
                "city": "京都市東山区",
                "district": "祇園町南側",
                "postal_code": "605-0074",
            }
        }
    )


class GeocodingRequest(BaseModel):
    """Geocoding request model"""

    address: str = Field(..., min_length=1, description="Address to geocode")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"address": "京都府京都市東山区祇園町南側570-120"}
        }
    )
