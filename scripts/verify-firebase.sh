#!/bin/bash

echo "🔥 Firebase設定の確認"
echo "====================="

# Firebase CLIのインストール確認
echo -n "✓ Firebase CLI: "
if command -v firebase &> /dev/null; then
    firebase --version
else
    echo "❌ 未インストール (npm install -g firebase-tools)"
    exit 1
fi

# プロジェクトの確認
echo -n "✓ Firebase プロジェクト: "
firebase projects:list 2>/dev/null | grep area-yield-os || echo "❌ 未設定"

# 環境変数の確認
echo ""
echo "📄 フロントエンド環境変数:"
if [ -f frontend/.env.local ]; then
    echo "  ✅ frontend/.env.local 存在"
    grep "NEXT_PUBLIC_FIREBASE" frontend/.env.local | sed 's/=.*/=***/' || true
else
    echo "  ❌ frontend/.env.local 未作成"
fi

echo ""
echo "📄 バックエンド環境変数:"
if [ -f backend/.env ]; then
    echo "  ✅ backend/.env 存在"
    grep "FIREBASE" backend/.env | sed 's/=.*/=***/' || true
else
    echo "  ⚠️  backend/.env 未作成（オプション）"
fi

echo ""
echo "🔑 サービスアカウントキー:"
if [ -f backend/firebase-service-account.json ]; then
    echo "  ✅ backend/firebase-service-account.json 存在"
else
    echo "  ❌ backend/firebase-service-account.json 未作成"
fi

echo ""
echo "✅ 確認完了！"
