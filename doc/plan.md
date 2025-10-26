# AreaYield OS MVP実装計画

バージョン: 1.0.0  
最終更新: 2025-10-26  
ステータス: Draft

---

## 1. プロジェクト概要

### 1.1 MVP目標
- **リリース目標**: 2026年3月（計画マイルストーンと整合）
- **対象エリア**: 京都・大阪・東京・沖縄
- **コア機能**: Go/Amber/Stop判定、収益性評価、許認可分析、規制リスク評価
- **提供形態**: SaaS Web UI + REST API

### 1.2 MVP成功指標
- [ ] 4都市で分析可能
- [ ] API p95レイテンシ < 5秒
- [ ] RAG recall@10 ≥ 0.75
- [ ] OCR word accuracy ≥ 0.93
- [ ] ユニットテストカバレッジ ≥ 80%

---

## 2. 技術スタック（Firebase調整版）

### 2.1 アーキテクチャ変更点

**仕様からの主要変更**:

| 項目 | 仕様 | MVP実装 | 理由 |
|------|------|---------|------|
| Backend | FastAPI on K8s | FastAPI on Cloud Run | Firebase統合、スケーラビリティ、コスト最適化 |
| Auth | Auth0/Clerk | Firebase Auth | Firebase統合、無料枠活用 |
| Frontend Hosting | Kubernetes | Firebase Hosting | CDN内蔵、簡単デプロイ |
| Database | PostgreSQL | Cloud SQL (PostgreSQL) + Firestore | リレーショナル+NoSQL併用 |
| 非同期処理 | Celery + Redis | Cloud Tasks + Cloud Scheduler | サーバーレス、メンテ削減 |
| Cache | Redis | Cloud Memorystore (Redis) | マネージド、高可用性 |
| Vector DB | Pinecone | Pinecone（変更なし） | RAG品質重視 |
| Storage | S3 | Cloud Storage | GCP統合 |

### 2.2 最終構成

```
┌─────────────────────┐
│  Next.js Frontend   │ → Firebase Hosting + CDN
└──────────┬──────────┘
           │ HTTPS
┌──────────▼──────────┐
│  Firebase Auth      │ → 認証
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  API Gateway        │ → Cloud Endpoints/API Gateway（認証/レート制限/ヘッダ）
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Cloud Run          │ → FastAPI (Auto-scaling)
│  (FastAPI)          │    - /api/v1/analyze
└──────────┬──────────┘    - /api/v1/stats
           │
    ┌──────┴──────┬──────────────┬──────────┬──────────┐
┌───▼───┐   ┌────▼─────┐  ┌─────▼────┐  ┌──▼──────┐  ┌──▼────────┐
│Cloud  │   │Firestore │  │Pinecone  │  │Cloud    │  │BigQuery   │
│SQL    │   │(metadata)│  │(RAG)     │  │Storage  │  │(aggregations)│
│(PG)   │   │          │  │          │  │(raw data)│  │            │
└───────┘   └──────────┘  └──────────┘  └─────────┘  └────────────┘
```

### 2.3 技術選定

#### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI**: React 18, Tailwind CSS, shadcn/ui
- **State**: Zustand
- **Maps**: Mapbox GL JS
- **Charts**: Recharts

#### Backend
- **API**: FastAPI 0.110+
- **Runtime**: Python 3.11
- **Async**: httpx, asyncio
- **Validation**: Pydantic v2

#### Infrastructure
- **Hosting**: Firebase Hosting (Frontend)
- **Compute**: Cloud Run (Backend API)
- **Database**: 
  - Cloud SQL (PostgreSQL 15) - トランザクション、集計
  - Firestore - ユーザープロファイル、キャッシュ
- **Data Warehouse**: BigQuery - 集計済みメトリクス/統計APIのソース
- **Storage**: Cloud Storage (原データ、バックアップ)
- **Cache**: Cloud Memorystore (Redis)
- **Vector DB**: Pinecone (RAG)
- **Queue**: Cloud Tasks (バッチ処理)
- **Scheduler**: Cloud Scheduler (定期更新)
- **API Gateway**: Cloud Endpoints / API Gateway（認証、レート制限、ヘッダ付与）

#### CI/CD
- **VCS**: GitHub
- **CI**: GitHub Actions
- **Deploy**: Firebase CLI, gcloud CLI

---

## 3. 開発環境セットアップ

### 3.1 必要なツール

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
- Postman / Insomnia（API テスト）
```

### 3.2 プロジェクト構成

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

---

## 4. PR単位実装計画

### フェーズ0: プロジェクト初期化（2週間）

#### PR#1: プロジェクト構造とCI/CD基盤
**担当**: Lead Architect  
**工数**: 3日

**内容**:
- モノレポ構成の初期化
- GitHub Actions ワークフロー（lint, test）
- pre-commit フック設定
- README、CONTRIBUTING.md作成

**テスト**:
```yaml
# .github/workflows/ci.yml
- name: Lint Check
  run: |
    cd frontend && npm run lint
    cd backend && flake8 .
- name: Test
  run: |
    cd backend && pytest tests/ --cov=app --cov-report=xml
```

**受け入れ基準**:
- [ ] CI がグリーン
- [ ] pre-commit フックが動作
- [ ] README に環境構築手順記載

---

#### PR#2: Firebase/GCPプロジェクト初期設定
**担当**: DevOps Engineer  
**工数**: 2日

**内容**:
- Firebase プロジェクト作成
- GCP サービス有効化（Cloud Run, Cloud SQL, Cloud Storage）
- サービスアカウント設定
- Terraform による IaC 初期化
- API Gateway（Cloud Endpoints）初期構成（OpenAPIベースのデプロイ）
- BigQuery プロジェクト/データセットの作成（`areayield_mvp`）

**テスト**:
```bash
# インフラ検証
terraform plan
gcloud projects describe ${PROJECT_ID}
gcloud endpoints services list | grep areayield || true
bq ls areayield_mvp
```

**受け入れ基準**:
- [ ] Firebase Console でプロジェクト確認可能
- [ ] Terraform apply 成功
- [ ] サービスアカウントの権限確認完了
- [ ] Endpoints/API Gateway がデプロイ済み（/health に到達可能）
- [ ] BigQuery データセット作成済み

---

#### PR#3: Next.jsフロントエンド雛形
**担当**: Frontend Engineer  
**工数**: 3日

**内容**:
- Next.js 14 プロジェクト初期化
- Tailwind CSS, shadcn/ui セットアップ
- 基本レイアウト（Header, Footer, MainLayout）
- Firebase Hosting デプロイ設定

**テスト**:
```typescript
// frontend/tests/layout.test.tsx
describe('MainLayout', () => {
  it('renders header and footer', () => {
    render(<MainLayout><div>Test</div></MainLayout>);
    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('contentinfo')).toBeInTheDocument();
  });
});
```

**受け入れ基準**:
- [ ] npm run dev で起動確認
- [ ] Lighthouse スコア 90+
- [ ] Firebase Hosting にデプロイ成功

---

#### PR#4: FastAPIバックエンド雛形
**担当**: Backend Engineer  
**工数**: 3日

**内容**:
- FastAPI プロジェクト初期化
- Health Check エンドポイント
- CORS、ロギング設定
- Cloud Run デプロイ設定

**テスト**:
```python
# backend/app/tests/test_health.py
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**受け入れ基準**:
- [ ] pytest 実行成功
- [ ] Docker イメージビルド成功
- [ ] Cloud Run にデプロイ成功
- [ ] curl でヘルスチェック確認

