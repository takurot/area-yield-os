# Terraform Infrastructure

AreaYield OSのGCPインフラ定義

## 概要

このディレクトリには、以下のリソースのTerraform定義が含まれています：

- Cloud Run (FastAPI)
- Cloud SQL (PostgreSQL)
- Firestore
- BigQuery
- Cloud Storage
- Cloud Memorystore (Redis)
- API Gateway
- Cloud Scheduler
- Cloud Tasks

## 使用方法

```bash
# 初期化
terraform init

# プランの確認
terraform plan

# 適用
terraform apply

# 破棄
terraform destroy
```

## 環境変数

```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="asia-northeast1"
```

