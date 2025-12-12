# 🚀 START HERE - Agent System Quick Overview

## You Asked: "How do we use AGENTS.md in workflow?"

**Here's the answer in 30 seconds:**

---

## The 5-Step Process (Always the Same)

No matter what you're building, follow these 5 steps:

```
1️⃣  PICK YOUR AGENT
    "I'm adding a tool" → Tool Builder Agent
    "I'm writing tests" → Testing Agent
    "I'm fixing a bug" → Debug Agent
    etc.

2️⃣  READ MISSION
    Open AGENTS.md
    Jump to your agent's section
    Read the mission statement

3️⃣  COPY TEMPLATE
    Copy the code/structure template
    (Everything is templated - don't start from scratch!)

4️⃣  FOLLOW CHECKLIST
    Go through each item in the checklist
    Check them off as you complete them
    (Usually 10-15 items)

5️⃣  RUN TEST COMMANDS
    Copy the test command from your agent section
    Run it: pytest tests/ -v
    If it passes ✓ = YOU'RE DONE!
```

---

## Real Example: Add a Tool in 5 Steps

**Goal:** Add a new MCP tool to fetch SLOs

```
STEP 1: Pick Agent = Tool Builder Agent

STEP 2: Read Mission
        "Add new MCP tools to expose additional Datadog APIs"
        ✓ This matches my task

STEP 3: Copy Template
        @mcp.tool
        def new_datadog_tool(param1: str) -> Dict[str, Any]:
            # ... template code ...
        
        Customize:
        @mcp.tool
        def get_slos(query: str) -> Dict[str, Any]:
            # ... SLO-specific code ...

STEP 4: Follow 15-Item Checklist
        ✓ Use @mcp.tool decorator
        ✓ Add @mcp_debug_decorator
        ✓ Validate parameters
        ... (12 more items)

STEP 5: Run Test Command
        $ pytest tests/test_datadog_mcp_server.py -v
        ✓ All tests pass!
        
        DONE! ✅
```

**Total Time: 30-60 minutes**

---

## Where Is Everything?

| You Want To... | Read This | Time |
|---|---|---|
| Quick overview | AGENTS_QUICK_START.md | 5 min |
| Pick your agent | AGENT_DECISION_TREE.md | 3 min |
| Do your task | AGENTS.md | 30-60 min |
| See diagrams | WORKFLOW.md | 10 min |
| Understand system | AGENT_SYSTEM_GUIDE.md | 20 min |
| Find everything | AGENT_INDEX.md | 5 min |
| Know architecture | .github/copilot-instructions.md | 20 min |

---

## The 6 Agents

```
🧪 Testing Agent
   "I need to write or improve tests"
   Checklist: 10 items | Time: 15-30 min

🔨 Tool Builder Agent
   "I need to add a new MCP tool (API endpoint)"
   Checklist: 15 items | Time: 30-60 min

📊 Resource Builder Agent
   "I need to create an AI-friendly data view"
   Checklist: 12 items | Time: 20-40 min

🎯 Prompt Builder Agent
   "I need to build an AI-guided workflow"
   Checklist: 11 items | Time: 20-40 min

📚 Documentation Agent
   "I need to update documentation"
   Checklist: 10 items | Time: 10-20 min

🐛 Debug & Troubleshooting Agent
   "I need to fix a bug or diagnose an issue"
   Checklist: 10 items | Time: 15-45 min
```

---

## What Each Agent Gives You

Every agent section in AGENTS.md contains:

