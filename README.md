# 🐕 Datadog MCP Server

**Enhanced Model Context Protocol (MCP) server for Datadog observability platform**

A production-ready MCP server that provides AI agents with intelligent access to Datadog monitoring data, metrics, logs, and advanced troubleshooting workflows through HTTP streamable transport with Server-Sent Events (SSE) support.

![FastMCP](https://img.shields.io/badge/FastMCP-2.10.6-blue) ![MCP](https://img.shields.io/badge/MCP-1.12.2-green) ![Python](https://img.shields.io/badge/Python-3.12+-yellow) ![Datadog](https://img.shields.io/badge/Datadog-API-purple)

## ✨ Features

### 🔧 **Core Tools**
- **`get_metrics`** - Query timeseries metrics with flexible time ranges
- **`list_metrics`** - Discover available metrics with filtering
- **`get_logs`** - Advanced log search with pagination and time precision
- **`get_next_datadog_logs_page`** - Cursor-based pagination for large log sets
- **`get_monitors`** - Monitor status and management
- **`list_dashboards`** - Dashboard discovery and listing

### 🤖 **AI-Powered Prompts**
- **`datadog-metrics-analysis`** - Automated metrics analysis and insights
- **`datadog-performance-diagnosis`** - Step-by-step performance troubleshooting workflow
- **`datadog-incident-commander`** - Intelligent incident response coordination
- **`datadog-time-range-advisor`** - Smart time range selection guidance

### 📊 **Smart Resources**
- **`datadog://metrics/{query}`** - Real-time metrics with AI analysis
- **`datadog://logs/{query}`** - Intelligent log search and analysis
- **`datadog://logs-detailed/{query}`** - Enhanced log analysis with full context
- **`datadog://health-check/{service_name}`** - Comprehensive service health assessment

### ⚡ **Advanced Capabilities**
- **Flexible Time Ranges**: Support for minutes, hours, days, weeks, and months
- **Intelligent Parameter Handling**: Smart defaults with comprehensive validation
- **AI Agent Optimization**: Structured workflows for autonomous troubleshooting
- **Production Ready**: Comprehensive error handling and logging

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Datadog API Key and Application Key
- Virtual environment (recommended)

### Installation

1. **Clone and setup**:
```bash
cd fastMCPserver
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your Datadog credentials:
# DD_API_KEY=your_datadog_api_key
# DD_APP_KEY=your_datadog_app_key  
# DD_SITE=us3.datadoghq.com  # or your Datadog site
```

3. **Start the server**:
```bash
python3 datadog_mcp_server.py
```

The server will start on `http://0.0.0.0:8080/mcp/`

## 🔧 Configuration

### Environment Variables

#### Core Configuration
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DD_API_KEY` | Datadog API Key | - | ✅ |
| `DD_APP_KEY` | Datadog Application Key | - | ✅ |
| `DD_SITE` | Datadog Site | `datadoghq.com` | ❌ |
| `MCP_SERVER_HOST` | Server host | `0.0.0.0` | ❌ |
| `MCP_SERVER_PORT` | Server port | `8080` | ❌ |

#### Debug Configuration
| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `MCP_DEBUG_LEVEL` | Debug logging level | `INFO` | `NONE`, `INFO`, `DEBUG`, `TRACE` |
| `MCP_DEBUG_REQUESTS` | Log incoming MCP requests | `false` | `true`, `false` |
| `MCP_DEBUG_RESPONSES` | Log outgoing MCP responses | `false` | `true`, `false` |
| `MCP_DEBUG_TIMING` | Include execution timing | `false` | `true`, `false` |
| `MCP_DEBUG_PARAMETERS` | Log function parameters | `false` | `true`, `false` |
| `MCP_DEBUG_PRETTY_PRINT` | Pretty print JSON in logs | `true` | `true`, `false` |
| `MCP_DEBUG_ERRORS` | Enhanced error logging | `true` | `true`, `false` |
| `MCP_DEBUG_MASK_SENSITIVE` | Mask API keys in logs | `true` | `true`, `false` |

#### Debug Level Guide
- **`NONE`**: Minimal logging, warnings and errors only
- **`INFO`**: Basic operation logs and debug messages  
- **`DEBUG`**: Detailed function calls, API requests/responses
- **`TRACE`**: Full request/response payloads, parameter details

### Datadog Sites
- **US1**: `datadoghq.com` (default)
- **US3**: `us3.datadoghq.com`
- **US5**: `us5.datadoghq.com` 
- **EU1**: `datadoghq.eu`
- **AP1**: `ap1.datadoghq.com`
- **GOV**: `ddog-gov.com`

## 📚 API Documentation

### Tools

#### `get_metrics`
Query timeseries metrics data from Datadog.

**Parameters:**
- `query` (string, required): Datadog metrics query (e.g., `"avg:system.cpu.user{*}"`)
- `hours_back` (integer, default: 1): Hours back from now to query
- `minutes_back` (integer, optional): Minutes back from now (overrides hours_back)

**Examples:**
```json
{
  "name": "get_metrics",
  "arguments": {
    "query": "avg:system.cpu.user{*}",
    "minutes_back": 30
  }
}
```

#### `get_logs`
Search Datadog logs with advanced filtering and pagination.

**Parameters:**
- `query` (string, required): Log search query
- `limit` (integer, default: 100): Number of logs per page (max 1000)
- `hours_back` (integer, optional): Hours back from now to search  
- `minutes_back` (integer, optional): Minutes back from now (overrides hours_back)
- `from_time` (string, optional): Start time in ISO format
- `to_time` (string, optional): End time in ISO format
- `indexes` (array, optional): List of log indexes to search
- `sort` (string, default: "timestamp"): Sort order
- `cursor` (string, optional): Pagination cursor
- `max_total_logs` (integer, optional): Maximum logs across all pages

**Examples:**
```json
{
  "name": "get_logs", 
  "arguments": {
    "query": "service:api-gateway AND status:error",
    "minutes_back": 30,
    "limit": 50,
    "sort": "-timestamp"
  }
}
```

#### `list_metrics`
Get list of available metrics with optional filtering.

**Parameters:**
- `filter_query` (string, optional): Filter metrics by name pattern

#### `get_monitors`
Get monitors data with state filtering.

**Parameters:**
- `group_states` (array, optional): Filter by states (e.g., ["Alert", "Warn"])

#### `list_dashboards`
Get list of available dashboards.

**Parameters:** None

#### `get_next_datadog_logs_page`
Get next page of logs using cursor-based pagination.

**Parameters:**
- `cursor` (string, required): Cursor from previous response
- `limit` (integer, default: 100): Number of logs to retrieve

### Prompts

#### `datadog-metrics-analysis`
Automated metrics analysis with AI insights.

#### `datadog-performance-diagnosis`
Structured performance troubleshooting workflow for AI agents.

**Parameters:**
- `service_name` (string): Name of the service to diagnose
- `symptoms` (string): Observed performance symptoms
- `severity` (string): Issue severity level

#### `datadog-incident-commander`
AI-powered incident command and coordination workflow.

**Parameters:**
- `severity` (string): Incident severity (low, medium, high, critical)
- `affected_services` (string): Comma-separated list of affected services
- `symptoms` (string): Observed incident symptoms
- `estimated_user_impact` (string): Estimated user impact percentage

#### `datadog-time-range-advisor`
Smart time range selection guidance for different analysis types.

**Parameters:**
- `analysis_type` (string): Type of analysis (performance, security, deployment, capacity)
- `suspected_timeframe` (string): When issue might have started
- `incident_impact` (string): Impact level

### Resources

#### `datadog://metrics/{query}`
Real-time metrics data with AI analysis and insights.

#### `datadog://logs/{query}`
Intelligent log search with formatted results and metadata.

#### `datadog://logs-detailed/{query}`
Enhanced log analysis with full context and detailed breakdown.

#### `datadog://health-check/{service_name}`
Comprehensive service health assessment with:
- Multi-dimensional health scoring
- Performance metrics analysis  
- Error rate evaluation
- AI-generated recommendations
- Business impact translation

## ⏰ Time Range Examples

### Quick Reference
```
⚡ Real-time: minutes_back=15, minutes_back=30
🕐 Recent: hours_back=1, hours_back=6, hours_back=24  
📅 Weekly: hours_back=168 (7×24)
📊 Monthly: hours_back=720 (30×24)
📈 Quarterly: hours_back=2160 (90×24)
```

### Common Scenarios
```json
// Active incident (last 15 minutes)
{"query": "status:error", "minutes_back": 15}

// Deployment verification (last 2 hours)  
{"query": "deploy OR release", "hours_back": 2}

// Weekly performance trends
{"query": "slow OR timeout", "hours_back": 168}

// Monthly capacity planning
{"query": "cpu OR memory", "hours_back": 720}
```

## 🧪 Testing with Postman

The server provides a robust HTTP API perfect for testing with Postman. Here's how to get started:

### 1. **Setup Postman Collection**

**Base URL:** `http://localhost:8080/mcp/`  
**Method:** `POST`  
**Headers:** `Content-Type: application/json`

### 2. **Test Tools**

#### List Available Tools
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

#### Get Metrics (30 minutes)
```json
{
  "jsonrpc": "2.0", 
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_metrics",
    "arguments": {
      "query": "avg:system.cpu.user{*}",
      "minutes_back": 30
    }
  }
}
```

#### Search Logs (Last Hour)
```json
{
  "jsonrpc": "2.0",
  "id": 1, 
  "method": "tools/call",
  "params": {
    "name": "get_logs",
    "arguments": {
      "query": "status:error",
      "hours_back": 1,
      "limit": 50,
      "sort": "-timestamp"
    }
  }
}
```

#### Get Time Range Advice
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call", 
  "params": {
    "name": "datadog-time-range-advisor",
    "arguments": {
      "analysis_type": "performance",
      "suspected_timeframe": "recent",
      "incident_impact": "high"
    }
  }
}
```

### 3. **Test Prompts**

#### Performance Diagnosis
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "datadog-performance-diagnosis", 
    "arguments": {
      "service_name": "api-gateway",
      "symptoms": "High response time, increased error rate",
      "severity": "high"
    }
  }
}
```

