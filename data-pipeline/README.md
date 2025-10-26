# Data Pipeline

AreaYield OSのデータ収集・処理パイプライン

## 概要

このディレクトリには、以下のコンポーネントが含まれています：

- **crawlers/**: データソースからのデータ収集
- **processors/**: データの変換・クリーニング
- **tests/**: パイプラインのテスト

## データソース

1. AirDNA API - 市場データ
2. 観光庁 - 民泊届出データ
3. 各自治体 - 旅館業許可データ
4. 国土交通省 - 用途地域データ
5. 自治体議会 - 議事録

## 実行方法

```bash
# 依存関係のインストール
pip install -r requirements.txt

# クローラーの実行例
python crawlers/airdna_crawler.py

# テストの実行
pytest tests/
```

