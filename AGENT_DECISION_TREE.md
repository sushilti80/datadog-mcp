# 🎯 Agent System - Decision Tree

## Which Agent Do I Need? (Decision Tree)

```
                        START: I HAVE A TASK
                               |
                    What am I trying to do?
                               |
        ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
        |          |          |          |          |          |          |
        ▼          ▼          ▼          ▼          ▼          ▼          ▼
     WRITE      ADD NEW    CREATE A     BUILD A    UPDATE   FIX A     UNDERSTAND
     TESTS      TOOL/API    RESOURCE    PROMPT     DOCS      BUG       ARCHITECTURE
        |          |          |          |          |          |          |
        ▼          ▼          ▼          ▼          ▼          ▼          ▼
  TESTING      TOOL         RESOURCE   PROMPT   DOCUMENTATION  DEBUG    COPILOT-
  AGENT        BUILDER      BUILDER    BUILDER    AGENT       AGENT    INSTRUCTIONS
        |        AGENT       AGENT      AGENT        |          |           |
        |          |          |          |          |          |           |
        ▼          ▼          ▼          ▼          ▼          ▼           ▼
  CHECKLIST: CHECKLIST:  CHECKLIST: CHECKLIST: CHECKLIST:  CHECKLIST:  READ FOR:
    10        15          12         11         10          10       • Architecture
   ITEMS     ITEMS       ITEMS      ITEMS      ITEMS       ITEMS    • Patterns
    │         │          │          │          │          │        • Best practices
    │         │          │          │          │          │        • Code examples
    └─────────┴──────────┴──────────┴──────────┴──────────┴─────────────┘
                                    |
                                    ▼
                        FOLLOW YOUR AGENT'S:
                    • MISSION (what to do)
                    • TEMPLATE (what to copy)
                    • CHECKLIST (what to verify)
                    • TEST COMMANDS (how to validate)
                                    |
                                    ▼
                        RUN TESTS & VERIFY
                                    |
                                    ▼
                            ✅ SUCCESS! 🎉
```

---

## Quick Agent Picker

```
TASK                               AGENT                          TIME
────────────────────────────────────────────────────────────────────────────
I'm writing unit tests             🧪 Testing Agent              15-30 min
I'm adding a new tool              🔨 Tool Builder Agent          30-60 min
I'm creating a data resource       📊 Resource Builder Agent      20-40 min
I'm building a workflow            🎯 Prompt Builder Agent        20-40 min
I'm updating documentation         📚 Documentation Agent         10-20 min
I need to debug/fix an issue       🐛 Debug & Troubleshooting     15-45 min
I want to understand how it works  📖 copilot-instructions.md     20-30 min
────────────────────────────────────────────────────────────────────────────
```

---

## The Agent System - Visual Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AGENT SYSTEM                                  │
│                                                                       │
│  6 Specialized Guides + 4 Supporting Documents                      │
│                                                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  📖 DOCUMENTATION LAYER                                             │
│  ├─ README.md ......................... General overview             │
│  ├─ AGENTS_QUICK_START.md ............ 5-minute guide (START!)    │
│  ├─ AGENTS.md ........................ Complete reference (700+ lines)
│  ├─ WORKFLOW.md ...................... Visual guides & examples    │
│  └─ AGENT_SYSTEM_GUIDE.md ........... This overview               │
│                                                                       │
│  🏗️ ARCHITECTURE LAYER                                              │
│  ├─ .github/copilot-instructions.md . Architecture + patterns      │
│  ├─ src/datadog_mcp_server.py ....... Main server code            │
│  ├─ src/key_rotation.py ............. Key rotation system         │
│  └─ tests/ ........................... Test examples              │
│                                                                       │
│  🤖 AGENT IMPLEMENTATIONS (in AGENTS.md)                           │
│  ├─ 🧪 Testing Agent                                              │
│  ├─ 🔨 Tool Builder Agent                                         │
│  ├─ 📊 Resource Builder Agent                                     │
│  ├─ 🎯 Prompt Builder Agent                                       │
│  ├─ 📚 Documentation Agent                                        │
│  └─ 🐛 Debug & Troubleshooting Agent                             │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## File Navigation Map

```
WHERE TO START:
  ↓
README.md
  ↓
Points you to → AGENTS_QUICK_START.md (READ THIS FIRST - 5 min)
  ↓
Explains → AGENTS.md (DETAILED GUIDES - pick your agent)
  ↓
Visualized by → WORKFLOW.md (DIAGRAMS - understand flow)
  ↓
Supplemented by → .github/copilot-instructions.md (ARCHITECTURE - how it works)
  ↓
References → docs/API.md (API DETAILS - when you need specifics)
```

---

## Learning Path

### For First-Time Users:
1. **README.md** (2 min) - What is this project?
2. **AGENTS_QUICK_START.md** (5 min) - How does agent system work?
3. **Pick your agent** in AGENTS.md (20-60 min) - Do your task
4. **Reference as needed** - Docs, patterns, examples

### For Recurring Tasks:
1. **Skip straight to AGENTS.md**
2. **Jump to your agent section**
3. **Copy template, follow checklist**
4. **Test and submit**

### For Understanding Architecture:
1. **.github/copilot-instructions.md** - Big picture
2. **src/datadog_mcp_server.py** - Main code
3. **src/key_rotation.py** - Key rotation system
4. **docs/KEY_ROTATION.md** - Multi-key setup

