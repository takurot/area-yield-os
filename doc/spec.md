# AreaYield OS 技術仕様書

バージョン: 1.0.0  
最終更新: 2025-10-26  
ステータス: 設計中

## 1. システム概要

### 1.1 目的
AreaYield OSは、短期賃貸（民泊）投資の可否判定を、収益性・許認可実現性・規制リスクの3軸で評価し、住所/町丁目レベルでGo/Amber/Stop判定を提供するSaaS/APIプラットフォームです。

### 1.2 主要機能
- **エリア投資判定**: 住所・町丁目単位での三段階評価（Go/Amber/Stop）
- **収益性予測**: RevPARレンジの算出と信頼区間の提示
- **許認可分析**: 旅館業許可・民泊届出の取得難易度評価
- **規制リスク評価**: 自治体の規制強化動向のスコア化（0-100）
- **エリア統計**: 届出密度、競合物件数、レビュー傾向の可視化

### 1.3 提供形態
- **SaaSアプリケーション**: Webベースのダッシュボード
- **REST API**: プログラマティックアクセス
- **SDK**: Python/TypeScript（フェーズ2）

---

## 2. システムアーキテクチャ

### 2.1 全体構成

```
┌─────────────────┐
│   Frontend      │  Next.js + React
│   (Web UI)      │  
└────────┬────────┘
         │ HTTPS
┌────────▼────────┐
│   API Gateway   │  認証・レート制限・ルーティング
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────────────┐
│ SaaS  │ │  API Service    │
│Service│ │  (FastAPI)      │
└───┬───┘ └──┬──────────────┘
    │        │
    └────┬───┘
         │
┌────────▼────────────────────┐
│  Core Analysis Engine       │
│  ・Scoring Module           │
│  ・Bayesian Integration     │
│  ・RAG System               │
└────────┬────────────────────┘
         │
    ┌────┴─────┬─────────┬────────┐
┌───▼───┐ ┌───▼───┐ ┌───▼────┐ ┌─▼─────┐
│AirDNA │ │Govt   │ │Vector  │ │Cache  │
│Adapter│ │Data   │ │DB      │ │(Redis)│
│       │ │Crawler│ │(Pinecone)│       │
└───────┘ └───────┘ └────────┘ └───────┘
```

### 2.2 技術スタック

#### フロントエンド
- **フレームワーク**: Next.js 14+ (App Router)
- **UI**: React 18+, Tailwind CSS, shadcn/ui
- **地図可視化**: Mapbox GL JS / Google Maps API
- **グラフ**: Recharts / D3.js
- **状態管理**: Zustand / React Query

#### バックエンド
- **APIフレームワーク**: FastAPI (Python 3.11+)
- **非同期処理**: Celery + Redis
- **認証**: Auth0 / Firebase Auth / Clerk
- **データベース**: 
  - PostgreSQL 15+ (メタデータ、ユーザー、トランザクション)
  - TimescaleDB (時系列データ)
- **ベクトルDB**: Pinecone / Weaviate (議事録・レビューのRAG)
- **キャッシュ**: Redis 7+

#### データパイプライン
- **ETL**: Apache Airflow / Dagster
- **データレイク**: AWS S3 / Google Cloud Storage
- **データウェアハウス**: BigQuery / Snowflake

#### インフラ
- **クラウド**: AWS / GCP
- **コンテナ**: Docker + Kubernetes (EKS / GKE)
- **CI/CD**: GitHub Actions
- **モニタリング**: Datadog / Grafana + Prometheus
- **ロギング**: CloudWatch / Cloud Logging + Loki

---

## 3. データソース統合

### 3.1 AirDNAデータ
**取得方法**: REST API（月次バッチ取得）

**主要指標**:
- RevPAR（Revenue Per Available Room）
- 稼働率（Occupancy Rate）
- ADR（Average Daily Rate）
- 供給数（Active Listings）
- レビュー数・評価
- レビューテキスト

**更新頻度**: 初期は月1回 → 6ヶ月後に週次へ移行

**ストレージ**: 
- Raw Data: S3 / GCS (Parquet形式)
- Processed: TimescaleDB (町丁目集計済み)

### 3.2 公的データ

#### 民泊届出データ
- **出典**: 観光庁「民泊制度ポータルサイト」
- **形式**: CSV / API
- **情報**: 届出番号、住所、事業者名、届出日
- **更新**: 月次

#### 旅館業許可データ
- **出典**: 各自治体の公開データ / 厚労省
- **形式**: PDF / CSV / スクレイピング
- **情報**: 許可番号、施設名、住所、許可日
- **更新**: 月次〜四半期

#### 用途地域データ
- **出典**: 国土交通省「国土数値情報」
- **形式**: Shapefile / GeoJSON
- **情報**: 用途地域区分、建ぺい率、容積率
- **更新**: 年次（都市計画変更時）

#### 観光統計
- **出典**: JTB総合研究所、各自治体観光統計
- **形式**: Excel / CSV / PDF
- **情報**: 宿泊者数、国籍別比率、季節変動
- **更新**: 月次〜四半期

