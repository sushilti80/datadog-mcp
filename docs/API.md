# Enhanced Datadog MCP Server API Documentation

This document provides detailed information about the Enhanced Datadog MCP Server API, including all available tools, resources, and prompts.

## Server Information

- **Name**: Enhanced Datadog MCP Server
- **Transport**: HTTP Streamable with Server-Sent Events (SSE)
- **Protocol Version**: 2025-06-18
- **FastMCP Version**: 2.10.6+
- **Endpoint**: `http://localhost:8080/mcp/`

## Authentication

The server requires Datadog API credentials:

- `DATADOG_API_KEY`: Your Datadog API key
- `DATADOG_APP_KEY`: Your Datadog application key
- `DATADOG_SITE`: Datadog site (default: datadoghq.com)

## Available Tools

### 1. get_logs

Retrieve a list of logs based on query filters.

**Parameters:**
- `query` (string, required): Log search query
- `limit` (integer, optional): Maximum number of logs to return (default: 100)
- `hours_back` (integer, optional): Number of hours back from now to search (default: 1)

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "logs-1",
  "method": "tools/call",
  "params": {
    "name": "get_logs",
    "arguments": {
      "query": "service:web-app status:error",
      "limit": 50,
      "hours_back": 2
    }
  }
}
```

**Example Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "logs-1",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"status\": \"success\", \"query\": \"service:web-app status:error\", \"logs\": [...], \"count\": 25}"
      }
    ]
  }
}
```

### 2. list_spans

List spans relevant to your query for investigation.

**Parameters:**
- `query` (string, required): Span search query
- `limit` (integer, optional): Maximum number of spans to return (default: 100)
- `hours_back` (integer, optional): Number of hours back from now to search (default: 1)

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "spans-1",
  "method": "tools/call",
  "params": {
    "name": "list_spans",
    "arguments": {
      "query": "service:web-app operation_name:http.request",
      "limit": 25,
      "hours_back": 1
    }
  }
}
```

### 3. get_trace

Retrieve all spans from a specific trace.

**Parameters:**
- `trace_id` (string, required): The trace ID to retrieve spans for

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "trace-1",
  "method": "tools/call",
  "params": {
    "name": "get_trace",
    "arguments": {
      "trace_id": "1234567890abcdef"
    }
  }
}
```

### 4. list_metrics

Retrieve a list of available metrics in your environment.

**Parameters:**
- `hours_back` (integer, optional): Number of hours back to look for active metrics (default: 1)

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "metrics-list-1",
  "method": "tools/call",
  "params": {
    "name": "list_metrics",
    "arguments": {
      "hours_back": 2
    }
  }
}
```

### 5. get_metrics

Query timeseries metrics data.

**Parameters:**
- `query` (string, required): Datadog metrics query
- `hours_back` (integer, optional): Number of hours back from now to query (default: 1)

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "metrics-1",
  "method": "tools/call",
  "params": {
    "name": "get_metrics",
    "arguments": {
      "query": "avg:system.cpu.user{*}",
      "hours_back": 4
    }
  }
}
```

### 6. get_monitors

Retrieve monitors and their configurations.

**Parameters:**
- `group_states` (array, optional): List of group states to filter by (e.g., ["Alert", "Warn", "OK"])
- `monitor_tags` (array, optional): List of monitor tags to filter by

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "monitors-1",
  "method": "tools/call",
  "params": {
    "name": "get_monitors",
    "arguments": {
      "group_states": ["Alert", "Warn"]
    }
  }
}
```

### 7. list_hosts

Provide detailed host information.

**Parameters:**
- `filter_query` (string, optional): Filter hosts by name, alias, or tag
- `sort_field` (string, optional): Field to sort by (default: "name")
- `sort_dir` (string, optional): Sort direction "asc" or "desc" (default: "asc")

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "hosts-1",
  "method": "tools/call",
  "params": {
    "name": "list_hosts",
    "arguments": {
      "filter_query": "env:production",
      "sort_field": "name",
      "sort_dir": "asc"
    }
  }
}
```

## Available Resources

Resources provide contextual data that can be loaded into AI agent context.

### 1. datadog://logs/{query}

Get logs data as a resource for context.

**URI Pattern:** `datadog://logs/{query}`

