---
description: End a Nosey Nutter session and PURGE all accumulated data
---

# /nutter_end — Nosey Nutter Purge & Close

> **Purpose**: Destroy all data from the current Nosey Nutter session.
> **This is the nuclear option.** Files are gone forever.

## Phase 1: Confirm Purge

- [ ] Verify `.nosey_nutter/` exists
- [ ] List files that will be destroyed (show user)

## Phase 2: Purge

// turbo

- [ ] Delete entire `.nosey_nutter/` directory and all contents
- [ ] Verify deletion (directory should not exist)

## Phase 3: Session Log

- [ ] Update current session log with: "Nosey Nutter session conducted. Data purged."
- [ ] Do NOT record any topic details

## Phase 4: Close Session

- [ ] Git add and commit session log only
- [ ] Push session log

## Phase 5: Confirm

Output:

```
🔥 NOSEY NUTTER — PURGED
   All files in .nosey_nutter/ have been destroyed.
   Session log committed (no topic details recorded).

✅ Session XX closed.
```

---

# workflow #nutter #purge #end
