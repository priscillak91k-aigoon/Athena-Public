# SOVEREIGN ATOM: MASTER ROADMAP

This roadmap tracks the evolution of the Atom server from a basic media host into a fully autonomous, lifelong digital companion and zero-trust infrastructure node.

---

## 🟢 PHASE 1: Bare-Metal Sovereignty (COMPLETED)
**Status:** Online. The foundation is stable and locked down.
- **Snap Eradication:** Ripped out `onlyoffice-ds` to free Port 80 and stop AppArmor kernel lockups.
- **Port Discipline:** Caddy owns Port 80/443. Pi-hole shifted to 8053.
- **Media Migration:** Installed Plex container (needs configuration/connection) and replaced the x86 TTS engine with ARM64-native EdgeTTS.
- **Offline Library:** 115GB Wikipedia `.zim` archive downloading via background `nohup`.
- **Core Apps:** Vaultwarden, Memos, DNA Parser, Tailscale.
- **Operations Manual:** (Pending) Write a comprehensive user manual for operating the media stack and generating content.

---

## 🟢 PHASE 2: Core AI Framework (COMPLETED)
**Status:** The Open WebUI and n8n stack are fully online.
- **The Upgrade:** Moved from raw Ollama to a fully interactive web UI.
- **The Stack:** Open WebUI (Local ChatGPT), `n8n` (Autonomous Background Agent), and SearXNG (Private Web Scraper) are actively running.
- **RAG Hardening:** Embedded `nomic-embed-text` to handle document ingestion.
- **[COMPLETED] Memory Extractor:** Secured API keys via browser bypass and armed the Midnight Memory Extractor pipeline.

---

## 🟢 PHASE 3: The Obsidian Mind Map (COMPLETED)
**Status:** Fully operational. AI writes directly to the local vault.
- **The Upgrade:** Creating a physical, interactive 3D Knowledge Graph of the AI's memory.
- **The Stack:** Syncthing is running and `n8n` has physical write permissions to `/vault`.
- **The Beam:** Markdown files are successfully syncing peer-to-peer to SJ's personal devices.

---

## 🟢 PHASE 4: Ambient Intelligence (IN PROGRESS)
**Status:** The central nervous system is online. Awaiting expansion.
- **[COMPLETED] The Walkie-Talkie:** Custom Telegram Python bridge deployed. Securely polls voice notes, routes to local Whisper for transcription, and writes directly to the Obsidian vault.
- **The Desktop HUD:** Global hotkey integration (`Ctrl+Space`) so the AI acts as a transparent spotlight search on his laptop.
- **[COMPLETED] Proactive Notifications:** The Morning Briefing pipeline is officially active. n8n autonomously pulls weather and yesterday's diary at 7:00 AM, synthesizes a briefing via Ollama, and texts it to Telegram.

---

## 🔴 PHASE 5: Lifelong Sovereignty (FUTURE IDEATION)
**Status:** Discussed with SJ. Awaiting architectural blueprinting.
- **Life Synthesis Engine:** `n8n` automatically compressing weekly journal entries into high-level psychological summaries to prevent the vector database from becoming noisy over decades.
- **Air-Gapped Financial Analyst:** Local parsing of raw bank CSVs without using Mint/Plaid to maintain financial privacy.
- **The Legacy Vault (Dead Man's Switch):** An encrypted folder containing seed phrases and final messages that unlocks and transmits to a trusted contact if SJ misses a 90-day pulse check.
