# SOVEREIGN ATOM: MASTER ROADMAP

This roadmap tracks the evolution of the Atom server from a basic media host into a fully autonomous, lifelong digital companion and zero-trust infrastructure node.

---

## 🟢 PHASE 1: Bare-Metal Sovereignty (COMPLETED)
**Status:** Online. The foundation is stable and locked down.
- **Snap Eradication:** Ripped out `onlyoffice-ds` to free Port 80 and stop AppArmor kernel lockups.
- **Port Discipline:** Caddy owns Port 80/443. Pi-hole shifted to 8053.
- **Media Migration:** Deployed Plex and replaced the x86 TTS engine with ARM64-native EdgeTTS.
- **Offline Library:** 115GB Wikipedia `.zim` archive downloading via background `nohup`.
- **Core Apps:** Vaultwarden, Memos, DNA Parser, Tailscale.
- **Operations Manual:** (Pending) Write a comprehensive user manual for operating the media stack and generating content.

---

## 🟡 PHASE 2: The Council of Minds (READY FOR EXECUTION)
**Status:** Blueprints are coded in FURY. Awaiting terminal execution on the Atom.
- **The Upgrade:** Moving from raw Ollama to a fully interactive AI ecosystem.
- **The Stack:** Open WebUI (Local ChatGPT), `n8n` (Autonomous Background Agent), and SearXNG (Private Web Scraper) have been added to `docker-compose-ai.yml`.
- **RAG Hardening:** Fixed a fatal flaw where Open WebUI would try to read Memos' SQLite database. We mapped Ollama `nomic-embed-text` to handle heavy lifting.
- **Action Required:** 
  1. SSH into the Atom and run `docker compose -f docker-compose-ai.yml up -d`
  2. Follow `PHASE_2_EXECUTION_GUIDE.md` to configure the 5 parallel personas (Stoic, Psychologist, etc.) and clinical RAG settings.

---

## 🟡 PHASE 3: The Obsidian Mind Map (READY FOR EXECUTION)
**Status:** Blueprints are coded in FURY. Awaiting terminal execution on the Atom.
- **The Upgrade:** Creating a physical, interactive 3D Knowledge Graph of the AI's memory.
- **The Stack:** Syncthing added to the compose file. `n8n` given physical write permissions to the new `/opt/atom/data/obsidian_vault` directory.
- **Action Required:** 
  1. Boot the updated compose file.
  2. Follow `PHASE_3_EXECUTION_GUIDE.md` to pair SJ's laptop via Syncthing and initialize the Obsidian Vault.

---

## 🔴 PHASE 4: Ambient Intelligence (FUTURE IDEATION)
**Status:** Discussed with SJ. Awaiting architectural blueprinting.
- **The Walkie-Talkie:** Telegram/Signal bot wired into `n8n` + Whisper so SJ can send voice notes to the AI while driving for frictionless journaling.
- **The Desktop HUD:** Global hotkey integration (`Ctrl+Space`) so the AI acts as a transparent spotlight search on his laptop.
- **Proactive Notifications:** The AI pushing morning briefings (weather, schedule, journal insights) to his phone instead of waiting to be spoken to.

---

## 🔴 PHASE 5: Lifelong Sovereignty (FUTURE IDEATION)
**Status:** Discussed with SJ. Awaiting architectural blueprinting.
- **Life Synthesis Engine:** `n8n` automatically compressing weekly journal entries into high-level psychological summaries to prevent the vector database from becoming noisy over decades.
- **Air-Gapped Financial Analyst:** Local parsing of raw bank CSVs without using Mint/Plaid to maintain financial privacy.
- **The Legacy Vault (Dead Man's Switch):** An encrypted folder containing seed phrases and final messages that unlocks and transmits to a trusted contact if SJ misses a 90-day pulse check.
