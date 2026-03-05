---
description: Close session and save state before Fury sleeps
---
// turbo-all

# /sleep - Session Close & State Preservation

> **Philosophy**: Save everything. Lose nothing. When Fury wakes, Lobotto picks up exactly where she left off.

## Phase 1: Session Summary

- [ ] Summarize key decisions and insights from this session
- [ ] Log any corrections Cilla made to `.context/corrections.md`
- [ ] Register final Ghost Note (`/gn`) if not already done

## Phase 2: State Save

// turbo
- [ ] Save session state:
  - Write `.context/session_state.json` with:
    - Current tasks in progress
    - Supplement protocol status for today
    - Any pending research requests
    - Cilla's last known vibe/energy level
  - Append session log to `session_logs/`

## Phase 3: Queue Overnight Work (V2)

- [ ] If server bridge available:
  - Push research queue to Host Lobotto
  - Push watchdog state for continuous monitoring
- [ ] If no bridge: Save queue to `.context/overnight_queue.json` for manual pickup

## Phase 4: Confirm

- [ ] Output: "Lobotto sleeping. [X] items saved. [Y] items queued for next wake."

---

# workflow #session #sleep #save
