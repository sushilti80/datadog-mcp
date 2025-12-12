# 🎯 Agent System Index

## All Documentation Files (In Order of Importance)

### 🌟 START HERE (5 minutes)
| File | What | When |
|------|------|------|
| **[AGENTS_QUICK_START.md](AGENTS_QUICK_START.md)** | Overview + 4 real examples | First time, quick reference |
| **[AGENT_DECISION_TREE.md](AGENT_DECISION_TREE.md)** | Visual flowcharts & decision trees | Decide which agent you need |

### 📖 Main Reference (30 min - 1 hour)
| File | What | When |
|------|------|------|
| **[AGENTS.md](AGENTS.md)** | Complete 6-agent guides with templates | When doing your specific task |
| **[WORKFLOW.md](WORKFLOW.md)** | Visual workflows + real scenarios | Understand the full process |

### 🏗️ Deep Dives (20-30 min)
| File | What | When |
|------|------|------|
| **[AGENT_SYSTEM_GUIDE.md](AGENT_SYSTEM_GUIDE.md)** | Complete system overview | Understand the whole picture |
| **[.github/copilot-instructions.md](.github/copilot-instructions.md)** | Architecture + patterns | Understand how it works |

### 📚 General Reference
| File | What | When |
|------|------|------|
| **[README.md](README.md)** | Features + setup | Installation & overview |
| **[docs/API.md](docs/API.md)** | Complete API reference | API details |
| **[docs/KEY_ROTATION.md](docs/KEY_ROTATION.md)** | Multi-key setup | Configuring multiple keys |

---

## Quick Navigation

### By What You Want to Do:

