#!/usr/bin/env python3
"""
Test script to verify key rotation functionality
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from key_rotation import (
    KeyPair, KeyPoolManager, KeyHealth, RotationStrategy,
    load_keys_from_environment, get_rotation_config,
    create_retry_decorator, detect_rate_limit_error
)

class TestKeyRotation(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.key_pool = KeyPoolManager(
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
            circuit_breaker_threshold=3,
            circuit_breaker_timeout=5
        )
        
        # Add test keys
        self.key1 = KeyPair("test_key_1", "api_key_1", "app_key_1")
        self.key2 = KeyPair("test_key_2", "api_key_2", "app_key_2")
        self.key3 = KeyPair("test_key_3", "api_key_3", "app_key_3")
        
        self.key_pool.add_key(self.key1)
        self.key_pool.add_key(self.key2)
        self.key_pool.add_key(self.key3)
    
    def test_key_pool_initialization(self):
        """Test key pool basic functionality"""
        status = self.key_pool.get_pool_status()
        
        self.assertEqual(status["total_keys"], 3)
        self.assertEqual(status["available_keys"], 3)
        self.assertEqual(status["rotation_strategy"], "round_robin")
    
    def test_round_robin_selection(self):
        """Test round robin key selection"""
        selected_keys = []
        
        # Select keys multiple times
        for _ in range(6):
            key = self.key_pool.get_key_by_strategy()
            selected_keys.append(key.id)
        
        # Should cycle through keys in order
        expected_pattern = ["test_key_1", "test_key_2", "test_key_3"] * 2
        self.assertEqual(selected_keys, expected_pattern)
    
    def test_rate_limit_handling(self):
        """Test rate limit detection and handling"""
        # Simulate rate limit on key 1
        self.key_pool.record_key_event("test_key_1", "rate_limit")
        
        # Key 1 should be unavailable
        status = self.key_pool.get_pool_status()
        self.assertEqual(status["available_keys"], 2)
        
        # Should select from remaining keys
        for _ in range(4):
            key = self.key_pool.get_key_by_strategy()
            self.assertNotEqual(key.id, "test_key_1")
    
    def test_circuit_breaker(self):
        """Test circuit breaker functionality"""
        # Trigger multiple errors on key 1
        for _ in range(4):  # Exceed threshold of 3
            self.key_pool.record_key_event("test_key_1", "error")
        
        # Key should be circuit broken
        key1_status = next(k for k in self.key_pool.keys if k.id == "test_key_1")
        self.assertEqual(key1_status.health, KeyHealth.ERROR)
        
        # Should not be available for selection
        available_keys = self.key_pool.get_available_keys()
        available_ids = [k.id for k in available_keys]
        self.assertNotIn("test_key_1", available_ids)
    
    def test_success_tracking(self):
        """Test success rate tracking"""
        # Record mixed results for key 1
        self.key_pool.record_key_event("test_key_1", "success", response_time=0.1)
        self.key_pool.record_key_event("test_key_1", "success", response_time=0.2)
        self.key_pool.record_key_event("test_key_1", "error")
        
        key1_status = next(k for k in self.key_pool.keys if k.id == "test_key_1")
        
        # Should have 2/3 success rate
        self.assertAlmostEqual(key1_status.get_success_rate(), 2/3, places=2)
        self.assertEqual(key1_status.metrics.consecutive_failures, 1)
    
    def test_adaptive_strategy(self):
        """Test adaptive selection strategy"""
        adaptive_pool = KeyPoolManager(rotation_strategy=RotationStrategy.ADAPTIVE)
        adaptive_pool.add_key(self.key1)
        adaptive_pool.add_key(self.key2)
        
        # Should work without errors
        key = adaptive_pool.get_key_by_strategy()
        self.assertIsNotNone(key)
        self.assertIn(key.id, ["test_key_1", "test_key_2"])


class TestEnvironmentLoading(unittest.TestCase):
    
    def test_single_key_loading(self):
        """Test loading single key from environment"""
        env_vars = {
            'DD_API_KEY': 'test_api_key',
            'DD_APP_KEY': 'test_app_key',
            'DD_SITE': 'us3.datadoghq.com'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            keys = load_keys_from_environment()
            
            self.assertEqual(len(keys), 1)
            self.assertEqual(keys[0].id, "primary")
            self.assertEqual(keys[0].api_key, "test_api_key")
            self.assertEqual(keys[0].app_key, "test_app_key")
            self.assertEqual(keys[0].site, "datadoghq.com")
    
    def test_multiple_key_loading(self):
        """Test loading multiple keys from environment"""
        env_vars = {
            'DD_API_KEY': 'api_key_1',
            'DD_APP_KEY': 'app_key_1',
            'DD_API_KEY_2': 'api_key_2',
            'DD_APP_KEY_2': 'app_key_2',
            'DD_API_KEY_3': 'api_key_3',
            'DD_APP_KEY_3': 'app_key_3',
            'DD_SITE_3': 'us3.datadoghq.com'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            keys = load_keys_from_environment()
            
            self.assertEqual(len(keys), 3)
            self.assertEqual(keys[0].id, "primary")
            self.assertEqual(keys[1].id, "key_2")
            self.assertEqual(keys[2].id, "key_3")
            self.assertEqual(keys[2].site, "us3.datadoghq.com")
    
    def test_json_key_loading(self):
        """Test loading keys from JSON format"""
        json_keys = json.dumps([
            {"api_key": "api1", "app_key": "app1", "site": "datadoghq.com"},
            {"api_key": "api2", "app_key": "app2", "site": "us3.datadoghq.com"}
        ])
        
        env_vars = {
            'DD_API_KEYS_JSON': json_keys
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            keys = load_keys_from_environment()
            
            self.assertEqual(len(keys), 2)
            self.assertEqual(keys[0].id, "json_key_1")
            self.assertEqual(keys[1].id, "json_key_2")
            self.assertEqual(keys[1].site, "us3.datadoghq.com")


class TestRetryDecorator(unittest.TestCase):
    
    def test_successful_operation(self):
        """Test retry decorator with successful operation"""
        key_pool = KeyPoolManager()
        key_pool.add_key(KeyPair("test_key", "api_key", "app_key"))
        
        @create_retry_decorator(key_pool, max_retries=3)
        def test_operation(key_pair):
            return f"success_with_{key_pair.id}"
        
        result = test_operation()
        self.assertEqual(result, "success_with_test_key")
    
    def test_rate_limit_retry(self):
        """Test retry on rate limit with key rotation"""
        key_pool = KeyPoolManager()
        key1 = KeyPair("key_1", "api_key_1", "app_key_1")
        key2 = KeyPair("key_2", "api_key_2", "app_key_2")
        key_pool.add_key(key1)
        key_pool.add_key(key2)
        
        call_count = 0
        
        @create_retry_decorator(key_pool, max_retries=3)
        def test_operation(key_pair):
            nonlocal call_count
            call_count += 1
            
            # Fail with rate limit on first key, succeed on second
            if key_pair.id == "key_1":
                raise Exception("429 Too Many Requests")
            return f"success_with_{key_pair.id}"
        
        result = test_operation()
        self.assertEqual(result, "success_with_key_2")
        self.assertEqual(call_count, 2)  # Should try both keys


class TestRateLimitDetection(unittest.TestCase):
    
    def test_rate_limit_detection(self):
        """Test rate limit error detection"""
        rate_limit_errors = [
            Exception("429 Too Many Requests"),
            Exception("Rate limit exceeded"),
            Exception("API quota exceeded"),
            Exception("Request throttled")
        ]
        
        for error in rate_limit_errors:
            is_rate_limited, reset_time = detect_rate_limit_error(error)
            self.assertTrue(is_rate_limited)
            self.assertIsNotNone(reset_time)
    
    def test_non_rate_limit_detection(self):
        """Test non-rate limit error detection"""
        other_errors = [
            Exception("401 Unauthorized"),
            Exception("500 Internal Server Error"),
            Exception("Network timeout")
        ]
        
        for error in other_errors:
            is_rate_limited, reset_time = detect_rate_limit_error(error)
            self.assertFalse(is_rate_limited)
            self.assertIsNone(reset_time)


if __name__ == '__main__':
    print("🧪 Running Key Rotation Tests")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2)