# AreaYield OS

短期賃貸（民泊）投資の可否判定を、収益性・許認可実現性・規制リスクの3軸で評価するSaaS/APIプラットフォーム

## 概要

AreaYield OSは、住所/町丁目レベルでGo/Amber/Stop判定を提供し、投資家が賢明な意思決定を行えるよう支援します。

### 主要機能

- **エリア投資判定**: 住所・町丁目単位での三段階評価（Go/Amber/Stop）
- **収益性予測**: RevPARレンジの算出と信頼区間の提示
- **許認可分析**: 旅館業許可・民泊届出の取得難易度評価
- **規制リスク評価**: 自治体の規制強化動向のスコア化（0-100）
- **エリア統計**: 届出密度、競合物件数、レビュー傾向の可視化

## プロジェクト構造

```
area-yield-os/
├── frontend/              # Next.js アプリ
│   ├── app/              # App Router
│   ├── components/       # UI コンポーネント
│   ├── lib/              # ユーティリティ
│   ├── public/           # 静的ファイル
│   └── tests/            # フロントエンドテスト
├── backend/              # FastAPI アプリ
│   ├── app/
│   │   ├── api/          # APIエンドポイント
│   │   ├── core/         # コアロジック（スコア計算）
│   │   ├── models/       # Pydanticモデル
│   │   ├── services/     # ビジネスロジック
│   │   └── tests/        # バックエンドテスト
│   ├── requirements.txt
│   └── Dockerfile
├── data-pipeline/        # ETL/データ更新
│   ├── crawlers/         # クローラー
│   ├── processors/       # データ処理
│   └── tests/
├── infrastructure/       # IaC
│   ├── terraform/        # GCP リソース
│   └── firebase/         # Firebase 設定
├── .github/
│   └── workflows/        # CI/CD
├── doc/                  # ドキュメント
└── scripts/              # ユーティリティスクリプト
```

## 技術スタック

### フロントエンド
- **Framework**: Next.js 14 (App Router)
- **UI**: React 18, Tailwind CSS, shadcn/ui
- **State**: Zustand
- **Maps**: Mapbox GL JS
- **Charts**: Recharts

### バックエンド
- **API**: FastAPI 0.110+
- **Runtime**: Python 3.11
- **Async**: httpx, asyncio
- **Validation**: Pydantic v2

### インフラ
- **Hosting**: Firebase Hosting (Frontend)
- **Compute**: Cloud Run (Backend API)
- **Database**: Cloud SQL (PostgreSQL 15) + Firestore
- **Data Warehouse**: BigQuery
- **Storage**: Cloud Storage
- **Cache**: Cloud Memorystore (Redis)
- **Vector DB**: Pinecone (RAG)
- **Queue**: Cloud Tasks
- **Scheduler**: Cloud Scheduler

## 環境構築

### 必要なツール

```bash
# 必須
- Node.js 18+
- Python 3.11+
- Docker Desktop
- gcloud CLI
- Firebase CLI
- Git

# 推奨
- VS Code + 拡張機能（Prettier, ESLint, Python, Tailwind）
```

### セットアップ手順

#### 1. リポジトリのクローン

```bash
git clone https://github.com/your-org/area-yield-os.git
cd area-yield-os
```

#### 2. バックエンドのセットアップ

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. フロントエンドのセットアップ

```bash
cd frontend
npm install
```

#### 4. 環境変数の設定

```bash
# backend/.env
cp backend/.env.example backend/.env
# 必要な環境変数を設定

# frontend/.env.local
cp frontend/.env.example frontend/.env.local
# 必要な環境変数を設定
```

#### 5. 開発サーバーの起動

```bash
# バックエンド
cd backend
uvicorn app.main:app --reload

# フロントエンド（別ターミナル）
cd frontend
npm run dev
```

## テスト

### バックエンド

```bash
cd backend
pytest app/tests/ -v --cov=app --cov-report=html
```

### フロントエンド

```bash
cd frontend
npm run test
npm run test:e2e
```

## デプロイ

### 本番環境へのデプロイ

```bash
# バックエンド（Cloud Run）
cd backend
gcloud builds submit --config cloudbuild.yaml

# フロントエンド（Firebase Hosting）
cd frontend
npm run build
firebase deploy --only hosting
```

## ドキュメント

- [技術仕様書](./doc/spec.md)
- [実装計画](./doc/plan.md)
- [ビジネス戦略](./doc/business.md)
- [API リファレンス](./doc/api-reference.md) *(準備中)*
- [貢献ガイド](./CONTRIBUTING.md)

## ライセンス

Copyright © 2025 AreaYield. All rights reserved.

## サポート

- **Email**: support@areayield.com
- **ドキュメント**: https://docs.areayield.com
- **Issue トラッカー**: https://github.com/your-org/area-yield-os/issues

## MVP目標

- **リリース目標**: 2026年3月
- **対象エリア**: 京都・大阪・東京・沖縄
- **成功指標**:
  - API p95レイテンシ < 5秒
  - RAG recall@10 ≥ 0.75
  - OCR word accuracy ≥ 0.93
  - ユニットテストカバレッジ ≥ 80%

