# Enhanced Datadog MCP Server

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.10.6+-green.svg)](https://gofastmcp.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Model Context Protocol (MCP) server that provides AI agents with seamless access to Datadog's observability platform. Built with FastMCP 2.10.6+ supporting HTTP Streamable Transport and MCP JSON Configuration Transport.

## 🚀 Features

- **Complete Datadog Integration**: Access logs, spans, traces, metrics, monitors, and hosts
- **HTTP Streamable Transport**: Full MCP protocol compliance with Server-Sent Events (SSE)
- **MCP JSON Configuration**: Compatible with Claude Desktop, VS Code, and other MCP clients
- **7 Core Tools**: Essential Datadog operations for AI-powered observability
- **Resource Access**: Contextual data via URI patterns
- **Investigation Prompts**: Pre-built workflows for common troubleshooting scenarios
- **Docker Support**: Containerized deployment for easy local testing
- **Production Ready**: Comprehensive error handling and security features

## 📋 Available Tools

### 🔍 Logs & Traces
- **`get_logs`**: Retrieve logs based on query filters
- **`list_spans`**: Investigate spans relevant to your query  
- **`get_trace`**: Retrieve all spans from a specific trace

### 📊 Metrics & Monitoring
- **`list_metrics`**: Get available metrics in your environment
- **`get_metrics`**: Query timeseries metrics data
- **`get_monitors`**: Retrieve monitors and their configurations

### 🖥️ Infrastructure
- **`list_hosts`**: Get detailed host information

## 🛠️ Quick Start

### Prerequisites

- Python 3.11+
- Datadog API and Application keys
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/datadog-mcp-server.git
   cd datadog-mcp-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Datadog credentials
   ```

4. **Run the server**
   ```bash
   python src/datadog_mcp_server.py
   ```

The server will start on `http://0.0.0.0:8080` with full MCP protocol support.

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t datadog-mcp-server .

# Run with environment file
docker run -p 8080:8080 --env-file .env datadog-mcp-server

# Or run with environment variables
docker run -p 8080:8080 \
  -e DATADOG_API_KEY=your_api_key \
  -e DATADOG_APP_KEY=your_app_key \
  datadog-mcp-server
```

### Docker Compose

```yaml
version: '3.8'
services:
  datadog-mcp:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATADOG_API_KEY=${DATADOG_API_KEY}
      - DATADOG_APP_KEY=${DATADOG_APP_KEY}
      - DATADOG_SITE=datadoghq.com
    restart: unless-stopped
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATADOG_API_KEY` | ✅ | - | Your Datadog API key |
| `DATADOG_APP_KEY` | ✅ | - | Your Datadog application key |
| `DATADOG_SITE` | ❌ | `datadoghq.com` | Datadog site (e.g., `datadoghq.eu`) |
| `MCP_SERVER_HOST` | ❌ | `0.0.0.0` | Server bind address |
| `MCP_SERVER_PORT` | ❌ | `8080` | Server port |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

### Getting Datadog Keys

1. Log in to your Datadog account
2. Go to **Organization Settings** → **API Keys**
3. Create or copy your **API Key**
4. Go to **Organization Settings** → **Application Keys**  
5. Create or copy your **Application Key**

## 🔌 Client Integration

### Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "datadog": {
      "command": "python",
      "args": ["/Users/Sushil.Tiwari/Downloads/datadog-mcp2/src/datadog_mcp_server.py"],
      "env": {
        "DATADOG_API_KEY": "######",
        "DATADOG_APP_KEY": "#####",
        "DATADOG_SITE": "#####3"
      }
    }
  }
}
```

### HTTP Client

```bash
# Initialize session
curl -X POST http://localhost:8080/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": "init",
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "capabilities": {},
      "clientInfo": {"name": "client", "version": "1.0"}
    }
  }'

# Query logs
curl -X POST http://localhost:8080/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": "logs",
    "method": "tools/call",
    "params": {
      "name": "get_logs",
      "arguments": {
        "query": "service:web-app ERROR",
        "limit": 50,
        "hours_back": 2
      }
    }
  }'
```

## 📖 Usage Examples

### Investigating Service Issues

```python
# Get error logs for a service
result = get_logs("service:web-app status:error", limit=100, hours_back=2)

# Find slow spans
spans = list_spans("service:web-app duration:>1s", limit=50, hours_back=1)

# Get full trace details
trace = get_trace("trace-id-here")

# Check service metrics
metrics = get_metrics("avg:trace.web-app.request.duration", hours_back=4)
```

### Performance Analysis

```python
# List available metrics
available_metrics = list_metrics(hours_back=1)

# Query multiple metrics
cpu_metrics = get_metrics("avg:system.cpu.user{*}", hours_back=24)
memory_metrics = get_metrics("avg:system.mem.used{*}", hours_back=24)

# Check monitor status
monitors = get_monitors(group_states=["Alert", "Warn"])
```

### Infrastructure Monitoring

```python
# List all hosts
all_hosts = list_hosts()

# Filter hosts by environment
prod_hosts = list_hosts(filter_query="env:production")

# Get host details sorted by name
hosts = list_hosts(sort_field="name", sort_dir="asc")
```

## 🔍 Available Resources

Access Datadog data as contextual resources:

- `datadog://logs/{query}` - Log data for context
- `datadog://spans/{query}` - Span data for analysis  
- `datadog://trace/{trace_id}` - Complete trace information
- `datadog://metrics/{query}` - Metrics data for context

## 🎯 Investigation Prompts

### Service Investigation

Use the `datadog-investigation` prompt for comprehensive service analysis:

```json
{
  "name": "datadog-investigation",
  "arguments": {
    "service_name": "web-app",
    "time_range_hours": 2,
    "issue_description": "High error rate and slow response times"
  }
}
```

### Performance Analysis

Use the `datadog-performance-analysis` prompt for metrics analysis:

```json
{
  "name": "datadog-performance-analysis", 
  "arguments": {
    "metric_query": "avg:trace.web-app.request.duration",
    "time_range_hours": 24
  }
}
```

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### Manual Testing

```bash
# Test server startup
python src/datadog_mcp_server.py

# Test with curl (in another terminal)
curl -X POST http://localhost:8080/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":"test","method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

## 🔒 Security

- **API Key Security**: Store keys in environment variables or secrets management
- **Network Security**: Use HTTPS in production
- **Access Control**: Implement authentication for production deployments
- **Origin Validation**: Built-in protection against DNS rebinding attacks
- **Non-root Container**: Docker image runs as non-root user

## 📊 Monitoring

Monitor the MCP server itself:

- **Health Checks**: Built-in health check endpoint
- **Logging**: Comprehensive logging with configurable levels
- **Metrics**: Track API call success rates and response times
- **Error Handling**: Graceful error handling with detailed error messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/datadog-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/datadog-mcp-server/discussions)
- **Documentation**: [FastMCP Docs](https://gofastmcp.com/)
- **Datadog API**: [Datadog API Documentation](https://docs.datadoghq.com/api/)

## 🙏 Acknowledgments

- [FastMCP](https://gofastmcp.com/) - The Python framework for MCP servers
- [Datadog](https://www.datadoghq.com/) - Observability platform
- [Model Context Protocol](https://modelcontextprotocol.io/) - The open standard for AI context

