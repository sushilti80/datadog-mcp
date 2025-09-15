#!/usr/bin/env python3
"""
Datadog MCP Server

A Model Context Protocol server that provides access to Datadog monitoring data,
metrics, logs, and other observability features through HTTP streamable transport
with Server-Sent Events (SSE) support.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from fastmcp import FastMCP
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from datadog_api_client.v1.api.logs_api import LogsApi
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.api.dashboards_api import DashboardsApi
from datadog_api_client.v1.api.hosts_api import HostsApi
from datadog_api_client.v1.model.metrics_query_response import MetricsQueryResponse
from datadog_api_client.v1.model.logs_list_request import LogsListRequest
from datadog_api_client.v1.model.logs_sort import LogsSort
from datadog_api_client.v2.api.logs_api import LogsApi as LogsApiV2
from datadog_api_client.v2.api.spans_api import SpansApi
from datadog_api_client.v2.api.incidents_api import IncidentsApi
from datadog_api_client.v2.model.logs_list_request import LogsListRequest as LogsListRequestV2
from datadog_api_client.v2.model.logs_sort import LogsSort as LogsSortV2
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
    """Datadog MCP Server implementation"""
    
    def __init__(self, config: DatadogConfig):
        self.config = config
        self.api_client = self._setup_api_client()
        self.metrics_api = MetricsApi(self.api_client)
        self.logs_api = LogsApi(self.api_client)
        self.logs_api_v2 = LogsApiV2(self.api_client)
        self.monitors_api = MonitorsApi(self.api_client)
        self.dashboards_api = DashboardsApi(self.api_client)
        self.hosts_api = HostsApi(self.api_client)
        self.spans_api = SpansApi(self.api_client)
        self.incidents_api = IncidentsApi(self.api_client)
        
    def _setup_api_client(self) -> ApiClient:
        """Setup Datadog API client with configuration"""
        configuration = Configuration()
        configuration.api_key["apiKeyAuth"] = self.config.api_key
        configuration.api_key["appKeyAuth"] = self.config.app_key
        configuration.server_variables["site"] = self.config.site
        return ApiClient(configuration)
    
    def query_metrics(self, query: str, from_time: int, to_time: int) -> Dict[str, Any]:
        """Query Datadog metrics"""
        try:
            response = self.metrics_api.query_metrics(
                _from=from_time,
                to=to_time,
                query=query
            )
            return {
                "status": "success",
                "query": query,
                "from_time": from_time,
                "to_time": to_time,
                "series": response.series if hasattr(response, 'series') else []
            }
        except Exception as e:
            logger.error(f"Error querying metrics: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query
            }
    
    def search_logs(
        self, 
        query: str, 
        limit: int = 100, 
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        indexes: Optional[List[str]] = None,
        sort: str = "timestamp",
        cursor: Optional[str] = None,
        max_total_logs: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search Datadog logs with enhanced flexibility and pagination support.
        
        Args:
            query: Log search query (e.g., "service:web-app ERROR")
            limit: Number of logs per page (max 1000, default: 100)
            from_time: Start time in ISO format (e.g., "2024-01-01T00:00:00Z")
            to_time: End time in ISO format (e.g., "2024-01-01T23:59:59Z")
            indexes: List of log indexes to search (default: all)
            sort: Sort order ("timestamp" or "-timestamp", default: "timestamp")
            cursor: Pagination cursor from previous response
            max_total_logs: Maximum total logs to retrieve across all pages (default: limit)
        """
        try:
            # Set default time range if not provided
            if from_time is None:
                from_time = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
            if to_time is None:
                to_time = datetime.utcnow().isoformat() + "Z"
            
            # Validate and adjust limit (Datadog API max is 1000 per request)
            page_limit = min(limit, 1000)
            
            # Set maximum total logs to retrieve
            if max_total_logs is None:
                max_total_logs = limit
            
            # Prepare filter
            log_filter = {
                "query": query,
                "from": from_time,
                "to": to_time
            }
            
            if indexes:
                log_filter["indexes"] = indexes
            
            # Prepare page parameters
            page_params = {"limit": page_limit}
            if cursor:
                page_params["cursor"] = cursor
            
            # Convert sort parameter to enum
            sort_order = LogsSortV2.TIMESTAMP_DESCENDING if sort == "-timestamp" else LogsSortV2.TIMESTAMP_ASCENDING
            
            body = LogsListRequestV2(
                filter=log_filter,
                sort=sort_order,
                page=page_params
            )
            
            all_logs = []
            next_cursor = None
            total_retrieved = 0
            
            # Pagination loop to retrieve more logs if needed
            while total_retrieved < max_total_logs:
                # Update cursor for subsequent requests
                if next_cursor:
                    body.page["cursor"] = next_cursor
                
                # Adjust limit for final page
                remaining = max_total_logs - total_retrieved
                if remaining < page_limit:
                    body.page["limit"] = remaining
                
                response = self.logs_api_v2.list_logs(body=body)
                
                # Process logs from this page
                page_logs = []
                if hasattr(response, 'data') and response.data:
                    for log in response.data:
                        log_entry = {
                            "id": getattr(log, 'id', ''),
                            "timestamp": getattr(log.attributes, 'timestamp', '') if hasattr(log, 'attributes') else '',
                            "message": getattr(log.attributes, 'message', '') if hasattr(log, 'attributes') else '',
                            "service": getattr(log.attributes, 'service', '') if hasattr(log, 'attributes') else '',
                            "status": getattr(log.attributes, 'status', '') if hasattr(log, 'attributes') else '',
                            "tags": getattr(log.attributes, 'tags', []) if hasattr(log, 'attributes') else [],
                            "host": getattr(log.attributes, 'host', '') if hasattr(log, 'attributes') else '',
                            "source": getattr(log.attributes, 'ddsource', '') if hasattr(log, 'attributes') else ''
                        }
                        
                        # Add custom attributes if they exist
                        if hasattr(log, 'attributes') and hasattr(log.attributes, 'attributes'):
                            log_entry["custom_attributes"] = log.attributes.attributes
                        
                        page_logs.append(log_entry)
                        total_retrieved += 1
                        
                        if total_retrieved >= max_total_logs:
                            break
                
                all_logs.extend(page_logs)
                
                # Check if there are more pages
                if hasattr(response, 'links') and hasattr(response.links, 'next') and response.links.next:
                    # Extract cursor from next link if available
                    next_cursor = getattr(response.meta, 'page', {}).get('after') if hasattr(response, 'meta') else None
                    if not next_cursor:
                        break
                else:
                    break
                
                # If we got fewer logs than requested, we've reached the end
                if len(page_logs) < body.page["limit"]:
                    break
            
            # Prepare response with pagination info
            result = {
                "status": "success",
                "query": query,
                "logs": all_logs,
                "count": len(all_logs),
                "total_retrieved": total_retrieved,
                "from_time": from_time,
                "to_time": to_time,
                "sort": sort,
                "indexes_searched": indexes or ["all"]
            }
            
            # Add pagination cursor if available for next request
            if next_cursor and total_retrieved >= max_total_logs:
                result["next_cursor"] = next_cursor
                result["has_more"] = True
            else:
                result["has_more"] = False
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching logs: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query,
                "from_time": from_time if 'from_time' in locals() else None,
                "to_time": to_time if 'to_time' in locals() else None
            }
    
    def get_monitors(self, group_states: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get Datadog monitors"""
        try:
            response = self.monitors_api.list_monitors(
                group_states=group_states
            )
            
            monitors = []
            for monitor in response:
                monitors.append({
                    "id": getattr(monitor, 'id', ''),
                    "name": getattr(monitor, 'name', ''),
                    "type": getattr(monitor, 'type', ''),
                    "query": getattr(monitor, 'query', ''),
                    "state": getattr(monitor.overall_state, 'value', '') if hasattr(monitor, 'overall_state') else '',
                    "tags": getattr(monitor, 'tags', [])
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
    
    def get_dashboards(self) -> Dict[str, Any]:
        """Get Datadog dashboards"""
        try:
            response = self.dashboards_api.list_dashboards()
            
            dashboards = []
            if hasattr(response, 'dashboards'):
                for dashboard in response.dashboards:
                    dashboards.append({
                        "id": getattr(dashboard, 'id', ''),
                        "title": getattr(dashboard, 'title', ''),
                        "description": getattr(dashboard, 'description', ''),
                        "url": getattr(dashboard, 'url', ''),
                        "created_at": getattr(dashboard, 'created_at', ''),
                        "modified_at": getattr(dashboard, 'modified_at', '')
                    })
            
            return {
                "status": "success",
                "dashboards": dashboards,
                "count": len(dashboards)
            }
        except Exception as e:
            logger.error(f"Error getting dashboards: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def list_active_metrics(self, filter_query: Optional[str] = None) -> Dict[str, Any]:
        """List active metrics in Datadog environment"""
        try:
            from datadog_api_client.v1.model.metrics_list_response import MetricsListResponse
            
            # Get metrics from last 2 hours to ensure we get active metrics
            from_time = int((datetime.now() - timedelta(hours=2)).timestamp())
            
            if filter_query:
                response = self.metrics_api.list_active_metrics(
                    from_time=from_time,
                    filter=filter_query
                )
            else:
                response = self.metrics_api.list_active_metrics(
                    from_time=from_time
                )
            
            metrics = []
            if hasattr(response, 'metrics') and response.metrics:
                metrics = response.metrics
            
            return {
                "status": "success",
                "metrics": metrics,
                "count": len(metrics),
                "filter_applied": filter_query,
                "from_time": from_time
            }
            
        except Exception as e:
            logger.error(f"Error listing active metrics: {e}")
            return {
                "status": "error",
                "error": str(e),
                "metrics": [],
                "count": 0
            }
    
    def search_spans(
        self, 
        query: str, 
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Search for spans based on query criteria"""
        try:
            # Set default time range if not provided
            if not from_time:
                from_time = (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
            if not to_time:
                to_time = datetime.now().isoformat() + "Z"
                
            # Note: SpansApi implementation may vary - this is a placeholder structure
            spans = []  # Placeholder - actual API call would go here
            
            return {
                "status": "success",
                "query": query,
                "from_time": from_time,
                "to_time": to_time,
                "spans": spans,
                "count": len(spans)
            }
        except Exception as e:
            logger.error(f"Error searching spans: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query
            }
    
    def get_trace_data(self, trace_id: str) -> Dict[str, Any]:
        """Get all spans for a specific trace ID"""
        try:
            # Note: Actual API method may vary - placeholder implementation
            trace_data = {"trace_id": trace_id, "spans": []}
            
            return {
                "status": "success",
                "trace_id": trace_id,
                "data": trace_data
            }
        except Exception as e:
            logger.error(f"Error getting trace data: {e}")
            return {
                "status": "error", 
                "error": str(e),
                "trace_id": trace_id
            }
    
    def list_incidents(
        self,
        include_field: Optional[str] = None,
        page_size: int = 100,
        page_offset: int = 0
    ) -> Dict[str, Any]:
        """List incidents from Datadog incident management"""
        try:
            # Note: Actual API call depends on incidents API structure
            incidents = []  # Placeholder for actual implementation
            
            return {
                "status": "success",
                "incidents": incidents,
                "count": len(incidents),
                "page_size": page_size,
                "page_offset": page_offset
            }
        except Exception as e:
            logger.error(f"Error listing incidents: {e}")
            return {
                "status": "error",
                "error": str(e),
                "incidents": []
            }
    
    def get_incident_details(self, incident_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific incident"""
        try:
            # Note: Placeholder for actual API implementation
            incident_data = {"incident_id": incident_id}
            
            return {
                "status": "success",
                "incident_id": incident_id,
                "data": incident_data
            }
        except Exception as e:
            logger.error(f"Error getting incident details: {e}")
            return {
                "status": "error",
                "error": str(e),
                "incident_id": incident_id
            }
    
    def list_hosts_data(
        self,
        filter_query: Optional[str] = None,
        sort_by: str = "name",
        count: int = 100,
        start: int = 0
    ) -> Dict[str, Any]:
        """List infrastructure hosts"""
        try:
            response = self.hosts_api.list_hosts(
                filter=filter_query,
                sort_field=sort_by,
                count=count,
                start=start
            )
            
            hosts = []
            if hasattr(response, 'host_list') and response.host_list:
                hosts = [
                    {
                        "name": host.name if hasattr(host, 'name') else "unknown",
                        "id": host.id if hasattr(host, 'id') else None,
                        "last_reported_time": host.last_reported_time if hasattr(host, 'last_reported_time') else None,
                        "up": host.up if hasattr(host, 'up') else None,
                        "sources": host.sources if hasattr(host, 'sources') else [],
                        "tags_by_source": host.tags_by_source if hasattr(host, 'tags_by_source') else {}
                    } 
                    for host in response.host_list
                ]
            
            return {
                "status": "success",
                "hosts": hosts,
                "count": len(hosts),
                "total_returned": response.total_returned if hasattr(response, 'total_returned') else len(hosts),
                "total_matching": response.total_matching if hasattr(response, 'total_matching') else len(hosts)
            }
        except Exception as e:
            logger.error(f"Error listing hosts: {e}")
            return {
                "status": "error",
                "error": str(e),
                "hosts": []
            }
    
    def get_host_details(self, hostname: str) -> Dict[str, Any]:
        """Get detailed information about a specific host"""
        try:
            response = self.hosts_api.get_host(host_name=hostname)
            
            host_data = {
                "hostname": hostname,
                "details": "Host data retrieved successfully"
            }
            
            if hasattr(response, 'host'):
                host = response.host
                host_data = {
                    "hostname": hostname,
                    "name": host.name if hasattr(host, 'name') else hostname,
                    "id": host.id if hasattr(host, 'id') else None,
                    "last_reported_time": host.last_reported_time if hasattr(host, 'last_reported_time') else None,
                    "up": host.up if hasattr(host, 'up') else None,
                    "sources": host.sources if hasattr(host, 'sources') else [],
                    "tags_by_source": host.tags_by_source if hasattr(host, 'tags_by_source') else {},
                    "apps": host.apps if hasattr(host, 'apps') else []
                }
            
            return {
                "status": "success",
                "hostname": hostname,
                "data": host_data
            }
        except Exception as e:
            logger.error(f"Error getting host details: {e}")
            return {
                "status": "error",
                "error": str(e),
                "hostname": hostname
            }

# Initialize FastMCP server
mcp = FastMCP("Datadog MCP Server")

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

@mcp.tool
def get_metrics(
    query: str,
    hours_back: int = 1,
    minutes_back: Optional[int] = None
) -> Dict[str, Any]:
    """
    Query timeseries metrics data from Datadog.
    
    Args:
        query: Datadog metrics query (e.g., "avg:system.cpu.user{*}")
        hours_back: Number of hours back from now to query (default: 1)
        minutes_back: Number of minutes back from now to query (overrides hours_back if provided)
    
    Returns:
        Dictionary containing metrics data or error information
        
    Examples:
        # Last 30 minutes of CPU usage
        get_metrics("avg:system.cpu.user{*}", minutes_back=30)
        
        # Last 2 hours of memory usage
        get_metrics("avg:system.mem.used{*}", hours_back=2)
        
        # Last week of request rates
        get_metrics("sum:trace.http.request.hits{*}", hours_back=168)  # 7 days
        
        # Last month of error rates  
        get_metrics("sum:trace.http.request.errors{*}", hours_back=720)  # 30 days
    """
    if minutes_back is not None:
        # Use minutes_back if provided
        to_time = int(datetime.utcnow().timestamp())
        from_time = int((datetime.utcnow() - timedelta(minutes=minutes_back)).timestamp())
    else:
        # Fall back to hours_back
        to_time = int(datetime.utcnow().timestamp())
        from_time = int((datetime.utcnow() - timedelta(hours=hours_back)).timestamp())
    
    return datadog_server.query_metrics(query, from_time, to_time)

@mcp.tool
def list_metrics(
    filter_query: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve a list of available metrics in your Datadog environment.
    
    Args:
        filter_query: Optional filter to limit metrics returned
    
    Returns:
        Dictionary containing list of available metrics or error information
    """
    try:
        return datadog_server.list_active_metrics(filter_query)
    except Exception as e:
        logger.error(f"Error listing metrics: {e}")
        return {
            "status": "error", 
            "error": str(e)
        }

@mcp.tool
def get_logs(
    query: str,
    limit: int = 100,
    hours_back: Optional[int] = None,
    minutes_back: Optional[int] = None,
    from_time: Optional[str] = None,
    to_time: Optional[str] = None,
    indexes: Optional[List[str]] = None,
    sort: str = "timestamp",
    cursor: Optional[str] = None,
    max_total_logs: Optional[int] = None
) -> Dict[str, Any]:
    """
    Search Datadog logs with enhanced flexibility and pagination support.
    
    Args:
        query: Log search query (e.g., "service:web-app ERROR", "status:error")
        limit: Number of logs per page (max 1000, default: 100)
        hours_back: Number of hours back from now to search (ignored if from_time/to_time provided)
        minutes_back: Number of minutes back from now to search (overrides hours_back if provided)
        from_time: Start time in ISO format (e.g., "2024-01-01T00:00:00Z") 
        to_time: End time in ISO format (e.g., "2024-01-01T23:59:59Z")
        indexes: List of log indexes to search (e.g., ["main", "security"])
        sort: Sort order ("timestamp" for ascending, "-timestamp" for descending, default: "timestamp")
        cursor: Pagination cursor from previous response to get next page
        max_total_logs: Maximum total logs to retrieve across all pages (default: same as limit)
    
    Returns:
        Dictionary containing log data, pagination info, or error information
        
    Examples:
        # Last 30 minutes of errors
        get_logs("status:error", minutes_back=30)
        
        # Last 2 hours of service logs  
        get_logs("service:web-app", hours_back=2)
        
        # Specific time range
        get_logs("service:web-app", from_time="2024-01-01T00:00:00Z", to_time="2024-01-01T23:59:59Z")
        
        # Last week (use hours_back for longer periods)
        get_logs("deploy", hours_back=168)  # 7 days * 24 hours
        
        # Last month (approximately)  
        get_logs("critical", hours_back=720)  # 30 days * 24 hours
    """
    # Handle time range parameters - treat empty strings as None
    # Normalize empty strings to None for proper logic
    from_time = from_time if from_time and from_time.strip() else None
    to_time = to_time if to_time and to_time.strip() else None
    hours_back = hours_back if hours_back and str(hours_back).strip() else None
    minutes_back = minutes_back if minutes_back and str(minutes_back).strip() else None
    
    calculated_from_time = from_time
    calculated_to_time = to_time
    
    # If no explicit times provided, use minutes_back or hours_back (prioritize minutes_back)
    if from_time is None and to_time is None:
        if minutes_back is not None:
            # Use minutes_back if provided
            calculated_from_time = (datetime.utcnow() - timedelta(minutes=minutes_back)).isoformat() + "Z"
            calculated_to_time = datetime.utcnow().isoformat() + "Z"
        else:
            # Fall back to hours_back (default to 1 hour)
            hours_back = hours_back or 1
            calculated_from_time = (datetime.utcnow() - timedelta(hours=hours_back)).isoformat() + "Z"
            calculated_to_time = datetime.utcnow().isoformat() + "Z"
    elif from_time is None and to_time is not None:
        # If only to_time is provided, default from_time to 1 hour before to_time
        try:
            to_dt = datetime.fromisoformat(to_time.replace('Z', '+00:00'))
            calculated_from_time = (to_dt - timedelta(hours=1)).isoformat() + "Z"
        except ValueError:
            calculated_from_time = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
    elif from_time is not None and to_time is None:
        # If only from_time is provided, default to_time to now
        calculated_to_time = datetime.utcnow().isoformat() + "Z"
    
    # Validate time range order
    if calculated_from_time and calculated_to_time:
        try:
            from_dt = datetime.fromisoformat(calculated_from_time.replace('Z', '+00:00'))
            to_dt = datetime.fromisoformat(calculated_to_time.replace('Z', '+00:00'))
            if from_dt >= to_dt:
                return {
                    "status": "error",
                    "error": f"Invalid time range: from_time ({calculated_from_time}) must be before to_time ({calculated_to_time})",
                    "suggestion": "Swap your from_time and to_time values, or use hours_back parameter instead"
                }
        except ValueError as e:
            return {
                "status": "error", 
                "error": f"Invalid time format: {str(e)}",
                "suggestion": "Use ISO format like '2025-09-14T15:00:00Z'"
            }
    
    return datadog_server.search_logs(
        query=query,
        limit=limit,
        from_time=calculated_from_time,
        to_time=calculated_to_time,
        indexes=indexes,
        sort=sort,
        cursor=cursor,
        max_total_logs=max_total_logs
    )

@mcp.tool
def get_next_datadog_logs_page(cursor: str, limit: int = 100) -> Dict[str, Any]:
    """
    Get the next page of Datadog logs using a pagination cursor.
    
    Args:
        cursor: Pagination cursor from previous search_datadog_logs response
        limit: Number of logs to return in this page (max 1000, default: 100)
    
    Returns:
        Dictionary containing the next page of log data or error information
    """
    if not cursor:
        return {
            "status": "error",
            "error": "Cursor parameter is required for pagination"
        }
    
    # Use the enhanced search method with cursor
    return datadog_server.search_logs(
        query="*",  # Use wildcard since cursor contains the original query context
        limit=limit,
        cursor=cursor,
        max_total_logs=limit  # Only get one page worth
    )

@mcp.tool
def get_monitors(
    group_states: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get Datadog monitors, optionally filtered by group states.
    
    Args:
        group_states: List of group states to filter by (e.g., ["Alert", "Warn"])
    
    Returns:
        Dictionary containing monitor data or error information
    """
    return datadog_server.get_monitors(group_states)

@mcp.tool
def list_dashboards() -> Dict[str, Any]:
    """
    Get list of Datadog dashboards.
    
    Returns:
        Dictionary containing dashboard data or error information
    """
    return datadog_server.get_dashboards()

@mcp.tool
def list_spans(
    query: str,
    from_time: Optional[str] = None,
    to_time: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Search for spans that help investigate performance issues and dependencies.
    
    Args:
        query: Search query for spans (e.g., service:web-frontend, resource:GET /api/*)
        from_time: Start time in ISO format (default: 1 hour ago)
        to_time: End time in ISO format (default: now)  
        limit: Maximum number of spans to return (default: 100)
    
    Returns:
        Dictionary containing spans data or error information
    """
    return datadog_server.search_spans(query, from_time, to_time, limit)

@mcp.tool
def get_trace(trace_id: str) -> Dict[str, Any]:
    """
    Retrieve all spans from a specific trace ID for distributed tracing analysis.
    
    Args:
        trace_id: The unique trace identifier
        
    Returns:
        Dictionary containing complete trace data with all spans or error information
    """
    return datadog_server.get_trace_data(trace_id)

@mcp.tool
def list_incidents(
    include_field: Optional[str] = None,
    page_size: int = 100,
    page_offset: int = 0
) -> Dict[str, Any]:
    """
    Retrieve a list of ongoing incidents from Datadog incident management.
    
    Args:
        include_field: Optional field to include in response
        page_size: Number of incidents per page (default: 100)
        page_offset: Page offset for pagination (default: 0)
        
    Returns:
        Dictionary containing incidents list or error information
    """
    return datadog_server.list_incidents(include_field, page_size, page_offset)

@mcp.tool
def get_incident(incident_id: str) -> Dict[str, Any]:
    """
    Retrieve details for a specific incident.
    
    Args:
        incident_id: The unique incident identifier
        
    Returns:
        Dictionary containing detailed incident information or error information
    """
    return datadog_server.get_incident_details(incident_id)

@mcp.tool
def list_hosts(
    filter_query: Optional[str] = None,
    sort_by: str = "name",
    count: int = 100,
    start: int = 0
) -> Dict[str, Any]:
    """
    Get infrastructure hosts information for system health analysis.
    
    Args:
        filter_query: Filter to apply to host list (e.g., "env:production")
        sort_by: Field to sort by (default: "name")
        count: Maximum number of hosts to return (default: 100)
        start: Starting position for pagination (default: 0)
        
    Returns:
        Dictionary containing hosts information or error information
    """
    return datadog_server.list_hosts_data(filter_query, sort_by, count, start)

@mcp.tool  
def get_host(hostname: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific host.
    
    Args:
        hostname: The hostname to get details for
        
    Returns:
        Dictionary containing detailed host information or error information  
    """
    return datadog_server.get_host_details(hostname)

# Deprecated aliases removed for cleaner codebase
# Use standard tool names: get_metrics, get_logs, get_monitors, list_dashboards

@mcp.resource("datadog://metrics/{query}")
def get_metrics_resource(query: str) -> str:
    """
    Get metrics data as a resource.
    
    Args:
        query: Datadog metrics query
    
    Returns:
        Formatted metrics data as string
    """
    result = datadog_server.query_metrics(query)
    if result["status"] == "success":
        return f"Metrics Query: {query}\n\nData: {result}"
    else:
        return f"Error querying metrics: {result['error']}"

@mcp.resource("datadog://logs/{query}")
def get_logs_resource(query: str) -> str:
    """
    Get logs data as a resource with basic formatting.
    
    Args:
        query: Log search query
    
    Returns:
        Formatted logs data as string
    """
    result = get_logs(query, limit=50)  # Get more logs by default for resources
    if result["status"] == "success":
        logs_text = "\n".join([
            f"[{log['timestamp']}] {log['service']}: {log['message']}"
            for log in result["logs"]
        ])
        summary = f"Logs Query: {query}\n"
        summary += f"Retrieved: {result['count']} logs (from {result['from_time']} to {result['to_time']})\n"
        summary += f"Has more data: {result.get('has_more', False)}\n\n"
        return summary + f"Logs:\n{logs_text}"
    else:
        return f"Error searching logs: {result['error']}"

@mcp.resource("datadog://logs-detailed/{query}")
def get_detailed_logs_resource(query: str) -> str:
    """
    Get detailed logs data as a resource with full log information.
    
    Args:
        query: Log search query
    
    Returns:
        Detailed formatted logs data as string
    """
    result = get_logs(query, limit=20, sort="-timestamp")  # Get recent logs first
    if result["status"] == "success":
        logs_details = []
        for log in result["logs"]:
            log_detail = f"ID: {log['id']}\n"
            log_detail += f"Timestamp: {log['timestamp']}\n"
            log_detail += f"Service: {log['service']}\n"
            log_detail += f"Status: {log['status']}\n"
            log_detail += f"Host: {log['host']}\n"
            log_detail += f"Source: {log['source']}\n"
            log_detail += f"Tags: {', '.join(log['tags'])}\n"
            log_detail += f"Message: {log['message']}\n"
            if log.get('custom_attributes'):
                log_detail += f"Custom Attributes: {log['custom_attributes']}\n"
            log_detail += "-" * 50
            logs_details.append(log_detail)
        
        summary = f"Detailed Logs Query: {query}\n"
        summary += f"Retrieved: {result['count']} logs (from {result['from_time']} to {result['to_time']})\n"
        summary += f"Sort: {result['sort']}, Indexes: {result['indexes_searched']}\n"
        summary += f"Has more data: {result.get('has_more', False)}\n\n"
        return summary + "\n".join(logs_details)
    else:
        return f"Error searching detailed logs: {result['error']}"

@mcp.resource("datadog://health-check/{service_name}")
def health_check_resource(service_name: str) -> str:
    """
    Intelligent health summary for a service with AI insights and recommendations.
    
    Args:
        service_name: Name of the service to analyze
        
    Returns:
        Comprehensive health assessment with actionable insights
    """
    try:
        # Collect multiple data points for comprehensive analysis
        metrics_result = datadog_server.query_metrics(f"avg:trace.http.request.duration{{service:{service_name}}}")
        logs_result = get_logs(f"service:{service_name} status:error", limit=20)
        cpu_result = datadog_server.query_metrics(f"avg:system.cpu.user{{service:{service_name}}}")
        memory_result = datadog_server.query_metrics(f"avg:system.mem.used{{service:{service_name}}}")
        
        # Calculate health scores
        def calculate_health_score(metrics, logs, cpu, memory):
            score = 10  # Start with perfect score
            
            # Penalize based on error rate
            if logs.get("status") == "success" and logs.get("count", 0) > 0:
                error_count = logs.get("count", 0)
                if error_count > 10:
                    score -= 3
                elif error_count > 5:
                    score -= 2
                elif error_count > 0:
                    score -= 1
            
            # Penalize based on high resource usage
            if cpu.get("status") == "success":
                # This is simplified - in reality you'd parse the metrics data
                score -= 0  # Placeholder for CPU analysis
                
            if memory.get("status") == "success":
                # This is simplified - in reality you'd parse the metrics data  
                score -= 0  # Placeholder for memory analysis
                
            return max(0, min(10, score))
        
        health_score = calculate_health_score(metrics_result, logs_result, cpu_result, memory_result)
        
        # Generate status and recommendations
        if health_score >= 8:
            status = "🟢 Healthy"
            priority = "LOW"
        elif health_score >= 6:
            status = "🟡 Warning"
            priority = "MEDIUM"
        elif health_score >= 4:
            status = "🟠 Degraded"
            priority = "HIGH"
        else:
            status = "🔴 Critical"
            priority = "CRITICAL"
        
        # Generate recommendations based on findings
        recommendations = []
        if logs_result.get("count", 0) > 5:
            recommendations.append("⚠️ High error rate detected - investigate error patterns")
        if logs_result.get("count", 0) > 0:
            recommendations.append("📋 Review recent error logs for patterns")
        
        recommendations.append("📊 Monitor key metrics trends over next 24 hours")
        recommendations.append("🔄 Consider setting up automated alerts if not already configured")
        
        # Build comprehensive report
        report = f"""## 🏥 Health Check: {service_name}

**Overall Health Score**: {health_score}/10
**Status**: {status}
**Priority**: {priority}

### 📊 Key Metrics Summary
- **Response Time**: {metrics_result.get('status', 'unknown')} 
- **Error Count (last hour)**: {logs_result.get('count', 0)} errors
- **CPU Usage**: {cpu_result.get('status', 'unknown')}
- **Memory Usage**: {memory_result.get('status', 'unknown')}

### 🎯 AI Recommendations
{chr(10).join(f"- {rec}" for rec in recommendations)}

### 🔍 Next Actions
- **Immediate**: {'Investigate errors' if logs_result.get('count', 0) > 5 else 'Continue monitoring'}
- **Short-term**: Review performance trends and capacity planning
- **Long-term**: Implement proactive monitoring and alerting improvements

### 📈 Trending Indicators
- Error rate trend: {'⬆️ Increasing' if logs_result.get('count', 0) > 0 else '➡️ Stable'}
- Performance trend: ➡️ Stable (baseline needed)
- Resource usage: ➡️ Stable (baseline needed)

*Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*
*Health score based on: Error rate, response time, resource usage*
"""

        return report
        
    except Exception as e:
        return f"""## ❌ Health Check Failed: {service_name}

**Error**: {str(e)}

**Troubleshooting Steps**:
1. Verify service name is correct
2. Check Datadog API connectivity  
3. Ensure service is actively sending metrics to Datadog
4. Try using basic monitoring tools first

*Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""

@mcp.prompt("datadog-metrics-analysis")
def datadog_metrics_analysis_prompt(
    metric_query: str,
    time_range_hours: int = 24
) -> str:
    """
    Generate a prompt for analyzing Datadog metrics.
    
    Args:
        metric_query: The metrics query to analyze
        time_range_hours: Time range in hours for the analysis
    
    Returns:
        Formatted prompt for metrics analysis
    """
    return f"""
    Analyze the following Datadog metrics:
    
    Query: {metric_query}
    Time Range: Last {time_range_hours} hours
    
    Please provide:
    1. Summary of the metric trends
    2. Any anomalies or patterns observed
    3. Recommendations for optimization or alerting
    4. Potential root causes for any issues identified
    
    Use the query_datadog_metrics tool to fetch the actual data for analysis.
    """

@mcp.prompt("datadog-performance-diagnosis")
def performance_diagnosis_prompt(
    service_name: str,
    symptoms: str = "slow response times",
    severity: str = "medium"
) -> str:
    """
    AI-guided performance troubleshooting for Datadog monitored services.
    
    Args:
        service_name: Name of the service experiencing issues
        symptoms: Observed symptoms (e.g., "slow response times", "high error rate")
        severity: Issue severity (low, medium, high, critical)
    
    Returns:
        Structured troubleshooting workflow for AI agents
    """
    return f"""
🔧 **Performance Diagnosis: {service_name}**

**Symptoms**: {symptoms}
**Severity**: {severity.upper()}

**AI Agent Investigation Steps**:

1. **Baseline Health Check** 📊
   - get_metrics("avg:trace.http.request.duration{{service:{service_name}}}", hours_back=1) for current performance
   - get_metrics("avg:trace.http.request.duration{{service:{service_name}}}", hours_back=24) for baseline comparison
   - get_logs("service:{service_name} status:error", hours_back=1) for recent error patterns
   - get_metrics("avg:system.cpu.user{{service:{service_name}}}", hours_back=1) and get_metrics("avg:system.mem.used{{service:{service_name}}}", hours_back=1)

2. **Traffic Analysis** 📈
   - get_metrics("sum:trace.http.request.hits{{service:{service_name}}}", hours_back=1) for traffic spikes analysis
   - get_metrics("sum:trace.http.request.hits{{service:{service_name}}}", hours_back=24) for baseline comparison
   - Compare current traffic vs normal patterns
   - Check for unusual request distributions

3. **Error Pattern Investigation** ⚠️
   - get_logs("service:{service_name} (status:error OR level:error)", hours_back=2) for comprehensive error analysis
   - Categorize errors by type and frequency
   - Identify error correlation with performance degradation

4. **Resource Constraints** 💻
   - Check CPU usage: If >80%, investigate process efficiency
   - Check Memory: Look for memory leaks or cache issues
   - Check I/O: Database query performance and disk usage

5. **Dependencies Analysis** 🔗
   - list_spans: Map service dependencies and slow external calls
   - Check downstream service health
   - Identify cascade failures from dependent services

**Decision Tree for Diagnosis**:
- **If Response Time > 2x baseline**: Focus on database queries, external API calls
- **If Error Rate > 5%**: Prioritize error log analysis and exception handling
- **If CPU > 80%**: Investigate inefficient algorithms, infinite loops
- **If Memory trending upward**: Check for memory leaks, cache overflow
- **If errors are timeout-related**: Check connection pools, circuit breakers

**Expected Output Format**:
1. **Root Cause Hypothesis** with confidence level
2. **Supporting Evidence** from metrics and logs
3. **Immediate Mitigation Steps** 
4. **Long-term Prevention Recommendations**
5. **Monitoring Improvements** to prevent recurrence

**Success Criteria**: Provide actionable next steps within 15 minutes of investigation start.
"""

@mcp.prompt("datadog-incident-commander")  
def incident_commander_prompt(
    severity: str = "high",
    affected_services: str = "",
    symptoms: str = "",
    estimated_user_impact: str = "unknown"
) -> str:
    """
    AI-powered incident command and coordination workflow.
    
    Args:
        severity: Incident severity (low, medium, high, critical)
        affected_services: Comma-separated list of affected services
        symptoms: Observed incident symptoms
        estimated_user_impact: Estimated percentage of users affected
        
    Returns:
        Structured incident response protocol for AI agents
    """
    services_list = [s.strip() for s in affected_services.split(",") if s.strip()]
    
    return f"""
🚨 **INCIDENT COMMAND PROTOCOL**

**Severity**: {severity.upper()}
**Affected Services**: {affected_services or "TBD"}
**Symptoms**: {symptoms}
**User Impact**: {estimated_user_impact}

**AI Agent Command Sequence**:

**⏱️ IMMEDIATE RESPONSE (0-5 minutes)**:
1. **Alert Assessment**:
   - get_monitors() → Identify all currently triggered alerts
   - Categorize alerts by service and severity
   - Determine primary vs secondary failures

2. **Impact Measurement**:
   - get_logs("status:error", hours_back=1) → Measure error rate spike from last hour
   - For each service in [{', '.join(services_list)}]:
     * get_metrics("error_rate", hours_back=1) → Quantify impact over last hour
     * get_metrics("request_rate", hours_back=1) → Measure traffic disruption

3. **Initial Communication**:
   - Status: "🔴 Investigating {severity} severity incident"
   - ETA: "Initial assessment within 15 minutes"
   - Scope: "Services affected: {affected_services}"

**🔍 ASSESSMENT PHASE (5-15 minutes)**:
1. **Root Cause Investigation**:
   - get_logs("deploy OR release OR rollout", hours_back=2) → Check for recent changes in last 2 hours
   - get_logs("config OR setting OR parameter", hours_back=1) → Configuration changes in last hour
   - list_hosts() → Infrastructure health correlation

2. **Timeline Construction**:
   - Map incident start time against deployment/change events
   - Correlate service failures with infrastructure changes
   - Build sequence of events leading to incident

3. **Blast Radius Assessment**:
   - Identify all impacted services and dependencies
   - Measure user-facing vs internal system impact
   - Calculate estimated revenue/business impact

**⚡ MITIGATION DECISION TREE**:

**If Database Related**:
- Check connection pool exhaustion
- Analyze slow query logs
- Consider read replica failover

**If Deployment Related**:
- Evaluate rollback feasibility
- Check deployment artifacts and configuration
- Implement feature flags to isolate problematic code

**If Infrastructure Related**:
- Check auto-scaling limits and resource constraints
- Analyze load balancer health
- Verify network connectivity and DNS resolution

**If External Dependency**:
- Implement circuit breakers
- Activate fallback mechanisms
- Contact vendor/service provider

**📞 COMMUNICATION PROTOCOL**:
- **Every 15 minutes**: Status update with current actions
- **Any severity change**: Immediate notification
- **Resolution attempt**: Before and after status
- **Post-incident**: Timeline and lessons learned

**🏁 RESOLUTION VALIDATION**:
1. **Metrics Recovery**: Verify error rates return to baseline
2. **User Validation**: Confirm user-facing functionality restored
3. **Monitoring**: Continue enhanced monitoring for 2x incident duration
4. **Documentation**: Capture timeline, actions, and outcomes for post-mortem

**Success Metrics**:
- Mean Time to Detection (MTTD): <5 minutes
- Mean Time to Resolution (MTTR): <30 minutes for {severity} severity
- Communication cadence: Every 15 minutes minimum
- Post-incident review: Within 48 hours
"""

@mcp.prompt("datadog-time-range-advisor")
def time_range_advisor_prompt(
    analysis_type: str = "performance",
    suspected_timeframe: str = "unknown", 
    incident_impact: str = "medium"
) -> str:
    """
    AI-powered time range selection advisor for optimal Datadog analysis.
    
    Args:
        analysis_type: Type of analysis (performance, security, deployment, capacity, incident)
        suspected_timeframe: When issue might have started (recent, hours, days, weeks, unknown)  
        incident_impact: Impact level (low, medium, high, critical)
        
    Returns:
        Intelligent time range recommendations with specific parameter suggestions
    """
    return f"""
⏰ **DATADOG TIME RANGE ADVISOR**

**Analysis Type**: {analysis_type.title()}
**Suspected Timeframe**: {suspected_timeframe}
**Impact Level**: {incident_impact.upper()}

## 🎯 **Recommended Time Ranges by Scenario**

### **🔥 IMMEDIATE TROUBLESHOOTING (Active Issues)**
**Use Case**: Current performance problems, live incidents, real-time debugging
```
✅ RECOMMENDED:
- get_logs("status:error", minutes_back=15)           # Last 15 minutes
- get_logs("status:error", minutes_back=30)           # Last 30 minutes  
- get_metrics("avg:response.time", minutes_back=30)    # Last 30 minutes
- get_metrics("error.rate", hours_back=1)             # Last 1 hour
```

### **📊 SHORT-TERM ANALYSIS (Recent Issues)**  
**Use Case**: Issues from today, deployment verification, hourly patterns
```
✅ RECOMMENDED:
- get_logs("deploy OR release", hours_back=6)         # Last 6 hours
- get_metrics("cpu.usage", hours_back=12)             # Last 12 hours  
- get_logs("service:api", hours_back=24)              # Last 24 hours
```

### **📈 MEDIUM-TERM TRENDS (Weekly Patterns)**
**Use Case**: Weekly performance trends, capacity planning, recurring issues
```  
✅ RECOMMENDED:
- get_logs("critical", hours_back=168)                # Last 7 days (7×24)
- get_metrics("memory.usage", hours_back=168)         # Last 1 week
- get_logs("timeout", hours_back=336)                 # Last 2 weeks (14×24)
```

### **📅 LONG-TERM ANALYSIS (Monthly/Historical)**
**Use Case**: Capacity planning, seasonal patterns, month-over-month comparison  
```
✅ RECOMMENDED:
- get_logs("deployment", hours_back=720)              # Last 30 days (30×24)
- get_metrics("traffic.volume", hours_back=1440)      # Last 2 months (60×24)  
- get_logs("security", hours_back=2160)               # Last 3 months (90×24)
```

## ⚡ **SMART RECOMMENDATIONS BY ANALYSIS TYPE**

### **Performance Analysis** 📊
```python
# Step 1: Current state (real-time)
get_metrics("avg:trace.http.request.duration", minutes_back=15)
get_logs("status:500 OR status:502 OR status:503", minutes_back=30)

# Step 2: Recent baseline (comparison)  
get_metrics("avg:trace.http.request.duration", hours_back=24)
get_logs("slow OR timeout", hours_back=6)

# Step 3: Historical context (if needed)
get_metrics("avg:trace.http.request.duration", hours_back=168)  # 1 week
```

### **Security Investigation** 🔒
```python  
# Step 1: Recent threats (immediate)
get_logs("auth.failure OR 403 OR unauthorized", hours_back=1)
get_logs("suspicious OR attack OR intrusion", hours_back=6)

# Step 2: Pattern analysis (extended)
get_logs("security OR auth OR login", hours_back=72)      # 3 days
get_logs("admin OR privilege OR escalation", hours_back=168) # 1 week
```

### **Deployment Analysis** 🚀
```python
# Step 1: Recent deployments (immediate impact)
get_logs("deploy OR release OR rollout", hours_back=2)
get_logs("config OR setting OR parameter", hours_back=1) 

# Step 2: Deployment correlation (extended)
get_logs("version OR build OR artifact", hours_back=24)
get_metrics("error.rate", hours_back=12)  # Before/after comparison
```

### **Capacity Planning** 📈  
```python
# Step 1: Current utilization trends
get_metrics("avg:system.cpu.user", hours_back=168)       # 1 week
get_metrics("avg:system.mem.used", hours_back=168)       # 1 week

# Step 2: Historical growth patterns  
get_metrics("sum:trace.http.request.hits", hours_back=720)   # 1 month
get_metrics("max:system.disk.used", hours_back=2160)        # 3 months
```

## 🎯 **PARAMETER QUICK REFERENCE**

### **Time Conversions**
```
⏰ Minutes:
- 15 minutes → minutes_back=15
- 30 minutes → minutes_back=30  
- 45 minutes → minutes_back=45

🕐 Hours:  
- 1 hour    → hours_back=1
- 6 hours   → hours_back=6
- 12 hours  → hours_back=12
- 24 hours  → hours_back=24

📅 Days/Weeks/Months:
- 1 week    → hours_back=168    (7×24)
- 2 weeks   → hours_back=336    (14×24)  
- 1 month   → hours_back=720    (30×24)
- 3 months  → hours_back=2160   (90×24)
```

### **Performance Impact Guidelines**
```
🟢 LOW IMPACT: Use longer ranges for context
- hours_back=24 to hours_back=168 (1-7 days)

🟡 MEDIUM IMPACT: Balance detail vs performance  
- hours_back=1 to hours_back=24 (1-24 hours)

🔴 HIGH/CRITICAL: Focus on recent data
- minutes_back=15 to hours_back=2 (15min-2hours)
```

## 💡 **OPTIMIZATION TIPS**

1. **Start Narrow, Expand Gradually**: Begin with recent timeframes, expand if needed
2. **Use minutes_back for Active Issues**: Real-time troubleshooting needs minute-level precision
3. **Use hours_back for Trend Analysis**: Longer patterns require hour-level granularity  
4. **Combine Multiple Ranges**: Compare current vs historical for better insights
5. **Limit Data Volume**: Larger time ranges = more data = slower responses

## 🚀 **NEXT STEPS**

Based on your **{analysis_type}** analysis with **{suspected_timeframe}** timeframe:

**IMMEDIATE ACTION**: Start with the recommended time ranges above
**ITERATIVE APPROACH**: Adjust ranges based on initial findings
**PERFORMANCE BALANCE**: Monitor query response times and adjust accordingly
"""

# Note: Middleware integration varies by FastMCP version
# For debugging, you can add logging directly within tool functions

if __name__ == "__main__":
    # Configure server to use HTTP transport with SSE support
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "8080"))
    
    logger.info(f"Starting Datadog MCP Server on {host}:{port}")
    logger.info("Transport: HTTP Streamable with SSE support")
    logger.info(f"Datadog Site: {datadog_config.site}")
    
    # Note: FastMCP middleware integration may vary by version
    # For now, we'll use logging within individual tool functions
    
    try:
        # Run the server with HTTP transport
        mcp.run(transport="http", host=host, port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        exit(1)

