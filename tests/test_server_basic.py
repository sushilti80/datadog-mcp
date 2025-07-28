#!/usr/bin/env python3
"""
Basic tests for Enhanced Datadog MCP Server
"""

import pytest
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_server_import():
    """Test that the server module can be imported"""
    # Set dummy environment variables
    os.environ['DATADOG_API_KEY'] = 'test_key'
    os.environ['DATADOG_APP_KEY'] = 'test_app_key'
    
    try:
        import datadog_mcp_server
        assert hasattr(datadog_mcp_server, 'mcp')
        assert hasattr(datadog_mcp_server, 'DatadogMCPServer')
        assert hasattr(datadog_mcp_server, 'DatadogConfig')
    except Exception as e:
        pytest.fail(f"Failed to import server module: {e}")


def test_datadog_config():
    """Test DatadogConfig creation"""
    from datadog_mcp_server import DatadogConfig
    
    config = DatadogConfig(
        api_key="test_api_key",
        app_key="test_app_key",
        site="datadoghq.com"
    )
    
    assert config.api_key == "test_api_key"
    assert config.app_key == "test_app_key"
    assert config.site == "datadoghq.com"


def test_server_tools_available():
    """Test that all required tools are available"""
    os.environ['DATADOG_API_KEY'] = 'test_key'
    os.environ['DATADOG_APP_KEY'] = 'test_app_key'
    
    import datadog_mcp_server
    
    # Check that the MCP instance exists
    assert hasattr(datadog_mcp_server, 'mcp')
    mcp_instance = datadog_mcp_server.mcp
    
    # The tools should be registered with FastMCP
    # We can't easily test the internal structure, but we can verify the module loaded
    assert mcp_instance.name == "Enhanced Datadog MCP Server"


def test_required_tools_defined():
    """Test that all required tool functions are defined"""
    os.environ['DATADOG_API_KEY'] = 'test_key'
    os.environ['DATADOG_APP_KEY'] = 'test_app_key'
    
    import datadog_mcp_server
    
    # Check that tool functions exist
    required_tools = [
        'get_logs',
        'list_spans', 
        'get_trace',
        'list_metrics',
        'get_metrics',
        'get_monitors',
        'list_hosts'
    ]
    
    for tool_name in required_tools:
        assert hasattr(datadog_mcp_server, tool_name), f"Tool {tool_name} not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

