#!/usr/bin/env python3
"""
Tests for the Datadog MCP server.
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Ensure module import can initialize the global server during test collection.
os.environ.setdefault("DATADOG_API_KEY", "test_key")
os.environ.setdefault("DATADOG_APP_KEY", "test_app_key")

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datadog_mcp_server import DatadogConfig, DatadogMCPServer, get_logs, get_trace, list_spans
from key_rotation import KeyPair, KeyPoolManager, RotationStrategy


@pytest.fixture
def key_pool():
    """Create a key pool with one test key."""
    pool = KeyPoolManager(rotation_strategy=RotationStrategy.ROUND_ROBIN)
    pool.add_key(
        KeyPair(
            id="test_key",
            api_key="test_api_key",
            app_key="test_app_key",
            site="us3.datadoghq.com",
        )
    )
    yield pool
    pool.stop_health_monitoring()


@pytest.fixture
def config(key_pool):
    """Create a DatadogConfig for tests."""
    return DatadogConfig(
        key_pool=key_pool,
        primary_site="us3.datadoghq.com",
    )


@pytest.fixture
def server(config):
    """Create a DatadogMCPServer for tests."""
    instance = DatadogMCPServer(config)
    yield instance
    instance.key_pool.stop_health_monitoring()


class TestDatadogConfig:
    """Test DatadogConfig dataclass."""

    def test_config_creation(self, key_pool):
        """Test creating a DatadogConfig instance."""
        config = DatadogConfig(
            key_pool=key_pool,
            primary_site="us3.datadoghq.com",
        )

        assert config.key_pool is key_pool
        assert config.primary_site == "us3.datadoghq.com"

    def test_config_default_site(self, key_pool):
        """Test default site value."""
        config = DatadogConfig(key_pool=key_pool)

        assert config.primary_site == "datadoghq.com"


class TestDatadogMCPServer:
    """Test DatadogMCPServer class."""

    def test_server_initialization(self, config):
        """Test server initialization."""
        server = DatadogMCPServer(config)

        assert server.config is config
        assert server.key_pool is config.key_pool
        assert server._api_client_cache == {}

        server.key_pool.stop_health_monitoring()

    @patch("datadog_mcp_server.ApiClient")
    @patch("datadog_mcp_server.Configuration")
    def test_get_api_client_caches_by_key(
        self,
        mock_configuration,
        mock_api_client,
        server,
        key_pool,
    ):
        """Test API clients are initialized once per key pair."""
        mock_config_instance = Mock()
        mock_config_instance.api_key = {}
        mock_config_instance.server_variables = {}
        mock_configuration.return_value = mock_config_instance

        mock_client_instance = Mock()
        mock_api_client.return_value = mock_client_instance

        key = key_pool.keys[0]
        first_client = server._get_api_client(key)
        second_client = server._get_api_client(key)

        assert first_client is mock_client_instance
        assert second_client is mock_client_instance
        assert mock_config_instance.api_key["apiKeyAuth"] == "test_api_key"
        assert mock_config_instance.api_key["appKeyAuth"] == "test_app_key"
        assert mock_config_instance.server_variables["site"] == "us3.datadoghq.com"
        mock_configuration.assert_called_once_with()
        mock_api_client.assert_called_once_with(mock_config_instance)

    def test_search_logs_success(self, server):
        """Test successful log retrieval."""
        expected_logs = [
            {
                "id": "log_123",
                "timestamp": "2025-01-01T00:00:00Z",
                "message": "Test log message",
                "service": "test-service",
            }
        ]

        with patch.object(
            server,
            "_execute_with_key_rotation",
            return_value=(expected_logs, None, 1),
        ):
            result = server.search_logs("test query", limit=10)

        assert result["status"] == "success"
        assert result["query"] == "test query"
        assert result["logs"] == expected_logs
        assert result["count"] == 1
        assert result["total_retrieved"] == 1
        assert result["has_more"] is False

    def test_search_logs_error(self, server):
        """Test log retrieval error handling."""
        with patch.object(
            server,
            "_execute_with_key_rotation",
            side_effect=Exception("API Error"),
        ):
            result = server.search_logs("test query")

        assert result["status"] == "error"
        assert "API Error" in result["error"]
        assert result["query"] == "test query"

    def test_list_spans_success(self, server):
        """Test successful span listing."""
        result = server.search_spans("test query", limit=10)

        assert result["status"] == "success"
        assert result["query"] == "test query"
        assert result["spans"] == []
        assert result["count"] == 0

    def test_get_trace_success(self, server):
        """Test successful trace retrieval."""
        result = server.get_trace_data("trace_456")

        assert result["status"] == "success"
        assert result["trace_id"] == "trace_456"
        assert result["data"] == {"trace_id": "trace_456", "spans": []}


class TestMCPTools:
    """Test MCP tool functions."""

    @patch("datadog_mcp_server.datadog_server")
    def test_get_logs_tool(self, mock_datadog_server):
        """Test get_logs MCP tool."""
        mock_datadog_server.search_logs.return_value = {
            "status": "success",
            "query": "test query",
            "logs": [{"id": "log_123", "message": "test"}],
            "count": 1,
        }

        result = get_logs("test query", limit=10, hours_back=1)

        assert result["status"] == "success"
        assert result["query"] == "test query"
        assert result["count"] == 1

        kwargs = mock_datadog_server.search_logs.call_args.kwargs
        assert kwargs["query"] == "test query"
        assert kwargs["limit"] == 10
        assert kwargs["from_time"] is not None
        assert kwargs["to_time"] is not None
        assert kwargs["indexes"] is None
        assert kwargs["sort"] == "timestamp"
        assert kwargs["cursor"] is None
        assert kwargs["max_total_logs"] is None

    @patch("datadog_mcp_server.datadog_server")
    def test_list_spans_tool(self, mock_datadog_server):
        """Test list_spans MCP tool."""
        mock_datadog_server.search_spans.return_value = {
            "status": "success",
            "query": "test query",
            "spans": [{"span_id": "span_123", "service": "test"}],
            "count": 1,
        }

        result = list_spans("test query", limit=10)

        assert result["status"] == "success"
        assert result["query"] == "test query"
        assert result["count"] == 1
        mock_datadog_server.search_spans.assert_called_once_with(
            "test query",
            None,
            None,
            10,
        )

    @patch("datadog_mcp_server.datadog_server")
    def test_get_trace_tool(self, mock_datadog_server):
        """Test get_trace MCP tool."""
        mock_datadog_server.get_trace_data.return_value = {
            "status": "success",
            "trace_id": "trace_456",
            "data": {"trace_id": "trace_456", "spans": []},
        }

        result = get_trace("trace_456")

        assert result["status"] == "success"
        assert result["trace_id"] == "trace_456"
        assert result["data"]["trace_id"] == "trace_456"
        mock_datadog_server.get_trace_data.assert_called_once_with("trace_456")


if __name__ == "__main__":
    pytest.main([__file__])