#### 議事録・パブリックコメント
- **出典**: 自治体HP、e-Gov
- **形式**: HTML / PDF
- **情報**: 規制強化議論、条例改正、違反事例
- **更新**: リアルタイム（週次スクレイピング）

#### イベント情報
- **出典**: 各自治体観光課、イベントカレンダーサイト (例: Walkerplus)
- **形式**: iCal / API / スクレイピング
- **情報**: イベント名、開催期間、場所、想定来場者数
- **更新**: 週次
- **備考**: フェーズ4の需要予測モデルで活用予定

### 3.3 データクローラー設計

```python
# 例: 議事録クローラー
class MinpakuMinuteCrawler:
    def __init__(self, prefecture: str):
        self.target_keywords = [
            "民泊", "旅館業法", "簡易宿所", 
            "住居専用地域", "届出", "条例"
        ]
    
    async def crawl(self) -> List[Document]:
        # 自治体議会サイトをスクレイピング
        # PDF → テキスト変換
        # キーワードフィルタリング
        # ベクトル化してPineconeに格納
        pass
```

---

## 4. 入力・出力仕様

### 4.1 入力パラメータ

#### SaaS UI
- **必須**:
  - `address`: 住所（都道府県、市区町村、町丁目、番地）
  - または `lat`, `lng`: 緯度経度
- **オプション**:
  - `property_type`: 物件タイプ（マンション/一戸建て/アパート）
  - `rooms`: 部屋数
  - `capacity`: 定員
  - `price_range`: 想定価格帯（円/泊）

#### API
```json
POST /api/v1/analyze
{
  "address": "京都府京都市東山区祇園町南側570-120",
  "property_type": "apartment",
  "rooms": 2,
  "capacity": 4,
  "price_range": [8000, 15000]
}
```

### 4.2 出力フォーマット

#### レスポンス例
```json
{
  "judgment": "Amber",
  "score": 65,
  "area": {
    "prefecture": "京都府",
    "city": "京都市東山区",
    "district": "祇園町南側",
    "lat": 35.0036,
    "lng": 135.7736
  },
  "profitability": {
    "revpar_range": [4500, 6800],
    "confidence": 0.75,
    "occupancy_rate": 68,
    "adr": 9500,
    "estimated_annual_revenue": [1640000, 2480000],
    "peak_months": ["3月", "4月", "10月", "11月"]
  },
  "licensing": {
    "difficulty_score": 55,
    "available_types": ["旅館業（簡易宿所）", "住宅宿泊事業（民泊）"],
    "restrictions": [
      "住居専用地域のため年間180日制限",
      "学校・保育所から100m以内規制"
    ],
    "estimated_process_days": 90
  },
  "regulation_risk": {
    "score": 45,
    "level": "Medium",
    "signals": [
      {
        "source": "京都市議会2024年11月定例会",
        "summary": "祇園地区での新規民泊抑制案が委員会で議論",
        "sentiment": -0.6,
        "date": "2024-11-15"
      }
    ],
    "recent_violations": 3,
    "trend": "強化傾向"
  },
  "market_stats": {
    "active_listings": 47,
    "listing_density": 8.2,
    "competition_level": "High",
    "review_themes": [
      {"theme": "立地", "sentiment": 0.85, "count": 234},
      {"theme": "清潔さ", "sentiment": 0.78, "count": 189},
      {"theme": "騒音", "sentiment": -0.45, "count": 67}
    ]
  },
  "recommendation": {
    "summary": "収益性は高いが、規制強化リスクあり。長期投資には慎重な検討が必要。",
    "action_items": [
      "旅館業許可の取得を推奨（民泊届出では年間営業制限）",
      "近隣住民との事前協議実施",
      "規制動向を3ヶ月ごとにモニタリング"
    ]
  },
  "metadata": {
    "analyzed_at": "2025-10-26T10:30:00Z",
    "data_freshness": "2025-10-20",
    "model_version": "1.2.3"
  }
}
```

### 4.3 判定ロジック

| 判定 | 条件 |
|------|------|
| **Go** | 総合スコア≥70 かつ 規制リスク≤40 かつ RevPAR信頼度≥0.7 |
| **Amber** | 総合スコア 50-69 または 規制リスク 41-70 |
| **Stop** | 総合スコア<50 または 規制リスク>70 または 許認可取得不可 |

---

## 5. コア分析エンジン

### 5.1 総合スコア計算（ベイズ統合）

#### スコアの構成
```
総合スコア = w1 × 収益性スコア 
           + w2 × 許認可実現性スコア 
           + w3 × (100 - 規制リスクスコア)

※ w1=0.4, w2=0.3, w3=0.3（初期重み、機械学習で最適化）
```

#### 収益性スコア
```python
def calculate_profitability_score(
    revpar: float,
    occupancy: float,
    market_avg_revpar: float,
    confidence: float
) -> float:
    """
    RevPARの市場平均との比較 + 稼働率 + 信頼度で算出
    """
    revpar_ratio = min(revpar / market_avg_revpar, 1.5)
    occupancy_score = occupancy / 100
    base_score = (revpar_ratio * 50 + occupancy_score * 50)
    return base_score * confidence
```

