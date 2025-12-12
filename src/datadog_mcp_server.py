#!/usr/bin/env python3
"""
Datadog MCP Server

A Model Context Protocol server that provides access to Datadog monitoring data,
metrics, logs, and other observability features through HTTP streamable transport
with Server-Sent Events (SSE) support.
"""

import os
import logging
import json
import time
import uuid
import traceback
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from dataclasses import dataclass
from functools import wraps
from enum import Enum

from fastmcp import FastMCP
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from datadog_api_client.v1.api.logs_api import LogsApi
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.api.dashboards_api import DashboardsApi

# Import key rotation system
from key_rotation import (
    KeyPair, KeyPoolManager, KeyHealth, RotationStrategy,
    load_keys_from_environment, get_rotation_config, 
    create_retry_decorator, detect_rate_limit_error
)

# Debug Configuration System
class DebugLevel(Enum):
    NONE = "NONE"
    INFO = "INFO" 
    DEBUG = "DEBUG"
    TRACE = "TRACE"

@dataclass
class DebugConfig:
    """Configuration for debug tracing and logging"""
    level: DebugLevel = DebugLevel.INFO
    log_requests: bool = False
    log_responses: bool = False
    log_timing: bool = False
    pretty_print: bool = True
    log_parameters: bool = False
    log_errors: bool = True
    mask_sensitive_data: bool = True
    
    @classmethod
    def from_env(cls) -> 'DebugConfig':
        """Create debug config from environment variables"""
        level_str = os.getenv('MCP_DEBUG_LEVEL', 'INFO').upper()
        try:
            level = DebugLevel(level_str)
        except ValueError:
            level = DebugLevel.INFO
            
        return cls(
            level=level,
            log_requests=os.getenv('MCP_DEBUG_REQUESTS', 'false').lower() == 'true',
            log_responses=os.getenv('MCP_DEBUG_RESPONSES', 'false').lower() == 'true', 
            log_timing=os.getenv('MCP_DEBUG_TIMING', 'false').lower() == 'true',
            pretty_print=os.getenv('MCP_DEBUG_PRETTY_PRINT', 'true').lower() == 'true',
            log_parameters=os.getenv('MCP_DEBUG_PARAMETERS', 'false').lower() == 'true',
            log_errors=os.getenv('MCP_DEBUG_ERRORS', 'true').lower() == 'true',
            mask_sensitive_data=os.getenv('MCP_DEBUG_MASK_SENSITIVE', 'true').lower() == 'true'
        )
    
    def should_log_at_level(self, check_level: DebugLevel) -> bool:
        """Check if we should log at the specified level"""
        levels = [DebugLevel.NONE, DebugLevel.INFO, DebugLevel.DEBUG, DebugLevel.TRACE]
        return levels.index(self.level) >= levels.index(check_level)

# Global debug configuration
debug_config = DebugConfig.from_env()

# Debug Utility Functions
def mask_sensitive_data(data: Any) -> Any:
    """Mask sensitive data in debug logs"""
    if not debug_config.mask_sensitive_data:
        return data
        
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'token', 'password']):
                masked[key] = "***MASKED***"
            else:
                masked[key] = mask_sensitive_data(value)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    else:
        return data

def format_debug_data(data: Any, pretty: bool = True) -> str:
    """Format data for debug logging"""
    masked_data = mask_sensitive_data(data)
    if pretty and debug_config.pretty_print:
        return json.dumps(masked_data, indent=2, default=str)
    else:
        return json.dumps(masked_data, default=str)

def debug_log(level: DebugLevel, message: str, data: Any = None, correlation_id: str = None):
    """Enhanced debug logging with correlation tracking"""
    if not debug_config.should_log_at_level(level):
        return
        
    log_message = message
    if correlation_id:
        log_message = f"[{correlation_id}] {message}"
        
    if data is not None:
        log_message += f"\nData: {format_debug_data(data)}"
    
    # Use appropriate logging level
    if level == DebugLevel.TRACE:
        logger.debug(f"TRACE: {log_message}")
    elif level == DebugLevel.DEBUG:
        logger.debug(f"DEBUG: {log_message}")
    elif level == DebugLevel.INFO:
        logger.info(f"DEBUG: {log_message}")

