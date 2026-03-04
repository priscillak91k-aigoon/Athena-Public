# Project State
**Last Updated**: 2026-03-04 (Session 29)

## System Status
- **AI**: Operational — Seven of Nine persona, 8-file boot sequence, 6 background processes
- **Context**: `.context/about_priscilla.md` is canonical source of truth
- **Intuition**: heuristics.md + case_studies.md + decision_journal.md (self-applying via dreaming)
- **Dreaming**: `athena_dreaming.py` v2 — every 4 hours, Claude-primary, self-applying, Telegram alerts
- **Security**: Hardened (BitLocker, Defender maxed, ASR rules, services pruned, McAfee purged)
- **Framework**: v7.5 (v8.0-alpha referenced — consolidation pending)

## Background Processes (Windows Scheduled Tasks)
| Task | Schedule | Status |
|------|----------|--------|
| AthenaDreaming | Every 4 hours | ✅ Active |
| AthenaMorningBriefing | 6:00 AM daily | ✅ Active |
| AthenaWatchdog_Morning_NAC | 6:25 AM daily | ✅ Active |
| AthenaWatchdog_Morning_Supps | 6:55 AM daily | ✅ Active |
| AthenaWatchdog_Evening_Fish | 6:25 PM daily | ✅ Active |
| AthenaWatchdog_Night_Mag | 8:55 PM daily | ✅ Active |

## Active Components
- **Life Hub** (`routine-app/`) — 90s retro dashboard, Supabase backend
- **Lobotto** — Discord + Telegram bots, XTTS-v2 voice
- **Munro Move** — plywood plan, awaiting ITM call
- **Health Data** — supplement protocol, DNA analysis, biometric tracking

## Pending Actions
- [ ] Restart PC (Core Isolation + BitLocker)
- [ ] Save BitLocker recovery key externally
- [ ] Windows Update (3 months behind)
- [ ] Ollama installation completion
- [ ] ITM Dunedin plywood order
- [ ] Vitamin D blood test
- [ ] Telegram bot persistent hosting
- [ ] Framework version consolidation
