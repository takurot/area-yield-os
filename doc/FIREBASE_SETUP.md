# Firebase セットアップガイド

最終更新: 2025-10-26  
プロジェクト: area-yield-os

---

## 📋 前提条件

- ✅ Firebase CLI インストール済み: v14.18.0
- ✅ Firebase プロジェクト作成済み: `area-yield-os`
- ✅ Firebase にログイン済み

---

## 🔧 設定手順

### 1. Firebase Console での有効化

Firebase Console にアクセス: https://console.firebase.google.com/project/area-yield-os

#### 1.1 Authentication の有効化

1. 左メニュー → **Authentication** → **Get started**
2. **Sign-in method** タブ
3. **Email/Password** を有効化
   - ✅ Email/Password
   - ⬜ Email link (passwordless) - オプション

#### 1.2 Firestore の有効化

1. 左メニュー → **Firestore Database** → **Create database**
2. **ロケーション**: `asia-northeast1` (Tokyo) 推奨
3. **セキュリティルール**: 本番モードで開始（後でデプロイ）

#### 1.3 Web アプリの登録

1. **Project settings** (⚙️) → **General** → **Your apps**
2. **Add app** → **Web** (</>) を選択
3. **アプリ名**: `AreaYield OS Web`
4. **Firebase Hosting**: ✅ チェック
5. **Register app** をクリック
6. **設定をコピー**（次のステップで使用）

---

### 2. フロントエンド環境変数の設定

```bash
# テンプレートをコピー
cd frontend
cp .env.local.example .env.local

# エディタで開く
code .env.local
# または
nano .env.local
```

Firebase Console の設定を使って以下を編集：

```env
# Firebase Configuration (Firebase Console から取得)
NEXT_PUBLIC_FIREBASE_API_KEY=<Your API Key>
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=area-yield-os.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=area-yield-os
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=area-yield-os.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=<Your Sender ID>
NEXT_PUBLIC_FIREBASE_APP_ID=<Your App ID>

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAPBOX_TOKEN=<取得後に設定>

# Environment
NEXT_PUBLIC_ENV=development
```

**取得方法**: Firebase Console → Project settings → Your apps → SDK setup and configuration

---

### 3. サービスアカウントキーの生成

#### 方法1: Firebase Console（推奨）

1. **Project settings** (⚙️) → **Service accounts** タブ
2. **Generate new private key** をクリック
3. ダウンロードしたJSONファイルを以下に配置：

```bash
mv ~/Downloads/area-yield-os-*.json backend/firebase-service-account.json
```

#### 方法2: gcloud CLI

```bash
# サービスアカウントを確認
gcloud iam service-accounts list --project=area-yield-os

# キーを生成（firebase-adminsdk のメールアドレスを使用）
gcloud iam service-accounts keys create backend/firebase-service-account.json \
  --iam-account=firebase-adminsdk-xxxxx@area-yield-os.iam.gserviceaccount.com \
  --project=area-yield-os
```

**⚠️ 重要**: このファイルは `.gitignore` に含まれています（絶対にコミットしない）

---

### 4. バックエンド環境変数の設定（オプション）

開発環境用：

```bash
cd backend
cp .env.example .env

# 編集（必要に応じて）
code .env
```

最小限の設定：

```env
# Firebase
FIREBASE_PROJECT_ID=area-yield-os
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json

# Database（ローカル開発用）
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/areayield_dev

# Environment
ENV=development
DEBUG=true
TESTING=false
```

---

### 5. Firestore ルールとインデックスのデプロイ

```bash
cd infrastructure/firebase

# プロジェクトを選択
firebase use area-yield-os

# Firestore ルールをデプロイ
firebase deploy --only firestore:rules

# Firestore インデックスをデプロイ
firebase deploy --only firestore:indexes
```

**確認**:

```bash
# デプロイされたルールを確認
firebase firestore:databases:list
```

---

### 6. 動作確認

#### 6.1 設定確認スクリプト

```bash
./scripts/verify-firebase.sh
```

期待される出力：

```
✓ Firebase CLI: 14.18.0
✓ Firebase プロジェクト: area-yield-os
✅ frontend/.env.local 存在
✅ backend/firebase-service-account.json 存在
```

#### 6.2 フロントエンド起動テスト

```bash
cd frontend
npm run dev
```

ブラウザで http://localhost:3000 にアクセス

#### 6.3 バックエンド起動テスト

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

ブラウザで http://localhost:8000/health にアクセス

期待されるレスポンス：

```json
{
  "status": "ok",
  "version": "0.1.0",
  "environment": "development",
  "checks": {
    "api": "ok",
    "database": "ok",
    "firestore": "ok"
  }
}
```

---

## 🔐 セキュリティのベストプラクティス

### 絶対にコミットしてはいけないファイル

- ✅ `.gitignore` に含まれていることを確認：
  - `backend/firebase-service-account.json`
  - `frontend/.env.local`
  - `backend/.env`

### 確認コマンド

```bash
# 追跡されていないことを確認
git status --ignored | grep -E "(firebase-service-account|\.env\.local)"
```

---

## 🚨 トラブルシューティング

### エラー: "Firebase not initialized"

**原因**: `firebase-service-account.json` が存在しない

**解決策**:
```bash
# ファイルの存在確認
ls -la backend/firebase-service-account.json

# 存在しない場合は Step 3 を再実行
```

### エラー: "Firestore rules deployment failed"

**原因**: Firebase プロジェクトが正しく選択されていない

**解決策**:
```bash
# プロジェクトを再選択
cd infrastructure/firebase
firebase use area-yield-os

# 再デプロイ
firebase deploy --only firestore:rules
```

### エラー: "CORS error in browser"

**原因**: フロントエンドの URL がバックエンドの `ALLOWED_ORIGINS` に含まれていない

**解決策**:
```bash
# backend/.env または backend/app/core/config.py で確認
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

## 📚 次のステップ

Firebase 設定完了後：

1. ✅ **GCP プロジェクトの設定** (Cloud SQL, BigQuery など)
2. ✅ **外部 API キーの取得**
   - Google Maps API
   - AirDNA API
   - OpenAI API
   - Pinecone API
3. ✅ **Phase 2 実装開始** (PR#8: Geocoding Service)

---

## 📞 サポート

問題が発生した場合：

1. `./scripts/verify-firebase.sh` を実行
2. Firebase Console でサービスの状態を確認
3. ログを確認: `firebase debug`