#### Incident Command
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "datadog-incident-commander",
    "arguments": {
      "severity": "critical",
      "affected_services": "api-gateway, database",
      "symptoms": "Service timeout, 500 errors",
      "estimated_user_impact": "25%"
    }
  }
}
```

### 4. **Test Resources**

#### Health Check Resource
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/read",
  "params": {
    "uri": "datadog://health-check/api-gateway"
  }
}
```

#### Metrics Resource  
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/read", 
  "params": {
    "uri": "datadog://metrics/avg:system.cpu.user{*}"
  }
}
```

### 5. **Common Testing Scenarios**

#### Error Investigation Workflow
```json
// Step 1: Get recent errors
{"name": "get_logs", "arguments": {"query": "status:error", "minutes_back": 30}}

// Step 2: Check error rate metrics  
{"name": "get_metrics", "arguments": {"query": "sum:trace.http.request.errors{*}", "hours_back": 1}}

// Step 3: Get service health assessment
// Use resources/read with uri: "datadog://health-check/your-service-name"
```

#### Performance Analysis Workflow  
```json
// Step 1: Get time range advice
{"name": "datadog-time-range-advisor", "arguments": {"analysis_type": "performance"}}

// Step 2: Follow the recommended time ranges
{"name": "get_metrics", "arguments": {"query": "avg:trace.http.request.duration{*}", "minutes_back": 30}}