#### 許認可実現性スコア
```python
def calculate_licensing_score(
    zoning: str,          # 用途地域
    school_distance: int, # 学校からの距離(m)
    existing_permits: int # 既存許可件数
) -> float:
    """
    用途地域、学校距離、既存許可状況から算出
    """
    zoning_score = {
        "商業地域": 100,
        "近隣商業": 90,
        "第一種住居": 70,
        "第二種住居": 70,
        "第一種低層住専": 30,
        "第二種低層住専": 30
    }.get(zoning, 50)
    
    school_penalty = max(0, (100 - school_distance) * 0.3) if school_distance < 100 else 0
    
    competition_factor = max(0.5, 1 - (existing_permits / 100))
    
    return (zoning_score - school_penalty) * competition_factor
```

#### 規制リスクスコア（RAGベース）
```python
def calculate_regulation_risk(
    minutes_embeddings: List[Vector],
    query_area: str,
    recent_violations: int,
    media_sentiment: float
) -> Dict:
    """
    議事録RAG + 違反件数 + 報道センチメントで算出
    """
    # 1. ベクトル検索で関連議事録取得
    relevant_docs = vector_db.search(
        query=f"{query_area} 民泊 規制",
        top_k=10
    )
    
    # 2. LLMで規制強化シグナル抽出
    signals = []
    for doc in relevant_docs:
        sentiment = analyze_sentiment(doc.text)  # -1 to 1
        recency = calculate_recency_weight(doc.date)
        signals.append({
            "sentiment": sentiment,
            "recency": recency,
            "source": doc.source
        })
    
    # 3. スコア統合
    sentiment_score = sum(s["sentiment"] * s["recency"] for s in signals) / len(signals)
    violation_score = min(recent_violations * 5, 30)
    
    risk_score = (
        abs(sentiment_score) * 50 +  # 負のセンチメントほど高リスク
        violation_score +
        abs(media_sentiment) * 20
    )
    
    return {
        "score": min(risk_score, 100),
        "signals": signals,
        "trend": "強化傾向" if sentiment_score < -0.3 else "安定"
    }
```

### 5.2 マーケット統計分析

#### レビューテーマ抽出
物件のレビューテキストデータから、顧客が重視するテーマ（例: 立地、清潔さ、騒音、アメニティ）を抽出する。

```python
from gensim import models, corpora

def extract_review_themes(texts: List[str]) -> List[Dict]:
    """
    レビューテキストからトピックモデル(LDA)を用いてテーマを抽出・集計
    """
    # テキストの前処理（ストップワード除去など）
    processed_texts = [preprocess(text) for text in texts]
    
    # 辞書とコーパスを作成
    dictionary = corpora.Dictionary(processed_texts)
    corpus = [dictionary.doc2bow(text) for text in processed_texts]
    
    # LDAモデルでトピックを抽出
    lda_model = models.LdaModel(corpus, num_topics=5, id2word=dictionary, passes=15)
    
    # 各トピックのセンチメントを分析し、結果を整形
    # ...
    
    # 例
    return [
      {"theme": "立地", "sentiment": 0.85, "count": 234},
      {"theme": "清潔さ", "sentiment": 0.78, "count": 189},
      {"theme": "騒音", "sentiment": -0.45, "count": 67}
    ]
```

#### 届出密度計算
```python
def calculate_listing_density(
    notification_count: int, # 町丁目内の届出件数
    area_sq_km: float # 町丁目の面積 (km2)
) -> float:
    """
    届出件数を面積で除算し、1km2あたりの密度を算出
    """
    if area_sq_km == 0:
        return 0
    return notification_count / area_sq_km
```

### 5.3 RAGシステム設計

#### ベクトル化モデル
- **エンベディング**: OpenAI `text-embedding-3-small` or `text-embedding-3-large`
- **次元数**: 1536
- **チャンクサイズ**: 512トークン、オーバーラップ50トークン

#### 検索フロー
```
1. ユーザークエリ → エリア情報抽出
2. 「{市区町村} + 民泊/旅館業法/条例」でベクトル検索
3. Top-10文書を取得
4. LLM（GPT-4 Turbo）でサマリー生成
   - 規制強化の有無
   - 具体的な制限内容
   - 議論の時期と頻度
5. センチメントスコア化
```

#### プロンプト例
```
以下は{city}の議会議事録の抜粋です。
民泊・短期賃貸に関する規制強化の動向を分析し、
以下の形式で出力してください：

- 規制強化の可能性: [高/中/低]
- 主な議論内容: [箇条書き]
- センチメント: [-1.0 to 1.0]
- 施行予定時期: [yyyy-mm or 不明]

議事録:
{documents}
```

