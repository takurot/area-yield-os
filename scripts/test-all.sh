#!/bin/bash

# Run all tests

set -e

echo "🧪 Running all tests..."
echo "======================"

# Backend tests
echo ""
echo "🐍 Running backend tests..."
cd backend
source venv/bin/activate || true
pytest app/tests/ -v --cov=app --cov-report=term
echo "✅ Backend tests passed"

# Frontend tests
echo ""
echo "⚛️  Running frontend tests..."
cd ../frontend
npm run test:ci
echo "✅ Frontend tests passed"

echo ""
echo "✨ All tests passed!"

