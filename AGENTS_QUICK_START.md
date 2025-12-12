# 🎯 AGENTS.md - Quick Start Guide

**AGENTS.md is a task-specific playbook. Here's how to use it in 5 minutes.**

---

## What is AGENTS.md?

It's a reference guide with **6 specialized agents**, each solving ONE type of problem:

| Agent | When to Use | What You Get |
|-------|-----------|-------------|
| 🧪 Testing | Writing/improving tests | Template + checklist + test commands |
| 🔨 Tool Builder | Adding new MCP tools | Template + checklist + 15 validation steps |
| 📊 Resource Builder | Creating data resources | Template + checklist + URI patterns |
| 🎯 Prompt Builder | Building AI workflows | Template + checklist + decision trees |
| 📚 Documentation | Updating docs | Examples + checklist + formatting guide |
| 🐛 Debug | Fixing issues | Commands + solutions + troubleshooting checklist |

---

## How to Use It (5 Steps)

### Step 1: Know Your Task
What are you doing RIGHT NOW?

```
Am I...
  → Writing a test? → Go to Testing Agent (page 1)
  → Adding a tool? → Go to Tool Builder Agent (page 2)
  → Making a resource? → Go to Resource Builder Agent (page 3)
  → Creating a prompt? → Go to Prompt Builder Agent (page 4)
  → Updating docs? → Go to Documentation Agent (page 5)
  → Fixing a bug? → Go to Debug Agent (page 6)
```

### Step 2: Open AGENTS.md
Click on the section link from the Table of Contents.

### Step 3: Copy the Template
Each agent has a **TEMPLATE** section - it's code/structure you copy and customize.

Example from Tool Builder Agent:
```python
@mcp.tool
def new_datadog_tool(param1: str) -> Dict[str, Any]:
    # ... copy this whole block ...
```

### Step 4: Follow the Checklist
Each agent has a **CHECKLIST** like:
```
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3
```

Go down the list. Check off each item. Don't skip any!

### Step 5: Run Test Commands
Each agent has **test commands** you can copy and run:
```bash
pytest tests/ -v
```

When it passes, you're done! ✅

---

## Real Examples

### Example A: Add a New Tool Called `get_slos()`

```
Step 1: Identify task = "Add a new tool"
         → Go to Tool Builder Agent

Step 2: Read Mission = "Add new MCP tools..."

Step 3: Copy Template = @mcp.tool code block
        Modify:
        - Replace "new_datadog_tool" with "get_slos"
        - Replace param1 with your params
        - Replace SomeDatadogApi with SLOsApi

Step 4: Follow Checklist
        - [ ] Use @mcp.tool decorator ✓
        - [ ] Use @mcp_debug_decorator ✓
        - [ ] Validate parameters ✓
        - [ ] Use _execute_with_key_rotation() ✓
        (check off all 15 items)

Step 5: Run Tests
        pytest tests/test_datadog_mcp_server.py -v
        ✓ If green = DONE!
```

---

### Example B: Fix "No Available Keys" Error

```
Step 1: Identify task = "Fix an error"
         → Go to Debug & Troubleshooting Agent

Step 2: Read Mission = "Diagnose and resolve issues..."

Step 3: Find Issue = "No available keys for selection"
        (It's in section "2. Common Issues & Solutions")

Step 4: Follow Solution Steps
        - Run: curl -X POST http://localhost:8080/mcp/ ...
        - Run: env | grep DD_
        - Check for 401/403 errors
        (follow all the steps)

Step 5: Check Debug Checklist
        - [ ] Enable debug level ✓
        - [ ] Check logs for correlation IDs ✓
        - [ ] Verify environment variables ✓
        (check off all 10 items when done)
```

---

### Example C: Write Tests for `get_slos()`

```
Step 1: Identify task = "Write tests"
         → Go to Testing Agent

Step 2: Read Mission = "Create comprehensive tests..."

Step 3: Copy Template = Unit Tests code block
        Modify:
        - Replace TestNewFeature with TestGetSlos
        - Replace test_feature_behavior with test_get_slos_success

Step 4: Follow Checklist
        - [ ] Unit tests for functions ✓
        - [ ] Integration tests ✓
        - [ ] Edge case handling ✓
        (check off all 10 items)

Step 5: Run Tests
        pytest tests/ -v --cov=src
        Check:
        - All tests pass ✓
        - Coverage > 80% ✓
        - No flaky tests ✓
```