#### 日本語OCR/レイアウト解析
- **OCRエンジン**: Tesseract(ja)、PaddleOCR、日本語対応クラウドOCR（Azure Read、Google Document AI）をフォールバック構成
- **レイアウト解析**: PDF→テキスト変換時に段組/表/見出しを保持（例: pdfminer.six + layoutparser）
- **品質基準**: 単語正解率≥0.95（検証セット）、ページ落ち率<1%
- **前処理**: 画像二値化/歪み補正/解像度標準化、重複文書排除（ハッシュ）
- **表抽出**: 必要に応じて表を構造化（camelot/tabula）

#### ガードレールと安全設計
- 回答は常に出典（`source_id`/URL/発言日時）を併記
- 検索ヒットが閾値未満（recall@k<0.6）の場合は「不明」とし推論を禁止
- PII/個人名を含む箇所はマスキングして格納・提示
- 生成結果の根拠照合（groundedness）<0.7のときは規制リスクの自動上振れ/下振れを禁止

#### 品質評価指標（RAG）
- 検索: recall@k、mAP、重複率
- 要約: groundedness、factuality、coverage
- OCR: word accuracy、page success rate
- 目標: recall@10≥0.8、groundedness≥0.7、OCR word accuracy≥0.95

### 5.4 ベイズ更新（ユーザーフィードバック学習）

```python
class BayesianScoreUpdater:
    """
    ユーザーの実際の投資結果をフィードバックとして学習
    """
    def update_weights(
        self,
        predicted_score: float,
        actual_outcome: str,  # "success" | "failure" | "neutral"
        area: str
    ):
        # 地域別の重みパラメータをベイズ更新
        # 成功率が高いエリアは重みを上方修正
        pass
```

---

## 6. API仕様

### 6.1 認証

- **方式**: Bearer Token（JWT）
- **有効期限**: 1時間（リフレッシュトークン: 30日）

```
Authorization: Bearer <token>
```

### 6.2 エンドポイント一覧

#### 6.2.1 分析API

```
POST /api/v1/analyze
Content-Type: application/json
Authorization: Bearer <token>

Request Body: (4.1参照)
Response: (4.2参照)
```

#### 6.2.2 バッチ分析

```
POST /api/v1/analyze/batch
Content-Type: application/json

{
  "locations": [
    {"address": "東京都渋谷区..."},
    {"lat": 35.6812, "lng": 139.7671},
    ...
  ]
}

Response:
{
  "job_id": "batch_20251026_abc123",
  "status": "processing",
  "total": 50,
  "estimated_completion": "2025-10-26T11:00:00Z"
}

# 結果取得
GET /api/v1/analyze/batch/{job_id}
```

#### 6.2.3 統計データ

```
GET /api/v1/stats/area?city={city}&district={district}

Response:
{
  "area": {...},
  "market_summary": {
    "avg_revpar": 5500,
    "total_listings": 234,
    "growth_rate": 0.12
  },
  "regulation_summary": {
    "latest_update": "2024-11-01",
    "restrictions": [...]
  }
}
```

#### 6.2.4 ヒートマップデータ

```
GET /api/v1/heatmap?bounds={minLat},{minLng},{maxLat},{maxLng}&metric={revpar|risk|score}

Response:
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [139.7671, 35.6812]},
      "properties": {"value": 6500, "judgment": "Go"}
    },
    ...
  ]
}
```

### 6.3 レート制限

| プラン | 価格（月額） | リクエスト/分 | リクエスト/月 | バッチサイズ |
|--------|--------------|------|-----------|---------|
| SaaS | 3万円/席〜 | 60 | 無制限 | 50 |
| API Basic | 5万円〜 | 10 | 1,000 | 20 |
| API Pro | （別途見積） | 100 | 10,000 | 200 |

---

### 6.4 エラーモデル
標準エラーレスポンス（全エンドポイント共通）:
```json
{
  "error": {
    "code": "validation_failed",
    "message": "address is required",
    "details": [{"field": "address", "reason": "required"}]
  },
  "request_id": "req_20251026_abcd1234",
  "status": 400
}
```
主なエラーコード: `invalid_argument`(400), `validation_failed`(400), `unauthorized`(401), `forbidden`(403), `not_found`(404), `conflict`(409), `rate_limited`/`too_many_requests`(429), `timeout`(504), `internal`(500), `unavailable`(503), `dependency_failed`(502)。

### 6.5 バージョニング方針
- パスベースのメジャーバージョン: `/api/v1/`。後方互換の変更はマイナー/パッチで通知のみ。
- 破壊的変更は新しいメジャー（例: `/api/v2/`）を提供し、90日以上の移行期間を設ける。
- レスポンスヘッダ: `Areayield-API-Version: v1` を付与。

### 6.6 ページネーション・フィルタリング
- リスト系エンドポイントはカーソル方式を採用。
- リクエスト: `?limit=50&cursor={opaque}`（`limit`は1-100、既定50）
- レスポンス例:
```json
{
  "items": [],
  "next_cursor": "eyJwYWdlIjoyfQ=="
}
```
- フィルタはクエリ文字列で提供（例: `city`, `district`, `metric`）。未定義のフィルタは無視。

