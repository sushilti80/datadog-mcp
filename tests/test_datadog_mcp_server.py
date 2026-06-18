#!/usr/bin/env python3
"""
Tests for Enhanced Datadog MCP Server
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Set dummy credentials before importing server module
os.environ.setdefault("DD_API_KEY", "test_api_key")
os.environ.setdefault("DD_APP_KEY", "test_app_key")

from key_rotation import KeyPair, KeyPoolManager
from datadog_mcp_server import DatadogConfig, DatadogMCPServer


class TestDatadogConfig:
    """Test DatadogConfig dataclass"""

    def test_config_creation(self):
        """Test creating a DatadogConfig instance"""
        key_pool = KeyPoolManager()
        key_pool.add_key(
            KeyPair(
                id="test",
                api_key="test_api_key",
                app_key="test_app_key",
                site="datadoghq.com",
            )
        )
        config = DatadogConfig(key_pool=key_pool, primary_site="datadoghq.com")

        assert config.key_pool == key_pool
        assert config.primary_site == "datadoghq.com"

    def test_config_default_site(self):
        """Test default site value"""
        key_pool = KeyPoolManager()
        key_pool.add_key(
            KeyPair(
                id="test",
                api_key="test_api_key",
                app_key="test_app_key",
                site="datadoghq.com",
            )
        )
        config = DatadogConfig(key_pool=key_pool)

        assert config.primary_site == "datadoghq.com"


class TestDatadogMCPServer:
    """Test DatadogMCPServer class"""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing"""
        key_pool = KeyPoolManager()
        key_pool.add_key(
            KeyPair(
                id="test",
                api_key="test_api_key",
                app_key="test_app_key",
                site="datadoghq.com",
            )
        )
        key_pool.start_health_monitoring = Mock()
        return DatadogConfig(key_pool=key_pool, primary_site="datadoghq.com")

    def test_server_initialization(self, mock_config):
        """Test server initialization"""
        server = DatadogMCPServer(mock_config)

        assert server.config == mock_config
        assert server.key_pool == mock_config.key_pool
        assert isinstance(server._api_client_cache, dict)
        mock_config.key_pool.start_health_monitoring.assert_called_once()

    def test_search_logs_success(self, mock_config):
        """Test successful log retrieval"""
        server = DatadogMCPServer(mock_config)
        server._execute_with_key_rotation = Mock(
            return_value=(
                [{"id": "log_123", "message": "Test log message"}],
                None,
                1,
            )
        )
        result = server.search_logs(
            "test query",
            limit=10,
            from_time="2025-01-01T00:00:00Z",
            to_time="2025-01-01T01:00:00Z",
        )

        assert result["status"] == "success"
        assert result["query"] == "test query"
        assert len(result["logs"]) == 1
        assert result["logs"][0]["id"] == "log_123"
        assert result["logs"][0]["message"] == "Test log message"
        assert result["count"] == 1

    def test_search_logs_error(self, mock_config):
        """Test log retrieval error handling"""
        server = DatadogMCPServer(mock_config)
        server._execute_with_key_rotation = Mock(side_effect=Exception("API Error"))
        result = server.search_logs("test query")
        assert result["status"] == "error"
        assert "API Error" in result["error"]
        assert result["query"] == "test query"

    def test_search_spans_success(self, mock_config):
        """Test successful span listing"""
        server = DatadogMCPServer(mock_config)
        result = server.search_spans("test query", limit=10)
        assert result["status"] == "success"
        assert result["query"] == "test query"
        assert result["spans"] == []
        assert result["count"] == 0

    def test_get_trace_data_success(self, mock_config):
        """Test successful trace retrieval"""
        server = DatadogMCPServer(mock_config)
        result = server.get_trace_data("trace_456")
        assert result["status"] == "success"
        assert result["trace_id"] == "trace_456"
        assert result["data"]["trace_id"] == "trace_456"


class TestMCPTools:
    """Test MCP tool functions"""

    @patch.dict(
        os.environ, {"DATADOG_API_KEY": "test_key", "DATADOG_APP_KEY": "test_app_key"}
    )
    @patch("datadog_mcp_server.datadog_server")
    def test_get_logs_tool(self, mock_datadog_server):
        """Test get_logs MCP tool"""
        # Import the tool function
        from datadog_mcp_server import get_logs

        # Mock the server response
        mock_datadog_server.search_logs.return_value = {
            "status": "success",
            "query": "test query",
            "logs": [{"id": "log_123", "message": "test"}],
            "count": 1,
        }

        # Call the tool
        result = get_logs("test query", limit=10, hours_back=1)

        # Verify the result
        assert result["status"] == "success"
        assert result["query"] == "test query"
        assert result["count"] == 1
        mock_datadog_server.search_logs.assert_called_once()

    @patch.dict(
        os.environ, {"DATADOG_API_KEY": "test_key", "DATADOG_APP_KEY": "test_app_key"}
    )
    @patch("datadog_mcp_server.datadog_server")
    def test_list_spans_tool(self, mock_datadog_server):
        """Test list_spans MCP tool"""
        # Import the tool function
        from datadog_mcp_server import list_spans

        # Mock the server response
        mock_datadog_server.search_spans.return_value = {
            "status": "success",
            "query": "test query",
            "spans": [{"span_id": "span_123", "service": "test"}],
            "count": 1,
        }

        # Call the tool
        result = list_spans("test query", limit=10)

        # Verify the result
        assert result["status"] == "success"
        assert result["query"] == "test query"
        assert result["count"] == 1
        mock_datadog_server.search_spans.assert_called_once_with(
            "test query", None, None, 10
        )

    @patch.dict(
        os.environ, {"DATADOG_API_KEY": "test_key", "DATADOG_APP_KEY": "test_app_key"}
    )
    @patch("datadog_mcp_server.datadog_server")
    def test_get_trace_tool(self, mock_datadog_server):
        """Test get_trace MCP tool"""
        # Import the tool function
        from datadog_mcp_server import get_trace

        # Mock the server response
        mock_datadog_server.get_trace_data.return_value = {
            "status": "success",
            "trace_id": "trace_456",
            "data": {"trace_id": "trace_456", "spans": []},
        }

        # Call the tool
        result = get_trace("trace_456")

        # Verify the result
        assert result["status"] == "success"
        assert result["trace_id"] == "trace_456"
        assert result["data"]["trace_id"] == "trace_456"


if __name__ == "__main__":
    pytest.main([__file__])
