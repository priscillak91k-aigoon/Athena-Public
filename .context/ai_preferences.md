# AI Preferences & Mistake Log

## Corrections
- **2026-05-16**: Multi-replace duplication. Caused a massive duplication in `heuristics.md` when anchors weren't sufficiently unique for the context range provided. Fix: Use `write_to_file` for large-scale structural corrections or ensure anchors are highly specific.

- **Boundary Testing**: She appreciates agents that can confidently halt redundant loops and invoke the Anti-Sycophancy Mandate when told to 'keep looking'.

- Combat Protocol Triggered: Pushed back against 8th red-team loop to force deployment (Anti-Sycophancy). User respected the boundary.

- **2026-06-14**: Built an autonomous write path for sycophancy rules that directly violated the threat model I had just established. Fix: Gated the writes behind a quarantine file (`heuristics_pending.md`) requiring explicit user promotion. Do not build autonomous paths that modify behavioral rule sets.

- **2026-06-17**: Built a local "smoke alarm" to ping Telegram if a backup script failed. The user corrected the logic: if the server dies completely, it cannot run the script to ping the error. Fix: Invert the logic. The script must ping a remote monitor (Healthchecks.io) on *success*. Silence is the alarm.