**I want to add a new tool**
→ [AGENTS_QUICK_START.md](AGENTS_QUICK_START.md) (Example 1)
→ [AGENTS.md](AGENTS.md#-tool-builder-agent)
→ Copy Template, Follow Checklist (15 items)

**I want to write tests**
→ [AGENTS_QUICK_START.md](AGENTS_QUICK_START.md) (Example 2)
→ [AGENTS.md](AGENTS.md#-testing-agent)
→ Copy Template, Follow Checklist (10 items)

**I want to create a resource**
→ [AGENTS_QUICK_START.md](AGENTS_QUICK_START.md) (Example 3)
→ [AGENTS.md](AGENTS.md#-resource-builder-agent)
→ Copy Template, Follow Checklist (12 items)

**I want to debug an issue**
→ [AGENTS_QUICK_START.md](AGENTS_QUICK_START.md) (Example 4)
→ [AGENTS.md](AGENTS.md#-debug--troubleshooting-agent)
→ Follow Solution Steps, Follow Checklist (10 items)

**I want to understand the architecture**
→ [.github/copilot-instructions.md](.github/copilot-instructions.md)
→ Read Architecture Overview + Code Patterns

**I want to see all available APIs**
→ [.github/copilot-instructions.md](.github/copilot-instructions.md#-tools-14-total)
→ Lists all 14 tools, 4 resources, 4 prompts

---

## The 6 Agents at a Glance

```
🧪 TESTING AGENT
   Mission: Create comprehensive tests
   Checklist: 10 items
   Time: 15-30 min
   
🔨 TOOL BUILDER AGENT
   Mission: Add new MCP tools (API endpoints)
   Checklist: 15 items
   Time: 30-60 min
   
📊 RESOURCE BUILDER AGENT
   Mission: Create AI-friendly data views
   Checklist: 12 items
   Time: 20-40 min
   
🎯 PROMPT BUILDER AGENT
   Mission: Build AI-guided workflows
   Checklist: 11 items
   Time: 20-40 min
   
📚 DOCUMENTATION AGENT
   Mission: Maintain accurate documentation
   Checklist: 10 items
   Time: 10-20 min
   
🐛 DEBUG & TROUBLESHOOTING AGENT
   Mission: Diagnose and fix issues
   Checklist: 10 items
   Time: 15-45 min
```

---

## Reading Order

### First Time Here?
1. This file (you're reading it!) ← 2 min
2. [AGENTS_QUICK_START.md](AGENTS_QUICK_START.md) ← 5 min
3. [AGENT_DECISION_TREE.md](AGENT_DECISION_TREE.md) ← 3 min
4. Jump to your agent in [AGENTS.md](AGENTS.md) ← 20-60 min
5. Done! ✅

### Regular Contributor?
1. Jump straight to [AGENTS.md](AGENTS.md)
2. Find your agent section
3. Copy template, follow checklist
4. Test and submit

### Want to Understand Everything?
1. [AGENT_SYSTEM_GUIDE.md](AGENT_SYSTEM_GUIDE.md) ← Complete overview
2. [.github/copilot-instructions.md](.github/copilot-instructions.md) ← Architecture
3. [src/datadog_mcp_server.py](src/datadog_mcp_server.py) ← Main code
4. [tests/](tests/) ← Examples

---

## File Relationships

```
You are here (INDEX)
    ↓
[AGENTS_QUICK_START.md] ← READ THIS FIRST
    ↓
[AGENTS.md] ← Pick your agent
    ├─ 🧪 Testing Agent
    ├─ 🔨 Tool Builder Agent
    ├─ 📊 Resource Builder Agent
    ├─ 🎯 Prompt Builder Agent
    ├─ 📚 Documentation Agent
    └─ 🐛 Debug Agent
    ↓
[WORKFLOW.md] (Visual guides)
    ↓
[.github/copilot-instructions.md] (Architecture)
    ↓
[Code Files]
    ├─ src/datadog_mcp_server.py
    ├─ src/key_rotation.py
    └─ tests/
```

---

## Key Concepts

### The 5-Step Process (Same for All Agents)
1. Read MISSION
2. Copy TEMPLATE
3. Customize
4. Follow CHECKLIST
5. Run TEST COMMANDS

### Each Agent Provides
- Mission statement (what to do)
- Working template (what to copy)
- Detailed checklist (what to verify)
- Test commands (how to validate)
- Success criteria (when you're done)

### Everything References
- Best practices
- Code patterns
- Real examples
- Common pitfalls

---

## Critical Rules

These apply everywhere:

1. **Always use `_execute_with_key_rotation()`** for API calls
2. **Never hardcode DD_SITE** - always read from environment
3. **Always use decorators**: `@mcp.tool`, `@mcp.resource`, `@mcp.prompt`
4. **Always include correlation_id** in responses
5. **Always follow the checklist** - don't skip items

---

## Common Workflows

### Adding a New Tool (30-60 min)
```
1. Read AGENTS.md → Tool Builder Agent
2. Copy @mcp.tool template
3. Customize with your tool name/logic
4. Follow 15-item checklist
5. Run: pytest tests/test_datadog_mcp_server.py -v
6. Update docs/API.md
7. Done! ✅
```

### Writing Tests (15-30 min)
```
1. Read AGENTS.md → Testing Agent
2. Copy test template
3. Customize for your function
4. Follow 10-item checklist
5. Run: pytest tests/ -v --cov=src
6. Check: Coverage > 80%
7. Done! ✅
```

### Debugging an Issue (15-45 min)
```
1. Read AGENTS.md → Debug Agent
2. Enable debug tracing (MCP_DEBUG_LEVEL=TRACE)
3. Find your issue in "Common Issues & Solutions"
4. Follow solution steps
5. Follow 10-item debug checklist
6. Verify with tests
7. Done! ✅
```

---

## When You're Stuck

**I don't know which agent to use:**
→ [AGENT_DECISION_TREE.md](AGENT_DECISION_TREE.md)

**I need a quick overview:**
→ [AGENTS_QUICK_START.md](AGENTS_QUICK_START.md)

**I need complete details:**
→ [AGENTS.md](AGENTS.md)

**I need visual diagrams:**
→ [WORKFLOW.md](WORKFLOW.md)

**I want to understand how it all works:**
→ [AGENT_SYSTEM_GUIDE.md](AGENT_SYSTEM_GUIDE.md)

**I need to understand the code:**
→ [.github/copilot-instructions.md](.github/copilot-instructions.md)

**I need API details:**
→ [docs/API.md](docs/API.md)

---

## Success Metrics

After using this system, you should be able to:

✅ Add a new tool in 30-60 minutes  
✅ Write tests in 15-30 minutes  
✅ Create a resource in 20-40 minutes  
✅ Build a prompt in 20-40 minutes  
✅ Update docs in 10-20 minutes  
✅ Debug an issue in 15-45 minutes  
✅ Never hardcode DD_SITE (critical!)  
✅ Always follow conventions  
✅ Know exactly when you're done  
✅ Submit with confidence  

---

## How to Get Started

### Right Now (Next 5 Minutes)
1. Open [AGENTS_QUICK_START.md](AGENTS_QUICK_START.md)
2. Read it (5 minutes)
3. Identify your task
4. Jump to that agent in [AGENTS.md](AGENTS.md)

### This Hour (30-60 Minutes)
1. Copy template
2. Customize for your task
3. Follow checklist
4. Run test commands
5. Submit

---

## Summary

You have:
- ✅ 6 task-specific agent guides
- ✅ Copy-paste templates for every type of work
- ✅ Detailed checklists to ensure quality
- ✅ Test commands to validate
- ✅ Real examples to learn from
- ✅ Architecture documentation
- ✅ Decision trees to pick the right path
- ✅ Visual workflows to understand the process

**Result:** You'll be productive in this codebase in minutes, not hours.

---

## Start Here

👉 **Open [AGENTS_QUICK_START.md](AGENTS_QUICK_START.md) RIGHT NOW** (5 minutes)

It's your gateway to everything else!

---

**Questions?** Every agent has a "Need Help?" section.  
**Confused?** Check [AGENT_DECISION_TREE.md](AGENT_DECISION_TREE.md).  
**Want details?** Read [AGENT_SYSTEM_GUIDE.md](AGENT_SYSTEM_GUIDE.md).  

Good luck! 🚀