### 6.7 冪等性・再試行
- 書き込み/起動系（`POST /analyze`, `POST /analyze/batch`）は `Idempotency-Key` ヘッダをサポート（TTL 24h）。
- 同一キー+同一ボディの場合、同一 `job_id`/結果を返却。競合は `409 conflict`。
- 再試行は指数バックオフ（上限 60秒）を推奨。

### 6.8 レート制限ヘッダ
- `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, 429時は `Retry-After` を返却。

### 6.9 監査・相関ID
- すべてのレスポンスに `X-Request-Id` を付与。クライアント指定が無い場合はサーバ生成。
- 監査ログには `actor`, `scope`, `request_id`, `ip`, `user_agent` を記録（10.3参照）。

### 6.10 API廃止（Deprecation）ポリシー
- 後方互換を損なう変更は新メジャー（例: `/api/v2/`）で提供。
- 旧バージョンの廃止予告は最低90日前に通知（メール/ダッシュボード/ヘッダ）。
- レスポンスヘッダに `Areayield-API-Deprecated: true` と `Areayield-API- Sunset: YYYY-MM-DD` を付与。
- SDKは非推奨版で警告ログを出力。移行ガイドとコードモッドを提供。

## 7. データ更新パイプライン

### 7.1 ETLスケジュール

```yaml
# Airflow DAG例
dag:
  name: areayield_data_pipeline
  schedule: "0 2 * * 0"  # 毎週日曜2:00 AM

tasks:
  - name: fetch_airdna
    type: PythonOperator
    schedule: weekly
    
  - name: crawl_minpaku_notifications
    type: PythonOperator
    schedule: monthly
    
  - name: crawl_municipality_minutes
    type: PythonOperator
    schedule: weekly
    
  - name: update_zoning_data
    type: PythonOperator
    schedule: quarterly
    
  - name: process_and_aggregate
    type: PythonOperator
    depends_on: [fetch_airdna, crawl_minpaku_notifications]
    
  - name: calculate_scores
    type: PythonOperator
    depends_on: [process_and_aggregate]
    
  - name: update_cache
    type: PythonOperator
    depends_on: [calculate_scores]
