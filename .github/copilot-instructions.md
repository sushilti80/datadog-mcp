# Datadog MCP Server - AI Agent Instructions

## Architecture Overview

This is a **FastMCP-based Model Context Protocol (MCP) server** that exposes Datadog observability APIs to AI agents. The architecture centers on two core systems:

1. **FastMCP Server** (`src/datadog_mcp_server.py`) - HTTP+SSE transport server with tools, resources, and prompts
2. **Key Rotation System** (`src/key_rotation.py`) - Intelligent multi-key management for rate limit avoidance

### Key Components

- **DatadogMCPServer class**: Main server with `_execute_with_key_rotation()` wrapper for all API calls
- **KeyPoolManager**: Manages 3-5 API key pairs with 5 rotation strategies (adaptive, round_robin, LRU, weighted, random)
- **Circuit Breaker**: Automatically isolates problematic keys after configurable failure threshold
- **Debug System**: Enum-based debug levels (NONE/INFO/DEBUG/TRACE) with correlation IDs and sensitive data masking

### Critical Pattern: DD_SITE Must Always Come From Environment

**NEVER hardcode Datadog site values**. Always use environment variables:

```python
# ✅ CORRECT - Always read from environment
site = os.getenv("DD_SITE") or os.getenv("DATADOG_SITE") or "us3.datadoghq.com"

# ✅ For numbered keys
site = os.getenv(f"DD_SITE_{i}") or os.getenv(f"DATADOG_SITE_{i}") or "us3.datadoghq.com"

# ❌ NEVER do this
site = "datadoghq.com"  # Wrong - hardcoded value
```

The default fallback `us3.datadoghq.com` should only appear in environment loading functions (`load_keys_from_environment()` in `key_rotation.py`), never in API client configuration.

## Development Workflows

### Running the Server

```bash
# Local development - reads .env file automatically
python3 src/datadog_mcp_server.py

# With debug tracing
MCP_DEBUG_LEVEL=TRACE python3 src/datadog_mcp_server.py

# Check server health on port 8080
curl http://localhost:8080/health
```

### Testing

```bash
# Run all tests including key rotation
pytest tests/ -v

# Run specific test suite
pytest tests/test_key_rotation.py -v

# Test with coverage
pytest tests/ --cov=src --cov-report=html
```

Use `scripts/run_tests.sh` for full test suite with linting and formatting checks.

### Multi-Key Configuration

Multiple API keys are **required** for production rate limit handling. Configuration supports:

1. **Numbered format** (preferred):
```bash
DD_API_KEY=primary_key
DD_APP_KEY=primary_app
DD_SITE=us3.datadoghq.com

DD_API_KEY_2=second_key
DD_APP_KEY_2=second_app
DD_SITE_2=us3.datadoghq.com  # Must be set per key
```

2. **JSON format** (alternative):
```bash
DD_API_KEYS_JSON='[{"api_key":"k1","app_key":"a1","site":"us3.datadoghq.com"}]'
```

## Code Patterns & Conventions

### Adding New Datadog API Tools

All tools MUST use the `_execute_with_key_rotation()` wrapper:

```python
@mcp.tool
def new_datadog_tool(param: str) -> str:
    """Tool description"""
    def _operation(key_pair: KeyPair, api_client: ApiClient):
        # Your API call using api_client
        api = SomeDatadogApi(api_client)
        return api.some_method()
    
    result = datadog_server._execute_with_key_rotation(
        "operation_name",
        _operation
    )
    return result
```

The wrapper automatically handles:
- Key selection based on rotation strategy
- Rate limit detection and key switching
- Circuit breaker triggering on consecutive failures
- Performance metrics and success rate tracking

### Debug Logging

Use `debug_log()` with appropriate levels:

```python
from src.datadog_mcp_server import debug_log, DebugLevel

debug_log(DebugLevel.INFO, "High-level operation", {"key": "value"})
debug_log(DebugLevel.DEBUG, "Detailed flow info", {"state": state})
debug_log(DebugLevel.TRACE, "Verbose internals", {"full_data": data})
```

Sensitive data (keys, tokens) is **automatically masked** when `MCP_DEBUG_MASK_SENSITIVE=true`.

### Time Range Handling

The server uses **flexible time parameters**:

```python
# Supported: minutes_back, hours_back, days_back, weeks_back, months_back
# Always convert to Unix timestamps (seconds since epoch)
from_time = int((datetime.now(timezone.utc) - timedelta(hours=hours_back)).timestamp())
to_time = int(datetime.now(timezone.utc).timestamp())
```

### Error Handling

Follow the established error categorization:

```python
try:
    result = api_call()
except Exception as e:
    error_category = categorize_error(e)  # Returns: API, Validation, Rate Limit, Network, etc.
    error_details = {
        "category": error_category,
        "message": str(e),
        "correlation_id": correlation_id
    }
    return {"status": "error", "error": error_details}
```

## Testing Conventions

### Key Rotation Tests

Mock the key pool manager to test rotation logic:

