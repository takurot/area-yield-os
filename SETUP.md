# AreaYield OS セットアップガイド

このドキュメントでは、AreaYield OSの開発環境を最初から構築する手順を説明します。

## 前提条件

以下のツールがインストールされていることを確認してください：

- **Node.js 18+**: https://nodejs.org/
- **Python 3.11+**: https://www.python.org/
- **Docker Desktop**: https://www.docker.com/products/docker-desktop
- **gcloud CLI**: https://cloud.google.com/sdk/docs/install
- **Firebase CLI**: `npm install -g firebase-tools`
- **Git**: https://git-scm.com/

推奨ツール：
- **VS Code**: https://code.visualstudio.com/
- **PostgreSQL 15** (ローカル開発用): https://www.postgresql.org/

## 1. リポジトリのクローン

```bash
git clone https://github.com/takurot/area-yield-os.git
cd area-yield-os
```

## 2. バックエンドのセットアップ

### 2.1 Python仮想環境の作成

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2.2 依存関係のインストール

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集して、必要な環境変数を設定してください：

```bash
# Application
ENV=development
DEBUG=true

# Database (ローカル開発用)
DATABASE_URL=postgresql://postgres:password@localhost:5432/areayield_dev

# Firebase
FIREBASE_PROJECT_ID=your-firebase-project-id
GOOGLE_APPLICATION_CREDENTIALS=./path/to/service-account-key.json

# External APIs (後で設定)
AIRDNA_API_KEY=your_key
OPENAI_API_KEY=your_key
PINECONE_API_KEY=your_key
GOOGLE_GEOCODING_API_KEY=your_key
```

### 2.4 ローカルデータベースのセットアップ

PostgreSQLがローカルで実行されている場合：

```bash
# データベースの作成
createdb areayield_dev

# マイグレーションの実行
alembic upgrade head
```

Dockerを使用する場合：

```bash
docker run --name areayield-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=areayield_dev \
  -p 5432:5432 \
  -d postgres:15
```

### 2.5 開発サーバーの起動

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

ブラウザで http://localhost:8000/docs にアクセスして、API ドキュメントを確認できます。

## 3. フロントエンドのセットアップ

### 3.1 依存関係のインストール

```bash
cd frontend
npm install
```

### 3.2 環境変数の設定

```bash
cp .env.example .env.local
```

`.env.local`ファイルを編集：

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_CONFIG='{"apiKey":"...","authDomain":"...","projectId":"..."}'
```

### 3.3 開発サーバーの起動

```bash
npm run dev
```

ブラウザで http://localhost:3000 にアクセスします。

## 4. Firebase プロジェクトのセットアップ

### 4.1 Firebase プロジェクトの作成

1. [Firebase Console](https://console.firebase.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. Authentication、Firestore、Hosting を有効化

### 4.2 Firebase CLI でログイン

```bash
firebase login
```

### 4.3 Firebase プロジェクトの初期化

```bash
cd infrastructure/firebase
firebase init
```

以下を選択：
- Firestore
- Hosting

## 5. GCP インフラのセットアップ（オプション）

本番環境またはステージング環境を構築する場合：

### 5.1 GCP プロジェクトの作成

```bash
gcloud projects create areayield-dev --name="AreaYield Development"
gcloud config set project areayield-dev
```

### 5.2 必要なAPIの有効化

```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  firestore.googleapis.com \
  bigquery.googleapis.com \
  storage-api.googleapis.com \
  redis.googleapis.com
```

### 5.3 Terraform でインフラを構築

```bash
cd infrastructure/terraform

# 初期化
terraform init

# 変数ファイルを作成
cat > terraform.tfvars <<EOF
project_id  = "areayield-dev"
region      = "asia-northeast1"
environment = "dev"
EOF

# プランの確認
terraform plan

# 適用
terraform apply
```

## 6. テストの実行

### 6.1 バックエンドテスト

```bash
cd backend
pytest app/tests/ -v --cov=app
```

### 6.2 フロントエンドテスト

```bash
cd frontend
npm run test
```

### 6.3 E2Eテスト

```bash
cd frontend
npx playwright install --with-deps
npm run test:e2e
```

### 6.4 全テストの実行

```bash
./scripts/test-all.sh
```

## 7. pre-commitフックの設定

```bash
pip install pre-commit
pre-commit install
```

これにより、コミット前に自動的にlintとフォーマットが実行されます。

## 8. よくある問題と解決方法

### データベース接続エラー

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解決方法**:
- PostgreSQLが起動しているか確認
- `DATABASE_URL`が正しいか確認
- ファイアウォール設定を確認

### Firebase初期化エラー

```
ValueError: The default Firebase app does not exist.
```

**解決方法**:
- `GOOGLE_APPLICATION_CREDENTIALS`が正しいパスか確認
- サービスアカウントキーJSONファイルが存在するか確認
- Firebase プロジェクトIDが正しいか確認

### Node.js依存関係エラー

```
npm ERR! code ERESOLVE
```

**解決方法**:
```bash
npm install --legacy-peer-deps
```

## 9. 開発ワークフロー

### ブランチ戦略

```
main          ← 本番環境
  └─ develop  ← 開発統合ブランチ
      └─ feature/PR-XXX-description  ← 機能ブランチ
```

### 新機能の開発

```bash
# developから機能ブランチを作成
git checkout develop
git pull origin develop
git checkout -b feature/PR-XXX-your-feature

# 変更を加える
# ...

# コミット
git add .
git commit -m "feat: your feature description"

# プッシュ
git push -u origin feature/PR-XXX-your-feature

# GitHub でPR作成
gh pr create --base develop --title "PR#XXX: Your Feature" --body "Description"
```

## 10. 次のステップ

セットアップが完了したら：

1. [STATUS.md](./STATUS.md) で現在の実装状況を確認
2. [doc/plan.md](./doc/plan.md) でPR単位の実装計画を確認
3. [doc/spec.md](./doc/spec.md) で技術仕様を確認
4. [CONTRIBUTING.md](./CONTRIBUTING.md) で貢献ガイドラインを確認

## サポート

問題が発生した場合：

1. [GitHub Issues](https://github.com/takurot/area-yield-os/issues) で既存の問題を検索
2. 新しいIssueを作成
3. Slackチャンネル #areayield-dev で質問

Happy Coding! 🚀