// Step 3: Get detailed performance diagnosis
{"name": "datadog-performance-diagnosis", "arguments": {"service_name": "api"}}
```

### 6. **Parameter Tips**

✅ **Correct Parameter Types:**
```json
{
  "hours_back": 2,          // Number, not string
  "minutes_back": 30,       // Number, not string  
  "limit": 100,             // Number, not string
  "from_time": "2025-09-14T15:00:00Z",  // ISO string
  "indexes": ["main"],      // Array, not string
  "sort": "-timestamp"      // String
}
```

❌ **Common Mistakes to Avoid:**
```json
{
  "hours_back": "2",        // String instead of number
  "minutes_back": "",       // Empty string instead of null/number
  "from_time": "2h",        // Relative time instead of ISO
  "indexes": "main"         // String instead of array
}
```

## 🏗️ Architecture

### Technology Stack
- **FastMCP 2.10.6** - High-performance MCP server framework
- **MCP Protocol 1.12.2** - Model Context Protocol compliance
- **Python 3.12+** - Modern Python with type hints
- **Datadog API Client** - Official Datadog Python SDK
- **HTTP + SSE** - Streamable transport with Server-Sent Events

### Design Principles
- **AI-First Design** - Optimized for AI agent interaction patterns
- **Production Ready** - Comprehensive error handling, logging, and validation
- **Developer Experience** - Clear APIs, helpful error messages, extensive examples
- **Performance Focused** - Efficient data handling and smart caching strategies
- **Standards Compliant** - Full MCP protocol compliance with FastMCP optimizations

## 🔍 Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check if port is in use
lsof -i :8080

# Check environment variables
echo $DD_API_KEY
echo $DD_APP_KEY

# Check logs for detailed errors
python3 datadog_mcp_server.py
```

