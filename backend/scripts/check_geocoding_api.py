#!/usr/bin/env python3
"""Check Geocoding API configuration"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
import httpx
import asyncio


async def check_api_key():
    """Check if API key works with a simple request"""
    api_key = settings.GOOGLE_MAPS_API_KEY
    
    if not api_key:
        print("❌ APIキーが設定されていません")
        return False
    
    print(f"✅ APIキーが設定されています (長さ: {len(api_key)})")
    print(f"   キーの先頭: {api_key[:10]}...")
    
    # シンプルなテストリクエスト
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": "Tokyo",
        "key": api_key,
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            data = response.json()
            
            status = data.get("status")
            
            print(f"\n📡 API レスポンスステータス: {status}")
            
            if status == "OK":
                print("✅ APIキーは正常に動作しています！")
                return True
            elif status == "REQUEST_DENIED":
                error_message = data.get("error_message", "Unknown error")
                print(f"❌ API リクエストが拒否されました")
                print(f"   エラーメッセージ: {error_message}")
                print("\n考えられる原因:")
                print("  1. Geocoding API が有効になっていない")
                print("  2. APIキーの「API の制限」で Geocoding API が許可されていない")
                print("  3. APIキーが無効または削除されている")
                return False
            elif status == "OVER_QUERY_LIMIT":
                print("⚠️  API クォータ上限に達しています")
                return False
            else:
                print(f"❌ 予期しないステータス: {status}")
                return False
                
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Geocoding API 設定確認\n")
    print("=" * 60)
    asyncio.run(check_api_key())
    print("=" * 60)