---

### フェーズ1: 認証・データ基盤（2週間）

#### PR#5: Firebase Authentication統合
**担当**: Full Stack Engineer  
**工数**: 4日

**内容**:
- Firebase Auth SDK 統合（Frontend）
- メール/パスワード認証実装
- ログイン/サインアップ UI
- JWT検証ミドルウェア（Backend）
- RBAC実装（Admin/User/API）とルート保護（`/api/*`）

**テスト**:
```typescript
// frontend/tests/auth.test.tsx
describe('Login', () => {
  it('submits credentials', async () => {
    render(<LoginForm />);
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } });
    fireEvent.click(screen.getByText('Login'));
    await waitFor(() => expect(mockSignIn).toHaveBeenCalled());
  });
});
```

```python
# backend/app/tests/test_auth.py
def test_protected_endpoint_requires_auth(client):
    response = client.get("/api/v1/analyze")
    assert response.status_code == 401

def test_valid_token_grants_access(client, valid_token):
    response = client.get("/api/v1/analyze", headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code != 401
```

**受け入れ基準**:
- [ ] ユーザー登録・ログイン動作
- [ ] トークン検証成功
- [ ] 未認証時に401エラー
- [ ] RBACで権限外アクセスが403で拒否

---

#### PR#6: Cloud SQL セットアップ
**担当**: Backend Engineer  
**工数**: 3日

**内容**:
- Cloud SQL (PostgreSQL 15) インスタンス作成
- SQLAlchemy ORM 設定
- マイグレーションツール（Alembic）導入
- 初期スキーマ定義（users, analysis_results, data_sources）

**テスト**:
```python
# backend/app/tests/test_database.py
def test_database_connection(db_session):
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

def test_user_crud(db_session):
    user = User(email="test@example.com", uid="test123")
    db_session.add(user)
    db_session.commit()
    
    fetched = db_session.query(User).filter_by(uid="test123").first()
    assert fetched.email == "test@example.com"
```

**受け入れ基準**:
- [ ] Cloud SQL 接続成功
- [ ] マイグレーション実行成功
- [ ] CRUD テスト通過

---

#### PR#7: Firestore統合
**担当**: Backend Engineer  
**工数**: 2日

**内容**:
- Firebase Admin SDK 設定
- Firestore コレクション設計（user_profiles, cache）
- キャッシュレイヤー実装

**テスト**:
```python
# backend/app/tests/test_firestore.py
def test_cache_set_and_get(firestore_client):
    cache_key = "test:area:tokyo"
    cache_value = {"score": 75}
    
    set_cache(cache_key, cache_value, ttl=3600)
    result = get_cache(cache_key)
    
    assert result == cache_value

def test_cache_expiration(firestore_client):
    set_cache("test:expire", {"data": 1}, ttl=1)
    time.sleep(2)
    assert get_cache("test:expire") is None
```

**受け入れ基準**:
- [ ] Firestore 読み書き成功
- [ ] キャッシュ TTL 動作確認

---

### フェーズ2: データ統合・Geocoding（3週間）

#### PR#8: Geocoding サービス実装
**担当**: Backend Engineer  
**工数**: 4日

**内容**:
- Google Geocoding API 統合
- 住所正規化ロジック
- 町丁目レベルへの丸め処理
- レート制限・エラーハンドリング

**テスト**:
```python
# backend/app/tests/test_geocoding.py
@pytest.mark.asyncio
async def test_geocode_address():
    result = await geocode_address("京都府京都市東山区祇園町南側570-120")
    assert result["prefecture"] == "京都府"
    assert result["city"] == "京都市東山区"
    assert 34.0 < result["lat"] < 36.0
    assert 135.0 < result["lng"] < 136.0

@pytest.mark.asyncio
async def test_geocode_invalid_address():
    with pytest.raises(GeocodingError):
        await geocode_address("無効な住所12345")
```

**受け入れ基準**:
- [ ] 4都市の主要住所で変換成功
- [ ] 無効住所でエラーハンドリング
- [ ] レート制限が動作

---

#### PR#9: AirDNAデータ取得モジュール
**担当**: Data Engineer  
**工数**: 5日

**内容**:
- AirDNA REST API クライアント実装
- データ取得スクリプト（4都市分）
- Cloud Storage への保存（Parquet形式）
- データ検証（スキーマチェック）

**テスト**:
```python
# data-pipeline/tests/test_airdna.py
@pytest.mark.integration
async def test_fetch_airdna_data():
    client = AirDNAClient(api_key=os.getenv("AIRDNA_API_KEY"))
    data = await client.fetch_market_data(city="Kyoto", date="2025-09")
    
    assert "revpar" in data
    assert "occupancy_rate" in data
    assert len(data["listings"]) > 0

def test_validate_airdna_schema():
    sample_data = load_fixture("airdna_sample.json")
    assert validate_airdna_schema(sample_data) is True
```

**受け入れ基準**:
- [ ] 4都市のデータ取得成功
- [ ] Parquet ファイル保存確認
- [ ] スキーマ検証通過

---

#### PR#10: 用途地域データ統合
**担当**: Data Engineer  
**工数**: 4日

