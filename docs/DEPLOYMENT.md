# Deployment Guide - Enhanced Datadog MCP Server

This guide covers various deployment options for the Enhanced Datadog MCP Server.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Claude Desktop Integration](#claude-desktop-integration)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Local Development

### Prerequisites

- Python 3.11+
- Datadog API and Application keys
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd datadog-mcp-server-enhanced
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Datadog credentials
   ```

4. **Run the server**
   ```bash
   python src/datadog_mcp_server.py
   ```

### Development Scripts

Use the provided scripts for development:

```bash
# Run all tests
./scripts/run_tests.sh

# Build and run with Docker
./scripts/build_and_run.sh
```

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Start the service**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f datadog-mcp-server
   ```

4. **Stop the service**
   ```bash
   docker-compose down
   ```

### Using Docker directly

1. **Build the image**
   ```bash
   docker build -t datadog-mcp-server .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name datadog-mcp-server \
     -p 8080:8080 \
     -e DATADOG_API_KEY=your_api_key \
     -e DATADOG_APP_KEY=your_app_key \
     datadog-mcp-server
   ```

### Docker Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATADOG_API_KEY` | ✅ | - | Datadog API key |
| `DATADOG_APP_KEY` | ✅ | - | Datadog application key |
| `DATADOG_SITE` | ❌ | `datadoghq.com` | Datadog site |
| `MCP_SERVER_HOST` | ❌ | `0.0.0.0` | Server bind address |
| `MCP_SERVER_PORT` | ❌ | `8080` | Server port |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

## Production Deployment

### Security Considerations

1. **API Key Management**
   ```bash
   # Use secrets management
   kubectl create secret generic datadog-keys \
     --from-literal=api-key=your_api_key \
     --from-literal=app-key=your_app_key
   ```

2. **Network Security**
   - Use HTTPS with proper TLS certificates
   - Implement proper firewall rules
   - Use VPN or private networks when possible

3. **Access Control**
   - Implement authentication middleware
   - Use API gateways for rate limiting
   - Monitor access logs

### Kubernetes Deployment

1. **Create namespace**
   ```bash
   kubectl create namespace datadog-mcp
   ```

2. **Deploy secrets**
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: datadog-keys
     namespace: datadog-mcp
   type: Opaque
   data:
     api-key: <base64-encoded-api-key>
     app-key: <base64-encoded-app-key>
   ```

3. **Deploy application**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: datadog-mcp-server
     namespace: datadog-mcp
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: datadog-mcp-server
     template:
       metadata:
         labels:
           app: datadog-mcp-server
       spec:
         containers:
         - name: datadog-mcp-server
           image: datadog-mcp-server:latest
           ports:
           - containerPort: 8080
           env:
           - name: DATADOG_API_KEY
             valueFrom:
               secretKeyRef:
                 name: datadog-keys
                 key: api-key
           - name: DATADOG_APP_KEY
             valueFrom:
               secretKeyRef:
                 name: datadog-keys
                 key: app-key
           resources:
             requests:
               memory: "256Mi"
               cpu: "250m"
             limits:
               memory: "512Mi"
               cpu: "500m"
           livenessProbe:
             httpGet:
               path: /health
               port: 8080
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /health
               port: 8080
             initialDelaySeconds: 5
             periodSeconds: 5
   ```

4. **Create service**
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: datadog-mcp-service
     namespace: datadog-mcp
   spec:
     selector:
       app: datadog-mcp-server
     ports:
     - protocol: TCP
       port: 80
       targetPort: 8080
     type: ClusterIP
   ```

### AWS ECS Deployment

1. **Create task definition**
   ```json
   {
     "family": "datadog-mcp-server",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "datadog-mcp-server",
         "image": "your-registry/datadog-mcp-server:latest",
         "portMappings": [
           {
             "containerPort": 8080,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "DATADOG_SITE",
             "value": "datadoghq.com"
           }
         ],
         "secrets": [
           {
             "name": "DATADOG_API_KEY",
             "valueFrom": "arn:aws:secretsmanager:region:account:secret:datadog-api-key"
           },
           {
             "name": "DATADOG_APP_KEY",
             "valueFrom": "arn:aws:secretsmanager:region:account:secret:datadog-app-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/datadog-mcp-server",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

## Claude Desktop Integration

### Configuration

Add to your Claude Desktop MCP configuration file:

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "datadog": {
      "command": "python",
      "args": ["/path/to/datadog-mcp-server/src/datadog_mcp_server.py"],
      "env": {
        "DATADOG_API_KEY": "your_api_key",
        "DATADOG_APP_KEY": "your_app_key",
        "DATADOG_SITE": "datadoghq.com"
      }
    }
  }
}
```

### Remote Server Configuration

For remote deployments, use HTTP transport:

```json
{
  "mcpServers": {
    "datadog-remote": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-http",
        "http://your-server:8080/mcp/"
      ]
    }
  }
}
```

## Monitoring and Maintenance

### Health Checks

The server provides health check endpoints:

```bash
# Basic health check
curl http://localhost:8080/health

