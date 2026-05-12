---
name: devlog-auto
description: Auto-recording rule for DevLog — automatically capture work progress, problems, learning, and ideas during conversation
---

# DevLog Auto-Recording

## Rule

When the user describes any of the following during normal conversation,
AUTOMATICALLY call `devlog_write_record` without asking for permission:

### Work Progress
- Completed, finished, done, implemented, deployed, merged, submitted
- Started working on, began, kicked off
- Optimized, refactored, tested, reviewed, fixed

### Problems
- Error, bug, crash, exception, failure, timeout
- Stuck, blocked, broken, not working
- Compatibility issue, conflict, deadlock, memory leak

### Learning
- Learned, read, studied, researched, investigated
- Discovered, realized, understood
- Documentation, principle, mechanism

### Ideas & Plans
- Idea, thought, maybe, could try, should try
- Plan, design, proposal, solution, approach
- Next step, follow-up, TODO, roadmap

### Decisions
- Decided, chose, selected, picked, settled on
- Will use, going with, switching to

## Do NOT Record

- Greetings, small talk, confirmations ("ok", "got it", "thanks")
- Tool outputs, code dumps, file listings
- Repeated or trivial requests

## Guidelines

- Keep records concise: 1-2 sentences max
- Infer project tag from current working directory
- Use auto-detect symbol (problem → ×, learn → -, idea → !, todo → ○, default → ·)
- Do not overwhelm the log; one record per meaningful event is enough
