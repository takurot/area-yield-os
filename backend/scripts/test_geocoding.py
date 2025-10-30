#!/usr/bin/env python3
"""Quick test script for Geocoding API"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.geocoding import geocode_address, GeocodingError


async def test_geocoding():
    """Test geocoding with sample addresses"""
    test_addresses = [
        "京都府京都市東山区祇園町南側570-120",
        "東京都渋谷区道玄坂1-2-3",
        "大阪府大阪市中央区難波5-1-60",
        "沖縄県那覇市おもろまち1-1-1",
    ]

    print("🧪 Geocoding API 動作確認テスト\n")
    print("=" * 60)

    for i, address in enumerate(test_addresses, 1):
        print(f"\n[{i}/{len(test_addresses)}] テスト中: {address}")
        try:
            result = await geocode_address(address)
            print(f"✅ 成功!")
            print(f"   緯度: {result.lat}")
            print(f"   経度: {result.lng}")
            print(f"   都道府県: {result.prefecture}")
            print(f"   市区町村: {result.city}")
            if result.district:
                print(f"   町丁目: {result.district}")
            if result.postal_code:
                print(f"   郵便番号: {result.postal_code}")
            print(f"   フォーマット済み住所: {result.formatted_address}")
        except GeocodingError as e:
            print(f"❌ エラー: {e}")
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")

    print("\n" + "=" * 60)
    print("✅ テスト完了")


if __name__ == "__main__":
    asyncio.run(test_geocoding())

