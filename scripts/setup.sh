#!/bin/bash

# AreaYield OS Setup Script

set -e

echo "🚀 AreaYield OS Setup"
echo "===================="

# Check for required tools
echo "📋 Checking required tools..."

command -v node >/dev/null 2>&1 || { echo "❌ Node.js is not installed"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is not installed"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed"; exit 1; }

echo "✅ All required tools are installed"

# Setup backend
echo ""
echo "🐍 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Backend setup complete"

# Setup frontend
echo ""
echo "⚛️  Setting up frontend..."
cd ../frontend
npm install
echo "✅ Frontend setup complete"

# Setup data pipeline
echo ""
echo "📊 Setting up data pipeline..."
cd ../data-pipeline
pip install -r requirements.txt
echo "✅ Data pipeline setup complete"

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and configure"
echo "  2. Run backend: cd backend && uvicorn app.main:app --reload"
echo "  3. Run frontend: cd frontend && npm run dev"

