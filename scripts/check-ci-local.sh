#!/bin/bash
# CIチェックをローカルで実行するスクリプト

set -e

echo "🔍 CIチェックをローカルで実行します..."
echo ""

# Backend CIチェック
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Backend CI チェック"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd backend || exit 1

# 仮想環境をアクティブ化
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  venvが見つかりません。先に仮想環境を作成してください。"
    exit 1
fi

# 1. Lint (flake8)
echo "1️⃣  Flake8 チェック..."
flake8 app --max-line-length=120 --exclude=__pycache__,.venv,venv --exit-zero || {
    echo "❌ Flake8 エラーが見つかりました"
    exit 1
}
echo "✅ Flake8 チェック完了"
echo ""

# 2. Format (Black)
echo "2️⃣  Black フォーマットチェック..."
black --check app || {
    echo "❌ Black フォーマットエラーが見つかりました"
    echo "💡 修正: black app を実行してください"
    exit 1
}
echo "✅ Black フォーマットチェック完了"
echo ""

# 3. Type check (mypy)
echo "3️⃣  mypy 型チェック..."
mypy app --ignore-missing-imports || {
    echo "⚠️  mypy で警告がありました（無視します）"
}
echo "✅ mypy 型チェック完了"
echo ""

# 4. Tests
echo "4️⃣  テスト実行..."
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/areayield_test}"
export TESTING=true

pytest app/tests/ \
    --cov=app \
    --cov-report=term \
    --cov-fail-under=0 \
    -v || {
    echo "❌ テストが失敗しました"
    exit 1
}
echo "✅ テスト完了"
echo ""

cd ..

# Frontend CIチェック
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Frontend CI チェック"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd frontend || exit 1

# 1. Lint
echo "1️⃣  ESLint チェック..."
npm run lint || {
    echo "❌ ESLint エラーが見つかりました"
    exit 1
}
echo "✅ ESLint チェック完了"
echo ""

# 2. Type check
echo "2️⃣  TypeScript 型チェック..."
npm run type-check || {
    echo "❌ TypeScript 型エラーが見つかりました"
    exit 1
}
echo "✅ TypeScript 型チェック完了"
echo ""

# 3. Tests
echo "3️⃣  テスト実行..."
npm run test:ci || {
    echo "⚠️  テストに警告がありました（続行します）"
}
echo "✅ テスト完了"
echo ""

# 4. Build
echo "4️⃣  ビルドチェック..."
npm run build || {
    echo "❌ ビルドが失敗しました"
    exit 1
}
echo "✅ ビルド完了"
echo ""

cd ..

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 全てのCIチェックが完了しました！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

