# 貢献ガイド

AreaYield OSへの貢献にご興味をお持ちいただきありがとうございます！このガイドでは、プロジェクトへの貢献方法について説明します。

## 開発プロセス

### ブランチ戦略

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

### コミットメッセージ規約

Conventional Commits形式を使用します：

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

### コーディング規約

#### Python (Backend)

- PEP 8準拠
- Black（フォーマッター）
- Flake8（リンター）
- mypy（型チェック）

```python
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

- ESLint + Prettier
- Airbnb スタイルガイド準拠

```typescript
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

## PR（プルリクエスト）の作成

### 1. Issue の作成

まず、関連する Issue を作成または確認してください。

### 2. ブランチの作成

```bash
git checkout develop
git pull origin develop
git checkout -b feature/PR-XXX-description
```

### 3. 変更の実装

- テスト駆動開発（TDD）を推奨
- 小さく、レビュー可能な単位で変更
- コミットメッセージ規約に従う

### 4. テストの実行

```bash
# バックエンド
cd backend
pytest app/tests/ -v --cov=app

# フロントエンド
cd frontend
npm run lint
npm run test
```

### 5. PRの作成

GitHub上でPRを作成し、PRテンプレートに従って記入してください。

## PRテンプレート

```markdown
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

## テスト方針

### カバレッジ目標

- ユニットテスト: 80%以上
- 統合テスト: 主要エンドポイント全て
- E2E: クリティカルパス全て

### テスト命名規則

```python
def test_<function>_<scenario>_<expected_result>():
    # 例: test_geocode_address_valid_input_returns_coordinates()
    pass
```

### テストの構造（AAA パターン）

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

## 完了定義（Definition of Done）

各PRがマージされるための条件:

- [ ] ✅ CI が全てグリーン（lint, test, build）
- [ ] ✅ コードレビュー承認（最低1名）
- [ ] ✅ ユニットテストカバレッジ ≥ 80%
- [ ] ✅ 統合テスト実施（該当する場合）
- [ ] ✅ ドキュメント更新（API変更、新機能）
- [ ] ✅ 手動テスト完了（UI変更）
- [ ] ✅ セキュリティチェック通過
- [ ] ✅ パフォーマンス基準クリア（該当する場合）

## レビュープロセス

1. **セルフレビュー**: PR作成前に自分でコードをレビュー
2. **自動チェック**: CI/CDが自動的にlint、test、buildを実行
3. **ピアレビュー**: チームメンバーが最低1名レビュー
4. **修正**: フィードバックに基づいて修正
5. **承認**: レビュアーが承認
6. **マージ**: develop ブランチにマージ

## よくある質問

### Q: 新しい機能を追加したい

A: まず Issue を作成し、チームと議論してください。承認後、feature ブランチで実装を開始します。

### Q: バグを見つけた

A: Issue を作成し、再現手順を記載してください。緊急の場合は Slack で通知してください。

### Q: ドキュメントの修正のみの場合

A: 小さな修正であれば、直接 PR を作成して問題ありません。

### Q: テストが失敗する

A: ローカルで `pytest` または `npm run test` を実行し、問題を特定してください。不明な場合はチームに相談してください。

## サポート

質問や問題がある場合は、以下の方法でサポートを受けられます：

- **Slack**: #areayield-dev チャンネル
- **Issue**: GitHub Issue トラッカー
- **Email**: dev-team@areayield.com

## 行動規範

すべての貢献者は、尊重と協力の精神を持って行動することが期待されます。

- 建設的なフィードバックを提供する
- 他者の意見を尊重する
- プロフェッショナルな態度を維持する
- 多様性を尊重する

## ライセンス

貢献することで、あなたの貢献がプロジェクトのライセンスに従うことに同意したものとみなされます。