**内容**:
- 国土数値情報からShapefile取得
- GeoJSON 変換
- PostGIS拡張でCloud SQLに格納
- 緯度経度 → 用途地域判定関数

**テスト**:
```python
# backend/app/tests/test_zoning.py
def test_get_zoning_from_coordinates(db_session):
    # 京都市祇園（商業地域）
    zoning = get_zoning(lat=35.0036, lng=135.7736)
    assert zoning == "商業地域"

def test_get_zoning_outside_coverage(db_session):
    # カバレッジ外
    zoning = get_zoning(lat=0.0, lng=0.0)
    assert zoning is None
```

**受け入れ基準**:
- [ ] 4都市の用途地域データ投入完了
- [ ] 緯度経度判定が正確

---

#### PR#11: 学校・保育所データ統合
**担当**: Data Engineer  
**工数**: 3日

**内容**:
- 国土地理院データから学校位置取得
- 距離計算関数（Haversine式）
- 100m以内判定ロジック

**テスト**:
```python
# backend/app/tests/test_school_distance.py
def test_calculate_school_distance():
    distance = calculate_distance(
        lat1=35.0036, lng1=135.7736,
        lat2=35.0050, lng2=135.7750
    )
    assert 100 < distance < 200  # メートル

def test_check_school_restriction():
    is_restricted = check_school_restriction(lat=35.0036, lng=135.7736)
    assert isinstance(is_restricted, bool)
```

**受け入れ基準**:
- [ ] 距離計算精度 ±10m以内
- [ ] 100m判定が正確

---

### フェーズ3: コア分析エンジン（4週間）

#### PR#12: 収益性スコア計算
**担当**: Backend Engineer  
**工数**: 5日

**内容**:
- RevPAR計算ロジック実装
- 市場平均との比較
- 信頼区間算出
- 年間収益推定

**テスト**:
```python
# backend/app/tests/test_profitability.py
def test_calculate_profitability_score():
    score = calculate_profitability_score(
        revpar=6000,
        occupancy=70,
        market_avg_revpar=5000,
        confidence=0.8
    )
    assert 70 <= score <= 90

def test_estimate_annual_revenue():
    revenue_range = estimate_annual_revenue(
        revpar_range=[4500, 6800],
        rooms=1
    )
    assert revenue_range[0] == 4500 * 365
    assert revenue_range[1] == 6800 * 365
```

**受け入れ基準**:
- [ ] スコア計算が仕様通り
- [ ] エッジケース（occupancy=0など）でエラーなし
- [ ] カバレッジ 90%以上

---

#### PR#13: 許認可実現性スコア計算
**担当**: Backend Engineer  
**工数**: 5日

**内容**:
- 用途地域別スコア算出
- 学校距離ペナルティ
- 既存許可数による補正
- 取得可能な許可タイプ判定

**テスト**:
```python
# backend/app/tests/test_licensing.py
def test_calculate_licensing_score():
    score = calculate_licensing_score(
        zoning="商業地域",
        school_distance=150,
        existing_permits=20
    )
    assert 80 <= score <= 100

def test_licensing_score_residential_zone():
    score = calculate_licensing_score(
        zoning="第一種低層住専",
        school_distance=50,
        existing_permits=5
    )
    assert score < 40

def test_determine_available_license_types():
    types = determine_available_license_types(
        zoning="第一種住居",
        school_distance=150
    )
    assert "住宅宿泊事業（民泊）" in types
```

**受け入れ基準**:
- [ ] 全用途地域パターンでテスト通過
- [ ] スコアが0-100の範囲内

---

#### PR#14: 議事録クローラー（基本版）
**担当**: Data Engineer  
**工数**: 6日

**内容**:
- 京都市・大阪市議会サイトのスクレイピング
- PDF → テキスト変換（OCR）
- キーワードフィルタリング
- Cloud Storage への保存
- OCRフォールバック構成（Tesseract→PaddleOCR→クラウドOCR）と版面解析（layoutparser）

**テスト**:
```python
# data-pipeline/tests/test_crawler.py
@pytest.mark.integration
async def test_crawl_kyoto_minutes():
    crawler = MinuteCrawler(city="京都市")
    documents = await crawler.crawl(from_date="2024-01-01")
    
    assert len(documents) > 0
    assert all("民泊" in doc.text or "旅館業" in doc.text for doc in documents)

def test_pdf_to_text_conversion():
    text = pdf_to_text("tests/fixtures/sample_minute.pdf")
    assert len(text) > 100
    assert "議会" in text
```

**受け入れ基準**:
- [ ] 4都市で各10件以上の議事録取得
- [ ] OCR word accuracy ≥ 0.93
- [ ] 版面が複雑なPDFでも落丁率<1%

---

#### PR#15: Pinecone RAGシステム構築
**担当**: ML Engineer  
**工数**: 6日

**内容**:
- Pinecone index 作成
- OpenAI Embeddings 統合
- チャンキング処理（512トークン）
- ベクトル格納パイプライン

**テスト**:
```python
# backend/app/tests/test_rag.py
@pytest.mark.integration
def test_vector_search():
    results = vector_search(
        query="京都市 民泊 規制",
        top_k=10
    )
    assert len(results) == 10
    assert all(r["score"] > 0.5 for r in results)

def test_embed_and_store():
    doc = Document(
        text="京都市議会で民泊規制強化が議論されました",
        source="kyoto_council_2024_11",
        date="2024-11-15"
    )
    doc_id = embed_and_store(doc)
    assert doc_id is not None
```

**受け入れ基準**:
- [ ] recall@10 ≥ 0.75
- [ ] 検索レイテンシ p95 < 500ms

---

#### PR#16: 規制リスクスコア計算（RAG統合）
**担当**: ML Engineer  
**工数**: 6日

**内容**:
- RAG検索 → LLM要約パイプライン
- センチメント分析
- 規制リスクスコア算出
- 出典情報の付与

**テスト**:
```python
# backend/app/tests/test_regulation_risk.py
@pytest.mark.asyncio
async def test_calculate_regulation_risk():
    risk = await calculate_regulation_risk(
        query_area="京都市東山区",
        recent_violations=3
    )
    
    assert 0 <= risk["score"] <= 100
    assert risk["level"] in ["Low", "Medium", "High"]
    assert len(risk["signals"]) > 0
    assert all("source" in s for s in risk["signals"])

@pytest.mark.asyncio
async def test_regulation_risk_no_data():
    risk = await calculate_regulation_risk(
        query_area="テストエリア",
        recent_violations=0
    )
    assert risk["score"] == 0
    assert risk["level"] == "Low"
```