```python
def test_new_feature(self):
    key_pool = KeyPoolManager(rotation_strategy=RotationStrategy.ROUND_ROBIN)
    key_pool.add_key(KeyPair("test_id", "api_key", "app_key", site="us3.datadoghq.com"))
    
    # Test with rotation
    key = key_pool.get_key_by_strategy()
    assert key.id == "test_id"
```

### Integration Tests

Real API tests require valid credentials:

```python
# Only run integration tests when credentials are available
@pytest.mark.skipif(not os.getenv("DD_API_KEY"), reason="Requires DD_API_KEY")
def test_real_api_call(self):
    # Test actual Datadog API
```

## Common Pitfalls

1. **Don't bypass key rotation**: Always use `_execute_with_key_rotation()`, never create API clients directly in tools
2. **Site configuration**: Never hardcode `datadoghq.com` - always read from `DD_SITE` environment variable
3. **Timestamp precision**: Datadog expects **seconds** (Unix epoch), not milliseconds
4. **Log pagination**: Use `cursor` from response for `get_next_datadog_logs_page`, not manual offset calculation
5. **FastMCP decorators**: Use `@mcp.tool`, `@mcp.resource("uri://pattern")`, `@mcp.prompt("name")` - order matters

## Docker Deployment

```bash
# Build with multi-key support
docker build -t datadog-mcp-server .

# Run with environment file
docker run --env-file .env -p 8080:8080 datadog-mcp-server

# Or use docker-compose for full stack
docker-compose up -d
```

## MCP Server Exposed APIs

### 🔧 Tools (14 total)
The server exposes 14 tools via `@mcp.tool` decorator:

**Monitoring & Metrics**:
- `get_metrics(query, hours_back, minutes_back)` - Query timeseries metrics with flexible time ranges
- `list_metrics(filter, days_back)` - Discover available metrics with filtering

**Logs & Search**:
- `get_logs(query, limit, hours_back, sort, indexes)` - Advanced log search with pagination
- `get_next_datadog_logs_page(cursor, limit)` - Cursor-based pagination for large log sets

**Infrastructure**:
- `get_monitors(monitor_ids, group_states, monitor_tags)` - Monitor status and management
- `list_dashboards()` - Dashboard discovery and listing
- `list_hosts(filter_query, sort_by, count, start)` - Infrastructure hosts information
- `get_host(hostname)` - Detailed information about a specific host

**Tracing & APM**:
- `list_spans(query, hours_back, limit)` - List APM spans for distributed tracing
- `get_trace(trace_id)` - Get detailed trace information

**Incidents**:
- `list_incidents(include_field, page_size, page_offset)` - Retrieve ongoing incidents
- `get_incident(incident_id)` - Get specific incident details

**System**:
- `server_health_check()` - Verify server status and Datadog API connectivity
- `get_key_pool_status()` - Monitor API key rotation system health

### 📊 Resources (4 total)
Smart resources via `@mcp.resource()` decorator with URI patterns:

- `datadog://metrics/{query}` - Real-time metrics with AI analysis
- `datadog://logs/{query}` - Intelligent log search with basic formatting
- `datadog://logs-detailed/{query}` - Enhanced log analysis with full context
- `datadog://health-check/{service_name}` - Comprehensive service health assessment

### 🤖 Prompts (4 total)
AI-guided workflows via `@mcp.prompt()` decorator:

- `datadog-metrics-analysis` - Automated metrics analysis and insights
- `datadog-performance-diagnosis` - Step-by-step performance troubleshooting workflow
- `datadog-incident-commander` - Intelligent incident response coordination
- `datadog-time-range-advisor` - Smart time range selection guidance

## Key Files to Reference

- `src/datadog_mcp_server.py` - Main server implementation, tool definitions (2200+ lines)
- `src/key_rotation.py` - Key pool manager, rotation strategies, circuit breaker (750+ lines)
- `docs/KEY_ROTATION.md` - Multi-key configuration guide with examples
- `docs/API.md` - Complete tool/resource/prompt API reference
- `tests/test_key_rotation.py` - Key rotation test patterns and examples
- `.env.example` - All available configuration options with presets
- `AGENTS.md` - Task-specific agent guidance for extending the server

## Debug Presets

Common debug configurations in `.env`:

```bash
# For 400 Bad Request issues
MCP_DEBUG_LEVEL=TRACE
MCP_DEBUG_REQUESTS=true
MCP_DEBUG_PARAMETERS=true

# For rate limit investigation
MCP_DEBUG_LEVEL=DEBUG
MCP_DEBUG_TIMING=true
MCP_DEBUG_RESPONSES=true

# For key rotation troubleshooting
MCP_DEBUG_LEVEL=TRACE
DD_KEY_ROTATION_STRATEGY=round_robin  # Simpler than adaptive
```

## When Modifying Key Rotation Logic

1. **Always preserve site configuration**: Each `KeyPair` must maintain its own `site` value from environment
2. **Test all strategies**: Changes to key selection affect all 5 rotation strategies
3. **Verify circuit breaker**: Ensure consecutive failure threshold still triggers correctly
4. **Check health monitoring**: Background thread must properly reset expired rate limits
5. **Update KEY_ROTATION.md**: Document any new environment variables or behavior changes
