## How to Use AGENTS.md - Visual Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  YOU HAVE A TASK                                            │
│  (write tests / add tool / make resource / fix bug / etc)   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: READ "AGENTS_QUICK_START.md"                      │
│  (5-minute overview of how everything works)               │
│  FILE: AGENTS_QUICK_START.md ← START HERE                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  PICK YOUR AGENT     │
        │                      │
        │  🧪 Testing Agent ───────────┐
        │  🔨 Tool Builder ────────┐   │
        │  📊 Resource Builder ──────┐ │
        │  🎯 Prompt Builder ────┐   │ │
        │  📚 Documentation ────┐ │   │ │
        │  🐛 Debug Agent ────┐ │ │   │ │
        │                    │ │ │   │ │
        └────────────────────┼─┼─┼───┼─┘
                             │ │ │   │
                ┌────────────┘ │ │   │
                │              │ │   │
                ▼              ▼ ▼   ▼
            AGENTS.md (Pick matching section)
            │
            ├─ Read MISSION statement
            │
            ├─ Copy TEMPLATE code/structure
            │
            ├─ Customize for YOUR task
            │
            ├─ Follow CHECKLIST (don't skip!)
            │  ✓ Item 1
            │  ✓ Item 2
            │  ✓ Item 3
            │  ... (all items)
            │
            ├─ Run TEST COMMANDS
            │  $ pytest tests/ -v
            │  $ [other commands provided]
            │
            └─ Verify SUCCESS CRITERIA
               ✅ All tests pass
               ✅ Coverage > 80%
               ✅ Code formatted correctly
               
                    ▼
            ┌──────────────────┐
            │  DONE! 🎉        │
            │  Your work is    │
            │  production-ready│
            └──────────────────┘
```

---

## File Relationships

```
README.md
└─ Points to AGENTS_QUICK_START.md (start here!)
   
AGENTS_QUICK_START.md (5-minute overview)
└─ Points to AGENTS.md for full details

AGENTS.md (Complete reference)
├─ 6 Agent Sections (pick ONE based on your task)
├─ Each has: Mission + Template + Checklist + Commands
├─ Examples for each scenario
└─ References to .github/copilot-instructions.md

.github/copilot-instructions.md (Architecture & patterns)
├─ Big picture architecture
├─ Code patterns & conventions
├─ Key rotation system
├─ API inventory (all tools/resources/prompts)
└─ Common pitfalls to avoid
```

---

## Quick Navigation Map

### I want to... → Read this section in AGENTS.md

| Goal | Agent | Section |
|------|-------|---------|
| Write tests | Testing Agent | Line 75 |
| Add new tool/API endpoint | Tool Builder Agent | Line 195 |
| Create data view (resource) | Resource Builder Agent | Line 300 |
| Build AI workflow (prompt) | Prompt Builder Agent | Line 380 |
| Update documentation | Documentation Agent | Line 480 |
| Debug/fix an issue | Debug & Troubleshooting Agent | Line 550 |
| Understand architecture | (not in AGENTS.md) | .github/copilot-instructions.md |

---

## The 5-Step Process (Always the Same)

No matter which agent you pick, the process is always:

```
┌─────────────────────────────────────────┐
│ STEP 1: Read Agent's MISSION            │
│ "Here's what this agent does"           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ STEP 2: Copy TEMPLATE                   │
│ Find the code/structure block            │
│ Copy it exactly                         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ STEP 3: Customize TEMPLATE              │
│ Fill in YOUR specific details            │
│ Change names/logic/parameters           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ STEP 4: Follow CHECKLIST                │
│ Go line by line ✓                       │
│ Check off each item                     │
│ Don't skip any!                         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ STEP 5: Run TEST COMMANDS               │
│ Copy the command from agent section      │
│ Run it: $ pytest tests/ -v              │
│ When it passes ✓ = YOU'RE DONE!         │
└─────────────────────────────────────────┘
```

This same process works for ALL 6 agents!

---

## Example: Real Scenario

**Scenario: "I want to add a tool to fetch SLOs"**

```
WHAT I'M DOING: Adding a new tool
                ↓
WHICH AGENT: Tool Builder Agent (in AGENTS.md)
             ↓
WHAT I DO:
  1. Open AGENTS.md
  2. Jump to "Tool Builder Agent" section
  3. Read Mission: "Add new MCP tools to expose..."
  4. Copy Template: @mcp.tool code block
  5. Customize:
     - Replace "new_datadog_tool" → "get_slos"
     - Replace params with SLO params
     - Replace API call with SLO API
  6. Follow Checklist:
     - [ ] Use @mcp.tool ✓
     - [ ] Use @mcp_debug_decorator ✓
     - [ ] Validate parameters ✓
     ... (all 15 items)
  7. Run Test Command:
     $ pytest tests/test_datadog_mcp_server.py -v
  8. See green checkmarks ✓
     → DONE!
```

---

## Why This System Works

❌ **Without AGENTS.md:**
- Search codebase for examples (15 min)
- Read docs scattered across files (20 min)
- Figure out best practices (30 min)
- Write code (30 min)
- Hope you didn't miss anything (scary!)
- Test and debug (30 min)
- **Total: 2+ hours, uncertain quality**

✅ **With AGENTS.md:**
- Open file (1 sec)
- Find your agent section (30 sec)
- Copy template (2 min)
- Customize (5-20 min)
- Follow checklist (5-20 min)
- Run tests (1 min)
- **Total: 15-45 min, guaranteed quality**

**3-4x faster. Less stress. Better results.**

---

## Files in This System

| File | Purpose | When to Read |
|------|---------|-------------|
| **AGENTS_QUICK_START.md** | Overview + real examples | FIRST (5 min) |
| **AGENTS.md** | Complete task guides + templates | When doing a specific task |
| **.github/copilot-instructions.md** | Architecture + patterns | For understanding "why" |
| **README.md** | General features + setup | For overview + installation |
| **docs/API.md** | Complete API reference | When you need API details |
| **docs/KEY_ROTATION.md** | Key rotation setup | When configuring multiple keys |

---

## Still Confused?

**Read this in order:**
1. This file (WORKFLOW.md) - you're reading it! ✓
2. AGENTS_QUICK_START.md (5 minutes)
3. Find your agent in AGENTS.md
4. Copy. Customize. Check. Test. Done.

**Stuck on something?** Check the agent's **"Need Help?"** section at the bottom of AGENTS.md.

---

Good luck! You've got everything you need. 🚀