---

## Template vs Checklist vs Test Commands

### What's a Template?
**Code you copy and fill in.** Look for code blocks:
```python
@mcp.tool
def new_tool():
    # ← This whole block is a template
    # Copy it, then customize:
    # 1. Change function name
    # 2. Change parameters
    # 3. Change logic
```

### What's a Checklist?
**A todo list you check off as you go:**
```
- [ ] Item 1 (not done)
- [x] Item 2 (done)
- [ ] Item 3 (not done)
```

### What's a Test Command?
**Commands you copy and run in terminal:**
```bash
pytest tests/ -v                    # Run all tests
pytest tests/test_key_rotation.py   # Run specific test
```

When the command succeeds (shows ✓), your work is validated!

---

## Why AGENTS.md Exists

Without AGENTS.md, you'd need to:
- 🔍 Search the codebase to find examples
- 📖 Read documentation to understand patterns
- 🤔 Figure out best practices from scratch
- ✍️ Write code without a template
- 🧪 Create tests from zero
- ✓ Hope you didn't miss anything

With AGENTS.md, you:
- ✅ Pick your agent (1 minute)
- ✅ Copy the template (2 minutes)
- ✅ Follow the checklist (5-30 minutes depending on complexity)
- ✅ Run test commands (1 minute)
- ✅ Done! Your work is validated

**Result**: Faster, consistent, higher quality contributions.

---

## Common Questions

**Q: Do I read the whole AGENTS.md file?**  
A: No! Only read YOUR agent's section. Skip the rest.

**Q: Can I combine agents?**  
A: Yes! If you're adding a tool + tests + docs:
1. Tool Builder Agent (write tool)
2. Testing Agent (write tests)
3. Documentation Agent (update docs)

**Q: What if I don't follow the checklist?**  
A: You might miss important steps. The checklist ensures quality.

**Q: Can I modify the template?**  
A: Yes! The template shows best practices. Customize it for your needs.

**Q: What's a correlation_id?**  
A: A unique ID to track one request through all logs. Helps with debugging.

**Q: What's key rotation?**  
A: Automatic switching between multiple API keys to avoid rate limits. Use `_execute_with_key_rotation()` wrapper.

**Q: Why can't I hardcode DD_SITE?**  
A: Because different environments use different Datadog sites (us3.datadoghq.com, eu1, etc). Always read from environment variables.

---

## File Organization

```
AGENTS.md (THIS FILE'S STRUCTURE)
├─ Quick Start: How to Use This Guide (READ THIS FIRST)
├─ Real-World Examples (GET INSPIRED)
├─ [AGENT 1] Testing Agent
│  ├─ Mission
│  ├─ Templates
│  ├─ Checklist
│  └─ Test Commands
├─ [AGENT 2] Tool Builder Agent
│  ├─ Mission
│  ├─ Template
│  ├─ Checklist
│  └─ Available APIs to Expose
├─ [AGENT 3] Resource Builder Agent
│  ├─ Mission
│  ├─ Template
│  ├─ Checklist
│  └─ Resource Ideas
├─ [AGENT 4] Prompt Builder Agent
│  ├─ Mission
│  ├─ Template
│  ├─ Checklist
│  └─ Prompt Ideas
├─ [AGENT 5] Documentation Agent
│  ├─ Mission
│  ├─ Documentation Tasks
│  └─ Checklist
├─ [AGENT 6] Debug & Troubleshooting Agent
│  ├─ Mission
│  ├─ Debug Workflow
│  ├─ Common Issues & Solutions
│  └─ Debug Checklist
├─ Workflow Diagram
└─ Quick Reference
```

---

## TL;DR (Too Long; Didn't Read)

1. **Pick your agent** based on what you're doing
2. **Copy the template** from your agent's section
3. **Follow the checklist** (don't skip items)
4. **Run test commands** to validate
5. **Done!** ✅

Go open **AGENTS.md** and find your section. You've got this! 🚀