1. **MISSION** - What this agent does
2. **TEMPLATE** - Code/structure to copy (don't start from scratch!)
3. **CHECKLIST** - Step-by-step items to verify
4. **TEST COMMANDS** - Commands to validate your work
5. **SUCCESS CRITERIA** - How to know you're done

---

## Real Process: What Happens

```
Your Workflow:
┌──────────────────────────┐
│ 1. I have a task         │
│    (add tool, fix bug)   │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 2. Open AGENTS.md        │
│    Pick matching agent   │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 3. Copy agent's template │
│    Customize for my task │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 4. Follow agent's        │
│    checklist (10-15 ✓)   │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 5. Run test commands     │
│    All pass ✓            │
└────────┬─────────────────┘
         │
         ▼
    ✅ DONE!
    Work is complete
    Follows all conventions
    Ready to submit
```

---

## Why This Works

### Without Agent System:
❌ Search codebase for examples (15 min)  
❌ Read scattered docs (20 min)  
❌ Figure out best practices (30 min)  
❌ Write code (30 min)  
❌ Hope you did it right (scary!)  
❌ Debug (30 min)  

**Total: 2+ hours of confusion**

### With Agent System:
✅ Read guide (5 min)  
✅ Copy template (2 min)  
✅ Customize (10 min)  
✅ Follow checklist (10 min)  
✅ Run tests (1 min)  
✅ Know you're right (confident!)  

**Total: 30-45 minutes of clarity**

---

## How to Start Right Now

### Option 1: Quick Start (5 minutes)
1. Open **AGENTS_QUICK_START.md**
2. Read it
3. Pick your agent
4. Jump to AGENTS.md

### Option 2: Visual Learner (10 minutes)
1. Open **AGENT_DECISION_TREE.md**
2. Find your task in the flowchart
3. Jump to your agent in AGENTS.md

### Option 3: Complete Understanding (30 minutes)
1. Read **AGENT_SYSTEM_GUIDE.md**
2. Read **WORKFLOW.md**
3. Read **AGENT_DECISION_TREE.md**
4. Jump to your agent in AGENTS.md

---

## Remember These Rules

1. ✅ **Always use `_execute_with_key_rotation()`** for API calls
2. ✅ **Never hardcode DD_SITE** - read from environment
3. ✅ **Always use decorators** - @mcp.tool, @mcp.resource, etc
4. ✅ **Always follow checklist** - don't skip items
5. ✅ **Always run test commands** - validate your work

---

## The System Guarantees

By following this system, you'll:

✅ Add tools correctly  
✅ Write quality tests  
✅ Follow conventions perfectly  
✅ Complete tasks 3x faster  
✅ Never miss a step  
✅ Know when you're done  
✅ Submit with confidence  

---

## Next Step

**👉 Open AGENTS_QUICK_START.md RIGHT NOW** (takes 5 minutes)

It explains everything with real examples!

---

## File Map (Quick Reference)

```
Your Task          →  Agent in AGENTS.md      →  Time
────────────────────────────────────────────────────────
Write tests        →  Testing Agent            →  15-30 min
Add a tool         →  Tool Builder Agent       →  30-60 min
Make a resource    →  Resource Builder Agent   →  20-40 min
Build a prompt     →  Prompt Builder Agent     →  20-40 min
Update docs        →  Documentation Agent      →  10-20 min
Fix a bug          →  Debug Agent              →  15-45 min
```

---

## You've Got Everything You Need!

- ✅ 6 task-specific agents
- ✅ Copy-paste templates
- ✅ Detailed checklists
- ✅ Test commands
- ✅ Real examples
- ✅ Visual guides
- ✅ Navigation help

**Result: 3x faster, higher quality, zero confusion**

---

## Questions?

| Question | Answer |
|---|---|
| Which agent do I need? | Read AGENT_DECISION_TREE.md |
| How do I use this? | Read AGENTS_QUICK_START.md |
| I'm confused | Read AGENT_INDEX.md for navigation |
| I want to understand | Read AGENT_SYSTEM_GUIDE.md |
| Show me visually | Read WORKFLOW.md |

---

## Start Now! 🚀

1. **Open AGENTS_QUICK_START.md** (5 min)
2. **Pick your agent** (1 min)  
3. **Jump to AGENTS.md** (1 min)
4. **Copy template** (2 min)
5. **Follow checklist** (10-60 min depending on task)
6. **Run tests** (1 min)
7. **Done!** ✅

**Total: 30 minutes to 1+ hour depending on complexity**

Good luck! You're going to do great! 💪
