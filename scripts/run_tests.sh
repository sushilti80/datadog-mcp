#!/bin/bash

# Enhanced Datadog MCP Server - Test Runner Script

set -e

echo "🧪 Running Enhanced Datadog MCP Server Tests"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "src/datadog_mcp_server.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install pytest pytest-asyncio pytest-cov black flake8 > /dev/null 2>&1

# Run code formatting check
echo "🎨 Checking code formatting..."
if ! black --check src/ tests/; then
    echo "❌ Code formatting issues found. Run 'black src/ tests/' to fix."
    exit 1
fi
echo "✅ Code formatting is correct"

# Run linting
echo "🔍 Running linting checks..."
if ! flake8 src/ tests/ --max-line-length=127 --ignore=E203,W503; then
    echo "❌ Linting issues found"
    exit 1
fi
echo "✅ Linting passed"

# Run tests
echo "🧪 Running unit tests..."
if ! pytest tests/ -v --cov=src --cov-report=term-missing; then
    echo "❌ Tests failed"
    exit 1
fi
echo "✅ All tests passed"

# Test Docker build
echo "🐳 Testing Docker build..."
if ! docker build -t datadog-mcp-server:test . > /dev/null 2>&1; then
    echo "❌ Docker build failed"
    exit 1
fi
echo "✅ Docker build successful"

# Test Docker run (basic smoke test)
echo "🚀 Testing Docker container startup..."
CONTAINER_ID=$(docker run -d --rm \
    -e DATADOG_API_KEY=test_key \
    -e DATADOG_APP_KEY=test_app_key \
    -p 8081:8080 \
    datadog-mcp-server:test)

# Wait a bit for container to start
sleep 5

# Check if container is still running
if ! docker ps | grep -q $CONTAINER_ID; then
    echo "❌ Docker container failed to start or crashed"
    docker logs $CONTAINER_ID
    exit 1
fi

# Stop the container
docker stop $CONTAINER_ID > /dev/null 2>&1
echo "✅ Docker container test passed"

echo ""
echo "🎉 All tests passed successfully!"
echo "✅ Code formatting: OK"
echo "✅ Linting: OK" 
echo "✅ Unit tests: OK"
echo "✅ Docker build: OK"
echo "✅ Docker run: OK"
echo ""
echo "Ready for deployment! 🚀"

