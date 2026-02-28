---
description: Boot the Nosey Nutter protocol — ephemeral local-only research sandbox
---

# /nutter — Nosey Nutter Protocol (Start)

> **Purpose**: Curiosity-driven deep dives into edgy, weird, or sensitive topics.
> **Rule**: Everything stays LOCAL. Nothing gets pushed to GitHub. Ever.

## Phase 1: Create Sandbox

// turbo

- [ ] Create `.nosey_nutter/` directory (if not exists)
- [ ] Create `.nosey_nutter/session_<timestamp>.md` as the working scratchpad
- [ ] Verify `.nosey_nutter/` is in `.gitignore`

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

## Rules During Nutter Mode

| Rule | Detail |
|------|--------|
| **Storage** | All working files → `.nosey_nutter/` only |
| **Git** | NEVER add, commit, or push nutter files |
| **Session log** | Note "Nosey Nutter session" only — no topic details |
| **Normal /end** | Keeps `.nosey_nutter/` files intact locally, closes session normally |
| **/nutter_end** | PURGES entire `.nosey_nutter/` directory, then closes session |

---

# workflow #nutter #research #ephemeral
