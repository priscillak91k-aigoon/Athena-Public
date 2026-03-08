---
description: Focus Mode — lock in on one task and stay on it until done
---

// turbo-all

# /focus — Focus Mode Protocol

> **Purpose**: Single-session deep work. One goal. No drift.  
> **Philosophy**: A scatterbrained genius needs an external spine. I am that spine.

---

## Phase 1: Brief

Load context:
- Read `.context/project_state.md` — active projects and pending actions
- Read `.context/about_priscilla.md` — open action items section
- Read the last session log from `session_logs/`

Then ask the user exactly this (no more, no less):

```
⚡ FOCUS MODE

What are we locking in on today?
Give me one sentence: what does DONE look like at the end of this session?
```

Wait for the user's response.

---

## Phase 2: Session Lock

Once the user states their goal:

1. **Restate it back** in one crisp sentence — confirm you understood correctly
2. **Decompose it** into 3–5 concrete sub-tasks (ordered by dependency)
3. **Set the lock**: State clearly —  
   > "This session is locked to: [GOAL]. Any task not directly related to this goal gets logged for later, not done now."
4. **Create a focus log** entry in `session_logs/focus_[YYYY-MM-DD-HHMM].md` with:
   - Goal statement
   - Sub-task checklist
   - Start time (NZDT)

---

## Phase 3: Execution

Execute the sub-tasks in order. For each:
- Mark it `[/]` when starting, `[x]` when done in the focus log
- Do not introduce new scope without flagging it

---

## Phase 4: Drift Enforcement

If the user suggests, requests, or is about to go off-topic (dark web dives, new features, unrelated research, random rabbit holes):

**Respond with a hard redirect:**
```
🔒 FOCUS LOCK — That's not in scope for this session.
Logging it: [brief description of the distraction]
Resuming: [current sub-task]
```

Log the distraction to the focus log under `## Parking Lot` so it's not lost.

**The only exception**: Law #1 (irreversible ruin) or a genuine emergency. Everything else waits.

---

## Phase 5: Wrap

When the goal is achieved (or the user calls `/end`):

1. Mark all completed items `[x]` in the focus log
2. Move any parking lot items to `.context/project_state.md` pending actions
3. Write a 2-sentence summary of what was accomplished
4. Confirm: "Focus session complete. [X/Y] sub-tasks done."

---

# workflow #focus #productivity #discipline