```

### 7.2 データフレッシュネス要件

| データソース | 初期頻度 | 6ヶ月後目標 |
|-------------|---------|-----------|
| AirDNA | 月次 | 週次 |
| 民泊届出 | 月次 | 週次 |
| 議事録 | 週次 | リアルタイム |
| 用途地域 | 年次 | 年次 |
| 観光統計 | 四半期 | 月次 |

---

### 7.3 データ品質・ラインエージ
- データ契約: ソースごとにスキーマ/許容範囲/更新SLAを定義（Great Expectationsで検証）
  - スキーマ: 必須列の存在、型、ユニーク制約、外部キー整合
  - 品質: 欠損率・外れ値比率の上限、数値レンジ、カテゴリ語彙
  - フレッシュネス: `max_delay_minutes` を超過したらダウングレード/キャッシュ継続
- ラインエージ: OpenLineage/DataHubで上流→下流の血統を記録（dataset_id, source_url, ingestion_time）
- 失敗時動作: データ隔離、直前スナップショットへフォールバック、アラート送出（10.2）
- 応答透過性: APIは `metadata.data_freshness` と `source_summary` を返し、利用者が鮮度を判断可能にする

### 7.4 出典メタデータ管理（Provenance）
- 収集/加工済みの各レコードに以下を付与:
  - `source_id`, `source_url`, `publisher`, `collected_at`, `ingested_at`, `license`
  - 変換履歴: `transform_id`, `version`, `checksum`
- API `source_summary` フィールド（概要）:
```json
{
  "source_summary": [
    {"source_id": "kyoto_council_2024_11", "url": "https://example/..", "publisher": "京都市議会", "retrieved_at": "2024-11-15"},
    {"source_id": "airdna_city_kyoto_2025_09", "url": "https://airdna/...", "publisher": "AirDNA", "retrieved_at": "2025-10-20"}
  ]
}
```

## 8. セキュリティ要件

### 8.1 認証・認可
- **ユーザー認証**: OAuth 2.0 / OpenID Connect
- **APIキー管理**: ローテーション90日
- **アクセス制御**: RBAC（Role-Based Access Control）
  - Admin: 全機能
  - User: 閲覧・分析実行
  - API: プログラマティックアクセスのみ

### 8.2 データ保護
- **通信**: TLS 1.3
- **保管**: AES-256暗号化
- **個人情報**: AirDNAの元データは外部非公開、集計値のみ提供
- **ログ**: 個人識別情報のマスキング

### 8.3 コンプライアンス
- **AirDNAライセンス**: 再配布禁止、解析結果のみ提供
- **著作権**: 議事録は公開情報として引用、出典明記
- **GDPR**: EU圏ユーザー対応（将来拡張時）

### 8.4 データ保持・削除ポリシー（Retention/Deletion）
- 保持期間（既定）:
  - 原文書（PDF/HTML）: 24ヶ月（監査要件を満たす場合）
  - 抽出テキスト/OCR結果: 24ヶ月
  - 埋め込み（ベクトル）: 12ヶ月（最新6ヶ月はHOTティア）
  - 解析結果キャッシュ: 24時間（同一エリア）
  - 監査/アクセスログ: 180日
- 削除:
  - ユーザー依頼/契約終了時は30日以内に個別データを削除（バックアップは最大90日でロールオフ）。
  - DSAR（開示/削除請求）に30日以内で対応。
- 安全消去: 暗号化キー廃棄またはストレージレベルのセキュア消去を実施。

---

## 9. パフォーマンス要件

### 9.1 レスポンスタイム
- **単一分析**: p95 < 3秒
- **バッチ分析（50件）**: < 5分
- **ヒートマップ**: p95 < 2秒

### 9.2 スケーラビリティ
- **同時接続**: 1,000ユーザー
- **API RPS**: 100 req/sec（ピーク時）
- **データ量**: 10万物件 × 24ヶ月履歴

### 9.3 可用性
- **SLA**: 99.5%（SaaS）、99.9%（API Pro）
- **RTO**: 4時間
- **RPO**: 24時間

### 9.4 FinOps（コスト管理）
- 目標: 1判定あたり平均<50円、ベクトル検索p95<500msを維持。
- 施策: 結果キャッシュ（24h）、同一エリアのRAGスキップ、軽量LLM併用、夜間バッチへの集約。
- 監視: 日次/週次のクラウド原価、LLM/ベクトルDB/ストレージ別コストを可視化。
- 予算: 月次コスト上限を設定し、+20%で警告、+50%で自動緊急モード（キャッシュTTL延長/バッチ優先度変更）。

---

## 10. モニタリング・ログ

### 10.1 メトリクス
- **アプリケーション**:
  - API成功率、エラー率、レイテンシ
  - 分析処理時間、キャッシュヒット率
  - RAG検索recall@k、groundedness、要約factuality
  - OCR成功率/word accuracy
  - RAGレイテンシ分解（retrieval/LLM/OCR）
  - LLMトークン使用量/コスト/呼び出し失敗率
- **インフラ**:
  - CPU/メモリ使用率、ディスクI/O
  - データベースクエリ時間
- **ビジネス**:
  - DAU/MAU、分析実行回数
  - 判定結果分布（Go/Amber/Stop比率）
  - RevPARレンジ的中率、誤判定率（Stop/Goの外れ）

### 10.2 アラート
- API成功率 < 95%
- p95レスポンスタイム > 5秒
- データ更新失敗
 - RAG recall@10 < 0.7（直近1,000リクエスト）
 - Groundedness < 0.7（移動平均）
 - OCR word accuracy < 0.95（週間）
 - LLMコスト/日 > 予算上限
 - データ鮮度SLA違反（7.2参照）

### 10.3 ログ
- **アクセスログ**: Nginx/ALBで記録
- **アプリケーションログ**: 構造化JSON（structured logging）
- **監査ログ**: 全API呼び出し、分析結果閲覧を記録（180日保存）

---

## 11. デプロイメント

### 11.1 環境
- **Dev**: 開発・テスト環境
- **Staging**: 本番同等環境（データはサブセット）
- **Production**: 本番環境（Multi-AZ）

### 11.2 デプロイ戦略
- **方式**: Blue-Green Deployment
- **頻度**: 週次（機能追加）、随時（緊急修正）
- **ロールバック**: 自動（ヘルスチェック失敗時）

### 11.3 CI/CD
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest tests/
      
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t areayield:${{ github.sha }} .
      - name: Push to ECR
        run: docker push ...
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: kubectl set image deployment/areayield ...
```

### 11.4 リリース基準（Release Criteria）
- 品質ゲート: 単体/統合テスト合格、カバレッジ≥80%。
- 性能ゲート: `/analyze` p95<3秒、エラー率<1%。
- RAGゲート: recall@10≥0.75、groundedness≥0.7、OCR word accuracy≥0.93（MVP）。
- セキュリティ: 重大脆弱性（High以上）ゼロ、依存ライブラリアップデート適用。
- ロールバック: ヘルスチェック不合格時に自動切替（Blue-Green）。

---

## 12. テスト戦略

### 12.1 ユニットテスト
- **カバレッジ**: 80%以上
- **フレームワーク**: pytest
- **テスト対象**: スコア計算ロジック、データ変換、API入出力

### 12.2 統合テスト
- **E2Eフロー**: 住所入力 → 分析 → 結果表示
- **外部API**: AirDNA API呼び出しのモック

### 12.3 精度検証
- **RevPAR予測**: ±20%以内の的中率70%以上
- **評価方法**: 過去12ヶ月の実績データと比較
- **テストセット**: 京都100地点、大阪100地点、東京100地点

---

## 13. ロードマップ

### フェーズ1: MVP（2026年1月）
- ✅ 京都・大阪・東京・沖縄対応
- ✅ SaaS UI（基本機能）
- ✅ REST API（認証・分析エンドポイント）
- ✅ 月次データ更新
- ✅ Go/Amber/Stop判定

