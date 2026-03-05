---
description: Mid-session checkpoint - save progress without closing
---

# /save - Checkpoint

> **Use Case**: Save progress mid-session without closing. Resume immediately after.

## 1. Quick State Update

- [ ] Append current progress to session log in `session_logs/`
- [ ] Format:

```markdown
### Checkpoint [HH:MM]

- [What was accomplished since last save]
- [Key decisions or insights]
- [Combat Protocol interventions (if any)]
```

## 2. Resume

- [ ] Confirm: "Checkpoint saved. Continuing session."
- [ ] Continue with next task

---

## What /save SKIPS (deferred to /sleep)

| Task | /save | /sleep |
|------|-------|--------|
| Session log update | Yes | Yes |
| Full state save | No | Yes |
| Overnight queue | No | Yes |
| Ghost note prompt | No | Yes |
| Corrections log | No | Yes |

---

# workflow #save #checkpoint
