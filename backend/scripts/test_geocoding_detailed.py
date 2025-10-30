#!/usr/bin/env python3
"""Detailed Geocoding API test with full error information"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
import httpx
import asyncio


async def test_detailed():
    """Test with detailed error information"""
    api_key = settings.GOOGLE_MAPS_API_KEY
    
    print("🔍 詳細なGeocoding APIテスト\n")
    print("=" * 60)
    print(f"API Key: {api_key[:15]}...{api_key[-5:] if len(api_key) > 20 else ''}")
    print(f"Key Length: {len(api_key)}")
    print("=" * 60)
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": "Tokyo",
        "key": api_key,
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            data = response.json()
            
            print(f"\n📡 HTTP Status Code: {response.status_code}")
            print(f"📡 Response Status: {data.get('status')}")
            
            if "error_message" in data:
                print(f"❌ Error Message: {data['error_message']}")
            
            print(f"\n📄 Full Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get("status") == "OK":
                print("\n✅ SUCCESS! API is working correctly.")
                return True
            else:
                print("\n❌ API call failed.")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_detailed())