#### API Authentication Errors
1. Verify your Datadog API key and Application key
2. Check your Datadog site setting
3. Ensure keys have required permissions

#### Postman Testing Issues
1. Use `Content-Type: application/json` header
2. Send parameters as numbers, not strings (e.g., `"hours_back": 2`)
3. Use proper ISO format for time strings
4. Check server logs for validation errors

#### Performance Issues
1. Use smaller time ranges for faster responses
2. Limit log search results with `limit` parameter
3. Use `minutes_back` for precise short-term analysis
4. Consider pagination for large datasets

#### Debug and Tracing
For troubleshooting MCP communication and API issues:

```bash
# Enable full debug tracing
export MCP_DEBUG_LEVEL=TRACE
export MCP_DEBUG_REQUESTS=true
export MCP_DEBUG_RESPONSES=true
export MCP_DEBUG_TIMING=true
export MCP_DEBUG_PARAMETERS=true

# Start server with debug enabled
python3 datadog_mcp_server.py
```

**Debug Use Cases:**
- **400 Bad Request Errors**: Enable `MCP_DEBUG_REQUESTS=true` to see exact request payloads
- **Empty Results**: Use `MCP_DEBUG_LEVEL=DEBUG` to trace API calls and responses
- **Performance Issues**: Enable `MCP_DEBUG_TIMING=true` to identify slow operations
- **Parameter Validation**: Use `MCP_DEBUG_PARAMETERS=true` to debug argument parsing

**Security Note**: In production, keep `MCP_DEBUG_MASK_SENSITIVE=true` to prevent API keys from appearing in logs.

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build image
docker build -t datadog-mcp-server .

# Run container
docker run -p 8080:8080 \
  -e DD_API_KEY=your_api_key \
  -e DD_APP_KEY=your_app_key \
  -e DD_SITE=us3.datadoghq.com \
  datadog-mcp-server
```

### Environment-Specific Configuration
- **Development**: Use `.env` file with debug logging
- **Staging**: Enable request/response logging for testing
- **Production**: Use environment variables, disable debug logs

### Monitoring
- Monitor server health at `/mcp/` endpoint
- Track API rate limits and usage
- Monitor response times and error rates
- Set up alerts for authentication failures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Update documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Documentation](https://gofastmcp.com)
- [Datadog API Documentation](https://docs.datadoghq.com/api/)
- [Datadog Python SDK](https://github.com/DataDog/datadog-api-client-python)

---

**🎉 Ready to enhance your AI agents with powerful Datadog observability!**

Start testing with Postman using the examples above, and explore the intelligent prompts and resources for advanced AI-powered troubleshooting workflows.
