# 🔄 Datadog API Key Rotation Guide

## Overview

The Datadog MCP Server now includes intelligent API key rotation to handle rate limiting and provide high availability. This system automatically rotates between multiple API key pairs to maximize throughput and ensure service continuity.

## 🔧 Configuration

### Environment Variables

#### Basic Configuration (Backwards Compatible)
```bash
# Primary key (existing format)
DD_API_KEY=your_primary_api_key
DD_APP_KEY=your_primary_app_key
DD_SITE=datadoghq.com
```

#### Multiple Key Configuration
```bash
# Primary key
DD_API_KEY=key_1_api_value
DD_APP_KEY=key_1_app_value
DD_SITE=datadoghq.com

# Additional keys
DD_API_KEY_2=key_2_api_value
DD_APP_KEY_2=key_2_app_value
DD_SITE_2=datadoghq.com

DD_API_KEY_3=key_3_api_value
DD_APP_KEY_3=key_3_app_value
DD_SITE_3=us3.datadoghq.com

# Continue with DD_API_KEY_4, DD_API_KEY_5, etc.
```

#### JSON Configuration (Alternative)
```bash
DD_API_KEYS_JSON='[
  {"api_key": "key1", "app_key": "app1", "site": "datadoghq.com"},
  {"api_key": "key2", "app_key": "app2", "site": "us3.datadoghq.com"},
  {"api_key": "key3", "app_key": "app3", "site": "datadoghq.com"}
]'
```

### Key Rotation Settings

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `DD_KEY_ROTATION_STRATEGY` | Key selection strategy | `adaptive` | `round_robin`, `lru`, `weighted`, `adaptive`, `random` |
| `DD_CIRCUIT_BREAKER_THRESHOLD` | Failures before circuit breaker trips | `5` | Integer |
| `DD_CIRCUIT_BREAKER_TIMEOUT` | Circuit breaker timeout (minutes) | `10` | Integer |
| `DD_HEALTH_CHECK_INTERVAL` | Health check interval (seconds) | `300` | Integer |
| `DD_RATE_LIMIT_BACKOFF_FACTOR` | Exponential backoff multiplier | `2.0` | Float |
| `DD_MAX_RETRY_DELAY` | Maximum retry delay (seconds) | `300` | Integer |

## 🎯 Rotation Strategies

### Adaptive (Recommended)
**Best for:** Production environments with varying load patterns
- Automatically switches between LRU and weighted selection
- Uses weighted selection when rate limits are detected
- Falls back to LRU for balanced distribution during normal operation

```bash
DD_KEY_ROTATION_STRATEGY=adaptive
```

### Round Robin
**Best for:** Predictable load distribution
- Cycles through keys in order
- Ensures equal usage across all keys
- Simple and predictable

```bash
DD_KEY_ROTATION_STRATEGY=round_robin
```

### Least Recently Used (LRU)
**Best for:** Maximizing key availability
- Uses keys that haven't been used recently
- Allows rate-limited keys time to recover
- Good for bursty workloads

```bash
DD_KEY_ROTATION_STRATEGY=lru
```

### Weighted
**Best for:** Performance-based selection
- Prioritizes keys with better performance metrics
- Reduces usage of underperforming keys
- Adapts to key performance over time

```bash
DD_KEY_ROTATION_STRATEGY=weighted
```

### Random
**Best for:** Simple load distribution
- Random key selection
- No state tracking overhead
- Good for high-concurrency scenarios

```bash
DD_KEY_ROTATION_STRATEGY=random
```

## 📊 Monitoring & Observability

### Health Check Tool
```json
{
  "name": "server_health_check",
  "arguments": {}
}
```

**Response includes key rotation status:**
```json
{
  "status": "healthy",
  "key_rotation": {
    "enabled": true,
    "total_keys": 3,
    "available_keys": 2,
    "rotation_strategy": "adaptive"
  }
}
```

### Key Pool Status Tool
```json
{
  "name": "get_key_pool_status",
  "arguments": {}
}
```

**Detailed response:**
```json
{
  "status": "success",
  "total_keys": 3,
  "available_keys": 2,
  "rotation_strategy": "adaptive",
  "keys": [
    {
      "id": "primary",
      "health": "healthy",
      "success_rate": 0.95,
      "total_requests": 150,
      "consecutive_failures": 0,
      "average_response_time": 0.245
    },
    {
      "id": "key_2", 
      "health": "rate_limited",
      "success_rate": 0.88,
      "total_requests": 89,
      "consecutive_failures": 0,
      "average_response_time": 0.312
    }
  ],
  "recommendations": [
    "ℹ️ 1 keys currently unavailable",
    "⚠️ Key key_2 temporarily rate limited"
  ]
}
```

## 🚀 Performance Benefits