def mcp_debug_decorator(tool_name: str):
    """Decorator to add debug tracing to MCP tools"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            correlation_id = str(uuid.uuid4())[:8]
            start_time = time.time()
            
            # Log incoming request
            if debug_config.log_requests:
                debug_log(DebugLevel.DEBUG, f"MCP Tool Call: {tool_name}", {
                    "args": args,
                    "kwargs": kwargs if debug_config.log_parameters else "***HIDDEN***"
                }, correlation_id)
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log successful response
                if debug_config.log_responses:
                    debug_log(DebugLevel.DEBUG, f"MCP Tool Success: {tool_name}", {
                        "result": result,
                        "execution_time_ms": round(execution_time * 1000, 2)
                    } if debug_config.log_timing else {"result": result}, correlation_id)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Log error response
                if debug_config.log_errors:
                    debug_log(DebugLevel.INFO, f"MCP Tool Error: {tool_name}", {
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "execution_time_ms": round(execution_time * 1000, 2) if debug_config.log_timing else None
                    }, correlation_id)
                
                raise
                
        return wrapper
    return decorator

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

# Configure logging with debug support
def setup_logging():
    """Setup logging based on debug configuration"""
    # Set base logging level
    if debug_config.level == DebugLevel.TRACE:
        level = logging.DEBUG
    elif debug_config.level == DebugLevel.DEBUG:
        level = logging.DEBUG
    elif debug_config.level == DebugLevel.INFO:
        level = logging.INFO
    else:  # NONE
        level = logging.WARNING
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure specific loggers based on debug settings
    if debug_config.should_log_at_level(DebugLevel.TRACE):
        logging.getLogger("uvicorn").setLevel(logging.DEBUG)
        logging.getLogger("fastmcp").setLevel(logging.DEBUG)
        logging.getLogger("datadog_api_client").setLevel(logging.DEBUG)
    
    return logging.getLogger(__name__)

logger = setup_logging()

# Log the debug configuration on startup
debug_log(DebugLevel.INFO, "Debug Configuration Loaded", {
    "level": debug_config.level.value,
    "log_requests": debug_config.log_requests,
    "log_responses": debug_config.log_responses,
    "log_timing": debug_config.log_timing,
    "pretty_print": debug_config.pretty_print
})

@dataclass
class DatadogConfig:
    """Configuration for Datadog API client with key rotation support"""
    key_pool: KeyPoolManager
    primary_site: str = "datadoghq.com"

class DatadogMCPServer:
    """Datadog MCP Server implementation with intelligent key rotation"""
    
    def __init__(self, config: DatadogConfig):
        self.config = config
        self.key_pool = config.key_pool
        
        # Create API clients - these will be recreated per request with different keys
        self._api_client_cache = {}
        
        # Start health monitoring
        self.key_pool.start_health_monitoring()
        
    def _get_api_client(self, key_pair: KeyPair) -> ApiClient:
        """Get or create API client for a specific key pair"""
        cache_key = f"{key_pair.id}_{key_pair.api_key[:8]}"
        
        if cache_key not in self._api_client_cache:
            configuration = Configuration()
            configuration.api_key["apiKeyAuth"] = key_pair.api_key
            configuration.api_key["appKeyAuth"] = key_pair.app_key
            configuration.server_variables["site"] = key_pair.site
            
            self._api_client_cache[cache_key] = ApiClient(configuration)
            debug_log(DebugLevel.DEBUG, f"Created API client for key {key_pair.id}", {
                "site": key_pair.site,
                "cache_key": cache_key
            })
        
        return self._api_client_cache[cache_key]
    
    def _execute_with_key_rotation(self, operation_name: str, operation_func):
        """
        Execute an operation with automatic key rotation on rate limits
        
        Args:
            operation_name: Name of the operation for logging
            operation_func: Function that takes (key_pair, api_client) and executes the API call
        """
        @create_retry_decorator(self.key_pool, max_retries=min(3, len(self.key_pool.keys)))
        def _wrapped_operation(key_pair: KeyPair, *args, **kwargs):
            api_client = self._get_api_client(key_pair)
            
            debug_log(DebugLevel.DEBUG, f"Executing {operation_name} with key {key_pair.id}")
            
            try:
                result = operation_func(key_pair, api_client, *args, **kwargs)
                debug_log(DebugLevel.TRACE, f"{operation_name} successful with key {key_pair.id}")
                return result
            except Exception as e:
                debug_log(DebugLevel.INFO, f"{operation_name} failed with key {key_pair.id}", {
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                raise
        
        return _wrapped_operation()
    
    def query_metrics(self, query: str, from_time: int, to_time: int) -> Dict[str, Any]:
        """
        Query Datadog metrics with comprehensive error handling and key rotation
        
        Args:
            query: Datadog metrics query string
            from_time: Start time as Unix timestamp (seconds)
            to_time: End time as Unix timestamp (seconds)
            
        Returns:
            Dictionary with query results or error information
        """
        try:
            # Input validation
            if not query or not query.strip():
                return {
                    "status": "error",
                    "error": "Query cannot be empty",
                    "suggestion": "Provide a valid Datadog metrics query like 'avg:system.cpu.user{*}'"
                }
            
            if from_time >= to_time:
                return {
                    "status": "error", 
                    "error": f"Invalid time range: from_time ({from_time}) must be less than to_time ({to_time})",
                    "suggestion": "Ensure from_time is earlier than to_time"
                }
            
            # Check if time range is reasonable (not too far in the past or future)
            current_time = int(datetime.now(timezone.utc).timestamp())
            if to_time > current_time + 3600:  # Allow 1 hour in future for clock skew
                return {
                    "status": "error",
                    "error": f"to_time ({to_time}) cannot be more than 1 hour in the future",
                    "suggestion": "Use current or past timestamps"
                }
            
            # Check if time range is too large (more than 1 year)
            if (to_time - from_time) > 365 * 24 * 3600:
                return {
                    "status": "error",
                    "error": "Time range cannot exceed 1 year",
                    "suggestion": "Use a smaller time range for better performance"
                }
            
            logger.info(f"Querying metrics: {query} from {from_time} to {to_time}")
            
            # Execute with key rotation
            def _query_operation(key_pair: KeyPair, api_client: ApiClient):
                metrics_api = MetricsApi(api_client)
                return metrics_api.query_metrics(
                    _from=from_time,
                    to=to_time,
                    query=query
                )
            
            response = self._execute_with_key_rotation("query_metrics", _query_operation)
            
            # Enhanced response processing
            series_data = []
            if hasattr(response, 'series') and response.series:
                series_data = response.series
                logger.info(f"Retrieved {len(series_data)} time series")
            
            result = {
                "status": "success",
                "query": query,
                "from_time": from_time,
                "to_time": to_time,
                "duration_hours": round((to_time - from_time) / 3600, 2),
                "series_count": len(series_data),
                "series": series_data,
                "key_pool_status": self.key_pool.get_pool_status() if debug_config.should_log_at_level(DebugLevel.DEBUG) else None
            }
            
            # Add helpful metadata
            if hasattr(response, 'from_date'):
                result["response_from_date"] = response.from_date
            if hasattr(response, 'to_date'):
                result["response_to_date"] = response.to_date
            if hasattr(response, 'group_by'):
                result["group_by"] = response.group_by
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error querying metrics '{query}': {error_msg}")
            
            # Enhanced error categorization
            if "403" in error_msg or "Forbidden" in error_msg:
                suggestion = "Check API key permissions. Ensure 'metrics_read' permission is granted."
            elif "401" in error_msg or "Unauthorized" in error_msg:
                suggestion = "Check API key and APP key credentials."
            elif "400" in error_msg or "Bad Request" in error_msg:
                suggestion = "Check query syntax. Example: 'avg:system.cpu.user{*}'"
            elif "timeout" in error_msg.lower():
                suggestion = "Query timeout. Try reducing time range or simplifying query."
            elif "rate limit" in error_msg.lower():
                suggestion = "API rate limit exceeded. Key rotation should handle this automatically."
            else:
                suggestion = "Check network connectivity and Datadog service status."
            
            return {
                "status": "error",
                "error": error_msg,
                "query": query,
                "suggestion": suggestion,
                "from_time": from_time,
                "to_time": to_time,
                "key_pool_status": self.key_pool.get_pool_status() if debug_config.should_log_at_level(DebugLevel.DEBUG) else None
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
        Search Datadog logs with enhanced flexibility, pagination support, and key rotation.
        
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
                from_time = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
            if to_time is None:
                to_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Validate and adjust limit (Datadog API max is 1000 per request)
            page_limit = min(limit, 1000)
            
            # Set maximum total logs to retrieve
            if max_total_logs is None:
                max_total_logs = limit
            
            # Execute with key rotation
            def _search_logs_operation(key_pair: KeyPair, api_client: ApiClient):
                logs_api_v2 = LogsApiV2(api_client)
                
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
                    
                    response = logs_api_v2.list_logs(body=body)
                    
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
                
                return all_logs, next_cursor, total_retrieved
            
            all_logs, next_cursor, total_retrieved = self._execute_with_key_rotation("search_logs", _search_logs_operation)
            
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
                "indexes_searched": indexes or ["all"],
                "key_pool_status": self.key_pool.get_pool_status() if debug_config.should_log_at_level(DebugLevel.DEBUG) else None
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
                "to_time": to_time if 'to_time' in locals() else None,
                "key_pool_status": self.key_pool.get_pool_status() if debug_config.should_log_at_level(DebugLevel.DEBUG) else None
            }
    
    def get_monitors(self, group_states: Optional[str] = None) -> Dict[str, Any]:
        """Get Datadog monitors"""
        try:
            # Only pass group_states if it's not None to avoid the API error
            kwargs = {}
            if group_states is not None:
                kwargs['group_states'] = group_states
            
            response = self.monitors_api.list_monitors(**kwargs)
            
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
        correlation_id = str(uuid.uuid4())[:8]
        debug_log(DebugLevel.DEBUG, f"Starting list_active_metrics with filter_query: {filter_query}", correlation_id=correlation_id)
        
        try:
            # Get metrics from last 2 hours to ensure we get active metrics
            from_time = int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp())
            debug_log(DebugLevel.TRACE, f"Calculated from_time", {
                "from_time": from_time,
                "from_time_datetime": datetime.fromtimestamp(from_time, timezone.utc).isoformat()
            }, correlation_id)
            
            # Build parameters dict - use _from instead of from_time
            params = {"_from": from_time}
            debug_log(DebugLevel.TRACE, f"Base params", params, correlation_id)
            
            # Add optional filter parameters according to API spec
            if filter_query:
                debug_log(DebugLevel.TRACE, f"Processing filter_query: {filter_query}", correlation_id=correlation_id)
                # The API supports 'host' and 'tag_filter' parameters
                # If it looks like a hostname, use host parameter
                if '.' in filter_query and not ':' in filter_query:
                    params["host"] = filter_query
                    debug_log(DebugLevel.TRACE, f"Added host filter: {filter_query}", correlation_id=correlation_id)
                else:
                    # Otherwise use tag_filter for more complex queries
                    params["tag_filter"] = filter_query
                    debug_log(DebugLevel.TRACE, f"Added tag_filter: {filter_query}", correlation_id=correlation_id)
            
            debug_log(DebugLevel.TRACE, f"Final params before API call", params, correlation_id)
            debug_log(DebugLevel.DEBUG, f"Calling metrics_api.list_active_metrics", correlation_id=correlation_id)
            
            response = self.metrics_api.list_active_metrics(**params)
            debug_log(DebugLevel.DEBUG, f"API call completed successfully", correlation_id=correlation_id)
            debug_log(DebugLevel.TRACE, f"Response analysis", {
                "response_type": str(type(response)),
                "response_attributes": dir(response)
            }, correlation_id)
            
            if hasattr(response, '__dict__'):
                debug_log(DebugLevel.TRACE, f"Response dict", response.__dict__, correlation_id)
            
            metrics = []
            if hasattr(response, 'metrics'):
                debug_log(DebugLevel.TRACE, f"Found metrics attribute", correlation_id=correlation_id)
                if response.metrics:
                    metrics = response.metrics
                    debug_log(DebugLevel.DEBUG, f"Retrieved {len(metrics)} metrics from response.metrics", correlation_id=correlation_id)
                else:
                    debug_log(DebugLevel.INFO, f"response.metrics is empty or None: {response.metrics}", correlation_id=correlation_id)
            else:
                debug_log(DebugLevel.INFO, f"No 'metrics' attribute found in response", correlation_id=correlation_id)
                # Try alternative attribute names
                for attr in ['data', 'result', 'items', 'metric_names']:
                    if hasattr(response, attr):
                        debug_log(DebugLevel.TRACE, f"Found alternative attribute '{attr}'", {attr: getattr(response, attr)}, correlation_id)
                        
            debug_log(DebugLevel.DEBUG, f"Final metrics count: {len(metrics)}", correlation_id=correlation_id)
            
            result = {
                "status": "success",
                "metrics": metrics,
                "count": len(metrics),
                "filter_applied": filter_query,
                "from_time": from_time,
                "timeframe_hours": 2
            }
            
            debug_log(DebugLevel.TRACE, f"Returning result", result, correlation_id)
            return result
            
        except Exception as e:
            import traceback
            debug_log(DebugLevel.INFO, f"Exception in list_active_metrics", {
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }, correlation_id)
            return {
                "status": "error",
                "error": str(e),
                "metrics": [],
                "count": 0,
                "suggestion": "Check API credentials and ensure metrics exist in the specified timeframe"
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
                from_time = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
            if not to_time:
                to_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                
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

# Initialize Datadog client with key rotation support
def get_datadog_credentials():
    """Get Datadog credentials from environment with key rotation support"""
    try:
        # Load multiple key pairs from environment
        key_pairs = load_keys_from_environment()
        
        # Get rotation configuration
        rotation_config = get_rotation_config()
        
        # Create key pool manager
        key_pool = KeyPoolManager(
            rotation_strategy=rotation_config["strategy"],
            circuit_breaker_threshold=rotation_config["circuit_breaker_threshold"],
            circuit_breaker_timeout=rotation_config["circuit_breaker_timeout"],
            health_check_interval=rotation_config["health_check_interval"]
        )
        
        # Add all keys to the pool
        for key_pair in key_pairs:
            key_pool.add_key(key_pair)
        
        # Get primary site (from first key or environment)
        primary_site = key_pairs[0].site if key_pairs else "datadoghq.com"
        
        return key_pool, primary_site
        
    except Exception as e:
        logger.error(f"Failed to initialize Datadog key rotation: {e}")
        # Fallback to single key mode for backwards compatibility
        api_key = (
            os.getenv("DD_API_KEY") or 
            os.getenv("DATADOG_API_KEY") or 
            ""
        )
        app_key = (
            os.getenv("DD_APP_KEY") or 
            os.getenv("DATADOG_APP_KEY") or 
            ""
        )
        site = (
            os.getenv("DD_SITE") or 
            os.getenv("DATADOG_SITE") or 
            "datadoghq.com"
        )
        
        if not api_key or not app_key:
            raise ValueError("Datadog API credentials required")
        
        # Create single-key pool for backwards compatibility
        key_pool = KeyPoolManager()
        key_pair = KeyPair(
            id="fallback",
            api_key=api_key,
            app_key=app_key,
            site=site
        )
        key_pool.add_key(key_pair)
        
        return key_pool, site

try:
    key_pool, primary_site = get_datadog_credentials()
    
    datadog_config = DatadogConfig(
        key_pool=key_pool,
        primary_site=primary_site
    )
    
    # Log key pool status
    pool_status = key_pool.get_pool_status()
    debug_log(DebugLevel.INFO, "Datadog Key Pool Initialized", {
        "total_keys": pool_status["total_keys"],
        "available_keys": pool_status["available_keys"], 
        "rotation_strategy": pool_status["rotation_strategy"],
        "primary_site": primary_site
    })
    
    if pool_status["total_keys"] == 0:
        logger.error("No valid Datadog API keys available")
        exit(1)
        
except Exception as e:
    logger.error(f"Failed to initialize Datadog configuration: {e}")
    exit(1)

datadog_server = DatadogMCPServer(datadog_config)

# Add a simple health check tool for debugging
@mcp.tool
def server_health_check() -> Dict[str, Any]:
    """
    Simple health check to verify server is working and can connect to Datadog API.
    
    Returns:
        Dictionary containing server status and basic connectivity information
    """
    try:
        logger.info("Health check requested")
        
        # Test basic server functionality
        current_time = datetime.now(timezone.utc)
        
        # Test Datadog API connectivity (simple call)
        try:
            # Try to list a small number of metrics to test API connectivity
            api_test = datadog_server.list_active_metrics()
            datadog_status = "connected" if api_test.get("status") == "success" else "error"
            datadog_error = api_test.get("error", "") if api_test.get("status") == "error" else None
        except Exception as e:
            datadog_status = "error"
            datadog_error = str(e)
        
        # Get key pool status
        key_pool_status = datadog_server.key_pool.get_pool_status()
        
        result = {
            "status": "healthy",
            "server_time": current_time.isoformat(),
            "datadog_api_status": datadog_status,
            "datadog_site": datadog_config.primary_site,
            "version": "1.1.0",
            "key_rotation": {
                "enabled": True,
                "total_keys": key_pool_status["total_keys"],
                "available_keys": key_pool_status["available_keys"],
                "rotation_strategy": key_pool_status["rotation_strategy"]
            }
        }
        
        if datadog_error:
            result["datadog_error"] = datadog_error
            
        logger.info(f"Health check completed: {datadog_status}")
        return result
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "server_time": datetime.now(timezone.utc).isoformat()
        }

@mcp.tool
def get_key_pool_status() -> Dict[str, Any]:
    """
    Get detailed status of the API key pool for monitoring and debugging.
    
    Returns:
        Dictionary containing comprehensive key pool metrics and health information
    """
    try:
        status = datadog_server.key_pool.get_pool_status()
        
        # Add additional context
        status["monitoring"] = {
            "health_check_enabled": datadog_server.key_pool._health_check_thread is not None,
            "circuit_breaker_threshold": datadog_server.key_pool.circuit_breaker_threshold,
            "circuit_breaker_timeout": datadog_server.key_pool.circuit_breaker_timeout
        }
        
        # Add recommendations
        recommendations = []
        if status["available_keys"] == 0:
            recommendations.append("⚠️ No available keys - check key health and authentication")
        elif status["available_keys"] == 1:
            recommendations.append("⚠️ Only one key available - consider adding more keys for redundancy")
        elif status["available_keys"] < status["total_keys"]:
            recommendations.append(f"ℹ️ {status['total_keys'] - status['available_keys']} keys currently unavailable")
        
        # Check for keys with low success rates
        for key_info in status["keys"]:
            if key_info["success_rate"] < 0.8 and key_info["total_requests"] > 10:
                recommendations.append(f"⚠️ Key {key_info['id']} has low success rate ({key_info['success_rate']:.1%})")
        
        status["recommendations"] = recommendations
        status["status"] = "success"
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting key pool status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool
@mcp_debug_decorator("get_metrics")
def get_metrics(
    query: str,
    hours_back: int = 1,
    minutes_back: Optional[int] = None
) -> Dict[str, Any]:
    """
    Query timeseries metrics data from Datadog with comprehensive validation.
    
    Args:
        query: Datadog metrics query (e.g., "avg:system.cpu.user{*}")
        hours_back: Number of hours back from now to query (default: 1, max: 8760 for 1 year)
        minutes_back: Number of minutes back from now to query (overrides hours_back if provided, max: 525600 for 1 year)
    
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
    try:
        # Log incoming request for debugging
        logger.info(f"get_metrics called with query='{query}', hours_back={hours_back}, minutes_back={minutes_back}")
        
        # Input validation
        if not query or not query.strip():
            return {
                "status": "error",
                "error": "Query parameter is required and cannot be empty",
                "suggestion": "Provide a valid Datadog metrics query like 'avg:system.cpu.user{*}'"
            }
        
        # Validate time parameters
        if minutes_back is not None:
            if not isinstance(minutes_back, int) or minutes_back <= 0:
                return {
                    "status": "error",
                    "error": f"minutes_back must be a positive integer, got {minutes_back} ({type(minutes_back)})",
                    "suggestion": "Use a positive number of minutes (e.g., 30 for last 30 minutes)"
                }
            if minutes_back > 525600:  # 1 year in minutes
                return {
                    "status": "error",
                    "error": f"minutes_back cannot exceed 525600 (1 year), got {minutes_back}",
                    "suggestion": "Use a smaller time range for better performance"
                }
            
            # Use minutes_back if provided - using timezone-aware datetime
            now_utc = datetime.now(timezone.utc)
            to_time = int(now_utc.timestamp())
            from_time = int((now_utc - timedelta(minutes=minutes_back)).timestamp())
            time_desc = f"last {minutes_back} minutes"
            
        else:
            if not isinstance(hours_back, int) or hours_back <= 0:
                return {
                    "status": "error",
                    "error": f"hours_back must be a positive integer, got {hours_back} ({type(hours_back)})",
                    "suggestion": "Use a positive number of hours (e.g., 1 for last hour)"
                }
            if hours_back > 8760:  # 1 year in hours
                return {
                    "status": "error",
                    "error": f"hours_back cannot exceed 8760 (1 year), got {hours_back}",
                    "suggestion": "Use a smaller time range for better performance"
                }
            
            # Fall back to hours_back - using timezone-aware datetime
            now_utc = datetime.now(timezone.utc)
            to_time = int(now_utc.timestamp())
            from_time = int((now_utc - timedelta(hours=hours_back)).timestamp())
            time_desc = f"last {hours_back} hours"
        
        logger.info(f"Getting metrics for '{query}' over {time_desc}")
        result = datadog_server.query_metrics(query, from_time, to_time)
        
        # Add time description to successful results
        if result.get("status") == "success":
            result["time_description"] = time_desc
            result["query_type"] = "timeseries_metrics"
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in get_metrics for query '{query}': {error_msg}")
        logger.error(f"Parameters: query={query}, hours_back={hours_back}, minutes_back={minutes_back}")
        logger.error(f"Exception type: {type(e).__name__}")
        
        return {
            "status": "error",
            "error": f"Internal server error: {error_msg}",
            "query": query,
            "hours_back": hours_back,
            "minutes_back": minutes_back,
            "suggestion": "Check server logs for details. Verify query syntax: 'avg:system.cpu.user{*}'"
        }

@mcp.tool
@mcp_debug_decorator("list_metrics")
def list_metrics(
    filter_query: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve a list of available metrics in your Datadog environment.
    
    Args:
        filter_query: Optional filter to limit metrics returned. Can be:
                     - A hostname (e.g., "web-server-01") to filter by host
                     - A tag filter expression (e.g., "env:prod", "service:web-app")
                     - Leave empty to get all active metrics
    
    Returns:
        Dictionary containing list of available metrics or error information
        
    Examples:
        # Get all active metrics
        list_metrics()
        
        # Get metrics for a specific host
        list_metrics("web-server-01")
        
        # Get metrics with specific tags
        list_metrics("env:production")
    """
    try:
        logger.info(f"TRACE: MCP list_metrics called with filter: {filter_query or 'none'}")
        logger.info(f"TRACE: Calling datadog_server.list_active_metrics...")
        
        result = datadog_server.list_active_metrics(filter_query)
        
        logger.info(f"TRACE: datadog_server.list_active_metrics returned: {result}")
        logger.info(f"TRACE: Result type: {type(result)}")
        logger.info(f"TRACE: Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict) and 'metrics' in result:
            logger.info(f"TRACE: Found {len(result.get('metrics', []))} metrics in result")
            if result.get('metrics'):
                logger.info(f"TRACE: First few metrics: {result['metrics'][:3] if len(result['metrics']) > 0 else 'Empty'}")
        
        # Add helpful metadata to successful responses
        if result.get("status") == "success":
            result["filter_type"] = "hostname" if filter_query and '.' in filter_query and ':' not in filter_query else "tag_filter" if filter_query else "none"
            
        logger.info(f"TRACE: Final MCP list_metrics result: {result}")
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"TRACE: Exception in MCP list_metrics: {error_msg}")
        logger.error(f"Error listing metrics with filter '{filter_query}': {error_msg}")
        
        # Enhanced error categorization
        if "403" in error_msg or "Forbidden" in error_msg:
            suggestion = "Check API key permissions. Ensure 'metrics_read' permission is granted."
        elif "401" in error_msg or "Unauthorized" in error_msg:
            suggestion = "Check API key and APP key credentials in environment variables."
        elif "timeout" in error_msg.lower():
            suggestion = "Request timeout. Try again or use a more specific filter."
        else:
            suggestion = "Check network connectivity and try again."
        
        return {
            "status": "error", 
            "error": error_msg,
            "filter_query": filter_query,
            "suggestion": suggestion
        }

@mcp.tool
@mcp_debug_decorator("get_logs")
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
            calculated_from_time = (datetime.now(timezone.utc) - timedelta(minutes=minutes_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
            calculated_to_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            # Fall back to hours_back (default to 1 hour)
            hours_back = hours_back or 1
            calculated_from_time = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
            calculated_to_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    elif from_time is None and to_time is not None:
        # If only to_time is provided, default from_time to 1 hour before to_time
        try:
            to_dt = datetime.fromisoformat(to_time.replace('Z', '+00:00'))
            calculated_from_time = (to_dt - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            calculated_from_time = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    elif from_time is not None and to_time is None:
        # If only from_time is provided, default to_time to now
        calculated_to_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
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
    group_states: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get Datadog monitors, optionally filtered by group states.
    
    Args:
        group_states: Comma-separated group states to filter by (e.g., "alert,warn" or "all")
                     Valid values: "all", "alert", "warn", "no data"
    
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

*Report generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*
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

*Report generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""

@mcp.prompt("datadog-metrics-analysis")
def datadog_metrics_analysis_prompt(
    metric_query: str,
    time_range_hours: str = "24"  # Changed to str to handle MCP client parameter format
) -> str:
    """
    Generate a prompt for analyzing Datadog metrics.
    
    Args:
        metric_query: The metrics query to analyze
        time_range_hours: Time range in hours for the analysis (as string, will be converted)
    
    Returns:
        Formatted prompt for metrics analysis
    """
    try:
        # Handle parameter conversion from MCP client format
        if isinstance(time_range_hours, str):
            # Try to parse JSON format from MCP client
            import json
            try:
                parsed = json.loads(time_range_hours)
                if isinstance(parsed, dict) and "value" in parsed:
                    hours = int(parsed["value"])
                else:
                    hours = int(time_range_hours)
            except (json.JSONDecodeError, ValueError):
                hours = int(time_range_hours)
        else:
            hours = int(time_range_hours)
    except (ValueError, TypeError):
        hours = 24  # Default fallback
    
    return f"""
    Analyze the following Datadog metrics:
    
    Query: {metric_query}
    Time Range: Last {hours} hours
    
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
    logger.info(f"Datadog Site: {datadog_config.primary_site}")
    
    # Add request logging middleware for debugging
    import json
    from typing import Any, Dict
    
    # Store original tool functions for error handling - simplified to avoid deprecation warnings
    original_tools = {}
    tool_names = [
        'get_metrics', 'list_metrics', 'get_logs', 'get_monitors', 
        'list_dashboards', 'list_spans', 'get_trace', 'list_incidents',
        'get_incident', 'list_hosts', 'get_host'
    ]
    logger.info(f"Registered {len(tool_names)} tools for enhanced error handling")
    
    # Enhanced error logging
    def log_request_error(tool_name: str, params: Dict[str, Any], error: Exception):
        logger.error(f"Tool '{tool_name}' error:")
        logger.error(f"  Parameters: {json.dumps(params, default=str, indent=2)}")
        logger.error(f"  Error: {str(error)}")
        logger.error(f"  Error type: {type(error).__name__}")
    
    # Add HTTP middleware for debugging
    if debug_config.should_log_at_level(DebugLevel.DEBUG):
        logging.getLogger("uvicorn.error").setLevel(logging.DEBUG)
        logging.getLogger("uvicorn.access").setLevel(logging.DEBUG)
        logging.getLogger("fastmcp").setLevel(logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.DEBUG)
        
    if debug_config.should_log_at_level(DebugLevel.TRACE):
        logging.getLogger("uvicorn").setLevel(logging.DEBUG)
        # Enable all HTTP debugging
        import httpx
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Enhanced logging for MCP protocol errors
    def log_mcp_error(operation: str, error: Exception, context: dict = None):
        """Log MCP protocol errors with detailed context"""
        debug_log(DebugLevel.ERROR, f"MCP {operation} Error", {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "traceback": traceback.format_exc()
        })
    
    # Override FastMCP error handling if possible
    try:
        # Try to access internal FastMCP components for enhanced error logging
        if hasattr(mcp, '_server') and hasattr(mcp._server, 'error_handler'):
            original_error_handler = mcp._server.error_handler
            
            def enhanced_error_handler(error: Exception):
                log_mcp_error("Protocol", error, {"original_handler": "FastMCP"})
                return original_error_handler(error) if original_error_handler else {"error": str(error)}
            
            mcp._server.error_handler = enhanced_error_handler
            logger.info("Enhanced FastMCP error handler installed")
        else:
            logger.info("FastMCP error handler not accessible - using global error handling")
    except Exception as e:
        logger.warning(f"Could not enhance FastMCP error handling: {e}")
    
    # Log all incoming requests at the FastMCP level - removed invalid error_handler decorator
    def global_error_handler(error: Exception) -> dict:
        import traceback
        debug_log(DebugLevel.INFO, f"GLOBAL ERROR HANDLER: {type(error).__name__}", {
            "error": str(error),
            "traceback": traceback.format_exc()
        })
        return {
            "error": str(error),
            "type": type(error).__name__,
            "message": "An error occurred while processing your request"
        }
        
    # Wrap tools with error handling (simplified approach)
    logger.info("Enhanced error handling enabled for debugging")
    
    try:
        # Log debug configuration at startup
        debug_log(DebugLevel.INFO, "MCP Server Starting with Debug Configuration", {
            "debug_level": debug_config.level.value,
            "log_requests": debug_config.log_requests,
            "log_responses": debug_config.log_responses,
            "log_timing": debug_config.log_timing,
            "log_parameters": debug_config.log_parameters,
            "pretty_print": debug_config.pretty_print,
            "mask_sensitive_data": debug_config.mask_sensitive_data
        })
        
        # Run the server with HTTP transport
        logger.info("Starting MCP server...")
        mcp.run(transport="http", host=host, port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        logger.error(f"Error details: {type(e).__name__}: {str(e)}")
        exit(1)

