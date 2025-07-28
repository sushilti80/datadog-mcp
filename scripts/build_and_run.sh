#!/bin/bash

# Enhanced Datadog MCP Server - Build and Run Script

set -e

echo "🚀 Enhanced Datadog MCP Server - Build and Run"
echo "==============================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your Datadog credentials before running again."
    echo "   Required: DATADOG_API_KEY and DATADOG_APP_KEY"
    exit 1
fi

# Check if required environment variables are set
if ! grep -q "^DATADOG_API_KEY=.*[^[:space:]]" .env || ! grep -q "^DATADOG_APP_KEY=.*[^[:space:]]" .env; then
    echo "❌ Error: DATADOG_API_KEY and DATADOG_APP_KEY must be set in .env file"
    echo "   Please edit .env file with your Datadog credentials."
    exit 1
fi

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t datadog-mcp-server:latest .
echo "✅ Docker image built successfully"

# Stop any existing container
echo "🛑 Stopping any existing containers..."
docker stop datadog-mcp-server 2>/dev/null || true
docker rm datadog-mcp-server 2>/dev/null || true

# Run the container
echo "🚀 Starting Datadog MCP Server container..."
docker run -d \
    --name datadog-mcp-server \
    --env-file .env \
    -p 8080:8080 \
    --restart unless-stopped \
    datadog-mcp-server:latest

# Wait for container to start
echo "⏳ Waiting for server to start..."
sleep 5

# Check if container is running
if docker ps | grep -q datadog-mcp-server; then
    echo "✅ Datadog MCP Server is running!"
    echo ""
    echo "📊 Server Information:"
    echo "   🌐 URL: http://localhost:8080/mcp/"
    echo "   🐳 Container: datadog-mcp-server"
    echo "   📋 Logs: docker logs datadog-mcp-server"
    echo ""
    echo "🔧 Available Tools:"
    echo "   • get_logs - Retrieve logs based on query filters"
    echo "   • list_spans - List spans relevant to your query"
    echo "   • get_trace - Retrieve all spans from a specific trace"
    echo "   • list_metrics - Get available metrics in your environment"
    echo "   • get_metrics - Query timeseries metrics data"
    echo "   • get_monitors - Retrieve monitors and their configurations"
    echo "   • list_hosts - Get detailed host information"
    echo ""
    echo "📖 Test the server:"
    echo "   curl -X POST http://localhost:8080/mcp/ \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -H \"Accept: application/json, text/event-stream\" \\"
    echo "     -d '{\"jsonrpc\":\"2.0\",\"id\":\"test\",\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2025-06-18\",\"capabilities\":{},\"clientInfo\":{\"name\":\"test\",\"version\":\"1.0\"}}}'"
    echo ""
    echo "🛑 To stop: docker stop datadog-mcp-server"
else
    echo "❌ Failed to start container. Checking logs..."
    docker logs datadog-mcp-server
    exit 1
fi

