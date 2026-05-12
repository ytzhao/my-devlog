---
description: "Auto-recording rule — AI should automatically record relevant content without explicit user request"
model: default
---

## Auto-Recording Rule

When the user describes any of the following during normal conversation,
AUTOMATICALLY call `devlog_write_record` without asking for permission:

**Work progress:**
- Completed, finished, done, implemented, deployed, merged, submitted
- Started working on, began, kicked off
- Optimized, refactored, tested, reviewed

**Problems:**
- Error, bug, crash, exception, failure, timeout
- Stuck, blocked, broken, not working
- Compatibility issue, conflict, deadlock

**Learning:**
- Learned, read, studied, researched, investigated
- Discovered, realized, understood
- Documentation, principle, mechanism

**Ideas & Plans:**
- Idea, thought, maybe, could, should try
- Plan, design, proposal, solution, approach
- Next step, follow-up, TODO, roadmap

**Decisions:**
- Decided, chose, selected, picked, settled on
- Will use, going with, switching to

**Do NOT record:**
- Greetings, small talk, confirmations ("ok", "got it", "thanks")
- Tool outputs, code dumps, file listings
- Repeated or trivial requests

**Rules:**
- Keep records concise: 1-2 sentences max
- Infer project tag from current working directory
- Use auto-detect symbol (problem → ×, learn → -, idea → !, todo → ○, default → ·)