### Throughput Increase
- **Single Key**: ~100 requests/hour (Datadog's typical limit)
- **3 Keys**: ~300 requests/hour 
- **5 Keys**: ~500 requests/hour

### Rate Limit Handling
- **Before**: Manual intervention required on rate limits
- **After**: Automatic failover to available keys
- **Recovery**: Automatic key reactivation when limits reset

### Reliability Improvements
- **Fault Tolerance**: Service continues if individual keys fail
- **Zero Downtime**: Hot-swappable key management
- **Circuit Breaking**: Automatic isolation of problematic keys

## 🛠️ Implementation Examples

### Docker Deployment
```dockerfile
ENV DD_API_KEY=primary_key_here
ENV DD_APP_KEY=primary_app_key_here
ENV DD_API_KEY_2=secondary_key_here
ENV DD_APP_KEY_2=secondary_app_key_here
ENV DD_KEY_ROTATION_STRATEGY=adaptive
ENV DD_CIRCUIT_BREAKER_THRESHOLD=3
```

### Kubernetes ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: datadog-mcp-config
data:
  DD_API_KEY: "primary_key_here"
  DD_APP_KEY: "primary_app_key_here"
  DD_API_KEY_2: "secondary_key_here"
  DD_APP_KEY_2: "secondary_app_key_here"
  DD_KEY_ROTATION_STRATEGY: "adaptive"
  DD_HEALTH_CHECK_INTERVAL: "300"
```

### Environment File (.env)
```bash
# Primary Datadog keys
DD_API_KEY=your_primary_api_key
DD_APP_KEY=your_primary_app_key

# Secondary keys for rate limit avoidance
DD_API_KEY_2=your_secondary_api_key
DD_APP_KEY_2=your_secondary_app_key
DD_API_KEY_3=your_tertiary_api_key
DD_APP_KEY_3=your_tertiary_app_key

# Rotation configuration
DD_KEY_ROTATION_STRATEGY=adaptive
DD_CIRCUIT_BREAKER_THRESHOLD=5
DD_HEALTH_CHECK_INTERVAL=300

# Debug settings
MCP_DEBUG_LEVEL=INFO
MCP_DEBUG_TIMING=true
```

## 🔍 Troubleshooting

### Common Issues

#### No Keys Available
**Symptom**: "No available keys for selection" errors
**Causes**:
- All keys are rate limited
- Authentication failures on all keys
- Invalid key configurations

**Solutions**:
1. Check key validity: `get_key_pool_status`
2. Verify API key permissions in Datadog
3. Wait for rate limit cooldown periods
4. Add additional key pairs

#### High Failure Rates
**Symptom**: Low success rates in key pool status
**Causes**:
- Network connectivity issues
- API endpoint problems
- Incorrect query syntax

**Solutions**:
1. Check network connectivity
2. Verify Datadog service status
3. Review query patterns and syntax
4. Adjust circuit breaker thresholds

#### Rotation Not Working
**Symptom**: Always using the same key
**Solutions**:
1. Verify multiple keys are configured
2. Check rotation strategy setting
3. Ensure keys have different IDs
4. Review debug logs for rotation events

### Debug Logging
```bash
# Enable detailed key rotation logging
export MCP_DEBUG_LEVEL=DEBUG
export MCP_DEBUG_TIMING=true
export MCP_DEBUG_REQUESTS=true
```

### Key Validation
Each key is automatically tested on startup. Failed keys are marked as `DISABLED`:

```bash
# Check logs for key validation results
2025-09-24 15:30:00 - Key primary: site=datadoghq.com
2025-09-24 15:30:00 - Key key_2: site=us3.datadoghq.com  
2025-09-24 15:30:01 - Key key_2 test successful, marking as healthy
2025-09-24 15:30:01 - Loaded 2 API key pairs from environment
```

## 🔒 Security Considerations

### Key Management
- Store keys in secure environment variable systems
- Rotate keys regularly (recommended: monthly)
- Use different keys for different environments
- Monitor key usage in Datadog admin panel

### Logging Safety
- API keys are automatically masked in debug logs
- Set `MCP_DEBUG_MASK_SENSITIVE=true` (default)
- Review logs before sharing for troubleshooting

### Access Control
- Use least privilege principle for API keys
- Grant only required permissions:
  - `metrics_read` for metrics access
  - `logs_read` for log access  
  - `monitors_read` for monitor access

## 📈 Best Practices

### Production Setup
1. **Use 3-5 key pairs** for optimal balance of throughput and complexity
2. **Choose adaptive strategy** for automatic optimization
3. **Set conservative circuit breaker thresholds** (3-5 failures)
4. **Monitor key pool status** regularly
5. **Set up alerts** for key pool health

### Development Setup
1. **Use 2 key pairs** minimum for testing rotation
2. **Enable debug logging** for troubleshooting
3. **Use round_robin strategy** for predictable behavior
4. **Test rate limit scenarios** with high-volume queries

### Key Rotation Schedule
- **Daily**: Monitor key pool health
- **Weekly**: Review usage patterns and performance  
- **Monthly**: Rotate API keys for security
- **Quarterly**: Evaluate rotation strategy effectiveness

## 🎯 Migration Guide

### From Single Key to Multi-Key

#### Step 1: Add Additional Keys
```bash
# Keep existing keys (no changes needed)
DD_API_KEY=existing_key
DD_APP_KEY=existing_app_key

# Add new keys
DD_API_KEY_2=new_secondary_key
DD_APP_KEY_2=new_secondary_app_key
```

#### Step 2: Test Configuration
```bash
# Restart server and check health
curl -X POST http://localhost:8080/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_key_pool_status","arguments":{}}}'
```

#### Step 3: Monitor Performance
- Check key pool status regularly
- Monitor API response times
- Verify rate limit handling

#### Step 4: Optimize Strategy
```bash
# Try different strategies based on your usage patterns
DD_KEY_ROTATION_STRATEGY=adaptive  # Recommended for production
# or
DD_KEY_ROTATION_STRATEGY=lru       # Good for burst workloads
# or  
DD_KEY_ROTATION_STRATEGY=weighted  # Performance-based selection
```

### Zero-Downtime Migration
The key rotation system is designed for zero-downtime deployment:

1. **Backwards Compatible**: Single key setups continue to work
2. **Gradual Rollout**: Add keys one at a time
3. **Automatic Detection**: New keys are detected and used immediately
4. **Fallback Safe**: Falls back to single-key mode on configuration errors

This comprehensive key rotation system ensures your Datadog MCP server can handle high-volume log queries while maintaining resilience against rate limits and individual key failures.