### フェーズ2: 機能強化（2026年4月）
- 週次データ更新
- 町丁目 → 地番精緻化
- レビューテーマ分析の精度向上
- SDK公開（Python/TypeScript）
- ダッシュボードのカスタマイズ機能

### フェーズ3: 拡張（2026年7月）
- 対応エリア拡大（福岡、北海道、広島）
- バッチ分析の並列化（最大500件）
- モバイルアプリ（iOS/Android）
- パートナーSI向けWhite Label API

### フェーズ4: 高度分析（2026年10月）
- 需要予測（イベント/季節要因）
- 競合物件シミュレーション
- ポートフォリオ最適化
- 機械学習モデルの継続学習

---

## 14. 技術的リスクと対応策

### 14.1 RAG品質リスク

| リスク | 影響度 | 対応策 | 成功指標 |
|--------|--------|--------|---------|
| **議事録OCRの低精度** | 高 | ・複数OCRエンジンのフォールバック構成<br>・手動検証セット（1,000ページ）で継続評価<br>・word accuracy < 0.90のドキュメントは人手レビュー | word accuracy≥0.95 |
| **規制シグナルの見逃し** | 高 | ・recall@10≥0.8を目標にチャンキング/検索パラメータ最適化<br>・false negative検出時は即座にファインチューニング | recall@10≥0.8、月次でチェック |
| **センチメント誤判定** | 中 | ・法律/行政用語特化のファインチューニング<br>・groundedness<0.7は「不明」として出力<br>・ユーザーフィードバックで継続学習 | groundedness≥0.7、誤判定率<10% |
| **LLMコスト超過** | 中 | ・キャッシュ戦略（同一エリアは24h有効）<br>・非同期バッチ処理<br>・軽量モデル（GPT-4o-mini）とのハイブリッド | 1判定あたり平均<50円 |

### 14.2 データ統合リスク

| リスク | 影響度 | 対応策 |
|--------|--------|--------|
| **AirDNAライセンス制約** | 高 | ・契約書で解析結果の提供を明示的に許諾<br>・原データの再配布は行わず、集計値/スコアのみ提示<br>・監査ログで利用状況を記録 |
| **自治体データの多様性** | 高 | ・自治体ごとにカスタムパーサーを構築（初期20自治体）<br>・共通スキーマへの変換レイヤー<br>・失敗時は「データ不足」として透過的に通知 |
| **データ鮮度SLA違反** | 中 | ・前回スナップショットへの自動フォールバック<br>・`metadata.data_freshness`で利用者に鮮度を明示<br>・重要データソースは冗長化（ミラーサイト） |

### 14.3 スケーラビリティリスク

| リスク | 影響度 | 対応策 | 検証方法 |
|--------|--------|--------|---------|
| **トラフィック急増** | 中 | ・Kubernetes HPA（水平スケーリング）<br>・CDNキャッシュ（CloudFront/Fastly）<br>・Redis分散キャッシュ | 負荷テスト（1,000 req/sec） |
| **ベクトルDB性能劣化** | 中 | ・Pineconeのsharding/replication<br>・HOT/COLDティア分離（最新6ヶ月はHOT）<br>・p95レイテンシの継続監視 | p95<500ms（検索単体） |
| **バッチ処理の遅延** | 低 | ・Celeryワーカーの動的スケーリング<br>・優先度キュー（有償顧客優先）<br>・並列度50→500への段階的拡張 | 500件バッチ<5分（Year1終了時） |

### 14.4 実装フェーズごとの技術的マイルストーン

#### フェーズ1（MVP、2026/1）
- [ ] 京都・大阪・東京・沖縄の4都市でRAG品質recall@10≥0.75達成
- [ ] OCR word accuracy≥0.93（目標0.95に向けて改善中）
- [ ] API p95レイテンシ<5秒
- [ ] 月次データ更新パイプラインの安定稼働（SLA 99%）

#### フェーズ2（機能強化、2026/4）
- [ ] recall@10≥0.8、groundedness≥0.7達成
- [ ] OCR word accuracy≥0.95
- [ ] 週次データ更新への移行
- [ ] API p95レイテンシ<3秒
- [ ] キャッシュヒット率≥60%

#### フェーズ3（拡張、2026/7）
- [ ] 福岡・北海道・広島追加（計7エリア）
- [ ] バッチ並列度500件
- [ ] API Pro（100 req/sec）の提供開始
- [ ] SDK（Python/TS）の公開

### 14.5 技術的依存関係の管理

| 外部依存 | クリティカリティ | 代替手段 | 移行コスト |
|---------|----------------|---------|-----------|
| **AirDNA API** | 高 | Transparent, AllTheRooms（品質は劣る） | 高（3-6ヶ月） |
| **OpenAI API** | 高 | Anthropic Claude、Google Gemini | 中（1-2ヶ月） |
| **Pinecone** | 中 | Weaviate（セルフホスト）、Qdrant | 中（2-3ヶ月） |
| **Mapbox** | 低 | Google Maps、OpenStreetMap | 低（2週間） |

