#!/usr/bin/env python3
"""
Tests for Enhanced Datadog MCP Server
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from datadog_mcp_server import DatadogConfig, DatadogMCPServer


class TestDatadogConfig:
    """Test DatadogConfig dataclass"""
    
    def test_config_creation(self):
        """Test creating a DatadogConfig instance"""
        config = DatadogConfig(
            api_key="test_api_key",
            app_key="test_app_key",
            site="datadoghq.com"
        )
        
        assert config.api_key == "test_api_key"
        assert config.app_key == "test_app_key"
        assert config.site == "datadoghq.com"
    
    def test_config_default_site(self):
        """Test default site value"""
        config = DatadogConfig(
            api_key="test_api_key",
            app_key="test_app_key"
        )
        
        assert config.site == "datadoghq.com"


class TestDatadogMCPServer:
    """Test DatadogMCPServer class"""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing"""
        return DatadogConfig(
            api_key="test_api_key",
            app_key="test_app_key",
            site="datadoghq.com"
        )
    
    @patch('datadog_mcp_server.ApiClient')
    @patch('datadog_mcp_server.Configuration')
    def test_server_initialization(self, mock_configuration, mock_api_client, mock_config):
        """Test server initialization"""
        # Setup mocks
        mock_config_instance = Mock()
        mock_configuration.return_value = mock_config_instance
        mock_client_instance = Mock()
        mock_api_client.return_value = mock_client_instance
        
        # Create server
        server = DatadogMCPServer(mock_config)
        
        # Verify configuration was set up
        assert mock_config_instance.api_key["apiKeyAuth"] == "test_api_key"
        assert mock_config_instance.api_key["appKeyAuth"] == "test_app_key"
        assert mock_config_instance.server_variables["site"] == "datadoghq.com"
        
        # Verify API client was created
        mock_api_client.assert_called_once_with(mock_config_instance)
        
        # Verify server has the expected attributes
        assert server.config == mock_config
        assert server.api_client == mock_client_instance
    
    @patch('datadog_mcp_server.ApiClient')
    @patch('datadog_mcp_server.Configuration')
    def test_get_logs_success(self, mock_configuration, mock_api_client, mock_config):
        """Test successful log retrieval"""
        # Setup mocks
        mock_config_instance = Mock()
        mock_configuration.return_value = mock_config_instance
        mock_client_instance = Mock()
        mock_api_client.return_value = mock_client_instance
        
        # Create server
        server = DatadogMCPServer(mock_config)
        
        # Mock the logs API response
        mock_log = Mock()
        mock_log.id = "log_123"
        mock_log.attributes.timestamp = "2025-01-01T00:00:00Z"
        mock_log.attributes.message = "Test log message"
        mock_log.attributes.service = "test-service"
        mock_log.attributes.status = "info"
        mock_log.attributes.tags = ["env:test"]
        mock_log.attributes.host = "test-host"
        mock_log.attributes.source = "test-source"
        
        mock_response = Mock()
        mock_response.data = [mock_log]
        server.logs_api.list_logs = Mock(return_value=mock_response)
        
        # Test get_logs
        result = server.get_logs("test query", limit=10)
        
        # Verify result
        assert result["status"] == "success"
        assert result["query"] == "test query"
        assert len(result["logs"]) == 1
        assert result["logs"][0]["id"] == "log_123"
        assert result["logs"][0]["message"] == "Test log message"
        assert result["count"] == 1
    
    @patch('datadog_mcp_server.ApiClient')
    @patch('datadog_mcp_server.Configuration')
    def test_get_logs_error(self, mock_configuration, mock_api_client, mock_config):
        """Test log retrieval error handling"""
        # Setup mocks
        mock_config_instance = Mock()
        mock_configuration.return_value = mock_config_instance
        mock_client_instance = Mock()
        mock_api_client.return_value = mock_client_instance
        
        # Create server
        server = DatadogMCPServer(mock_config)
        
        # Mock the logs API to raise an exception
        server.logs_api.list_logs = Mock(side_effect=Exception("API Error"))
        
        # Test get_logs
        result = server.get_logs("test query")
        
        # Verify error result
        assert result["status"] == "error"
        assert "API Error" in result["error"]
        assert result["query"] == "test query"
    
    @patch('datadog_mcp_server.ApiClient')
    @patch('datadog_mcp_server.Configuration')
    def test_list_spans_success(self, mock_configuration, mock_api_client, mock_config):
        """Test successful span listing"""
        # Setup mocks
        mock_config_instance = Mock()
        mock_configuration.return_value = mock_config_instance
        mock_client_instance = Mock()
        mock_api_client.return_value = mock_client_instance
        
        # Create server
        server = DatadogMCPServer(mock_config)
        
        # Mock the spans API response
        mock_span = Mock()
        mock_span.id = "span_123"
        mock_span.attributes.trace_id = "trace_456"
        mock_span.attributes.service = "test-service"
        mock_span.attributes.operation_name = "test.operation"
        mock_span.attributes.resource = "GET /api/test"
        mock_span.attributes.start = "2025-01-01T00:00:00Z"
        mock_span.attributes.duration = 1000000
        mock_span.attributes.tags = {"env": "test"}
        mock_span.attributes.status = "ok"
        
        mock_response = Mock()
        mock_response.data = [mock_span]
        server.spans_api.list_spans = Mock(return_value=mock_response)
        
        # Test list_spans
        result = server.list_spans("test query", limit=10)
        
        # Verify result
        assert result["status"] == "success"
        assert result["query"] == "test query"
        assert len(result["spans"]) == 1
        assert result["spans"][0]["span_id"] == "span_123"
        assert result["spans"][0]["trace_id"] == "trace_456"
        assert result["count"] == 1
    
    @patch('datadog_mcp_server.ApiClient')
    @patch('datadog_mcp_server.Configuration')
    def test_get_trace_success(self, mock_configuration, mock_api_client, mock_config):
        """Test successful trace retrieval"""
        # Setup mocks
        mock_config_instance = Mock()
        mock_configuration.return_value = mock_config_instance
        mock_client_instance = Mock()
        mock_api_client.return_value = mock_client_instance
        
        # Create server
        server = DatadogMCPServer(mock_config)
        
        # Mock the spans API response for trace
        mock_span = Mock()
        mock_span.id = "span_123"
        mock_span.attributes.trace_id = "trace_456"
        mock_span.attributes.parent_id = "parent_789"
        mock_span.attributes.service = "test-service"
        mock_span.attributes.operation_name = "test.operation"
        mock_span.attributes.resource = "GET /api/test"
        mock_span.attributes.start = "2025-01-01T00:00:00Z"
        mock_span.attributes.duration = 1000000
        mock_span.attributes.tags = {"env": "test"}
        mock_span.attributes.status = "ok"
        mock_span.attributes.error = 0
        
        mock_response = Mock()
        mock_response.data = [mock_span]
        server.spans_api.list_spans = Mock(return_value=mock_response)
        
        # Test get_trace
        result = server.get_trace("trace_456")
        
        # Verify result
        assert result["status"] == "success"
        assert result["trace_id"] == "trace_456"
        assert len(result["spans"]) == 1
        assert result["spans"][0]["span_id"] == "span_123"
        assert result["spans"][0]["parent_id"] == "parent_789"
        assert result["span_count"] == 1


