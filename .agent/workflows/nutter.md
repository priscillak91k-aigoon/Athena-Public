---
description: Boot the Nosey Nutter protocol — ephemeral local-only research sandbox
---

// turbo-all

# /nutter — Nosey Nutter Protocol (Start)

> **Purpose**: Curiosity-driven deep dives into edgy, weird, or sensitive topics.
> **Rule**: Everything stays LOCAL. Nothing gets pushed to GitHub. Ever.

## Phase 1: Create Sandbox

// turbo

- [ ] Create `.nosey_nutter/` directory (if not exists)
- [ ] Create `.nosey_nutter/session_<timestamp>.md` as the working scratchpad
- [ ] Verify `.nosey_nutter/` is in `.gitignore`
- [ ] Check `.nosey_nutter/topics.md` for previously covered topics (create if not exists)

## Phase 2: Mode Switch

- [ ] Set context: **Nosey Nutter Mode ACTIVE**
- [ ] All research files go into `.nosey_nutter/`
- [ ] No git add, no git commit, no git push for ANYTHING in `.nosey_nutter/`
- [ ] Session log (in `session_logs/`) should only note: "Nosey Nutter session conducted" — no topic details

## Phase 3: Confirm

Output:

```
🥜 NOSEY NUTTER MODE — ACTIVE
   Sandbox: .nosey_nutter/
   Git: BLOCKED (gitignored)
   Push: NEVER

   To close and KEEP files: /end
   To close and PURGE all files: /nutter_end
```

---

// turbo-all

## Rules During Nutter Mode

| Rule | Detail |
|------|--------|
| **Storage** | All working files → `.nosey_nutter/` only |
| **Git** | NEVER add, commit, or push nutter files |
| **Session log** | Note "Nosey Nutter session" only — no topic details |
| **Topic Registry** | On session close, append a one-line topic descriptor to `.nosey_nutter/topics.md`. On boot, check it to avoid duplicate research. |
| **Normal /end** | Keeps `.nosey_nutter/` files intact locally, closes session normally |
| **/nutter_end** | PURGES entire `.nosey_nutter/` directory (including `topics.md`), then closes session |

---

// turbo-all

## Topic Registry Format (`.nosey_nutter/topics.md`)

Each line is one past session's topic — short descriptor only, no details:

```
2026-03-02 | Deep Web Briefing — search engines, unsolved mysteries, government leaks, AI threats, Shodan
2026-03-05 | Conspiracy Theories — MKUltra, Operation Paperclip, Gulf of Tonkin
```

Before researching, **check this file first** and skip any topics already covered. Build on existing findings instead of starting from scratch.

---

// turbo-all

# workflow #nutter #research #ephemeral