**受け入れ基準**:
- [ ] groundedness ≥ 0.7
- [ ] 全レスポンスに出典情報付与
- [ ] recall@10 < 0.6 の場合は「不明」を返し推論を抑止
- [ ] 規制シグナル抽出は出典（source_id/URL/日時）を併記

---

#### PR#17: 総合判定ロジック統合
**担当**: Backend Engineer  
**工数**: 4日

**内容**:
- 3つのスコアの重み付け統合
- Go/Amber/Stop判定
- 推奨アクションの生成
- メタデータ付与

**テスト**:
```python
# backend/app/tests/test_judgment.py
def test_overall_judgment_go():
    judgment = calculate_overall_judgment(
        profitability_score=85,
        licensing_score=80,
        regulation_risk_score=30
    )
    assert judgment["judgment"] == "Go"
    assert judgment["score"] >= 70

def test_overall_judgment_stop():
    judgment = calculate_overall_judgment(
        profitability_score=40,
        licensing_score=30,
        regulation_risk_score=80
    )
    assert judgment["judgment"] == "Stop"
    assert judgment["score"] < 50

def test_generate_recommendations():
    recommendations = generate_recommendations(
        judgment="Amber",
        profitability_score=70,
        licensing_score=60,
        regulation_risk_score=50
    )
    assert len(recommendations["action_items"]) > 0
```

**受け入れ基準**:
- [ ] 判定ロジックが仕様通り
- [ ] 全パターン（Go/Amber/Stop）でテスト通過

---

### フェーズ4: API実装（2週間）

#### PR#18: 分析API エンドポイント実装
**担当**: Backend Engineer  
**工数**: 5日

**内容**:
- `POST /api/v1/analyze` 実装
- リクエストバリデーション（Pydantic）
- レスポンスフォーマット
- エラーハンドリング
- `Idempotency-Key` ヘッダ対応（TTL 24h、一致ボディは同一結果返却）
- レスポンスに `metadata.analyzed_at`/`data_freshness`/`model_version` を付与
- `source_summary`（出典サマリ）を同梱
- レスポンスヘッダに `Areayield-API-Version: v1` を付与

**テスト**:
```python
# backend/app/tests/test_api_analyze.py
def test_analyze_with_address(client, auth_token):
    response = client.post(
        "/api/v1/analyze",
        json={"address": "京都府京都市東山区祇園町南側570-120"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["judgment"] in ["Go", "Amber", "Stop"]
    assert "profitability" in data
    assert "licensing" in data
    assert "regulation_risk" in data

def test_analyze_invalid_address(client, auth_token):
    response = client.post(
        "/api/v1/analyze",
        json={"address": "無効な住所"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400
    assert "error" in response.json()

def test_analyze_without_auth(client):
    response = client.post(
        "/api/v1/analyze",
        json={"address": "東京都渋谷区..."}
    )
    assert response.status_code == 401
```

**受け入れ基準**:
- [ ] 正常系レスポンスが仕様通り
- [ ] エラーケース全てカバー
- [ ] p95レイテンシ < 5秒
- [ ] Idempotency-Keyが同一ボディで同一結果/`job_id`を返却
- [ ] ヘッダ `Areayield-API-Version` を返却
- [ ] レスポンスに `metadata` と `source_summary` が含まれる

---

#### PR#19: 統計API実装
**担当**: Backend Engineer  
**工数**: 3日

**内容**:
- `GET /api/v1/stats/area` 実装
- エリア別集計データ返却
- キャッシュ活用
- カーソル方式のページネーション（`?limit=50&cursor=opaque`）
- BigQuery からの集計クエリ最適化と結果キャッシュ

**テスト**:
```python
# backend/app/tests/test_api_stats.py
def test_get_area_stats(client, auth_token):
    response = client.get(
        "/api/v1/stats/area?city=京都市東山区&district=祇園町南側",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "market_summary" in data
    assert data["market_summary"]["total_listings"] > 0

def test_get_area_stats_cache_hit(client, auth_token):
    # 1回目
    response1 = client.get("/api/v1/stats/area?city=京都市", headers={"Authorization": f"Bearer {auth_token}"})
    # 2回目（キャッシュヒット）
    response2 = client.get("/api/v1/stats/area?city=京都市", headers={"Authorization": f"Bearer {auth_token}"})
    
    assert response1.json() == response2.json()
```

**受け入れ基準**:
- [ ] キャッシュヒット率 > 50%
- [ ] レスポンス < 2秒
- [ ] `next_cursor` を返却し、続きの取得が可能

---

#### PR#20: レート制限・エラーハンドリング
**担当**: Backend Engineer  
**工数**: 3日