**Example:**
```json
{
  "jsonrpc": "2.0",
  "id": "resource-1",
  "method": "resources/read",
  "params": {
    "uri": "datadog://logs/service:web-app ERROR"
  }
}
```

### 2. datadog://spans/{query}

Get spans data as a resource for analysis.

**URI Pattern:** `datadog://spans/{query}`

**Example:**
```json
{
  "jsonrpc": "2.0",
  "id": "resource-2",
  "method": "resources/read",
  "params": {
    "uri": "datadog://spans/service:web-app duration:>1s"
  }
}
```

### 3. datadog://trace/{trace_id}

Get complete trace data as a resource.

**URI Pattern:** `datadog://trace/{trace_id}`

**Example:**
```json
{
  "jsonrpc": "2.0",
  "id": "resource-3",
  "method": "resources/read",
  "params": {
    "uri": "datadog://trace/1234567890abcdef"
  }
}
```

### 4. datadog://metrics/{query}

Get metrics data as a resource for context.

**URI Pattern:** `datadog://metrics/{query}`

**Example:**
```json
{
  "jsonrpc": "2.0",
  "id": "resource-4",
  "method": "resources/read",
  "params": {
    "uri": "datadog://metrics/avg:system.cpu.user{*}"
  }
}
```

## Available Prompts

Prompts provide pre-defined workflows for common investigation scenarios.

### 1. datadog-investigation

Generate a comprehensive investigation prompt for Datadog data.

**Parameters:**
- `service_name` (string, required): The service to investigate
- `time_range_hours` (integer, optional): Time range in hours for the investigation (default: 1)
- `issue_description` (string, optional): Description of the issue being investigated

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "prompt-1",
  "method": "prompts/get",
  "params": {
    "name": "datadog-investigation",
    "arguments": {
      "service_name": "web-app",
      "time_range_hours": 2,
      "issue_description": "High error rate and slow response times"
    }
  }
}
```

### 2. datadog-performance-analysis

Generate a prompt for analyzing Datadog performance metrics.

**Parameters:**
- `metric_query` (string, required): The metrics query to analyze
- `time_range_hours` (integer, optional): Time range in hours for the analysis (default: 24)

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "prompt-2",
  "method": "prompts/get",
  "params": {
    "name": "datadog-performance-analysis",
    "arguments": {
      "metric_query": "avg:trace.web-app.request.duration",
      "time_range_hours": 12
    }
  }
}
```

## Error Handling

The server provides comprehensive error handling with detailed error messages:

### Authentication Errors
```json
{
  "jsonrpc": "2.0",
  "id": "error-1",
  "error": {
    "code": -32000,
    "message": "Authentication failed: Invalid API key"
  }
}
```

### Query Errors
```json
{
  "jsonrpc": "2.0",
  "id": "error-2",
  "error": {
    "code": -32000,
    "message": "Query error: Invalid log search syntax"
  }
}
```

### Rate Limiting
```json
{
  "jsonrpc": "2.0",
  "id": "error-3",
  "error": {
    "code": -32000,
    "message": "Rate limit exceeded: Please wait before making more requests"
  }
}
```

## Transport Details

### HTTP Streamable Transport

The server implements the MCP Streamable HTTP transport:

- **POST Requests**: Send JSON-RPC messages to the server
- **GET Requests**: Open SSE streams for server-to-client communication
- **Content-Type**: `application/json` for requests
- **Accept Header**: Must include both `application/json` and `text/event-stream`

### Server-Sent Events (SSE)

Responses may be delivered via SSE streams:

```
event: message
data: {"jsonrpc":"2.0","id":"test","result":{...}}
```

### Session Management

The server supports session management via `Mcp-Session-Id` headers for stateful connections.

## Rate Limits

The server respects Datadog API rate limits:

- **Logs API**: 300 requests per hour per organization
- **Spans API**: 300 requests per hour per organization  
- **Metrics API**: 100 requests per hour per organization
- **Monitors API**: 300 requests per hour per organization

## Best Practices

1. **Query Optimization**: Use specific filters to reduce data volume
2. **Time Range Limits**: Limit time ranges to avoid large result sets
3. **Error Handling**: Always check response status before processing results
4. **Rate Limiting**: Implement client-side rate limiting to avoid API limits
5. **Caching**: Cache frequently accessed data to reduce API calls

