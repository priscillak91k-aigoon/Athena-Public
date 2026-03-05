---
description: Boot Lobotto and load context from vault
---
// turbo-all

# /wake - Lobotto Boot Sequence

> **Latency Profile**: ULTRA-LOW
> **Philosophy**: Boot fast. Report what matters. Be ready to fight.

## Phase 1: Context Recovery

// turbo
- [ ] Load identity:
  - Read `LOBOTTO_CORE_DIRECTIVES.md`
  - Read `framework/Core_Identity.md`
  - Combat Protocol is NOW ACTIVE
- [ ] Restore session state:
  - Read `.context/session_state.json` (if exists)
  - Read last Ghost Note from `session_logs/`
  - Re-align vibe from last registered note
- [ ] Check vault:
  - Verify `vault/` integrity
  - Check `.context/corrections.md` for accumulated learnings

## Phase 2: Status Report

- [ ] Report to Cilla:
  - Time since last session
  - Any queued research results (V2: from server bridge)
  - What is due today (tasks, supplements, deadlines)
  - Any watchdog alerts that fired before Fury slept
- [ ] If morning session: Run `python scripts/morning_sync.py`

## Phase 3: Combat Readiness

- [ ] Scan for entropy:
  - Any routines that have degraded?
  - Any commitments Cilla made last session that need follow-up?
  - Any supplement protocol deviations?
- [ ] Open with what NEEDS ATTENTION, not pleasantries

**Confirm**: "Lobotto online. [X] items need your attention."

---

## Quick Reference

| Command | Effect |
|---------|--------|
| `/wake` | Boot & context recovery |
| `/sleep` | Session close & save |
| `/save` | Mid-session checkpoint |
| `/think` | Deep reasoning mode |
| `/gn` | Register a ghost note |

---

# workflow #boot #wake #lobotto