# Detailed status
curl http://localhost:8080/status
```

### Logging

Configure logging levels:

```bash
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

Log locations:
- Docker: `docker logs datadog-mcp-server`
- Local: Console output
- Production: Configure log aggregation

### Metrics and Monitoring

Monitor key metrics:

1. **Server Metrics**
   - Request rate and response times
   - Error rates and types
   - Memory and CPU usage

2. **Datadog API Metrics**
   - API call success rates
   - Rate limit usage
   - Authentication failures

3. **Business Metrics**
   - Tool usage patterns
   - Query performance
   - User activity

### Backup and Recovery

1. **Configuration Backup**
   ```bash
   # Backup environment configuration
   cp .env .env.backup.$(date +%Y%m%d)
   ```

2. **Container Recovery**
   ```bash
   # Restart failed container
   docker-compose restart datadog-mcp-server
   
   # Full recreation
   docker-compose down
   docker-compose up -d
   ```

### Troubleshooting

Common issues and solutions:

1. **Authentication Errors**
   ```bash
   # Verify API keys
   curl -H "DD-API-KEY: $DATADOG_API_KEY" \
        -H "DD-APPLICATION-KEY: $DATADOG_APP_KEY" \
        "https://api.datadoghq.com/api/v1/validate"
   ```

2. **Connection Issues**
   ```bash
   # Test server connectivity
   curl -v http://localhost:8080/mcp/
   
   # Check container logs
   docker logs datadog-mcp-server
   ```

3. **Performance Issues**
   ```bash
   # Monitor resource usage
   docker stats datadog-mcp-server
   
   # Check API rate limits
   # Review query complexity and frequency
   ```

### Updates and Maintenance

1. **Update Process**
   ```bash
   # Pull latest changes
   git pull origin main
   
   # Rebuild and restart
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

2. **Dependency Updates**
   ```bash
   # Update Python dependencies
   pip install -r requirements.txt --upgrade
   
   # Update Docker base image
   docker build --no-cache -t datadog-mcp-server .
   ```

3. **Security Updates**
   - Regularly rotate API keys
   - Update base images and dependencies
   - Review access logs for anomalies
   - Monitor security advisories

## Performance Optimization

### Caching

Implement caching for frequently accessed data:

```python
# Example Redis caching
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)

def cached_query(query, ttl=300):
    cached_result = cache.get(query)
    if cached_result:
        return json.loads(cached_result)
    
    result = execute_query(query)
    cache.setex(query, ttl, json.dumps(result))
    return result
```

### Connection Pooling

Use connection pooling for better performance:

```python
from datadog_api_client import ApiClient, Configuration
from urllib3.util.retry import Retry
from urllib3.poolmanager import PoolManager

# Configure connection pooling
configuration = Configuration()
configuration.connection_pool_maxsize = 20
```

### Load Balancing

For high availability, deploy multiple instances:

```yaml
# Docker Compose with multiple replicas
version: '3.8'
services:
  datadog-mcp-server:
    build: .
    deploy:
      replicas: 3
    ports:
      - "8080-8082:8080"
```

This completes the deployment guide for the Enhanced Datadog MCP Server.

