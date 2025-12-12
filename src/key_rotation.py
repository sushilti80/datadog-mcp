#!/usr/bin/env python3
"""
Datadog API Key Rotation Manager

Implements intelligent key rotation strategies to avoid rate limiting
and provide high availability for Datadog API access.
"""

import os
import time
import logging
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple, Callable
from datetime import datetime, timedelta, timezone
import random
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class KeyHealth(Enum):
    """Health status of an API key pair"""
    HEALTHY = "healthy"
    RATE_LIMITED = "rate_limited" 
    ERROR = "error"
    DISABLED = "disabled"
    TESTING = "testing"

class RotationStrategy(Enum):
    """Key selection strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_RECENTLY_USED = "lru"
    WEIGHTED = "weighted"
    ADAPTIVE = "adaptive"
    RANDOM = "random"

@dataclass
class KeyUsageMetrics:
    """Track usage statistics for a key pair"""
    total_requests: int = 0
    successful_requests: int = 0
    rate_limited_requests: int = 0
    error_requests: int = 0
    last_used: Optional[datetime] = None
    last_rate_limit: Optional[datetime] = None
    last_error: Optional[datetime] = None
    average_response_time: float = 0.0
    consecutive_failures: int = 0

@dataclass
class KeyPair:
    """Represents a Datadog API key pair with metadata"""
    id: str
    api_key: str
    app_key: str
    site: str = "us3.datadoghq.com"
    health: KeyHealth = KeyHealth.TESTING
    metrics: KeyUsageMetrics = field(default_factory=KeyUsageMetrics)
    rate_limit_reset_time: Optional[datetime] = None
    circuit_breaker_reset_time: Optional[datetime] = None
    weight: float = 1.0  # For weighted selection
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = KeyUsageMetrics()
    
    def is_available(self) -> bool:
        """Check if key is available for use"""
        if self.health == KeyHealth.DISABLED:
            return False
        
        # Check if rate limit has expired
        if self.health == KeyHealth.RATE_LIMITED:
            if self.rate_limit_reset_time and datetime.now(timezone.utc) > self.rate_limit_reset_time:
                self.health = KeyHealth.HEALTHY
                self.rate_limit_reset_time = None
                logger.info(f"Key {self.id} rate limit expired, marking as healthy")
        
        # Check if circuit breaker should reset
        if self.health == KeyHealth.ERROR:
            if self.circuit_breaker_reset_time and datetime.now(timezone.utc) > self.circuit_breaker_reset_time:
                self.health = KeyHealth.TESTING
                self.circuit_breaker_reset_time = None
                logger.info(f"Key {self.id} circuit breaker reset, marking for testing")
        
        return self.health in [KeyHealth.HEALTHY, KeyHealth.TESTING]
    
    def record_success(self, response_time: float = 0.0):
        """Record a successful API call"""
        self.metrics.total_requests += 1
        self.metrics.successful_requests += 1
        self.metrics.last_used = datetime.now(timezone.utc)
        self.metrics.consecutive_failures = 0
        
        # Update average response time with exponential moving average
        if self.metrics.average_response_time == 0:
            self.metrics.average_response_time = response_time
        else:
            self.metrics.average_response_time = (
                0.9 * self.metrics.average_response_time + 0.1 * response_time
            )
        
        # Mark as healthy if it was in testing state
        if self.health == KeyHealth.TESTING:
            self.health = KeyHealth.HEALTHY
            logger.info(f"Key {self.id} test successful, marking as healthy")
    
    def record_rate_limit(self, reset_time: Optional[datetime] = None):
        """Record a rate limit event"""
        self.metrics.total_requests += 1
        self.metrics.rate_limited_requests += 1
        self.metrics.last_rate_limit = datetime.now(timezone.utc)
        self.health = KeyHealth.RATE_LIMITED
        
        # Set rate limit reset time (default to 1 hour if not provided)
        self.rate_limit_reset_time = reset_time or (
            datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        logger.warning(f"Key {self.id} rate limited, reset at {self.rate_limit_reset_time}")
    
    def record_error(self, error_type: str = "unknown"):
        """Record an error event"""
        self.metrics.total_requests += 1
        self.metrics.error_requests += 1
        self.metrics.last_error = datetime.now(timezone.utc)
        self.metrics.consecutive_failures += 1
        
        logger.error(f"Key {self.id} error: {error_type}, consecutive failures: {self.metrics.consecutive_failures}")
    
    def trigger_circuit_breaker(self, timeout_minutes: int = 10):
        """Trigger circuit breaker for this key"""
        self.health = KeyHealth.ERROR
        self.circuit_breaker_reset_time = datetime.now(timezone.utc) + timedelta(minutes=timeout_minutes)
        logger.warning(f"Key {self.id} circuit breaker triggered, will reset at {self.circuit_breaker_reset_time}")
    
    def get_success_rate(self) -> float:
        """Calculate success rate for this key"""
        if self.metrics.total_requests == 0:
            return 0.0
        return self.metrics.successful_requests / self.metrics.total_requests
    
    def get_weight(self) -> float:
        """Calculate dynamic weight based on performance"""
        base_weight = self.weight
        success_rate = self.get_success_rate()
        
        # Adjust weight based on recent performance
        if self.metrics.consecutive_failures > 3:
            return base_weight * 0.1
        elif self.metrics.consecutive_failures > 0:
            return base_weight * 0.5
        elif success_rate > 0.95:
            return base_weight * 1.2
        
        return base_weight

class KeyPoolManager:
    """Manages a pool of Datadog API keys with intelligent rotation"""
    
    def __init__(
        self, 
        rotation_strategy: RotationStrategy = RotationStrategy.ADAPTIVE,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 10,
        health_check_interval: int = 300
    ):
        self.keys: List[KeyPair] = []
        self.rotation_strategy = rotation_strategy
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.health_check_interval = health_check_interval
        
        # Thread safety
        self._lock = threading.RLock()
        self._current_index = 0
        self._health_check_thread = None
        self._shutdown = False
        
        # Strategy-specific state
        self._lru_order: List[str] = []
        
        logger.info(f"KeyPoolManager initialized with strategy: {rotation_strategy.value}")
    
    def add_key(self, key_pair: KeyPair):
        """Add a key pair to the pool"""
        with self._lock:
            self.keys.append(key_pair)
            self._lru_order.append(key_pair.id)
            logger.info(f"Added key {key_pair.id} to pool, total keys: {len(self.keys)}")
    
    def remove_key(self, key_id: str):
        """Remove a key pair from the pool"""
        with self._lock:
            self.keys = [k for k in self.keys if k.id != key_id]
            if key_id in self._lru_order:
                self._lru_order.remove(key_id)
            logger.info(f"Removed key {key_id} from pool, remaining keys: {len(self.keys)}")
    
    def get_available_keys(self) -> List[KeyPair]:
        """Get all available keys"""
        with self._lock:
            return [k for k in self.keys if k.is_available()]
    
    def get_key_by_strategy(self) -> Optional[KeyPair]:
        """Select a key based on the configured strategy"""
        available_keys = self.get_available_keys()
        
        if not available_keys:
            logger.error("No available keys for selection")
            return None
        
        with self._lock:
            if self.rotation_strategy == RotationStrategy.ROUND_ROBIN:
                return self._select_round_robin(available_keys)
            elif self.rotation_strategy == RotationStrategy.LEAST_RECENTLY_USED:
                return self._select_lru(available_keys)
            elif self.rotation_strategy == RotationStrategy.WEIGHTED:
                return self._select_weighted(available_keys)
            elif self.rotation_strategy == RotationStrategy.ADAPTIVE:
                return self._select_adaptive(available_keys)
            elif self.rotation_strategy == RotationStrategy.RANDOM:
                return self._select_random(available_keys)
            else:
                return available_keys[0]  # Fallback
    
    def _select_round_robin(self, available_keys: List[KeyPair]) -> KeyPair:
        """Round robin key selection"""
        if not available_keys:
            return None
        
        key = available_keys[self._current_index % len(available_keys)]
        self._current_index = (self._current_index + 1) % len(available_keys)
        return key
    
    def _select_lru(self, available_keys: List[KeyPair]) -> KeyPair:
        """Least recently used key selection"""
        if not available_keys:
            return None
        
        # Sort by last used time (None values first)
        sorted_keys = sorted(
            available_keys,
            key=lambda k: k.metrics.last_used or datetime.min.replace(tzinfo=timezone.utc)
        )
        
        selected_key = sorted_keys[0]
        
        # Update LRU order
        if selected_key.id in self._lru_order:
            self._lru_order.remove(selected_key.id)
        self._lru_order.append(selected_key.id)
        
        return selected_key
    
    def _select_weighted(self, available_keys: List[KeyPair]) -> KeyPair:
        """Weighted random key selection based on performance"""
        if not available_keys:
            return None
        
        weights = [key.get_weight() for key in available_keys]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return random.choice(available_keys)
        
        # Weighted random selection
        r = random.random() * total_weight
        cumulative = 0
        for key, weight in zip(available_keys, weights):
            cumulative += weight
            if r <= cumulative:
                return key
        
        return available_keys[-1]  # Fallback
    
    def _select_adaptive(self, available_keys: List[KeyPair]) -> KeyPair:
        """Adaptive selection based on current conditions"""
        if not available_keys:
            return None
        
        # Check if any keys are under rate limit pressure
        rate_limited_recently = [
            k for k in self.keys 
            if k.metrics.last_rate_limit and 
            (datetime.now(timezone.utc) - k.metrics.last_rate_limit) < timedelta(minutes=30)
        ]
        
        if rate_limited_recently:
            # Use weighted selection to avoid problematic keys
            return self._select_weighted(available_keys)
        else:
            # Use LRU for balanced distribution
            return self._select_lru(available_keys)
    
    def _select_random(self, available_keys: List[KeyPair]) -> KeyPair:
        """Random key selection"""
        return random.choice(available_keys) if available_keys else None
    
    def record_key_event(self, key_id: str, event_type: str, **kwargs):
        """Record an event for a specific key"""
        with self._lock:
            key = next((k for k in self.keys if k.id == key_id), None)
            if not key:
                logger.warning(f"Key {key_id} not found for event recording")
                return
            
            if event_type == "success":
                key.record_success(kwargs.get("response_time", 0.0))
            elif event_type == "rate_limit":
                key.record_rate_limit(kwargs.get("reset_time"))
            elif event_type == "error":
                key.record_error(kwargs.get("error_type", "unknown"))
                
                # Check circuit breaker threshold
                if key.metrics.consecutive_failures >= self.circuit_breaker_threshold:
                    key.trigger_circuit_breaker(self.circuit_breaker_timeout)
    
    def get_pool_status(self) -> Dict:
        """Get comprehensive status of the key pool"""
        with self._lock:
            status = {
                "total_keys": len(self.keys),
                "available_keys": len(self.get_available_keys()),
                "rotation_strategy": self.rotation_strategy.value,
                "keys": []
            }
            
            for key in self.keys:
                key_status = {
                    "id": key.id,
                    "health": key.health.value,
                    "success_rate": key.get_success_rate(),
                    "total_requests": key.metrics.total_requests,
                    "consecutive_failures": key.metrics.consecutive_failures,
                    "last_used": key.metrics.last_used.isoformat() if key.metrics.last_used else None,
                    "average_response_time": key.metrics.average_response_time,
                    "weight": key.get_weight()
                }
                status["keys"].append(key_status)
            
            return status
    
    def start_health_monitoring(self):
        """Start background health monitoring thread"""
        if self._health_check_thread is None or not self._health_check_thread.is_alive():
            self._health_check_thread = threading.Thread(
                target=self._health_check_loop,
                daemon=True
            )
            self._health_check_thread.start()
            logger.info("Health monitoring thread started")
    
    def stop_health_monitoring(self):
        """Stop background health monitoring"""
        self._shutdown = True
        if self._health_check_thread and self._health_check_thread.is_alive():
            self._health_check_thread.join(timeout=5)
        logger.info("Health monitoring stopped")
    
    def _health_check_loop(self):
        """Background health check loop"""
        while not self._shutdown:
            try:
                self._perform_health_checks()
                time.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health check error: {e}")
                time.sleep(60)  # Longer sleep on error
    
    def _perform_health_checks(self):
        """Perform health checks on all keys"""
        with self._lock:
            for key in self.keys:
                if key.health == KeyHealth.TESTING:
                    # TODO: Implement actual API health check
                    # For now, just mark as healthy after a delay
                    if (datetime.now(timezone.utc) - (key.metrics.last_error or datetime.min.replace(tzinfo=timezone.utc))) > timedelta(minutes=5):
                        key.health = KeyHealth.HEALTHY
                        logger.info(f"Key {key.id} health check passed")


def load_keys_from_environment() -> List[KeyPair]:
    """Load multiple API key pairs from environment variables"""
    keys = []
    
    # Load primary key (backwards compatibility)
    api_key = os.getenv("DD_API_KEY") or os.getenv("DATADOG_API_KEY")
    app_key = os.getenv("DD_APP_KEY") or os.getenv("DATADOG_APP_KEY") 
    site = os.getenv("DD_SITE") or os.getenv("DATADOG_SITE") or "us3.datadoghq.com"
    
    if api_key and app_key:
        keys.append(KeyPair(
            id="primary",
            api_key=api_key,
            app_key=app_key,
            site=site
        ))
    
    # Load additional numbered keys
    i = 2
    while True:
        api_key = os.getenv(f"DD_API_KEY_{i}") or os.getenv(f"DATADOG_API_KEY_{i}")
        app_key = os.getenv(f"DD_APP_KEY_{i}") or os.getenv(f"DATADOG_APP_KEY_{i}")
        site = os.getenv(f"DD_SITE_{i}") or os.getenv(f"DATADOG_SITE_{i}") or "us3.datadoghq.com"
        
        if not api_key or not app_key:
            break
            
        keys.append(KeyPair(
            id=f"key_{i}",
            api_key=api_key,
            app_key=app_key,
            site=site
        ))
        i += 1
    
    # Try JSON format as alternative
    if not keys:
        json_keys = os.getenv("DD_API_KEYS_JSON")
        if json_keys:
            try:
                key_data = json.loads(json_keys)
                for i, key_info in enumerate(key_data):
                    keys.append(KeyPair(
                        id=f"json_key_{i+1}",
                        api_key=key_info.get("api_key"),
                        app_key=key_info.get("app_key"),
                        site=key_info.get("site", "us3.datadoghq.com")
                    ))
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse DD_API_KEYS_JSON: {e}")
    
    if not keys:
        logger.error("No Datadog API keys found in environment variables")
        raise ValueError("At least one valid API key pair is required")
    
    logger.info(f"Loaded {len(keys)} API key pairs from environment")
    for key in keys:
        logger.info(f"Key {key.id}: site={key.site}")
    
    return keys


def get_rotation_config() -> Dict:
    """Get key rotation configuration from environment"""
    return {
        "strategy": RotationStrategy(
            os.getenv("DD_KEY_ROTATION_STRATEGY", "adaptive").lower()
        ),
        "circuit_breaker_threshold": int(
            os.getenv("DD_CIRCUIT_BREAKER_THRESHOLD", "5")
        ),
        "circuit_breaker_timeout": int(
            os.getenv("DD_CIRCUIT_BREAKER_TIMEOUT", "10")
        ),
        "health_check_interval": int(
            os.getenv("DD_HEALTH_CHECK_INTERVAL", "300")
        ),
        "rate_limit_backoff_factor": float(
            os.getenv("DD_RATE_LIMIT_BACKOFF_FACTOR", "2.0")
        ),
        "max_retry_delay": int(
            os.getenv("DD_MAX_RETRY_DELAY", "300")
        )
    }


def detect_rate_limit_error(exception) -> Tuple[bool, Optional[datetime]]:
    """
    Detect if an exception is due to rate limiting and extract reset time
    
    Returns:
        (is_rate_limited, reset_time)
    """
    error_str = str(exception).lower()
    
    # Check for common rate limit indicators
    rate_limit_indicators = [
        "rate limit",
        "429",
        "too many requests", 
        "quota exceeded",
        "throttled"
    ]
    
    if any(indicator in error_str for indicator in rate_limit_indicators):
        # Try to extract reset time from headers or error message
        # This would need to be adapted based on actual Datadog API responses
        reset_time = datetime.now(timezone.utc) + timedelta(hours=1)  # Default
        return True, reset_time
    
    return False, None


def create_retry_decorator(key_pool: KeyPoolManager, max_retries: int = 3):
    """Create a retry decorator that uses key rotation on failures"""
    
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                # Get a key for this attempt
                key_pair = key_pool.get_key_by_strategy()
                if not key_pair:
                    logger.error("No available keys for retry attempt")
                    if last_exception:
                        raise last_exception
                    else:
                        raise RuntimeError("No available API keys")
                
                try:
                    start_time = time.time()
                    
                    # Execute function with selected key
                    result = func(key_pair, *args, **kwargs)
                    
                    # Record success
                    response_time = time.time() - start_time
                    key_pool.record_key_event(
                        key_pair.id, 
                        "success", 
                        response_time=response_time
                    )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if it's a rate limit error
                    is_rate_limited, reset_time = detect_rate_limit_error(e)
                    
                    if is_rate_limited:
                        key_pool.record_key_event(
                            key_pair.id,
                            "rate_limit",
                            reset_time=reset_time
                        )
                        logger.warning(f"Rate limit hit for key {key_pair.id}, trying next key")
                        continue
                    else:
                        # Record other errors
                        key_pool.record_key_event(
                            key_pair.id,
                            "error", 
                            error_type=type(e).__name__
                        )
                        
                        # Don't retry on authentication errors
                        if "401" in str(e) or "403" in str(e):
                            logger.error(f"Authentication error with key {key_pair.id}: {e}")
                            raise
                        
                        if attempt == max_retries - 1:
                            raise
                        
                        logger.warning(f"Error with key {key_pair.id}, retrying: {e}")
                        time.sleep(2 ** attempt)  # Exponential backoff
            
            # If we get here, all retries failed
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator