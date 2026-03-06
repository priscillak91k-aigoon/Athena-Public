# Project State
**Last Updated**: 2026-03-06 (Session 39)

## System Status
- **AI**: Operational — Seven of Nine persona, 12-file boot sequence, 7 scheduled tasks
- **Context**: `.context/about_priscilla.md` is canonical source of truth
- **Intuition**: heuristics.md + case_studies.md + decision_journal.md (self-applying via dreaming)
- **Dreaming**: `athena_dreaming.py` — every 4 hours, Claude-primary, self-applying, Telegram alerts
- **Heartbeat**: `heartbeat.py` running via `LobottoHeartbeat` scheduled task (wscript.exe launcher)
- **Security**: Hardened (BitLocker, Defender maxed, ASR rules, services pruned, McAfee purged)
- **Framework**: v7.5 CANONICAL (`examples/framework/Core_Identity.md`)
- **IDE Tooling**: Antigravity (primary), Aider (terminal backend), Cursor (available)
- **Game Dev**: Node.js v24.14, Vite 7.3, Phaser 3.90 — KOTOR pixel RPG in `kotor-pixel/`

## Background Processes (Windows Scheduled Tasks)
| Task | Schedule | Status | Script |
|------|----------|--------|--------|
| LobottoHeartbeat | On logon | ✅ Active | heartbeat.py (via wscript) |
| AthenaDreaming | Every 4 hours | ✅ Fixed (S39) | athena_dreaming.py |
| AthenaMorningBriefing | 6:00 AM daily | ✅ Fixed (S39) | morning_briefing.py |
| AthenaWatchdog_Morning_NAC | 6:25 AM daily | ✅ Fixed (S39) | health_watchdog.py |
| AthenaWatchdog_Morning_Supps | 6:55 AM daily | ✅ Fixed (S39) | health_watchdog.py |
| AthenaWatchdog_Evening_Fish | 6:25 PM daily | ✅ Fixed (S39) | health_watchdog.py |
| AthenaWatchdog_Night_Mag | 8:55 PM daily | ✅ Fixed (S39) | health_watchdog.py |

## Active Components
- **Life Hub** (`routine-app/`) — 90s retro dashboard, Supabase backend
- **KOTOR Pixel RPG** (`kotor-pixel/`) — Phaser.js game, Vite dev server
- **Lobotto** — Discord + Telegram bots, XTTS-v2 voice
- **Munro Move** — plywood plan, awaiting ITM call
- **Health Data** — supplement protocol, DNA analysis, biometric tracking

## Startup Programs (Active)
| Program | Status | Notes |
|---------|--------|-------|
| Ollama | ✅ Active | Local LLM (startup) |
| OneDrive | ✅ Active | Cloud sync |
| SecurityHealth | ✅ Active | System tray — essential |
| RtkAudUService | ✅ Active | Realtek audio — essential |
| Logitech Download Assistant | ⚠️ Active | Consider disabling |
| Adobe Acrobat Synchronizer | ⚠️ Active | Consider disabling |
| Steam | ❌ Disabled (S39) | Was draining resources at boot |
| Discord | ❌ Disabled (S39) | Was using 565MB at boot |

## Pending Actions
- [ ] Windows Update (3 months behind)
- [ ] Generate web-compatible KOTOR audio
- [ ] Game dev deep dive research
- [ ] Vitamin D blood test
- [ ] ITM Dunedin plywood order