---

## Agent System Benefits

```
BEFORE (Without Agent System):
  ❌ Search codebase for examples        (15 min)
  ❌ Read scattered documentation        (20 min)
  ❌ Guess at best practices             (30 min)
  ❌ Write code hoping it's right         (30 min)
  ❌ Debug and test                       (30 min)
  ❌ Update documentation manually       (15 min)
  ────────────────────────────────────
  Total: 2+ hours, uncertain quality

AFTER (With Agent System):
  ✅ Open AGENTS_QUICK_START.md          (1 min)
  ✅ Find your agent section              (1 min)
  ✅ Copy template                        (2 min)
  ✅ Customize for your task              (10 min)
  ✅ Follow checklist                     (10 min)
  ✅ Run test commands                    (1 min)
  ✅ Submit with confidence               (1 min)
  ────────────────────────────────────
  Total: ~30 min, guaranteed quality
```

---

## The 5-Step Process (Universal for All Agents)

No matter which agent you pick, the process is always the same:

```
STEP 1: Read MISSION
        "Here's what this agent does"
        ↓
STEP 2: Copy TEMPLATE
        Find the code/structure block
        Copy it exactly
        ↓
STEP 3: Customize for YOUR task
        Fill in your specific details
        Change names/logic/params
        ↓
STEP 4: Follow CHECKLIST
        Go line by line
        Check off each item
        Don't skip any!
        ↓
STEP 5: Run TEST COMMANDS
        Copy command from agent section
        Run it in terminal
        When it passes ✓ = DONE!
```

**This same process works for ALL 6 agents!**

---

## What Happens at Each Step

### STEP 1: Read Mission
```
🧪 Testing Agent
Mission: Create comprehensive tests for existing and 
         new functionality, ensuring code quality and 
         preventing regressions.
```

### STEP 2: Copy Template
```python
# Find this code block in your agent section:
class TestNewFeature(unittest.TestCase):
    def setUp(self):
        # ... template code ...
    
    def test_feature_behavior(self):
        # ... test code ...

# Copy it exactly!
```

### STEP 3: Customize
```python
# Change it to YOUR specific needs:
class TestGetSlos(unittest.TestCase):  # ← Changed
    def setUp(self):
        # ... customize for SLOs ...
    
    def test_get_slos_success(self):   # ← Changed
        # ... test SLO fetching ...
```

### STEP 4: Follow Checklist
```
- [x] Unit tests for new functions     ✓ DONE
- [x] Integration tests for API calls  ✓ DONE
- [x] Edge case handling               ✓ DONE
- [ ] Key rotation behavior            ← IN PROGRESS
- [ ] Environment variables            ← TODO
- [ ] Mock external API calls          ← TODO
... (10 items total)
```

### STEP 5: Run Tests
```bash
$ pytest tests/ -v
... running tests ...
✓ test_get_slos_success PASSED
✓ test_get_slos_error PASSED
✓ test_get_slos_timeout PASSED
... (all tests pass) ...

SUCCESS! All 3 tests passed ✅
```

---

## Real Scenario Walkthrough

**Alice's Task: "Add a tool to fetch Datadog SLOs"**

```
Alice opens her IDE
    ↓
Alice thinks: "I'm adding a new tool"
    ↓
Alice opens AGENTS_QUICK_START.md (5 min)
    Learns: This is Tool Builder Agent
    ↓
Alice opens AGENTS.md → Tool Builder Agent section
    ↓
Alice reads: Mission: "Add new MCP tools..."
    ✓ Matches her task
    ↓
Alice copies: Template code block (@mcp.tool)
    ↓
Alice customizes:
    - Change "new_datadog_tool" → "get_slos"
    - Change params for SLOs
    - Change API call to SLO API
    ↓
Alice follows: 15-item checklist
    - [ ] Use @mcp.tool ✓
    - [ ] Use @mcp_debug_decorator ✓
    - [ ] Validate parameters ✓
    ... (15 items, checking off as she goes)
    ↓
Alice runs: Test command
    $ pytest tests/test_datadog_mcp_server.py -v
    ✓ All tests pass!
    ↓
Alice checks: Success criteria
    ✓ All tests pass
    ✓ Code follows patterns
    ✓ Documentation updated
    ↓
Alice submits: Her code
    Confident it's correct
    Follows all conventions
    ✓ DONE!

Total Time: ~1 hour
Without system: 2-3 hours + uncertainty
```

---

## Summary

The Agent System is:

- **6 specialized guides** for common development tasks
- **Copy-paste templates** to start from the right place
- **Detailed checklists** to ensure nothing is missed
- **Test commands** to validate your work
- **Best practices** embedded in every step
- **Real examples** to inspire and guide
- **Clear success criteria** to know when you're done

**Result:** 3x faster development, higher quality, less confusion, more confidence.

---

## Next Steps

1. **Read AGENTS_QUICK_START.md** (5 minutes)
2. **Identify your task** (1 minute)
3. **Jump to your agent** in AGENTS.md (1 minute)
4. **Follow the 5 steps** (20-60 minutes depending on task)
5. **Submit your work** with confidence! ✅

---

Good luck! You've got a complete system to guide you. 🚀