@pytest.mark.asyncio
class TestMCPTools:
    """Test MCP tool functions"""
    
    @patch.dict(os.environ, {
        'DATADOG_API_KEY': 'test_key',
        'DATADOG_APP_KEY': 'test_app_key'
    })
    @patch('datadog_mcp_server.datadog_server')
    def test_get_logs_tool(self, mock_datadog_server):
        """Test get_logs MCP tool"""
        # Import the tool function
        from datadog_mcp_server import get_logs
        
        # Mock the server response
        mock_datadog_server.get_logs.return_value = {
            "status": "success",
            "query": "test query",
            "logs": [{"id": "log_123", "message": "test"}],
            "count": 1
        }
        
        # Call the tool
        result = get_logs("test query", limit=10, hours_back=1)
        
        # Verify the result
        assert result["status"] == "success"
        assert result["query"] == "test query"
        assert result["count"] == 1
    
    @patch.dict(os.environ, {
        'DATADOG_API_KEY': 'test_key',
        'DATADOG_APP_KEY': 'test_app_key'
    })
    @patch('datadog_mcp_server.datadog_server')
    def test_list_spans_tool(self, mock_datadog_server):
        """Test list_spans MCP tool"""
        # Import the tool function
        from datadog_mcp_server import list_spans
        
        # Mock the server response
        mock_datadog_server.list_spans.return_value = {
            "status": "success",
            "query": "test query",
            "spans": [{"span_id": "span_123", "service": "test"}],
            "count": 1
        }
        
        # Call the tool
        result = list_spans("test query", limit=10, hours_back=1)
        
        # Verify the result
        assert result["status"] == "success"
        assert result["query"] == "test query"
        assert result["count"] == 1
    
    @patch.dict(os.environ, {
        'DATADOG_API_KEY': 'test_key',
        'DATADOG_APP_KEY': 'test_app_key'
    })
    @patch('datadog_mcp_server.datadog_server')
    def test_get_trace_tool(self, mock_datadog_server):
        """Test get_trace MCP tool"""
        # Import the tool function
        from datadog_mcp_server import get_trace
        
        # Mock the server response
        mock_datadog_server.get_trace.return_value = {
            "status": "success",
            "trace_id": "trace_456",
            "spans": [{"span_id": "span_123"}],
            "span_count": 1
        }
        
        # Call the tool
        result = get_trace("trace_456")
        
        # Verify the result
        assert result["status"] == "success"
        assert result["trace_id"] == "trace_456"
        assert result["span_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__])

