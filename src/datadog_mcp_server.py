#!/usr/bin/env python3
"""
Enhanced Datadog MCP Server

A comprehensive Model Context Protocol server that provides access to Datadog
monitoring data, metrics, logs, traces, spans, monitors, and hosts through
HTTP streamable transport with Server-Sent Events (SSE) support.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from fastmcp import FastMCP
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.api.hosts_api import HostsApi
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.api.spans_api import SpansApi
from datadog_api_client.v2.model.logs_list_request import LogsListRequest
from datadog_api_client.v2.model.logs_sort import LogsSort
from datadog_api_client.v2.model.spans_list_request import SpansListRequest
from datadog_api_client.v2.model.spans_sort import SpansSort
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatadogConfig:
    """Configuration for Datadog API client"""
    api_key: str
    app_key: str
    site: str = "datadoghq.com"

class DatadogMCPServer:
    """Enhanced Datadog MCP Server implementation"""
    
    def __init__(self, config: DatadogConfig):
        self.config = config
        self.api_client = self._setup_api_client()
        self.metrics_api = MetricsApi(self.api_client)
        self.logs_api = LogsApi(self.api_client)
        self.spans_api = SpansApi(self.api_client)
        self.monitors_api = MonitorsApi(self.api_client)
        self.hosts_api = HostsApi(self.api_client)
        
    def _setup_api_client(self) -> ApiClient:
        """Setup Datadog API client with configuration"""
        configuration = Configuration()
        configuration.api_key["apiKeyAuth"] = self.config.api_key
        configuration.api_key["appKeyAuth"] = self.config.app_key
        configuration.server_variables["site"] = self.config.site
        return ApiClient(configuration)
    
    def get_logs(self, query: str, limit: int = 100, from_time: Optional[str] = None, to_time: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve logs based on query filters"""
        try:
            if from_time is None:
                from_time = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
            if to_time is None:
                to_time = datetime.utcnow().isoformat() + "Z"
            
            body = LogsListRequest(
                filter={
                    "query": query,
                    "from": from_time,
                    "to": to_time
                },
                sort=LogsSort.TIMESTAMP_ASCENDING,
                page={
                    "limit": limit
                }
            )
            
            response = self.logs_api.list_logs(body=body)
            
            logs = []
            if hasattr(response, 'data') and response.data:
                for log in response.data:
                    logs.append({
                        "id": getattr(log, 'id', ''),
                        "timestamp": getattr(log.attributes, 'timestamp', ''),
                        "message": getattr(log.attributes, 'message', ''),
                        "service": getattr(log.attributes, 'service', ''),
                        "status": getattr(log.attributes, 'status', ''),
                        "tags": getattr(log.attributes, 'tags', []),
                        "host": getattr(log.attributes, 'host', ''),
                        "source": getattr(log.attributes, 'source', '')
                    })
            
            return {
                "status": "success",
                "query": query,
                "logs": logs,
                "count": len(logs),
                "from_time": from_time,
                "to_time": to_time
            }
        except Exception as e:
            logger.error(f"Error retrieving logs: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query
            }
    
    def list_spans(self, query: str, limit: int = 100, from_time: Optional[str] = None, to_time: Optional[str] = None) -> Dict[str, Any]:
        """List spans relevant to the query"""
        try:
            if from_time is None:
                from_time = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
            if to_time is None:
                to_time = datetime.utcnow().isoformat() + "Z"
            
            body = SpansListRequest(
                filter={
                    "query": query,
                    "from": from_time,
                    "to": to_time
                },
                sort=SpansSort.TIMESTAMP_ASCENDING,
                page={
                    "limit": limit
                }
            )
            
            response = self.spans_api.list_spans(body=body)
            
            spans = []
            if hasattr(response, 'data') and response.data:
                for span in response.data:
                    spans.append({
                        "span_id": getattr(span, 'id', ''),
                        "trace_id": getattr(span.attributes, 'trace_id', ''),
                        "service": getattr(span.attributes, 'service', ''),
                        "operation_name": getattr(span.attributes, 'operation_name', ''),
                        "resource": getattr(span.attributes, 'resource', ''),
                        "start_time": getattr(span.attributes, 'start', ''),
                        "duration": getattr(span.attributes, 'duration', 0),
                        "tags": getattr(span.attributes, 'tags', {}),
                        "status": getattr(span.attributes, 'status', '')
                    })
            
            return {
                "status": "success",
                "query": query,
                "spans": spans,
                "count": len(spans),
                "from_time": from_time,
                "to_time": to_time
            }
        except Exception as e:
            logger.error(f"Error listing spans: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query
            }
    
    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        """Retrieve all spans from a specific trace"""
        try:
            # Use spans API to get all spans for a specific trace
            query = f"trace_id:{trace_id}"
            body = SpansListRequest(
                filter={
                    "query": query,
                    "from": (datetime.utcnow() - timedelta(hours=24)).isoformat() + "Z",
                    "to": datetime.utcnow().isoformat() + "Z"
                },
                sort=SpansSort.TIMESTAMP_ASCENDING,
                page={
                    "limit": 1000  # Get all spans for the trace
                }
            )
            
            response = self.spans_api.list_spans(body=body)
            
            spans = []
            if hasattr(response, 'data') and response.data:
                for span in response.data:
                    spans.append({
                        "span_id": getattr(span, 'id', ''),
                        "trace_id": getattr(span.attributes, 'trace_id', ''),
                        "parent_id": getattr(span.attributes, 'parent_id', ''),
                        "service": getattr(span.attributes, 'service', ''),
                        "operation_name": getattr(span.attributes, 'operation_name', ''),
                        "resource": getattr(span.attributes, 'resource', ''),
                        "start_time": getattr(span.attributes, 'start', ''),
                        "duration": getattr(span.attributes, 'duration', 0),
                        "tags": getattr(span.attributes, 'tags', {}),
                        "status": getattr(span.attributes, 'status', ''),
                        "error": getattr(span.attributes, 'error', 0)
                    })
            
            return {
                "status": "success",
                "trace_id": trace_id,
                "spans": spans,
                "span_count": len(spans)
            }
        except Exception as e:
            logger.error(f"Error retrieving trace: {e}")
            return {
                "status": "error",
                "error": str(e),
                "trace_id": trace_id
            }
    
    def list_metrics(self, from_time: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve a list of available metrics in the environment"""
        try:
            if from_time is None:
                from_time = int((datetime.utcnow() - timedelta(hours=1)).timestamp())
            
            response = self.metrics_api.list_active_metrics(
                _from=from_time
            )
            
            metrics = []
            if hasattr(response, 'metrics') and response.metrics:
                for metric in response.metrics:
                    metrics.append({
                        "metric": metric,
                        "type": "unknown"  # Type info not available in list endpoint
                    })
            
            return {
                "status": "success",
                "metrics": metrics,
                "count": len(metrics),
                "from_time": from_time
            }
        except Exception as e:
            logger.error(f"Error listing metrics: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_metrics(self, query: str, from_time: int, to_time: int) -> Dict[str, Any]:
        """Query timeseries metrics data"""
        try:
            response = self.metrics_api.query_metrics(
                _from=from_time,
                to=to_time,
                query=query
            )
            
            series_data = []
            if hasattr(response, 'series') and response.series:
                for series in response.series:
                    series_data.append({
                        "metric": getattr(series, 'metric', ''),
                        "display_name": getattr(series, 'display_name', ''),
                        "unit": getattr(series, 'unit', ''),
                        "pointlist": getattr(series, 'pointlist', []),
                        "scope": getattr(series, 'scope', ''),
                        "interval": getattr(series, 'interval', 0),
                        "length": getattr(series, 'length', 0)
                    })
            
            return {
                "status": "success",
                "query": query,
                "from_time": from_time,
                "to_time": to_time,
                "series": series_data,
                "series_count": len(series_data)
            }
        except Exception as e:
            logger.error(f"Error querying metrics: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query
            }
    
    def get_monitors(self, group_states: Optional[List[str]] = None, monitor_tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Retrieve monitors and their configurations"""
        try:
            response = self.monitors_api.list_monitors(
                group_states=group_states,
                tags=monitor_tags
            )
            
            monitors = []
            for monitor in response:
                monitors.append({
                    "id": getattr(monitor, 'id', ''),
                    "name": getattr(monitor, 'name', ''),
                    "type": getattr(monitor, 'type', ''),
                    "query": getattr(monitor, 'query', ''),
                    "message": getattr(monitor, 'message', ''),
                    "state": getattr(monitor.overall_state, 'value', '') if hasattr(monitor, 'overall_state') else '',
                    "tags": getattr(monitor, 'tags', []),
                    "options": getattr(monitor, 'options', {}),
                    "created": getattr(monitor, 'created', ''),
                    "modified": getattr(monitor, 'modified', ''),
                    "creator": getattr(monitor, 'creator', {})
                })
            
            return {
                "status": "success",
                "monitors": monitors,
                "count": len(monitors)
            }
        except Exception as e:
            logger.error(f"Error getting monitors: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def list_hosts(self, filter_query: Optional[str] = None, sort_field: str = "name", sort_dir: str = "asc") -> Dict[str, Any]:
        """Provide detailed host information"""
        try:
            response = self.hosts_api.list_hosts(
                filter=filter_query,
                sort_field=sort_field,
                sort_dir=sort_dir
            )
            
            hosts = []
            if hasattr(response, 'host_list') and response.host_list:
                for host in response.host_list:
                    hosts.append({
                        "name": getattr(host, 'name', ''),
                        "aliases": getattr(host, 'aliases', []),
                        "apps": getattr(host, 'apps', []),
                        "aws_name": getattr(host, 'aws_name', ''),
                        "host_name": getattr(host, 'host_name', ''),
                        "id": getattr(host, 'id', ''),
                        "is_muted": getattr(host, 'is_muted', False),
                        "last_reported_time": getattr(host, 'last_reported_time', ''),
                        "meta": getattr(host, 'meta', {}),
                        "metrics": getattr(host, 'metrics', {}),
                        "mute_timeout": getattr(host, 'mute_timeout', ''),
                        "sources": getattr(host, 'sources', []),
                        "tags_by_source": getattr(host, 'tags_by_source', {}),
                        "up": getattr(host, 'up', False)
                    })
            
            return {
                "status": "success",
                "hosts": hosts,
                "count": len(hosts),
                "total_returned": getattr(response, 'total_returned', 0),
                "total_matching": getattr(response, 'total_matching', 0)
            }
        except Exception as e:
            logger.error(f"Error listing hosts: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

# Initialize FastMCP server
mcp = FastMCP("Enhanced Datadog MCP Server")

# Initialize Datadog client
datadog_config = DatadogConfig(
    api_key=os.getenv("DATADOG_API_KEY", ""),
    app_key=os.getenv("DATADOG_APP_KEY", ""),
    site=os.getenv("DATADOG_SITE", "datadoghq.com")
)

if not datadog_config.api_key or not datadog_config.app_key:
    logger.error("DATADOG_API_KEY and DATADOG_APP_KEY must be set in environment variables")
    exit(1)

datadog_server = DatadogMCPServer(datadog_config)

# MCP Tools
@mcp.tool
def get_logs(
    query: str,
    limit: int = 100,
    hours_back: int = 1
) -> Dict[str, Any]:
    """
    Retrieve a list of logs based on query filters.
    
    Args:
        query: Log search query (e.g., "service:web-app ERROR")
        limit: Maximum number of logs to return (default: 100)
        hours_back: Number of hours back from now to search (default: 1)
    
    Returns:
        Dictionary containing log data or error information
    """
    from_time = (datetime.utcnow() - timedelta(hours=hours_back)).isoformat() + "Z"
    to_time = datetime.utcnow().isoformat() + "Z"
    return datadog_server.get_logs(query, limit, from_time, to_time)

@mcp.tool
def list_spans(
    query: str,
    limit: int = 100,
    hours_back: int = 1
) -> Dict[str, Any]:
    """
    List spans relevant to your query for investigation.
    
    Args:
        query: Span search query (e.g., "service:web-app operation_name:http.request")
        limit: Maximum number of spans to return (default: 100)
        hours_back: Number of hours back from now to search (default: 1)
    
    Returns:
        Dictionary containing span data or error information
    """
    from_time = (datetime.utcnow() - timedelta(hours=hours_back)).isoformat() + "Z"
    to_time = datetime.utcnow().isoformat() + "Z"
    return datadog_server.list_spans(query, limit, from_time, to_time)

@mcp.tool
def get_trace(trace_id: str) -> Dict[str, Any]:
    """
    Retrieve all spans from a specific trace.
    
    Args:
        trace_id: The trace ID to retrieve spans for
    
    Returns:
        Dictionary containing all spans in the trace or error information
    """
    return datadog_server.get_trace(trace_id)

@mcp.tool
def list_metrics(hours_back: int = 1) -> Dict[str, Any]:
    """
    Retrieve a list of available metrics in your environment.
    
    Args:
        hours_back: Number of hours back to look for active metrics (default: 1)
    
    Returns:
        Dictionary containing available metrics or error information
    """
    from_time = int((datetime.utcnow() - timedelta(hours=hours_back)).timestamp())
    return datadog_server.list_metrics(from_time)

@mcp.tool
def get_metrics(
    query: str,
    hours_back: int = 1
) -> Dict[str, Any]:
    """
    Query timeseries metrics data.
    
    Args:
        query: Datadog metrics query (e.g., "avg:system.cpu.user{*}")
        hours_back: Number of hours back from now to query (default: 1)
    
    Returns:
        Dictionary containing metrics data or error information
    """
    to_time = int(datetime.utcnow().timestamp())
    from_time = int((datetime.utcnow() - timedelta(hours=hours_back)).timestamp())
    return datadog_server.get_metrics(query, from_time, to_time)

@mcp.tool
def get_monitors(
    group_states: Optional[List[str]] = None,
    monitor_tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Retrieve monitors and their configurations.
    
    Args:
        group_states: List of group states to filter by (e.g., ["Alert", "Warn", "OK"])
        monitor_tags: List of monitor tags to filter by
    
    Returns:
        Dictionary containing monitor data or error information
    """
    return datadog_server.get_monitors(group_states, monitor_tags)

@mcp.tool
def list_hosts(
    filter_query: Optional[str] = None,
    sort_field: str = "name",
    sort_dir: str = "asc"
) -> Dict[str, Any]:
    """
    Provide detailed host information.
    
    Args:
        filter_query: Filter hosts by name, alias, or tag (e.g., "env:production")
        sort_field: Field to sort by (default: "name")
        sort_dir: Sort direction "asc" or "desc" (default: "asc")
    
    Returns:
        Dictionary containing host information or error information
    """
    return datadog_server.list_hosts(filter_query, sort_field, sort_dir)

# MCP Resources
@mcp.resource("datadog://logs/{query}")
def get_logs_resource(query: str) -> str:
    """
    Get logs data as a resource.
    
    Args:
        query: Log search query
    
    Returns:
        Formatted logs data as string
    """
    result = get_logs(query)
    if result["status"] == "success":
        logs_text = "\n".join([
            f"[{log['timestamp']}] {log['service']}: {log['message']}"
            for log in result["logs"]
        ])
        return f"Logs Query: {query}\n\nLogs:\n{logs_text}"
    else:
        return f"Error retrieving logs: {result['error']}"

@mcp.resource("datadog://spans/{query}")
def get_spans_resource(query: str) -> str:
    """
    Get spans data as a resource.
    
    Args:
        query: Span search query
    
    Returns:
        Formatted spans data as string
    """
    result = list_spans(query)
    if result["status"] == "success":
        spans_text = "\n".join([
            f"[{span['start_time']}] {span['service']}.{span['operation_name']} - {span['duration']}ns"
            for span in result["spans"]
        ])
        return f"Spans Query: {query}\n\nSpans:\n{spans_text}"
    else:
        return f"Error retrieving spans: {result['error']}"

@mcp.resource("datadog://trace/{trace_id}")
def get_trace_resource(trace_id: str) -> str:
    """
    Get trace data as a resource.
    
    Args:
        trace_id: Trace ID
    
    Returns:
        Formatted trace data as string
    """
    result = get_trace(trace_id)
    if result["status"] == "success":
        spans_text = "\n".join([
            f"  {span['service']}.{span['operation_name']} ({span['duration']}ns)"
            for span in result["spans"]
        ])
        return f"Trace ID: {trace_id}\n\nSpans:\n{spans_text}"
    else:
        return f"Error retrieving trace: {result['error']}"

@mcp.resource("datadog://metrics/{query}")
def get_metrics_resource(query: str) -> str:
    """
    Get metrics data as a resource.
    
    Args:
        query: Datadog metrics query
    
    Returns:
        Formatted metrics data as string
    """
    result = get_metrics(query)
    if result["status"] == "success":
        return f"Metrics Query: {query}\n\nData: {result}"
    else:
        return f"Error querying metrics: {result['error']}"

# MCP Prompts
@mcp.prompt("datadog-investigation")
def datadog_investigation_prompt(
    service_name: str,
    time_range_hours: int = 1,
    issue_description: str = ""
) -> str:
    """
    Generate a comprehensive investigation prompt for Datadog data.
    
    Args:
        service_name: The service to investigate
        time_range_hours: Time range in hours for the investigation
        issue_description: Description of the issue being investigated
    
    Returns:
        Formatted prompt for comprehensive investigation
    """
    return f"""
    Investigate the following service issue in Datadog:
    
    Service: {service_name}
    Time Range: Last {time_range_hours} hours
    Issue: {issue_description}
    
    Please perform the following investigation steps:
    
    1. **Logs Analysis**
       - Use get_logs to search for errors: "service:{service_name} status:error"
       - Look for warning patterns: "service:{service_name} status:warn"
    
    2. **Traces and Spans Analysis**
       - Use list_spans to find slow operations: "service:{service_name}"
       - Identify error traces and get full trace details with get_trace
    
    3. **Metrics Analysis**
       - Check service performance metrics: "avg:trace.{service_name}.request.duration"
       - Monitor error rates: "sum:trace.{service_name}.request.errors"
       - Review throughput: "sum:trace.{service_name}.request.hits"
    
    4. **Infrastructure Analysis**
       - Use list_hosts to check host health for the service
       - Review host-level metrics if issues are found
    
    5. **Monitor Status**
       - Use get_monitors to check if any monitors are alerting for this service
    
    Provide a summary of findings and recommendations for resolution.
    """

@mcp.prompt("datadog-performance-analysis")
def datadog_performance_analysis_prompt(
    metric_query: str,
    time_range_hours: int = 24
) -> str:
    """
    Generate a prompt for analyzing Datadog performance metrics.
    
    Args:
        metric_query: The metrics query to analyze
        time_range_hours: Time range in hours for the analysis
    
    Returns:
        Formatted prompt for performance analysis
    """
    return f"""
    Analyze the following Datadog performance metrics:
    
    Query: {metric_query}
    Time Range: Last {time_range_hours} hours
    
    Please provide:
    1. Summary of the metric trends using get_metrics
    2. Any anomalies or patterns observed
    3. Correlation with related metrics
    4. Recommendations for optimization or alerting
    5. Potential root causes for any issues identified
    
    Use the available Datadog tools to fetch and analyze the data.
    """

if __name__ == "__main__":
    # Configure server to use HTTP transport with SSE support
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "8080"))
    
    logger.info(f"Starting Enhanced Datadog MCP Server on {host}:{port}")
    logger.info("Transport: HTTP Streamable with SSE support")
    logger.info(f"Datadog Site: {datadog_config.site}")
    logger.info("Available tools: get_logs, list_spans, get_trace, list_metrics, get_metrics, get_monitors, list_hosts")
    
    # Run the server with HTTP transport
    mcp.run(transport="http", host=host, port=port)