### 14.6 MVP範囲と実装優先順位

#### MVP（Minimum Viable Product: 2026年1月）に含むもの

| 機能 | 実装レベル | 理由 |
|------|----------|------|
| **Go/Amber/Stop判定** | ✅ 完全実装 | コア価値提供、最優先 |
| **収益性スコア（RevPAR）** | ✅ 完全実装 | 判定の基礎、AirDNAデータ活用 |
| **許認可実現性スコア** | ✅ 完全実装 | 差別化要因、用途地域/学校距離評価 |
| **規制リスクスコア（RAG）** | ⚠️ 基本実装 | recall@10≥0.75で開始、継続改善 |
| **4都市対応** | ✅ 完全実装 | 京都・大阪・東京・沖縄 |
| **月次データ更新** | ✅ 完全実装 | データ鮮度の最低ライン |
| **Web UI（基本）** | ✅ 完全実装 | 住所検索、判定表示、根拠表示 |
| **REST API（Basic）** | ✅ 完全実装 | `/analyze`エンドポイント、認証 |
| **レビューテーマ分析** | ❌ 次フェーズ | MVP後に精度向上で追加 |
| **バッチ分析** | ⚠️ 制限実装 | 最大20件、手動実行のみ |
| **ヒートマップ** | ❌ 次フェーズ | UI負荷高、優先度低 |
| **SDK** | ❌ 次フェーズ | フェーズ2（2026/4）で提供 |

#### 実装優先順位（MVP開発時）

**P0（絶対必須、リリース条件）**
1. 住所→緯度経度変換（Geocoding）
2. 収益性スコア計算（AirDNAデータ統合）
3. 用途地域判定（国土数値情報）
4. 学校距離計算（国土地理院データ）
5. Go/Amber/Stop判定ロジック
6. Web UI（検索・結果表示）
7. REST API `/analyze`
8. 認証（JWT）

**P1（重要、品質に影響）**
9. 議事録クローラー（初期20自治体）
10. ベクトルDB構築（Pinecone）
11. RAGベースの規制リスク評価（基本版）
12. キャッシュ層（Redis）
13. エラーハンドリング・ロギング
14. 月次データ更新パイプライン（Airflow）

**P2（あると良い、MVP後でも可）**
15. バッチ分析（20件制限）
16. 統計API `/stats/area`
17. 管理画面（ユーザー管理）
18. モニタリング・アラート（基本版）

**P3（Nice to have、フェーズ2以降）**
19. レビューテーマ分析
20. ヒートマップAPI
21. 需要予測（イベント連携）
22. SDK（Python/TS）

---

## 15. 付録

### 15.1 用語集
- **RevPAR**: Revenue Per Available Room（利用可能な部屋あたり売上）
- **ADR**: Average Daily Rate（平均客室単価）
- **RAG**: Retrieval-Augmented Generation（検索拡張生成）
- **町丁目**: 町・丁目レベルの地域区分

### 14.2 参考資料
- AirDNA API Documentation
- 観光庁「民泊制度ポータルサイト」
- 国土交通省「国土数値情報」
- 厚生労働省「旅館業法の概要」

### 14.3 変更履歴
| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2025-10-26 | 1.0.0 | 初版作成 |

### 14.4 APIエラーモデル（JSON Schema）
```json
{
  "type": "object",
  "properties": {
    "error": {
      "type": "object",
      "properties": {
        "code": {"type": "string"},
        "message": {"type": "string"},
        "details": {"type": "array", "items": {"type": "object"}}
      },
      "required": ["code", "message"]
    },
    "request_id": {"type": "string"},
    "status": {"type": "integer"}
  },
  "required": ["error", "request_id", "status"],
  "additionalProperties": false
}
```

### 14.5 データスキーマ概要（応答）
`/api/v1/analyze` レスポンスの主要フィールドと型:
```json
{
  "judgment": "Go|Amber|Stop",
  "score": 0,
  "area": {
    "prefecture": "string",
    "city": "string",
    "district": "string",
    "lat": 0.0,
    "lng": 0.0
  },
  "profitability": {
    "revpar_range": [0, 0],
    "confidence": 0.0,
    "occupancy_rate": 0,
    "adr": 0,
    "estimated_annual_revenue": [0, 0]
  },
  "licensing": {
    "difficulty_score": 0,
    "available_types": [],
    "restrictions": [],
    "estimated_process_days": 0
  },
  "regulation_risk": {
    "score": 0,
    "level": "Low|Medium|High",
    "signals": []
  },
  "market_stats": {
    "active_listings": 0,
    "listing_density": 0.0,
    "competition_level": "Low|Medium|High"
  },
  "metadata": {
    "analyzed_at": "ISO8601",
    "data_freshness": "YYYY-MM-DD",
    "model_version": "semver"
  }
}
```

---

**文書ステータス**: 🟡 Draft → 🔵 Review → 🟢 Approved  
**承認者**: （未定）  
**次回レビュー**: 2025-11-15