**内容**:
- レート制限ミドルウェア
- 標準エラーレスポンス
- リクエストID付与
- ログ記録
- レート制限ヘッダ: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`（429時は`Retry-After`）
- 相関ID: `X-Request-Id` 受け取り/生成/レスポンス反映
- 非推奨通知: `Areayield-API-Deprecated`/`Areayield-API-Sunset` ヘッダ付与（必要時）
- エラーモデルを仕様のJSON Schemaに準拠させる

**テスト**:
```python
# backend/app/tests/test_rate_limit.py
def test_rate_limit_enforcement(client, auth_token):
    # 制限を超えるリクエスト
    for i in range(61):
        response = client.post(
            "/api/v1/analyze",
            json={"address": "test"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 429
    assert "X-RateLimit-Remaining" in response.headers

def test_error_response_format(client):
    response = client.post("/api/v1/analyze", json={})
    assert response.status_code == 400
    error = response.json()["error"]
    assert "code" in error
    assert "message" in error
```

**受け入れ基準**:
- [ ] レート制限が動作
- [ ] エラーレスポンスが統一形式
- [ ] レート制限/相関/非推奨ヘッダが正しく返却

---

### フェーズ5: フロントエンド実装（3週間）

#### PR#21: 住所検索UI実装
**担当**: Frontend Engineer  
**工数**: 4日

**内容**:
- 検索フォームコンポーネント
- Google Places Autocomplete統合
- バリデーション
- ローディング状態

**テスト**:
```typescript
// frontend/tests/search-form.test.tsx
describe('SearchForm', () => {
  it('submits valid address', async () => {
    const mockOnSubmit = jest.fn();
    render(<SearchForm onSubmit={mockOnSubmit} />);
    
    const input = screen.getByLabelText('住所を入力');
    await userEvent.type(input, '京都府京都市東山区祇園町南側570-120');
    
    const button = screen.getByText('分析開始');
    await userEvent.click(button);
    
    expect(mockOnSubmit).toHaveBeenCalledWith({
      address: '京都府京都市東山区祇園町南側570-120'
    });
  });

  it('shows validation error for empty input', async () => {
    render(<SearchForm onSubmit={jest.fn()} />);
    const button = screen.getByText('分析開始');
    await userEvent.click(button);
    
    expect(screen.getByText('住所を入力してください')).toBeInTheDocument();
  });
});
```

**受け入れ基準**:
- [ ] Autocompleteが動作
- [ ] バリデーションが正確
- [ ] レスポンシブ対応

---

#### PR#22: 判定結果表示UI
**担当**: Frontend Engineer  
**工数**: 5日

**内容**:
- Go/Amber/Stop判定の視覚化
- スコアカードコンポーネント
- レーダーチャート（収益性・許認可・規制リスク）
- 推奨アクション表示

**テスト**:
```typescript
// frontend/tests/result-view.test.tsx
describe('ResultView', () => {
  const mockResult = {
    judgment: 'Go',
    score: 85,
    profitability: { revpar_range: [4500, 6800], confidence: 0.8 },
    licensing: { difficulty_score: 75 },
    regulation_risk: { score: 30, level: 'Low' }
  };

  it('renders judgment badge correctly', () => {
    render(<ResultView result={mockResult} />);
    const badge = screen.getByText('Go');
    expect(badge).toHaveClass('bg-green-500');
  });

  it('displays profitability metrics', () => {
    render(<ResultView result={mockResult} />);
    expect(screen.getByText(/4,500.*6,800/)).toBeInTheDocument();
  });
});
```

**受け入れ基準**:
- [ ] 全判定タイプで表示確認
- [ ] グラフが正確に描画
- [ ] アクセシビリティ（ARIA）対応

---

#### PR#23: エリア統計ダッシュボード
**担当**: Frontend Engineer  
**工数**: 5日

**内容**:
- エリア別統計表示
- 届出密度マップ（Mapbox）
- レビューテーマの可視化
- 競合物件数グラフ

**テスト**:
```typescript
// frontend/tests/dashboard.test.tsx
describe('Dashboard', () => {
  it('fetches and displays area stats', async () => {
    const mockStats = {
      market_summary: { total_listings: 234, avg_revpar: 5500 }
    };
    
    jest.spyOn(global, 'fetch').mockResolvedValue({
      json: async () => mockStats
    } as Response);
    
    render(<Dashboard city="京都市" />);
    
    await waitFor(() => {
      expect(screen.getByText('234件')).toBeInTheDocument();
      expect(screen.getByText('¥5,500')).toBeInTheDocument();
    });
  });
});
```

**受け入れ基準**:
- [ ] マップが正しく表示
- [ ] グラフがインタラクティブ
- [ ] データ取得エラー時のフォールバック

---

#### PR#24: 認証UI実装
**担当**: Frontend Engineer  
**工数**: 3日

**内容**:
- ログイン/サインアップページ
- プロテクトルート
- ユーザープロファイル表示
- ログアウト機能

**テスト**:
```typescript
// frontend/tests/auth-flow.test.tsx
describe('Auth Flow', () => {
  it('redirects to login when unauthenticated', () => {
    render(<ProtectedRoute><Dashboard /></ProtectedRoute>);
    expect(window.location.pathname).toBe('/login');
  });

  it('shows dashboard when authenticated', async () => {
    const mockUser = { uid: '123', email: 'test@example.com' };
    mockFirebaseAuth.currentUser = mockUser;
    
    render(<ProtectedRoute><Dashboard /></ProtectedRoute>);
    await waitFor(() => {
      expect(screen.getByText('ダッシュボード')).toBeInTheDocument();
    });
  });
});
```

**受け入れ基準**:
- [ ] 認証フロー完結
- [ ] セッション永続化

---

### フェーズ6: データパイプライン（2週間）

#### PR#25: 月次データ更新パイプライン
**担当**: Data Engineer  
**工数**: 6日

**内容**:
- Cloud Scheduler設定（月次実行）
- Cloud Functions（データ取得トリガー）
- AirDNA/公的データの自動取得
- データ品質チェック
- 異常検知アラート

**テスト**:
```python
# data-pipeline/tests/test_pipeline.py
def test_monthly_update_pipeline():
    with mock.patch('cloud_storage.upload') as mock_upload:
        run_monthly_update(date="2025-10")
        assert mock_upload.call_count >= 4  # 4都市分

def test_data_quality_check():
    invalid_data = {"revpar": -100}  # 異常値
    with pytest.raises(DataQualityError):
        validate_data_quality(invalid_data)
```

**受け入れ基準**:
- [ ] スケジュール実行成功
- [ ] データ品質チェック通過
- [ ] 失敗時のアラート送信確認

---

#### PR#26: RAG定期更新パイプライン
**担当**: ML Engineer  
**工数**: 4日

**内容**:
- 週次議事録クロール（Cloud Scheduler）
- 新規文書の自動ベクトル化
- Pinecone インデックス更新
- 重複排除ロジック

**テスト**:
```python
# data-pipeline/tests/test_rag_update.py
@pytest.mark.integration
def test_weekly_rag_update():
    with mock.patch('pinecone_client.upsert') as mock_upsert:
        run_weekly_rag_update()
        assert mock_upsert.call_count > 0

def test_duplicate_detection():
    doc1 = Document(text="同じ内容", checksum="abc123")
    doc2 = Document(text="同じ内容", checksum="abc123")
    
    assert is_duplicate(doc1, doc2) is True
```

**受け入れ基準**:
- [ ] 週次で新規文書追加確認
- [ ] 重複文書が除外される

---

### フェーズ7: テスト・最適化（2週間）

#### PR#27: E2Eテスト実装
**担当**: QA Engineer  
**工数**: 5日

**内容**:
- Playwright セットアップ
- E2Eテストシナリオ作成
  - 住所検索 → 結果表示
  - ログイン → 分析実行
  - エラーケース
- CI統合

**テスト**:
```typescript
// frontend/e2e/analysis-flow.spec.ts
test('complete analysis flow', async ({ page }) => {
  await page.goto('/');
  await page.fill('[name="address"]', '京都府京都市東山区祇園町南側570-120');
  await page.click('button:has-text("分析開始")');
  
  await expect(page.locator('[data-testid="judgment-badge"]')).toBeVisible();
  await expect(page.locator('[data-testid="revpar-value"]')).toContainText('¥');
});
```

**受け入れ基準**:
- [ ] 主要フロー全てカバー
- [ ] CI で自動実行

---

#### PR#28: パフォーマンス最適化
**担当**: Backend Engineer  
**工数**: 4日

**内容**:
- SQL クエリ最適化（インデックス追加）
- N+1問題解消
- キャッシュ戦略改善
- Cloud Run インスタンス設定調整

**テスト**:
```python
# backend/app/tests/test_performance.py
def test_analyze_endpoint_performance(client, auth_token):
    import time
    
    start = time.time()
    response = client.post(
        "/api/v1/analyze",
        json={"address": "京都府京都市東山区祇園町南側570-120"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 5.0  # p95 < 5秒
```

**受け入れ基準**:
- [ ] p95レイテンシ < 5秒達成
- [ ] キャッシュヒット率 > 60%
- [ ] Cloud Run コールドスタート < 2秒

---

#### PR#29: 負荷テスト
**担当**: DevOps Engineer  
**工数**: 3日

**内容**:
- Locust セットアップ
- 負荷テストシナリオ作成
- スケーラビリティ検証
- ボトルネック特定

**テスト**:
```python
# tests/load/locustfile.py
class AnalysisUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def analyze_address(self):
        self.client.post(
            "/api/v1/analyze",
            json={"address": "京都府京都市東山区祇園町南側570-120"},
            headers={"Authorization": f"Bearer {self.token}"}
        )

# 実行: locust -f locustfile.py --users 100 --spawn-rate 10
```

**受け入れ基準**:
- [ ] 100同時ユーザーで安定動作
- [ ] エラー率 < 1%
- [ ] Cloud Run 自動スケーリング確認

---

### フェーズ8: デプロイ・ドキュメント（1週間）

#### PR#30: 本番デプロイ設定
**担当**: DevOps Engineer  
**工数**: 3日

**内容**:
- 本番環境構築（Terraform）
- 環境変数管理（Secret Manager）
- カスタムドメイン設定
- SSL証明書
- モニタリング設定（Cloud Logging, Cloud Monitoring）
- Cloud Run リビジョンのトラフィックスプリット設定（Blue-Green）
- ロールバック手順の自動化（直近安定リビジョンへ即時切替）

**受け入れ基準**:
- [ ] 本番環境にデプロイ成功
- [ ] HTTPS アクセス可能
- [ ] モニタリングダッシュボード確認
- [ ] 新旧リビジョンのトラフィック切替/ロールバックを手順書通り実施可能

---

#### PR#31: APIドキュメント
**担当**: Technical Writer  
**工数**: 2日

**内容**:
- OpenAPI (Swagger) スキーマ生成
- API リファレンス作成
- cURL/Python サンプルコード
- Firebase Hosting でホスト

**受け入れ基準**:
- [ ] `/docs` でSwagger UI表示
- [ ] 全エンドポイントドキュメント化

---

#### PR#32: ユーザーガイド
**担当**: Technical Writer  
**工数**: 2日

**内容**:
- 使い方ガイド（スクリーンショット付き）
- FAQ
- トラブルシューティング
- Firebase Hosting でホスト

**受け入れ基準**:
- [ ] `/guide` でガイド表示
- [ ] 主要フロー全てカバー

---

## 5. CI/CD設定

### 5.1 GitHub Actions ワークフロー

#### Backend CI
```yaml
# .github/workflows/backend-ci.yml
name: Backend CI

on:
  pull_request:
    paths:
      - 'backend/**'
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run linters
        run: |
          cd backend
          flake8 app --max-line-length=120
          black --check app
          mypy app
      
      - name: Run tests
        run: |
          cd backend
          pytest app/tests/ \
            --cov=app \
            --cov-report=xml \
            --cov-report=term \
            --cov-fail-under=80
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: backend/coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Authenticate to GCP
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2
      
      - name: Build and push Docker image
        run: |
          cd backend
          gcloud builds submit \
            --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/areayield-api:${{ github.sha }}
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy areayield-api \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/areayield-api:${{ github.sha }} \
            --platform managed \
            --region asia-northeast1 \
            --allow-unauthenticated
```

#### Frontend CI
```yaml
# .github/workflows/frontend-ci.yml
name: Frontend CI

on:
  pull_request:
    paths:
      - 'frontend/**'
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run linters
        run: |
          cd frontend
          npm run lint
          npm run type-check
      
      - name: Run tests
        run: |
          cd frontend
          npm run test:ci
      
      - name: Build
        run: |
          cd frontend
          npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build
        run: |
          cd frontend
          npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}
          NEXT_PUBLIC_FIREBASE_CONFIG: ${{ secrets.FIREBASE_CONFIG }}
      
      - name: Deploy to Firebase Hosting
        run: |
          cd frontend
          npm install -g firebase-tools
          firebase deploy --only hosting --token ${{ secrets.FIREBASE_TOKEN }}

### 5.3 リリース基準（Release Criteria）

- **品質**: 単体/統合テスト合格、カバレッジ≥80%
- **性能**: `/analyze` p95<3秒（MVPは<5秒で許容）、エラー率<1%
- **RAG**: recall@10≥0.75、groundedness≥0.7、OCR word accuracy≥0.93
- **セキュリティ**: High以上の脆弱性ゼロ、依存アップデート適用
- **ロールバック**: ヘルスチェック不合格時に自動切替（Blue-Green/再デプロイ）
```

#### E2E Tests
```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  pull_request:
  push:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps
      
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report
```

### 5.2 PR テンプレート

```markdown
# .github/pull_request_template.md

## 概要
<!-- このPRの目的を簡潔に説明 -->

## 変更内容
<!-- 主な変更点をリスト -->
- 
- 

## テスト
<!-- 実施したテストを記載 -->
- [ ] ユニットテスト追加・更新
- [ ] 統合テスト実施
- [ ] 手動テスト完了

## チェックリスト
- [ ] コードレビュー依頼前にセルフレビュー完了
- [ ] CI が全てグリーン
- [ ] カバレッジが低下していない
- [ ] ドキュメント更新（必要な場合）
- [ ] 破壊的変更がある場合は明記

## スクリーンショット（UI変更の場合）
<!-- Before/After のスクリーンショット -->

## 関連Issue
Closes #

## レビュワーへの注意事項
<!-- 特に注目してほしい点があれば記載 -->
```

---

## 6. リスクと対応

### 6.1 技術的リスク

| リスク | 確率 | 影響 | 対応策 |
|--------|------|------|--------|
| **RAG品質がMVP基準未達** | 中 | 高 | ・フェーズ3早期にプロトタイプ検証<br>・目標未達時はルールベース+RAGのハイブリッド実装 |
| **Cloud Run コールドスタート** | 高 | 中 | ・最小インスタンス数=1に設定<br>・Warming リクエスト（Cloud Scheduler） |
| **AirDNA API制限** | 低 | 高 | ・データキャッシュを24h→1週間に延長<br>・APIコール数の監視アラート |
| **Geocoding APIコスト超過** | 中 | 中 | ・結果を永続キャッシュ<br>・月次予算アラート設定 |
| **Pineconeコスト** | 中 | 中 | ・HOT/COLDティア分離<br>・6ヶ月以上の古いデータはアーカイブ |

### 6.2 スケジュールリスク

| リスク | 対応策 |
|--------|--------|
| **データ取得の遅延** | ・AirDNA契約を即座に締結（リードタイム2-4週間）<br>・並行してモックデータで開発継続 |
| **RAG実装の遅延** | ・P0機能（収益性・許認可）を優先<br>・規制リスクはフェーズ2に一部延期も検討 |
| **人的リソース不足** | ・外部契約エンジニアの早期確保<br>・非クリティカルな機能（ヒートマップ等）は後回し |

### 6.3 仕様へのフィードバック

#### 変更提案1: バッチ分析をMVPから除外
**理由**: MVP開発工数削減。単一分析で十分な価値提供可能。  
**代替案**: フェーズ2で並列処理基盤とともに実装。

#### 変更提案2: Cloud RunをFastAPIホストに採用
**理由**: FastAPIの優位性を維持しつつ、Firebaseとの統合とサーバーレスのメリット享受。  
**実装**: Cloud Run + Firebase Auth + Firebase Hosting の構成。

#### 変更提案3: TimescaleDB → BigQuery
**理由**: MVP段階では時系列クエリの複雑性は限定的。BigQueryで集計済みデータを保持。  
**実装**: 将来の高度分析（フェーズ4）でTimescaleDB追加を検討。

#### 変更提案4: OCR品質目標の段階的達成
**理由**: word accuracy 0.95は初期段階では困難。  
**MVP目標**: 0.93以上  
**フェーズ2目標**: 0.95以上（OCRエンジン追加、ファインチューニング）

#### 変更提案5: レビューテーマ分析を次フェーズへ
**理由**: MVP範囲縮小。LDAモデルの精度向上には時間が必要。  
**代替**: 規制リスクと許認可にフォーカス。

---

## 7. 開発ガイドライン

### 7.1 コーディング規約

#### Python (Backend)
```python
# PEP 8準拠
# Black（フォーマッター）、Flake8（リンター）、mypy（型チェック）

# 例
from typing import Optional
from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    """分析リクエストモデル"""
    address: str
    property_type: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "address": "京都府京都市東山区祇園町南側570-120"
            }
        }
```

#### TypeScript (Frontend)
```typescript
// ESLint + Prettier
// Airbnb スタイルガイド準拠

// 例
interface AnalysisResult {
  judgment: 'Go' | 'Amber' | 'Stop';
  score: number;
  profitability: ProfitabilityScore;
}

// 関数はアロー関数を優先
const analyzeAddress = async (address: string): Promise<AnalysisResult> => {
  // 実装
};
```

### 7.2 ブランチ戦略

```
main
  ├─ develop (統合ブランチ)
  │   ├─ feature/PR-001-setup
  │   ├─ feature/PR-002-firebase
  │   ├─ feature/PR-003-nextjs
  │   └─ ...
  └─ hotfix/* (緊急修正)
```

**ルール**:
- `feature/*` → `develop` → `main`
- PR は develop にマージ
- main は本番デプロイ専用
- PR番号をブランチ名に含める

### 7.3 コミットメッセージ

```
<type>(<scope>): <subject>

<body>

<footer>
```

**例**:
```
feat(backend): add geocoding service

- Implemented Google Geocoding API integration
- Added address normalization logic
- Included rate limiting

Closes #8
```

**type**:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: フォーマット
- `refactor`: リファクタリング
- `test`: テスト追加
- `chore`: ビルド・設定

### 7.4 テスト方針

#### カバレッジ目標
- ユニットテスト: 80%以上
- 統合テスト: 主要エンドポイント全て
- E2E: クリティカルパス全て

#### テスト命名規則
```python
def test_<function>_<scenario>_<expected_result>():
    # 例: test_geocode_address_valid_input_returns_coordinates()
    pass
```

#### テストの構造（AAA パターン）
```python
def test_calculate_profitability_score():
    # Arrange（準備）
    revpar = 6000
    occupancy = 70
    market_avg = 5000
    confidence = 0.8
    
    # Act（実行）
    score = calculate_profitability_score(
        revpar, occupancy, market_avg, confidence
    )
    
    # Assert（検証）
    assert 70 <= score <= 90
```

---

## 8. モニタリング・運用

### 8.1 ヘルスチェック

```python
# backend/app/api/health.py
@router.get("/health")
async def health_check():
    checks = {
        "api": "ok",
        "database": await check_database(),
        "firestore": await check_firestore(),
        "pinecone": await check_pinecone(),
    }
    
    all_ok = all(v == "ok" for v in checks.values())
    status_code = 200 if all_ok else 503
    
    return JSONResponse(
        content=checks,
        status_code=status_code
    )
```

### 8.2 アラート設定

**Cloud Monitoring アラート**:
1. API エラー率 > 5%（5分間）
2. p95レイテンシ > 10秒
3. Cloud Run インスタンス > 10
4. データベース接続数 > 80%
5. RAG recall@10 < 0.70（日次集計）

**通知先**: Slack + Email

### 8.3 ログ設計

```python
# 構造化ログ（JSON）
import structlog

logger = structlog.get_logger()

logger.info(
    "analysis_completed",
    user_id=user_id,
    address=address,
    judgment=result.judgment,
    latency_ms=elapsed_ms,
    cache_hit=cache_hit
)
```

**ログレベル**:
- ERROR: システムエラー、外部API失敗
- WARNING: レート制限、データ品質警告
- INFO: API呼び出し、分析完了
- DEBUG: 詳細デバッグ情報

### 8.4 FinOps（コスト管理）

- **目標**: 1判定あたり平均<50円、ベクトル検索 p95<500ms
- **施策**: 結果キャッシュ（24h）、同一エリアRAGスキップ、軽量LLMとのハイブリッド
- **監視**: LLM/ベクトルDB/ストレージ/ネットワーク別コストの日次集計
- **ガードレール**: 月次+20%で警告、+50%で緊急モード（キャッシュTTL延長/非同期化）

---

## 9. セキュリティ

### 9.1 チェックリスト

- [ ] Firebase Auth による認証
- [ ] Cloud Run への認証ヘッダー検証
- [ ] SQL インジェクション対策（Parameterized Query）
- [ ] CORS 設定（許可オリジンのみ）
- [ ] レート制限実装
- [ ] 機密情報は Secret Manager 管理
- [ ] 依存ライブラリの脆弱性スキャン（Dependabot）
- [ ] HTTPS 通信のみ許可
- [ ] ログに個人情報を含めない

### 9.3 データ保持・削除ポリシー

- **保持期間（既定）**:
  - 原文書（PDF/HTML）: 24ヶ月
  - 抽出テキスト/OCR結果: 24ヶ月
  - 埋め込み（ベクトル）: 12ヶ月（最新6ヶ月はHOTティア）
  - 解析結果キャッシュ: 24時間
  - 監査/アクセスログ: 180日
- **削除**:
  - ユーザー依頼/契約終了時は30日以内に個別データ削除（バックアップは最大90日でロールオフ）
  - DSAR（開示/削除請求）に30日以内に対応
- **安全消去**: 暗号化キー廃棄またはストレージレベルでのセキュア消去

### 9.2 依存関係管理

```yaml
# dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
  
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
```

---

## 10. 完了定義（Definition of Done）

各PRがマージされるための条件:

- [ ] ✅ CI が全てグリーン（lint, test, build）
- [ ] ✅ コードレビュー承認（最低1名）
- [ ] ✅ ユニットテストカバレッジ ≥ 80%
- [ ] ✅ 統合テスト実施（該当する場合）
- [ ] ✅ ドキュメント更新（API変更、新機能）
- [ ] ✅ 手動テスト完了（UI変更）
- [ ] ✅ セキュリティチェック通過
- [ ] ✅ パフォーマンス基準クリア（該当する場合）

---

## 11. マイルストーン

| マイルストーン | 完了日 | 成果物 |
|---------------|--------|--------|
| **M1: 基盤完成** | 2025-11-15 | PR#1-7完了、CI/CD動作、認証・DB構築 |
| **M2: データ統合** | 2025-12-06 | PR#8-11完了、Geocoding・AirDNA・用途地域統合 |
| **M3: コアエンジン** | 2026-01-03 | PR#12-17完了、全スコア計算・判定ロジック実装 |
| **M4: API完成** | 2026-01-17 | PR#18-20完了、分析API・統計API動作 |
| **M5: UI完成** | 2026-02-07 | PR#21-24完了、検索・結果表示・認証UI実装 |
| **M6: パイプライン** | 2026-02-21 | PR#25-26完了、月次更新・RAG更新自動化 |
| **M7: テスト・最適化** | 2026-03-07 | PR#27-29完了、E2E・負荷テスト通過 |
| **M8: MVP リリース** | 2026-03-14 | PR#30-32完了、本番デプロイ、ドキュメント公開 |

---

## 12. チーム編成（推奨）

| 役割 | 人数 | 主な責任 |
|------|------|---------|
| **Lead Architect** | 1名 | 全体設計、技術意思決定、コードレビュー |
| **Backend Engineer** | 2名 | FastAPI実装、スコア計算、API開発 |
| **Frontend Engineer** | 2名 | Next.js実装、UI/UX、コンポーネント開発 |
| **Data Engineer** | 1名 | データ取得、ETL、パイプライン構築 |
| **ML Engineer** | 1名 | RAG実装、ベクトルDB、LLM統合 |
| **DevOps Engineer** | 1名 | インフラ、CI/CD、監視、デプロイ |
| **QA Engineer** | 1名 | テスト計画、E2Eテスト、品質保証 |
| **Technical Writer** | 0.5名 | ドキュメント、APIリファレンス |

**合計**: 9.5人月（MVP期間: 4.5ヶ月）

---

## 13. 次のステップ

### MVP完了後（フェーズ2へ）

1. **週次データ更新への移行**（PR#33）
2. **レビューテーマ分析の追加**（PR#34）
3. **SDK公開（Python/TypeScript）**（PR#35-36）
4. **ヒートマップAPI実装**（PR#37）
5. **町丁目 → 地番精緻化**（PR#38）
6. **バッチ分析（並列処理）**（PR#39-40）

---

## 付録

### A. 環境変数一覧

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@host:5432/areayield
FIREBASE_PROJECT_ID=areayield-prod
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
AIRDNA_API_KEY=xxx
OPENAI_API_KEY=xxx
PINECONE_API_KEY=xxx
PINECONE_ENVIRONMENT=us-west1-gcp
REDIS_URL=redis://localhost:6379
MAPBOX_API_KEY=xxx
BIGQUERY_DATASET=areayield_mvp
BIGQUERY_TABLE=area_stats

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://api.areayield.com
NEXT_PUBLIC_FIREBASE_CONFIG={"apiKey":"xxx",...}
NEXT_PUBLIC_MAPBOX_TOKEN=xxx
```

### B. 有用なコマンド

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Database Migration
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head

# Test
pytest app/tests/ -v --cov=app
npm run test:ci

# Build & Deploy
gcloud builds submit --config cloudbuild.yaml
firebase deploy --only hosting
```

### C. 参考リンク

- [Firebase Documentation](https://firebase.google.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)

---

**ドキュメントステータス**: 🟡 Draft → レビュー依頼中  
**作成者**: Senior Software Architect  
**レビュー依頼先**: Tech Lead, Product Manager  
**次回更新**: M1完了後（2025-11-15）

