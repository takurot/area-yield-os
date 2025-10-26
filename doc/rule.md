# AreaYield OS 開発規約（Design & Implementation Rules）

バージョン: 1.0.0  
最終更新: 2025-10-26  
対象: モノレポ `area-yield-os` 全体（Frontend/Backend/Data/Infra/Docs）

本規約は技術仕様書（`doc/spec.md`）および実装計画（`doc/plan.md`）に準拠し、MVP〜将来拡張まで一貫した品質・一貫性・保守性を担保することを目的とする。

---

## 1. 総則

- 本規約は全リポジトリメンバーに適用する。違反はコードレビューで指摘・是正する。
- 仕様の矛盾や未定義事項がある場合は、製品責任者/テックリードへエスカレーションし、合意後に本書へ反映する（PRで更新）。
- 本規約は `spec.md` と `plan.md` を上位文書とし、乖離が生じた場合は上位文書を優先する。
- 設計上の重要な技術的決定（例: DBの選定、大規模なアーキテクチャ変更）については、ADR (Architecture Decision Record) を `doc/adr` ディレクトリに作成することを推奨。

---

## 2. リポジトリ構成とブランチ戦略

- モノレポ配下の大枠構成は `doc/plan.md` の「3.2 プロジェクト構成」に準拠する。
- ブランチ戦略（`doc/plan.md` 7.2）
  - main: 本番デプロイ専用
  - develop: 統合ブランチ
  - feature/*: 機能単位の作業ブランチ（例: `feature/PR-018-analyze-endpoint`）。GitHub Issues等のチケット番号を用いる `feature/TICKET-123-xxx` 形式を推奨。
- PR は基本 `feature/* -> develop`。`develop -> main` はリリース時のみ。
- PR テンプレートを必須とし（`doc/plan.md` 5.2）、チェックリストを満たさないPRはレビュー対象外。
- コミットメッセージ（`doc/plan.md` 7.3）
  - 形式: `type(scope): subject`（英語推奨、簡潔に）
  - type: feat, fix, docs, style, refactor, test, chore

---

## 3. コーディング規約（共通）

- 可読性第一。早期 return を優先し、ネストは 2〜3 段以内。
- 例外処理は必要最小限。握りつぶし禁止。再スロー時はコンテキストを保持。
- 変数/関数は意味的に明確な命名（省略語・1〜2文字名禁止）。
- コメントは「意図・背景・非自明な理由」のみに限定（自明な処理の説明は禁止）。
- 行長: 120 列目を目安。ツール既定に従う（Black/ESLint/Prettier）。
- 日付・時間は UTC 保持、入出力で明示（ISO8601）。
- 機密情報のハードコード禁止。GCP Secret Manager 等を使用（`doc/plan.md` 9.1）。
- ログは構造化 JSON（`spec.md` 10.3、`plan.md` 8.3）。PII は必ずマスク。

---

## 4. Python（Backend/FastAPI）

- バージョン: Python 3.11 / FastAPI 0.110+ / Pydantic v2（`doc/plan.md` 2.3）
- フォーマッタ/リンタ/型
  - Black, Flake8, mypy を必須（CIで強制、`doc/plan.md` 5.1）。
  - 公開関数・クラスは型注釈必須。`Any` の安易な使用禁止。
- 命名規則
  - ファイル・モジュール: `snake_case.py`
  - 変数/関数: `snake_case`
  - クラス/例外: `PascalCase`（例外は `...Error`）
  - 定数: `UPPER_SNAKE_CASE`
  - 非公開: 先頭 `_` を付与
- 構成
  - `app/api`（ルーター）, `app/core`（ドメイン/スコア）, `app/models`（Pydantic/ORM）, `app/services`（外部I/O）
  - 依存分離: 外部APIクライアント/httpx は `services` に集約。
- FastAPI ルール
  - ルーターは機能単位で分割し `APIRouter(prefix="/api/v1")` を厳守（`spec.md` 6.5）。
  - 入出力モデルは Pydantic v2 の `BaseModel` を使用し、`Field(examples=["..."])` 等でサンプル値を付与。
  - フロントエンドとの連携を考慮し、Pydanticモデルの `model_config` でエイリアス（`alias_generator=to_camel`）を設定し、JSONキーを `camelCase` へ自動変換することを推奨。
  - エラーは標準エラーモデル（`spec.md` 6.4）に統一。`HTTPException` ラップ時も JSON 形を崩さない。
  - CORS は許可オリジンのみに限定。`/health` は無認証可。
- 例外・リトライ
  - 外部I/O（AirDNA, Pinecone, GCP）は指数バックオフ、タイムアウト設定必須（`spec.md` 6.7）。
  - 冪等キー `Idempotency-Key` を `POST /analyze` 等でサポート（TTL 24h）。
- DB/スキーマ
  - Cloud SQL (PostgreSQL 15) + SQLAlchemy + Alembic（`doc/plan.md` PR#6）。
  - テーブル/カラムは `snake_case`。PK は `uuid`（v4/v7のいずれかに統一、MVPは v4）。
  - 監査系カラム: `created_at`, `updated_at`（UTC, NOT NULL, DEFAULT）。
  - 外部キー・ユニーク制約・必要なインデックスを必須定義。
- ロギング
  - `structlog` で JSON 出力。`event`, `request_id`, `user_id`, `latency_ms`, `cache_hit` などキーを統一（`doc/plan.md` 8.3）。
- テスト
  - pytest + pytest-asyncio、AAAパターン、命名規則 `test_<function>_<scenario>_<expected>()`（`doc/plan.md` 7.4）。
  - カバレッジ>=80%（`doc/plan.md` 1.2, 5.1）。

---

## 5. TypeScript/React（Frontend/Next.js 14）

- バージョン: Node 18 / Next.js 14 App Router / React 18（`doc/plan.md` 2.3）
- ツールチェーン
  - ESLint + Prettier + TypeScript strict。`any` 禁止、`unknown`→ナローイング。
  - テスト: Jest + React Testing Library、E2E: Playwright（`doc/plan.md` フェーズ7）。
- 命名規則
  - 変数/関数: `camelCase`
  - 型/インターフェース/コンポーネント: `PascalCase`
  - 定数: `UPPER_SNAKE_CASE`
  - ファイル: コンポーネントは `PascalCase.tsx`、フックは `useXxx.ts`、ユーティリティは `kebab-case.ts`
  - Export: 原則 named export、デフォルト export は避ける。
- UI/状態
  - Tailwind CSS + shadcn/ui。ARIA/アクセシビリティを遵守。
  - 状態は Zustand、データ取得は `fetch`/React Query を検討（MVPは軽量実装）。
- API 呼び出し
  - `NEXT_PUBLIC_API_URL` を使用。全リクエストで `Authorization: Bearer <token>`（Firebase Auth）
  - API レイヤは `frontend/lib/api.ts` に集約し、入出力型を定義。
- セキュリティ
  - 環境変数は `.env.local` 管理、`NEXT_PUBLIC_` 以外はクライアントへ露出禁止。
- テスト
  - クリティカルパス（検索→分析→表示）を E2E で担保（`doc/plan.md` PR#27）。

---

## 6. API 設計・運用規約

- バージョニング: `/api/v1/`（`spec.md` 6.5）。後方互換を壊す変更は `/api/v2/`。
- 認証: Firebase Auth JWT（`Authorization: Bearer <token>`）。有効期限・更新は `spec.md` 6.1 に準拠。
- レート制限: プラン別（`spec.md` 6.3）。ヘッダ `X-RateLimit-*` と429時 `Retry-After` を返却（`spec.md` 6.8）。
- 冪等性: `POST /api/v1/analyze` 等で `Idempotency-Key` 対応（TTL 24h, 409 競合）。
- 相関ID/監査: `X-Request-Id` を受理/生成しレスポンスへ反映（`spec.md` 6.9）。
- エラーモデル: `spec.md` 6.4/付録JSON Schemaに完全準拠。フロントエンドでの処理分岐を容易にするため、`error_code` フィールド（例: `invalid_parameter`）を定義・活用する。例外時も統一形式。
- ページネーション: カーソル方式 `?limit=50&cursor=opaque`（`spec.md` 6.6）。
- Deprecation: `Areayield-API-Deprecated`, `Areayield-API-Sunset` を付与（`spec.md` 6.10）。
- レスポンスヘッダ: `Areayield-API-Version: v1` を常時付与（`spec.md` 6.5）。

---

## 7. データ・スキーマ・パイプライン規約

- データ契約/品質: Great Expectations 等でスキーマ・レンジ・欠損率を検証（`spec.md` 7.3）。
- ラインエージ/出典: DataHub/OpenLineage で血統管理、`source_id`/`url` 等のプロビナンスを保持（`spec.md` 7.4）。
- ストレージ層
  - Raw: Cloud Storage（Parquet/原文書）
  - 集計: BigQuery（`areayield_mvp` データセット、テーブルは `snake_case`）
  - キャッシュ: Firestore/Redis（用途に応じて選択、TTL 明示）
- ETL/スケジュールは `spec.md` 7.1/`doc/plan.md` フェーズ6に従う。

---

## 8. RAG/ML 規約

- Embeddings: OpenAI `text-embedding-3-*`、1536次元、チャンク 512 トークン/重なり 50（`spec.md` 5.3）。
- Pinecone: インデックス作成/アップサートは重複排除・HOT/COLD ティア設計（`spec.md` 9.4, 14.3）。
- 品質基準: recall@10≥0.75（MVP）、groundedness≥0.7、OCR word accuracy≥0.93（`spec.md` 5.3, 11.4）。
- ガードレール: 出典必須、再現性不十分（recall 未達）は「不明」返却、推論抑止（`spec.md` 5.3）。
- 生成/集計結果に PII が含まれる場合は不可視化またはマスキング。

---

## 9. セキュリティ・コンプライアンス

- 通信: TLS 1.3、HTTPのみ許可。
- 認可: RBAC（Admin/User/API）。サーバ側で権限検証（`spec.md` 8.1）。
- 秘匿情報: Secret Manager/環境変数。リポジトリ・ログ出力への混入禁止。
- データ保持・削除: `spec.md` 8.4/`doc/plan.md` 9.1 に準拠し、自動削除を運用（原則 24ヶ月/12ヶ月/24h/180日）。
- ライセンス順守: AirDNA 再配布禁止。提供は解析結果/集計値のみ（`spec.md` 8.3）。

---

## 10. ロギング・モニタリング・アラート

- ログ: 構造化 JSON（`event`, `level`, `timestamp`, `request_id`, `actor`, `ip`, `user_agent`, `latency_ms`, `cache_hit`）
- メトリクス/KPIs: API 成功率/レイテンシ、RAG recall/groundedness/OCR、LLM コスト（`spec.md` 10.1）。
- アラート閾値: `spec.md` 10.2 に準拠（例: API成功率<95%, p95>5s など）。

---

## 11. テスト・品質ゲート

- カバレッジ: ≥80%（MVP）。重要ロジックは 90% 以上を推奨。
- 種別: ユニット/統合/E2E/負荷/精度検証（`spec.md` 12, `doc/plan.md` フェーズ7）。
- テスト観点: 正常系だけでなく、異常系・境界値テストを網羅的に記述する。
- CI 必須チェック（`doc/plan.md` 5.1）
  - Lint（Frontend/Backend）
  - Type check（TS） / mypy（Python）
  - Test（カバレッジ閾値厳守）
  - Build（Next.js/Container）
- パフォーマンス基準: `/analyze` p95<5秒（MVP）、将来<3秒（`spec.md` 9.1, 11.4）。

---

## 12. 実装ルール（詳細）

- 制御フロー
  - 早期 return、ガード句を優先。深いネスト禁止。
  - try/except は「例外発生があり得る箇所」に限定。握り潰し禁止、適切なログとエラー変換。
- 依存関係
  - バージョンはレンジではなく下限/固定を基本（再現性担保）。セキュリティアップデートは週次（Dependabot, `doc/plan.md` 9.2）。
- I18N/ロケール
  - ユーザー表示文言はUI層で管理。API は英語メッセージを基本、詳細は `details` に構造化。
- フロントエンドのデータ取得
  - API 層を一箇所に集約し、型安全に扱う。エラーはトースト/バナーで統一表示。
- バックエンドのキャッシュ
  - 同一エリア24hキャッシュ（RAG/結果）を基本（`spec.md` 9.4）。キー命名は `namespace:entity:identifier`。

---

## 13. Infrastructure as Code (Terraform)

- ツール: Terraform >= 1.5
- フォーマット: `terraform fmt -recursive` を pre-commit/CI で強制。
- 構成: 環境分離（`dev`/`prd`）は workspace を使用。共通リソースはモジュール化し `infrastructure/terraform/modules` 配下で管理。
- 命名規則: リソース名は `gcp_project-service-env` のように接頭辞を統一。変数は `snake_case`。
- 状態管理: GCS バケットで tfstate を一元管理・ロック。
- 機密情報: `.tfvars` ファイルに直接記述せず、Secret Manager 経由で参照。

---

## 14. 命名規則（横断）

- API パス: `kebab-case`、リソースは複数形、バージョンは `/api/v1` 固定。
- JSON フィールド: `snake_case`（バックエンド内部）/ フロント公開は仕様通り（`spec.md` 4.2 のキー名を遵守）。Pydanticのエイリアス機能で `camelCase` 変換を推奨。
- DB テーブル/カラム: `snake_case`。リレーションは `<entity>_id`。
- イベント名/ログキー: `snake_case`。メトリクスは英語の短い識別子を使用。
- フィーチャーフラグ: `ff_<feature>_<purpose>`。

---

## 15. PR/レビュー/リリース

- PR 規模はレビュー 30 分以内を目安（大規模変更は分割）。
- スクリーンショット・APIサンプル・テスト結果を PR に必ず添付（UI/API 変更時）。
- リリース基準: `spec.md` 11.4 / `doc/plan.md` 5.3 に準拠（品質/性能/RAG/セキュリティ/ロールバック）。
- デプロイ: Backend は Cloud Run、Frontend は Firebase Hosting（`doc/plan.md` 2.2, 5.1）。

---

## 16. 付録（参考設定）

- Backend Lint コマンド（CI と一致）
  - `flake8 app --max-line-length=120 && black --check app && mypy app`
- Frontend Lint/TypeCheck
  - `npm run lint && npm run type-check`
- 推奨 pre-commit フック
  - Python: black, flake8, mypy, pytest -q（変更差分のみ）
  - TS: eslint --fix, prettier --check, type-check（差分対象）

---

## 変更履歴

- 2025-10-26: v1.0.0 初版作成（`spec.md` v1.0.0, `plan.md` v1.0.0 準拠）
- 2025-10-26: v1.1.0 シニアエンジニアレビューに基づき改善（ADR、ブランチ戦略、IaC規約、テスト観点、APIエラーコード等）
