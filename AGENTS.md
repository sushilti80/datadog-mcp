# 🤖 Agent Task Guidelines - Datadog MCP Server

This document provides specialized guidance for AI agents working on specific tasks for the Datadog MCP Server.

## 🚀 Quick Start: How to Use This Guide

### **Step 1: Identify What You Want to Do**
Pick ONE task from this list:
- ✅ **Write tests** → Go to [Testing Agent](#testing-agent)
- ✅ **Add a new tool** (API endpoint) → Go to [Tool Builder Agent](#tool-builder-agent)
- ✅ **Create a resource** (AI-friendly data view) → Go to [Resource Builder Agent](#resource-builder-agent)
- ✅ **Build a prompt** (AI workflow) → Go to [Prompt Builder Agent](#prompt-builder-agent)
- ✅ **Update documentation** → Go to [Documentation Agent](#documentation-agent)
- ✅ **Debug an issue** → Go to [Debug & Troubleshooting Agent](#debug--troubleshooting-agent)

### **Step 2: Read Your Agent's Mission**
Each agent section starts with a clear **Mission** statement telling you what to do.

### **Step 3: Copy the Template**
Each agent provides a **template** - copy it and fill in the blanks with your specific details.

### **Step 4: Follow the Checklist**
Go through the **checklist** line-by-line. Check off each item as you complete it. Don't skip any!

### **Step 5: Validate with Commands**
Each agent provides **test commands** and **success criteria** to verify your work is correct.

---

## 📋 Table of Contents

1. [Testing Agent](#testing-agent)
2. [Tool Builder Agent](#tool-builder-agent)
3. [Resource Builder Agent](#resource-builder-agent)
4. [Prompt Builder Agent](#prompt-builder-agent)
5. [Documentation Agent](#documentation-agent)
6. [Debug & Troubleshooting Agent](#debug--troubleshooting-agent)

---

## 💡 Real-World Examples

### Example 1: I Want to Add a New Tool
**Scenario**: You want to add a tool called `get_slos()` to fetch Service Level Objectives.

1. Go to **Tool Builder Agent** section
2. Copy the **Tool Template** (the `@mcp.tool` Python code)
3. Replace `new_datadog_tool` with `get_slos` 
4. Replace the docstring and logic with SLO API calls
5. Go through **Tool Building Checklist** - check off each item
6. Run test: `pytest tests/test_datadog_mcp_server.py -v`
7. Update `docs/API.md` with your new tool
8. Done! Your tool is now available to AI agents

### Example 2: I Want to Write Tests
**Scenario**: You want to test the new `get_slos()` tool.

1. Go to **Testing Agent** section
2. Copy the **Unit Tests template** code
3. Replace test name/details to match your tool
4. Add test cases for success, errors, edge cases
5. Go through **Testing Checklist** - check off each item
6. Run: `pytest tests/ -v`
7. Check: "Code coverage > 80%"
8. Done! Your tests are protecting the codebase

### Example 3: I Want to Create a Resource
**Scenario**: You want to create a resource showing SLO status: `datadog://slo-status/{slo_id}`

1. Go to **Resource Builder Agent** section
2. Copy the **Resource Template** Python code
3. Replace `{resource-type}` with `slo-status`
4. Replace identifier with `slo_id`
5. Fill in the logic to fetch and format SLO data
6. Go through **Resource Building Checklist** - check off each item
7. Test the URI pattern matches correctly
8. Update `docs/API.md` with example URIs
9. Done! Your resource is now available

### Example 4: I Need to Debug an Issue
**Scenario**: You see error "No available keys for selection"

1. Go to **Debug & Troubleshooting Agent** section
2. Find the matching issue: **"No available keys for selection"**
3. Follow the exact commands provided
4. Go through **Debug Checklist** - check off each item
5. Use the provided troubleshooting resources
6. Once fixed, verify with `pytest tests/test_key_rotation.py -v`
7. Done! Issue resolved

---

---

## 🧪 Testing Agent

### Mission
Create comprehensive tests for existing and new functionality, ensuring code quality and preventing regressions.

### Key Files
- `tests/test_key_rotation.py` - Key rotation system tests
- `tests/test_datadog_mcp_server.py` - Main server tests
- `tests/test_server_basic.py` - Basic functionality tests

### Testing Patterns

#### 1. Unit Tests for Key Rotation
```python
import unittest
from key_rotation import KeyPair, KeyPoolManager, RotationStrategy

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.key_pool = KeyPoolManager(
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
            circuit_breaker_threshold=3
        )
        self.key1 = KeyPair("test_1", "api_1", "app_1", site="us3.datadoghq.com")
        self.key_pool.add_key(self.key1)
    
    def test_feature_behavior(self):
        # Test implementation
        result = self.key_pool.get_key_by_strategy()
        self.assertEqual(result.id, "test_1")
```

#### 2. Integration Tests with Mocking
```python
from unittest.mock import Mock, patch
from datadog_mcp_server import DatadogMCPServer

@patch('datadog_mcp_server.ApiClient')
def test_api_call_with_rotation(mock_client):
    # Setup mock
    mock_api = Mock()
    mock_client.return_value = mock_api
    
    # Test tool call
    result = get_metrics("test.metric", hours_back=1)
    
    # Verify
    assert result["status"] == "success"
    mock_api.some_method.assert_called_once()
```

#### 3. Test Commands
```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_key_rotation.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run tests matching pattern
pytest tests/ -k "test_rotation" -v

# Run with debug output
pytest tests/ -v -s --log-cli-level=DEBUG
```

### Testing Checklist
- [ ] Unit tests for new functions/methods
- [ ] Integration tests for API calls
- [ ] Edge case handling (empty responses, rate limits, errors)
- [ ] Key rotation behavior under failure scenarios
- [ ] Environment variable loading and validation
- [ ] Mock external Datadog API calls
- [ ] Test all error paths and exception handling
- [ ] Verify debug logging at different levels
- [ ] Test concurrent requests (threading safety)
- [ ] Validate time range conversions

### Success Criteria
- All tests pass: `pytest tests/ -v`
- Code coverage > 80%: `pytest tests/ --cov=src`
- No flaky tests (run 10 times, all pass)
- Tests complete in < 30 seconds

---

## 🔨 Tool Builder Agent

### Mission
Add new MCP tools to expose additional Datadog APIs, following established patterns and conventions.

### Tool Template
```python
@mcp.tool
@mcp_debug_decorator("new_tool_name")
def new_datadog_tool(
    param1: str,
    param2: int = 10,
    hours_back: Optional[int] = None,
    minutes_back: Optional[int] = None
) -> Dict[str, Any]:
    """
    Brief description of what this tool does.
    
    Args:
        param1: Description of required parameter
        param2: Description of optional parameter (default: 10)
        hours_back: Number of hours back from now (optional)
        minutes_back: Number of minutes back from now (optional)
    
    Returns:
        Dictionary with status (success/error) and result data
    """
    correlation_id = str(uuid.uuid4())
    
    try:
        # Validate parameters
        if not param1:
            return {
                "status": "error",
                "error": "param1 is required",
                "error_type": "ValidationError",
                "correlation_id": correlation_id
            }
        
        # Calculate time range
        to_time = int(datetime.now(timezone.utc).timestamp())
        if minutes_back:
            from_time = int((datetime.now(timezone.utc) - timedelta(minutes=minutes_back)).timestamp())
        else:
            hours = hours_back or 1
            from_time = int((datetime.now(timezone.utc) - timedelta(hours=hours)).timestamp())
        
        # Execute with key rotation
        def _operation(key_pair: KeyPair, api_client: ApiClient):
            api = SomeDatadogApi(api_client)
            return api.some_method(
                param1=param1,
                param2=param2,
                _from=from_time,
                to=to_time
            )
        
        result = datadog_server._execute_with_key_rotation(
            "new_tool_operation",
            _operation
        )
        
        # Format response
        return {
            "status": "success",
            "data": result,
            "from_time": datetime.fromtimestamp(from_time, tz=timezone.utc).isoformat(),
            "to_time": datetime.fromtimestamp(to_time, tz=timezone.utc).isoformat(),
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        logger.error(f"Error in new_tool: {e}", exc_info=True)
        error_category = categorize_error(e)
        
        return {
            "status": "error",
            "error": str(e),
            "error_type": error_category,
            "correlation_id": correlation_id,
            "suggestion": get_error_suggestion(error_category)
        }
```

### Tool Building Checklist
- [ ] Use `@mcp.tool` decorator
- [ ] Add `@mcp_debug_decorator("tool_name")` for tracing
- [ ] Implement comprehensive docstring with Args/Returns
- [ ] Validate all required parameters
- [ ] Support flexible time ranges (hours_back, minutes_back)
- [ ] Use `_execute_with_key_rotation()` wrapper
- [ ] Return structured dict with `status` field
- [ ] Include `correlation_id` in all responses
- [ ] Categorize errors with `categorize_error()`
- [ ] Add helpful error suggestions
- [ ] Log operations with appropriate debug levels
- [ ] Convert timestamps to seconds (not milliseconds)
- [ ] Add unit tests in `tests/test_datadog_mcp_server.py`
- [ ] Update `docs/API.md` with tool documentation
- [ ] Test with actual Datadog API (integration test)

### Available Datadog APIs to Expose
Check the [Datadog API documentation](https://docs.datadoghq.com/api/latest/) for:
- Events API - Create, retrieve, and search events
- Service Level Objectives (SLOs) - Manage and query SLOs
- Downtimes - Schedule maintenance windows
- Synthetics - Synthetic monitoring tests
- RUM (Real User Monitoring) - Frontend performance data
- Security Monitoring - Security signals and rules
- CI Visibility - Pipeline and test analytics

---

## 📊 Resource Builder Agent

### Mission
Create smart MCP resources that provide formatted, AI-friendly data views of Datadog information.

### Resource Template
```python
@mcp.resource("datadog://{resource-type}/{identifier}")
def new_resource(identifier: str) -> str:
    """
    Provide formatted {resource-type} data for AI analysis.
    
    Args:
        identifier: The unique identifier for this resource
        
    Returns:
        Formatted string with comprehensive data and context
    """
    try:
        # Fetch data using existing tools
        result = get_datadog_data(identifier)
        
        if result["status"] != "success":
            return f"❌ Error fetching {identifier}: {result.get('error', 'Unknown error')}"
        
        # Format for AI readability
        output = f"📊 {resource-type.title()}: {identifier}\n"
        output += f"{'=' * 60}\n\n"
        
        # Add summary section
        output += "## Summary\n"
        output += f"Status: {result.get('status_info', 'Unknown')}\n"
        output += f"Last Updated: {result.get('last_update', 'N/A')}\n\n"
        
        # Add detailed data
        output += "## Detailed Information\n"
        for key, value in result.get('details', {}).items():
            output += f"- {key}: {value}\n"
        
        # Add AI insights section
        output += "\n## AI Analysis Recommendations\n"
        output += "- Analyze trends in the data\n"
        output += "- Compare against baseline metrics\n"
        output += "- Identify anomalies or patterns\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Resource error for {identifier}: {e}")
        return f"❌ Error processing resource: {str(e)}"
```

### Resource Building Checklist
- [ ] Use `@mcp.resource("uri://pattern")` decorator
- [ ] URI pattern includes dynamic parameters in `{brackets}`
- [ ] Return formatted string (not dict) for AI readability
- [ ] Include clear section headers with visual separators
- [ ] Provide summary statistics at the top
- [ ] Format timestamps as ISO 8601 for clarity
- [ ] Add context and interpretation hints for AI
- [ ] Handle errors gracefully with helpful messages
- [ ] Use emojis for visual parsing (📊 ✅ ❌ ⚠️ 💡)
- [ ] Keep response concise (< 5000 chars for typical use)
- [ ] Test resource URI pattern matching
- [ ] Document in `docs/API.md` with example URIs

### Resource Ideas
- `datadog://service-map/{service}` - Service dependency visualization
- `datadog://alert-summary/{time-range}` - Recent alerts aggregation
- `datadog://performance-report/{service}/{date}` - Daily performance digest
- `datadog://cost-analysis/{time-range}` - Infrastructure cost breakdown
- `datadog://security-posture/{service}` - Security findings summary

---

## 🎯 Prompt Builder Agent

### Mission
Create AI-guided workflows that help agents perform complex multi-step Datadog investigations.

### Prompt Template
```python
@mcp.prompt("datadog-workflow-name")
def workflow_prompt(
    context_param: str,
    severity: str = "medium",
    time_range: str = "24h"
) -> str:
    """
    AI-guided workflow for {specific investigation type}.
    
    Args:
        context_param: Main context for the investigation
        severity: Investigation depth (low, medium, high, critical)
        time_range: Time range to analyze (e.g., "1h", "24h", "7d")
        
    Returns:
        Structured investigation workflow for AI agents
    """
    return f"""
🎯 **{Workflow Name}: {context_param}**

**Context**: {context_param}
**Severity**: {severity.upper()}
**Time Range**: {time_range}

---

## 📋 Investigation Steps

### 1. Initial Assessment 🔍
**Objective**: Establish baseline understanding

**Actions**:
- `get_metrics("relevant.metric{{context:{context_param}}}", hours_back=1)`
- `get_logs("service:{context_param} status:error", hours_back=1)`

**Expected Insights**:
- Current state vs normal baseline
- Recent error patterns or anomalies
- Resource utilization trends

---

### 2. Deep Dive Analysis 🔬
**Objective**: Identify root causes

**Actions**:
- Analyze specific subsystems or dependencies
- Correlate metrics with log patterns
- Check for cascading failures

**Decision Tree**:
- **If metric > threshold**: Investigate [specific area]
- **If errors > 5%**: Focus on [error category]
- **If resource constrained**: Check [resource type]

---

### 3. Impact Assessment 📊
**Objective**: Quantify business impact

**Actions**:
- Measure user-facing metrics
- Calculate SLO violations
- Estimate affected user count

---

### 4. Remediation Planning 🛠️
**Objective**: Define actionable next steps

**Immediate Actions**:
1. [Critical fix step 1]
2. [Critical fix step 2]

**Long-term Prevention**:
1. [Architectural improvement]
2. [Monitoring enhancement]

---

## ✅ Success Criteria
- Root cause identified with 80%+ confidence
- Actionable remediation plan provided
- Clear business impact assessment
- Preventive measures recommended

## 📝 Output Format
Provide:
1. **Root Cause** (with supporting evidence)
2. **Impact Estimate** (users, revenue, SLO)
3. **Remediation Steps** (immediate + long-term)
4. **Monitoring Gaps** (what to add)
"""
```

### Prompt Building Checklist
- [ ] Use `@mcp.prompt("kebab-case-name")` decorator
- [ ] Start with clear objective and context
- [ ] Break into numbered sequential steps
- [ ] Include specific tool calls with parameters
- [ ] Provide decision trees for branching logic
- [ ] Add "Expected Insights" for each step
- [ ] Define clear success criteria
- [ ] Specify output format requirements
- [ ] Use emojis for step identification
- [ ] Keep total prompt < 2000 tokens
- [ ] Test prompt with actual AI agent
- [ ] Document in `docs/API.md` with use cases

### Prompt Ideas
- `datadog-cost-optimization` - Identify resource waste and optimization opportunities
- `datadog-capacity-planning` - Forecast resource needs based on trends
- `datadog-security-audit` - Systematic security posture review
- `datadog-slo-analysis` - Deep dive on SLO violations and improvements
- `datadog-dependency-mapping` - Trace service dependencies and failure modes

---

## 📚 Documentation Agent

### Mission
Maintain comprehensive, accurate documentation for all server features and APIs.

### Documentation Tasks

#### 1. Update API.md
When adding tools/resources/prompts:
```markdown
### tool_name

Brief description of functionality.

**Parameters:**
- `param1` (string, required): Description
- `param2` (integer, optional): Description (default: 10)
- `hours_back` (integer, optional): Time range in hours (default: 1)

**Returns:**
- `status` (string): "success" or "error"
- `data` (object): Result data when successful
- `error` (string): Error message when failed

**Example Request:**
\`\`\`json
{
  "jsonrpc": "2.0",
  "id": "example-1",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "param1": "value",
      "param2": 20
    }
  }
}
\`\`\`

**Example Response:**
\`\`\`json
{
  "jsonrpc": "2.0",
  "id": "example-1",
  "result": {
    "status": "success",
    "data": {...}
  }
}
\`\`\`
```

#### 2. Update README.md
Add to appropriate sections:
- Features list (if major capability)
- Quick Start (if config required)
- Use Cases (if new workflow enabled)

#### 3. Update KEY_ROTATION.md
For key rotation changes:
- New environment variables
- Changed behavior
- Migration notes
- Troubleshooting tips

### Documentation Checklist
- [ ] Update `docs/API.md` with new tools/resources/prompts
- [ ] Add example requests and responses
- [ ] Update `README.md` if user-facing changes
- [ ] Update `.env.example` with new variables
- [ ] Add inline code comments for complex logic
- [ ] Update `AGENTS.md` if new patterns emerge
- [ ] Run spell check on markdown files
- [ ] Verify all code examples are valid
- [ ] Check all links work correctly
- [ ] Update version numbers where applicable

---

## 🐛 Debug & Troubleshooting Agent

### Mission
Diagnose and resolve issues with the MCP server, key rotation, or Datadog API integration.

### Debug Workflow

#### 1. Enable Debug Tracing
```bash
# Set in .env or export
export MCP_DEBUG_LEVEL=TRACE
export MCP_DEBUG_REQUESTS=true
export MCP_DEBUG_RESPONSES=true
export MCP_DEBUG_TIMING=true
export MCP_DEBUG_PARAMETERS=true

# Run server
python3 src/datadog_mcp_server.py
```

#### 2. Common Issues & Solutions

**Issue: "No available keys for selection"**
```bash
# Check key pool status
curl -X POST http://localhost:8080/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_key_pool_status"}}'

# Verify environment variables
env | grep DD_

# Check key authentication
# Look for 401/403 errors in logs
```

**Issue: "Rate limit exceeded"**
```python
# Check if keys are rotating
# Look for "Rate limit hit for key X, trying next key" in logs

# Verify rotation strategy
# Check DD_KEY_ROTATION_STRATEGY in .env

# Add more keys if needed
# Set DD_API_KEY_2, DD_API_KEY_3, etc.
```

**Issue: "Site configuration error"**
```bash
# Verify DD_SITE is set correctly
echo $DD_SITE

# Check it's not hardcoded
grep -r "datadoghq.com" src/ --exclude="*.pyc"

# Should only appear in default values for env loading
```

**Issue: "400 Bad Request" from MCP client**
```bash
# Check MCP protocol version compatibility
# Ensure FastMCP 2.10.6+

# Verify request format
# Use MCP_DEBUG_REQUESTS=true to see incoming requests

# Check for missing required parameters
```

#### 3. Testing Specific Components

**Test Key Rotation:**
```bash
pytest tests/test_key_rotation.py -v -s
```

**Test API Connectivity:**
```python
# Create test script
from key_rotation import load_keys_from_environment
keys = load_keys_from_environment()
print(f"Loaded {len(keys)} keys")
for key in keys:
    print(f"  - {key.id}: site={key.site}")
```

**Test Tool Execution:**
```bash
# Use curl with MCP protocol
curl -X POST http://localhost:8080/mcp/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "server_health_check",
      "arguments": {}
    }
  }'
```

### Debug Checklist
- [ ] Enable appropriate debug level for issue
- [ ] Check server logs for correlation IDs
- [ ] Verify environment variables are loaded
- [ ] Test with single key first (simpler)
- [ ] Check Datadog API status page
- [ ] Verify network connectivity to Datadog
- [ ] Test API keys with `curl` to Datadog directly
- [ ] Review recent code changes (git diff)
- [ ] Check for Python package version mismatches
- [ ] Test in clean virtual environment

### Troubleshooting Resources
- Datadog API Status: https://status.datadoghq.com/
- FastMCP Issues: https://github.com/jlowin/fastmcp/issues
- MCP Specification: https://modelcontextprotocol.io/
- Server logs: Check correlation_id for request tracing
- Key rotation logs: Look for "Key X selected" and "Key X failed"

---

## 🚀 Quick Reference

### Run Tests
```bash
pytest tests/ -v                          # All tests
pytest tests/test_key_rotation.py -v     # Key rotation only
pytest tests/ --cov=src                   # With coverage
```

### Run Server
```bash
python3 src/datadog_mcp_server.py        # Normal mode
MCP_DEBUG_LEVEL=TRACE python3 src/...   # Debug mode
```

### Build Docker
```bash
docker build -t datadog-mcp-server .
docker run --env-file .env -p 8080:8080 datadog-mcp-server
```

### Code Quality
```bash
black src/ tests/                         # Format code
flake8 src/ tests/                        # Lint code
pytest tests/ --cov=src --cov-report=html # Coverage report
```

---

## 📞 Need Help?

- Check `docs/API.md` for complete API reference
- Check `docs/KEY_ROTATION.md` for multi-key setup
- Check `.github/copilot-instructions.md` for code patterns
- Review `README.md` for general usage
- Look at existing tests in `tests/` for examples

---

## 🎯 Workflow Diagram

```
START: I have a task
  ↓
  Pick ONE from the 6 agents ↙
  ├─ Testing Agent?
  ├─ Tool Builder Agent?
  ├─ Resource Builder Agent?
  ├─ Prompt Builder Agent?
  ├─ Documentation Agent?
  └─ Debug & Troubleshooting Agent?
  ↓
Read Agent's MISSION statement
  ↓
Copy the TEMPLATE code
  ↓
Fill in your specific details
  ↓
Go through CHECKLIST ✓✓✓
  ↓
Run provided TEST COMMANDS
  ↓
Check SUCCESS CRITERIA
  ↓
DONE! 🎉
```

---

## ✅ Checklist for Using This Guide

When starting any task:

- [ ] I read the "Quick Start: How to Use This Guide" section above
- [ ] I identified which agent matches my task (Testing, Tool, Resource, Prompt, Doc, or Debug)
- [ ] I found my agent's section in the table of contents
- [ ] I read the agent's **Mission** statement
- [ ] I copied the **Template** code
- [ ] I customized the template with my specific details
- [ ] I have my agent's **Checklist** open and ready
- [ ] I'm going through the checklist item by item
- [ ] I've completed all checklist items
- [ ] I ran the provided **Test Commands** from my agent
- [ ] All **Success Criteria** are met
- [ ] I'm ready to commit/share my work

---

## 🆘 Still Confused?

### Common Questions

**Q: Which agent do I need?**  
A: Look at what you're trying to DO:
- Writing test code? → Testing Agent
- Writing @mcp.tool code? → Tool Builder Agent  
- Writing @mcp.resource code? → Resource Builder Agent
- Writing @mcp.prompt code? → Prompt Builder Agent
- Updating markdown docs? → Documentation Agent
- Fixing a bug/error? → Debug Agent

**Q: Do I need to read the whole file?**  
A: No! Just read YOUR agent's section. Skip the others.

**Q: What if my task doesn't fit one agent?**  
A: Combine agents. E.g., adding a new tool probably means:
1. Tool Builder Agent (write the tool)
2. Testing Agent (write tests)
3. Documentation Agent (update docs)

**Q: What are templates?**  
A: Code examples you copy and modify. Find them in your agent section - they're in code blocks like this:
```python
# This is a template - copy this and fill in the blanks
@mcp.tool
def your_tool_name():
    pass
```

**Q: What are checklists?**  
A: Step-by-step todo lists. Go through each item and check it off:
```
- [ ] Item 1 - do this first
- [ ] Item 2 - do this second
- [ ] Item 3 - do this third
```

**Q: What are test commands?**  
A: Pre-written commands that validate your work. Copy and run them in the terminal:
```bash
pytest tests/test_key_rotation.py -v  # Example test command
```

---

## 📞 Getting Help

1. **Read your agent's section** - it has all the answers
2. **Copy the template** - don't write from scratch
3. **Follow the checklist** - do it step by step
4. **Run test commands** - they verify your work
5. **Check success criteria** - confirm it's working

If you're still stuck, look at existing code in the codebase:
- Existing tools in `src/datadog_mcp_server.py`
- Existing tests in `tests/test_key_rotation.py`
- Existing docs in `docs/API.md`

**Remember**: All new tools MUST use `_execute_with_key_rotation()` wrapper and NEVER hardcode DD_SITE values!

---

## 📚 MCP Concepts Quick Reference

If you're new to MCP (Model Context Protocol), here's what each term means:

- **Tool** (`@mcp.tool`): A function AI agents can call. Like an API endpoint. Example: `get_metrics()`
- **Resource** (`@mcp.resource`): A formatted data view for AI agents. Has a URI like `datadog://logs/{query}`. Returns formatted text.
- **Prompt** (`@mcp.prompt`): A workflow guide that shows AI agents step-by-step how to solve a problem. Like a tutorial.
- **Decorator** (`@mcp.tool`, `@mcp.resource`, etc.): Python syntax that tells FastMCP "this is a tool/resource/prompt"
- **Key Rotation**: System that switches between multiple API keys automatically to avoid rate limits
- **Correlation ID**: A unique ID to track a request through logs
- **Error Categorization**: Sorting errors into types (API, Validation, Rate Limit, Network, etc.)

---
