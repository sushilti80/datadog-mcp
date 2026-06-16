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

from datadog_mcp_server import DatadogConfig, DatadogMCPServer
from key_rotation import KeyPoolManager, KeyPair


class TestDatadogConfig:
    """Test DatadogConfig dataclass"""

    def test_config_creation(self):
        """Test creating a DatadogConfig instance"""
        mock_pool = Mock(spec=KeyPoolManager)
        config = DatadogConfig(key_pool=mock_pool, primary_site="us3.datadoghq.com")

        assert config.key_pool == mock_pool
        assert config.primary_site == "us3.datadoghq.com"

    def test_config_default_site(self):
        """Test default site value"""
        mock_pool = Mock(spec=KeyPoolManager)
        config = DatadogConfig(key_pool=mock_pool)

        assert config.primary_site == "datadoghq.com"


class TestDatadogMCPServer:
    """Test DatadogMCPServer class"""

    @pytest.fixture
    def mock_key_pool(self):
        """Create a mock key pool for testing"""
        mock_pool = Mock(spec=KeyPoolManager)
        mock_pool.start_health_monitoring = Mock()
        mock_pool.get_pool_status = Mock(return_value={
            "total_keys": 1,
            "available_keys": 1,
            "rotation_strategy": "round_robin"
        })
        mock_key = Mock(spec=KeyPair)
        mock_key.id = "test_key_1"
        mock_key.api_key = "test_api_key"
        mock_key.app_key = "test_app_key"
        mock_key.site = "datadoghq.com"
        mock_pool.keys = [mock_key]
        mock_pool.get_key_by_strategy = Mock(return_value=mock_key)
        return mock_pool

    @pytest.fixture
    def mock_config(self, mock_key_pool):
        """Create a mock config for testing"""
        return DatadogConfig(key_pool=mock_key_pool)

    def test_server_initialization(self, mock_config, mock_key_pool):
        """Test server initialization"""
        server = DatadogMCPServer(mock_config)

        assert server.config == mock_config
        assert server.key_pool == mock_key_pool
        mock_key_pool.start_health_monitoring.assert_called_once()

    def test_query_metrics_empty_query(self, mock_config):
        """Test query_metrics rejects empty query"""
        server = DatadogMCPServer(mock_config)

        result = server.query_metrics("", 0, 3600)

        assert result["status"] == "error"
        assert "empty" in result["error"].lower()

    def test_query_metrics_invalid_time_range(self, mock_config):
        """Test query_metrics rejects invalid time range"""
        server = DatadogMCPServer(mock_config)

        result = server.query_metrics("avg:system.cpu.user{*}", 3600, 0)

        assert result["status"] == "error"
        assert "time range" in result["error"].lower()

    def test_search_spans_returns_success(self, mock_config):
        """Test search_spans returns a valid response structure"""
        server = DatadogMCPServer(mock_config)

        result = server.search_spans("service:test", limit=10)

        assert result["status"] == "success"
        assert "spans" in result
        assert "query" in result
        assert result["query"] == "service:test"

    def test_get_trace_data_returns_success(self, mock_config):
        """Test get_trace_data returns a valid response structure"""
        server = DatadogMCPServer(mock_config)

        result = server.get_trace_data("trace_abc123")

        assert result["status"] == "success"
        assert "trace_id" in result


class TestMCPTools:
    """Test MCP tool functions"""

    @patch("datadog_mcp_server.datadog_server")
    def test_get_logs_tool(self, mock_datadog_server):
        """Test get_logs MCP tool"""
        from datadog_mcp_server import get_logs

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

    @patch("datadog_mcp_server.datadog_server")
    def test_list_spans_tool(self, mock_datadog_server):
        """Test list_spans MCP tool"""
        from datadog_mcp_server import list_spans

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

    @patch("datadog_mcp_server.datadog_server")
    def test_get_trace_tool(self, mock_datadog_server):
        """Test get_trace MCP tool"""
        from datadog_mcp_server import get_trace

        mock_datadog_server.get_trace_data.return_value = {
            "status": "success",
            "trace_id": "trace_456",
            "spans": [{"span_id": "span_123"}],
            "span_count": 1,
        }

        result = get_trace("trace_456")

        assert result["status"] == "success"
        assert result["trace_id"] == "trace_456"
        assert result["span_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__])

