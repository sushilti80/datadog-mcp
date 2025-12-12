# 🐕 Datadog MCP Server

**Enhanced Model Context Protocol (MCP) server for Datadog observability platform**

A production-ready MCP server that provides AI agents with intelligent access to Datadog monitoring data, metrics, logs, and advanced troubleshooting workflows through HTTP streamable transport with Server-Sent Events (SSE) support.

---

## 🚀 **NEW: Contributing to This Project?**

### **👉 [START_HERE.md](START_HERE.md) ← Open this first!** (30 seconds)

Learn how to add tools, write tests, debug issues, or update docs using our **6-Agent Development System**.  
No confusion, no scattered docs - just clear templates and checklists.

**Or pick your path:**
- ✅ **5-min quick start** → [AGENTS_QUICK_START.md](AGENTS_QUICK_START.md)
- ✅ **Pick your agent** → [AGENT_DECISION_TREE.md](AGENT_DECISION_TREE.md)  
- ✅ **Task-specific guides** → [AGENTS.md](AGENTS.md)
- ✅ **Visual workflows** → [WORKFLOW.md](WORKFLOW.md)
- ✅ **Complete system guide** → [AGENT_SYSTEM_GUIDE.md](AGENT_SYSTEM_GUIDE.md)

---

![FastMCP](https://img.shields.io/badge/FastMCP-2.10.6-blue) ![MCP](https://img.shields.io/badge/MCP-1.12.2-green) ![Python](https://img.shields.io/badge/Python-3.12+-yellow) ![Datadog](https://img.shields.io/badge/Datadog-API-purple)

## 📚 Contributing & Development

**Want to add a new tool, resource, prompt, or fix a bug?** Start here:
- **[AGENTS_QUICK_START.md](AGENTS_QUICK_START.md)** ← Read this first (5 min overview)
- **[AGENTS.md](AGENTS.md)** ← Complete task-specific guides with templates
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** ← Code patterns & architecture

Pick your task, follow the agent guide, and you'll be productive in minutes!

## 🆕 What's New

### Version 1.1.0 (September 2025)
- **🔄 Multi-Key Rotation System**: Intelligent API key rotation to handle rate limiting proactively
- **Enhanced Debug System**: Comprehensive debug tracing with correlation IDs and performance timing
- **AI-Powered Prompts**: New intelligent prompts for incident response and performance diagnosis
- **Advanced Time Range Support**: Flexible minute/hour-based time parameters with smart defaults
- **Health Check Resources**: Comprehensive service health assessment with AI recommendations
- **Cursor-Based Pagination**: Efficient handling of large log datasets with pagination support
- **Production-Ready Logging**: Configurable debug levels with sensitive data masking
- **Error Handling**: Enhanced error categorization with actionable suggestions

### Recent Improvements
- Added support for all major Datadog sites (US1, US3, US5, EU1, AP1, GOV)
- Implemented smart parameter validation with helpful error messages
- Enhanced resource endpoints with detailed metadata and analysis
- Added time range advisor for optimal query performance
- Improved MCP protocol compliance with FastMCP optimizations
- **🔄 Intelligent Key Rotation**: Multi-key support with automatic rate limit handling
- **📈 Throughput Scaling**: 3-5x increased API capacity with multiple keys
- **🛡️ Circuit Breaker Protection**: Automatic isolation of problematic keys

## 🎯 Use Cases

### 🤖 AI Agent Automation
Perfect for powering AI agents that need autonomous access to observability data:

#### **Incident Response Bot**
```python
# Automated incident detection and response
1. Monitor error rates: get_logs("status:error", minutes_back=5)
2. Analyze impact: get_metrics("error.rate", hours_back=1) 
3. Generate response plan: datadog-incident-commander prompt
4. Execute mitigation steps based on AI recommendations
```

#### **Performance Optimization Assistant**
```python
# Proactive performance monitoring
1. Baseline analysis: get_metrics("response.time", hours_back=24)
2. Anomaly detection: Compare current vs historical patterns
3. Root cause analysis: datadog-performance-diagnosis prompt
4. Optimization recommendations with business impact
```

#### **Capacity Planning Advisor** 
```python
# Data-driven capacity decisions
1. Trend analysis: get_metrics("cpu,memory,disk", hours_back=720)
2. Growth forecasting: Historical pattern analysis
3. Resource optimization: Identify over/under-provisioned resources
4. Cost optimization: Resource efficiency recommendations
```

### 🏢 Enterprise Monitoring
Streamline enterprise observability workflows:

#### **Multi-Service Health Dashboard**
```python
# Comprehensive service ecosystem monitoring
services = ["api-gateway", "user-service", "payment-service"]
for service in services:
    health = datadog://health-check/{service}
    # Aggregate health scores, identify dependencies
```

#### **SLA Monitoring and Reporting**
```python
# Automated SLA compliance tracking
1. Error rate monitoring: get_logs("service:api status:error")
2. Performance tracking: get_metrics("p95.response.time")
3. Availability calculation: Uptime percentage analysis
4. Executive reporting: Business-friendly metrics translation
```

#### **Security Investigation Workflows**
```python
# Automated security incident response
1. Threat detection: get_logs("auth.failure OR 403 OR suspicious")
2. Impact assessment: Identify affected services and users
3. Timeline reconstruction: Correlate events across services
4. Remediation guidance: Security-focused recommendations
```

## ✨ Features

### 🔧 **Core Tools**
- **`get_metrics`** - Query timeseries metrics with flexible time ranges
- **`list_metrics`** - Discover available metrics with filtering
- **`get_logs`** - Advanced log search with pagination and time precision
- **`get_next_datadog_logs_page`** - Cursor-based pagination for large log sets
- **`get_monitors`** - Monitor status and management
- **`list_dashboards`** - Dashboard discovery and listing
- **`get_key_pool_status`** - 🔄 Monitor API key rotation system health

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
- **🔄 Multi-Key Rotation**: Intelligent API key rotation with 5 different strategies  
- **Flexible Time Ranges**: Support for minutes, hours, days, weeks, and months
- **Intelligent Parameter Handling**: Smart defaults with comprehensive validation
- **AI Agent Optimization**: Structured workflows for autonomous troubleshooting
- **Production Ready**: Comprehensive error handling and logging
- **Rate Limit Avoidance**: Proactive and reactive rate limit handling
- **Circuit Breaker Protection**: Automatic failover for problematic keys

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

#### 🔄 Key Rotation Configuration
| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `DD_API_KEY_2`, `DD_API_KEY_3`... | Additional API keys | - | ❌ |
| `DD_APP_KEY_2`, `DD_APP_KEY_3`... | Additional APP keys | - | ❌ |
| `DD_KEY_ROTATION_STRATEGY` | Rotation strategy | `adaptive` | `round_robin`, `lru`, `weighted`, `adaptive`, `random` |
| `DD_CIRCUIT_BREAKER_THRESHOLD` | Failures before circuit breaker trips | `5` | Integer |
| `DD_CIRCUIT_BREAKER_TIMEOUT` | Circuit breaker timeout (minutes) | `10` | Integer |
| `DD_HEALTH_CHECK_INTERVAL` | Health check interval (seconds) | `300` | Integer |

**📖 See [Key Rotation Guide](docs/KEY_ROTATION.md) for detailed configuration**

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
// Basic CPU usage over last 30 minutes
{
  "name": "get_metrics",
  "arguments": {
    "query": "avg:system.cpu.user{*}",
    "minutes_back": 30
  }
}

// Memory usage for specific service over last 2 hours
{
  "name": "get_metrics", 
  "arguments": {
    "query": "avg:system.mem.used{service:api-gateway}",
    "hours_back": 2
  }
}

// Request rate trends over last week
{
  "name": "get_metrics",
  "arguments": {
    "query": "sum:trace.http.request.hits{env:production}",
    "hours_back": 168
  }
}

// Error rate by service over last 24 hours
{
  "name": "get_metrics",
  "arguments": {
    "query": "sum:trace.http.request.errors{*} by {service}",
    "hours_back": 24
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
// Recent errors from API gateway (last 30 minutes)
{
  "name": "get_logs", 
  "arguments": {
    "query": "service:api-gateway AND status:error",
    "minutes_back": 30,
    "limit": 50,
    "sort": "-timestamp"
  }
}

// Deployment-related logs from last 2 hours
{
  "name": "get_logs",
  "arguments": {
    "query": "deploy OR release OR rollout",
    "hours_back": 2,
    "limit": 100
  }
}

// Critical errors from specific time window
{
  "name": "get_logs",
  "arguments": {
    "query": "status:critical OR level:critical",
    "from_time": "2025-09-24T10:00:00Z",
    "to_time": "2025-09-24T12:00:00Z",
    "limit": 200
  }
}

// Authentication failures from security index
{
  "name": "get_logs",
  "arguments": {
    "query": "auth.failure OR unauthorized OR 403",
    "hours_back": 24,
    "indexes": ["security", "audit"],
    "max_total_logs": 500
  }
}

// Performance issues with pagination
{
  "name": "get_logs",
  "arguments": {
    "query": "slow OR timeout OR performance",
    "hours_back": 6,
    "limit": 100,
    "max_total_logs": 1000
  }
}
```

#### `list_metrics`
Get list of available metrics with optional filtering.

**Parameters:**
- `filter_query` (string, optional): Filter metrics by name pattern

**Examples:**
```json
// List all available metrics
{
  "name": "list_metrics",
  "arguments": {}
}

// Filter metrics for specific host
{
  "name": "list_metrics",
  "arguments": {
    "filter_query": "web-server-01"
  }
}

// Filter by environment tag
{
  "name": "list_metrics",
  "arguments": {
    "filter_query": "env:production"
  }
}

// Filter by service
{
  "name": "list_metrics",
  "arguments": {
    "filter_query": "service:api-gateway"
  }
}
```

#### `get_monitors`
Get monitors data with state filtering.

**Parameters:**
- `group_states` (array, optional): Filter by states (e.g., ["Alert", "Warn"])

**Examples:**
```json
// Get all monitors
{
  "name": "get_monitors",
  "arguments": {}
}

// Get only alerting monitors
{
  "name": "get_monitors",
  "arguments": {
    "group_states": "alert"
  }
}

// Get monitors in warning or alert state
{
  "name": "get_monitors", 
  "arguments": {
    "group_states": "alert,warn"
  }
}
```

#### `list_dashboards`
Get list of available dashboards.

**Parameters:** None

**Examples:**
```json
// List all dashboards
{
  "name": "list_dashboards",
  "arguments": {}
}
```

#### `get_next_datadog_logs_page`
Get next page of logs using cursor-based pagination.

**Parameters:**
- `cursor` (string, required): Cursor from previous response
- `limit` (integer, default: 100): Number of logs to retrieve

**Examples:**
```json
// Continue pagination from previous search
{
  "name": "get_next_datadog_logs_page",
  "arguments": {
    "cursor": "eyJhZnRlciI6IjIwMjUtMDktMjRUMTU6MzA6MDBaIn0",
    "limit": 100
  }
}

// Get larger page size for batch processing
{
  "name": "get_next_datadog_logs_page",
  "arguments": {
    "cursor": "eyJhZnRlciI6IjIwMjUtMDktMjRUMTU6MzA6MDBaIn0",
    "limit": 500
  }
}
```

#### `get_key_pool_status`
Get detailed status of the API key rotation system for monitoring and debugging.

**Parameters:** None

**Examples:**
```json
// Monitor key rotation system health
{
  "name": "get_key_pool_status",
  "arguments": {}
}
```

**Response includes:**
```json
{
  "status": "success", 
  "total_keys": 3,
  "available_keys": 2,
  "rotation_strategy": "adaptive",
  "keys": [
    {
      "id": "primary",
      "health": "healthy", 
      "success_rate": 0.95,
      "total_requests": 150,
      "consecutive_failures": 0,
      "average_response_time": 0.245
    }
  ],
  "recommendations": [
    "ℹ️ 1 keys currently unavailable"
  ]
}
```

### Prompts

#### `datadog-metrics-analysis`
Automated metrics analysis with AI insights.

**Examples:**
```json
// Analyze CPU trends over last 24 hours
{
  "name": "datadog-metrics-analysis",
  "arguments": {
    "metric_query": "avg:system.cpu.user{env:production}",
    "time_range_hours": "24"
  }
}

// Analyze error rates with AI recommendations  
{
  "name": "datadog-metrics-analysis",
  "arguments": {
    "metric_query": "sum:trace.http.request.errors{*} by {service}",
    "time_range_hours": "168"
  }
}
```

#### `datadog-performance-diagnosis`
Structured performance troubleshooting workflow for AI agents.

**Parameters:**
- `service_name` (string): Name of the service to diagnose
- `symptoms` (string): Observed performance symptoms
- `severity` (string): Issue severity level

**Examples:**
```json
// High response time investigation
{
  "name": "datadog-performance-diagnosis",
  "arguments": {
    "service_name": "api-gateway",
    "symptoms": "Response times increased by 300% in last hour",
    "severity": "high"
  }
}

// Memory leak investigation
{
  "name": "datadog-performance-diagnosis", 
  "arguments": {
    "service_name": "payment-processor",
    "symptoms": "Memory usage continuously increasing, occasional OOM errors",
    "severity": "critical"
  }
}

// Database performance issues
{
  "name": "datadog-performance-diagnosis",
  "arguments": {
    "service_name": "user-service",
    "symptoms": "Slow database queries, connection pool exhaustion",
    "severity": "medium"
  }
}
```

#### `datadog-incident-commander`
AI-powered incident command and coordination workflow.

**Parameters:**
- `severity` (string): Incident severity (low, medium, high, critical)
- `affected_services` (string): Comma-separated list of affected services
- `symptoms` (string): Observed incident symptoms
- `estimated_user_impact` (string): Estimated user impact percentage

**Examples:**
```json
// Critical multi-service outage
{
  "name": "datadog-incident-commander",
  "arguments": {
    "severity": "critical",
    "affected_services": "api-gateway, payment-service, user-authentication",
    "symptoms": "Complete service outage, 100% error rate, users cannot login",
    "estimated_user_impact": "85%"
  }
}

// High severity database issue
{
  "name": "datadog-incident-commander",
  "arguments": {
    "severity": "high", 
    "affected_services": "database-cluster, reporting-service",
    "symptoms": "Database connection timeouts, slow query performance",
    "estimated_user_impact": "25%"
  }
}

// Deployment-related incident
{
  "name": "datadog-incident-commander",
  "arguments": {
    "severity": "medium",
    "affected_services": "api-gateway",
    "symptoms": "Increased error rate after deployment, partial functionality affected",
    "estimated_user_impact": "15%"
  }
}
```

#### `datadog-time-range-advisor`
Smart time range selection guidance for different analysis types.

**Parameters:**
- `analysis_type` (string): Type of analysis (performance, security, deployment, capacity)
- `suspected_timeframe` (string): When issue might have started
- `incident_impact` (string): Impact level

**Examples:**
```json
// Performance analysis guidance
{
  "name": "datadog-time-range-advisor",
  "arguments": {
    "analysis_type": "performance",
    "suspected_timeframe": "recent",
    "incident_impact": "high"
  }
}

// Security investigation guidance
{
  "name": "datadog-time-range-advisor",
  "arguments": {
    "analysis_type": "security", 
    "suspected_timeframe": "hours",
    "incident_impact": "critical"
  }
}

// Capacity planning guidance
{
  "name": "datadog-time-range-advisor",
  "arguments": {
    "analysis_type": "capacity",
    "suspected_timeframe": "weeks",
    "incident_impact": "medium"
  }
}

// Deployment verification guidance
{
  "name": "datadog-time-range-advisor",
  "arguments": {
    "analysis_type": "deployment",
    "suspected_timeframe": "recent",
    "incident_impact": "low"
  }
}
```

### Resources

#### `datadog://metrics/{query}`
Real-time metrics data with AI analysis and insights.

**Examples:**
```json
// Get CPU metrics with analysis
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/read",
  "params": {
    "uri": "datadog://metrics/avg:system.cpu.user{env:production}"
  }
}

// Get request rate trends
{
  "jsonrpc": "2.0", 
  "id": 1,
  "method": "resources/read",
  "params": {
    "uri": "datadog://metrics/sum:trace.http.request.hits{service:api-gateway}"
  }
}
```

#### `datadog://logs/{query}`
Intelligent log search with formatted results and metadata.

**Examples:**
```json
// Get recent errors with context
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/read", 
  "params": {
    "uri": "datadog://logs/service:api-gateway status:error"
  }
}

// Get deployment-related logs
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/read",
  "params": {
    "uri": "datadog://logs/deploy OR release OR rollout"
  }
}
```

#### `datadog://logs-detailed/{query}`
Enhanced log analysis with full context and detailed breakdown.

**Examples:**
```json
// Detailed error analysis
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/read",
  "params": {
    "uri": "datadog://logs-detailed/status:500 OR status:502 OR status:503"
  }
}

// Security incident analysis
{
  "jsonrpc": "2.0",
  "id": 1, 
  "method": "resources/read",
  "params": {
    "uri": "datadog://logs-detailed/auth.failure OR unauthorized OR 403"
  }
}
```

#### `datadog://health-check/{service_name}`
Comprehensive service health assessment with:
- Multi-dimensional health scoring
- Performance metrics analysis  
- Error rate evaluation
- AI-generated recommendations
- Business impact translation

**Examples:**
```json
// API Gateway health assessment
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/read",
  "params": {
    "uri": "datadog://health-check/api-gateway"
  }
}

// Database service health check
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/read", 
  "params": {
    "uri": "datadog://health-check/database-primary"
  }
}

// Payment service comprehensive analysis
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/read",
  "params": {
    "uri": "datadog://health-check/payment-processor"
  }
}
```

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

### Performance Optimization

#### Query Optimization Strategies
```bash
# ✅ Efficient queries (fast responses)
get_logs("service:api status:error", minutes_back=15, limit=50)
get_metrics("avg:response.time{service:api}", hours_back=1)

# ❌ Inefficient queries (slow responses)  
get_logs("*", hours_back=168, limit=10000)  # Too broad, too much data
get_metrics("*", hours_back=720)            # Wildcard with long range
```

#### Memory and Network Optimization
```python
# Use pagination for large datasets
page_1 = get_logs("service:api", hours_back=24, limit=100)
if page_1.get("has_more"):
    page_2 = get_next_datadog_logs_page(page_1["next_cursor"], limit=100)

# Batch related queries efficiently
metrics_queries = [
    ("cpu", "avg:system.cpu.user{service:api}"),
    ("memory", "avg:system.mem.used{service:api}"),
    ("requests", "sum:trace.http.request.hits{service:api}")
]
```

#### Time Range Selection Best Practices
```python
# Match time range to use case
Real-time troubleshooting:    minutes_back=15-30
Recent issue investigation:   hours_back=1-6  
Trend analysis:              hours_back=24-168
Capacity planning:           hours_back=720-2160

# Use specific ranges instead of defaults
get_logs("deploy", hours_back=2)     # ✅ Specific to deployment window
get_logs("deploy")                   # ❌ Uses default 1 hour
```

#### Caching and Rate Limiting
```python
# Implement client-side caching for repeated queries
cache_key = f"metrics:{query}:{hours_back}"
if cache_key not in cache or cache_expired(cache_key):
    result = get_metrics(query, hours_back=hours_back)
    cache[cache_key] = result

# Respect API rate limits with exponential backoff
import time
def get_metrics_with_retry(query, hours_back, max_retries=3):
    for attempt in range(max_retries):
        try:
            return get_metrics(query, hours_back=hours_back)
        except RateLimitError:
            time.sleep(2 ** attempt)  # Exponential backoff
```

#### Resource Usage Guidelines
| Query Type | Recommended Limit | Max Time Range | Expected Response |
|------------|-------------------|----------------|-------------------|
| Real-time logs | 50-100 | 15-30 minutes | < 2 seconds |
| Historical logs | 100-500 | 1-24 hours | 2-10 seconds |
| Metrics (single) | N/A | 1-168 hours | < 5 seconds |
| Metrics (multiple) | 5-10 queries | 1-24 hours | 5-30 seconds |
| Health checks | N/A | 1-2 hours | < 10 seconds |

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
