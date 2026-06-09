# 📖 Sovereign Atom: Operations Manual

> [!NOTE]
> Welcome to the Atom's sovereign media infrastructure. This manual outlines how to operate the services from anywhere in the world without relying on cloud providers.

---

## 🌐 The Zero-Trust Network (Tailscale)

> [!IMPORTANT]
> The Atom server is invisible to the public internet. To access any of the services below while away from your home WiFi, you **must** use Tailscale.

**Connection Steps:**
1. Install the **Tailscale** app on your phone, laptop, or tablet.
2. Log in with your authorized account.
3. Toggle the VPN to **Active**.
4. You can now use the `100.x` IP addresses or `.tailnet` domains exactly as if you were sitting in your living room.

---

## 🎧 Audiobookshelf (The Library)

> *Your private, sovereign replacement for Audible.*

### Access Points

| Connection Type | URL |
| :--- | :--- |
| **Tailscale IP** | `http://100.73.93.94:13378` |
| **MagicDNS** | `http://audio.atom.tailnet` |
| **Home WiFi** | `http://192.168.88.50:13378` |

### Usage Guide
1. Open the URL in your browser or download the official **Audiobookshelf App** (iOS/Android) and use the URL as the Server Address.
2. **Streaming:** Click any book and hit play. It will stream directly from the Atom to your device.
3. **Offline Listening:** Use the mobile app to "Download" a book to your phone before a flight or road trip.
4. **Progress Sync:** Your listening progress automatically syncs across all devices.

---

## 🏭 EdgeTTS (The Audiobook Generator)

> *Your private factory for converting text/EPUBs into high-quality, human-like neural audio.*

### Access Points

| Connection Type | URL |
| :--- | :--- |
| **Tailscale IP** | `http://100.73.93.94:7860` |
| **MagicDNS** | `http://tts.atom.tailnet` |
| **Home WiFi** | `http://192.168.88.50:7860` |

### How to Generate a Book
1. Obtain an `.epub` file of the book you want.
2. Open the EdgeTTS URL and drag your `.epub` into the upload box.
3. **Configure Settings:**
   > [!WARNING]
   > **Output Directory:** You must set this to exactly `/app/output`. If you forget this, the book will be lost inside the container matrix.
   
   - **Worker Count:** Set between `5` and `8` for maximum speed.
   - **Voice:** Select your preferred narrator. *(Recommended: `en-GB-ThomasNeural` for a classic, deep storyteller vibe).*
   - **Voice Rate/Pitch:** For a "sleep story" or older narrator feel, drop Rate to `-15` and Pitch to `-10`.
4. Hit **Start**. You can close your laptop. The Atom will autonomously crunch the entire book in the background and drop it into your library.
   > [!TIP]
   > **Library Sync:** Once the generation finishes, you may need to open Audiobookshelf and click **Scan Library** for the new book to physically appear.

> [!TIP]
> **Previewing Voices:** You can test voices in real-time using the [Microsoft Voice Gallery](https://speech.microsoft.com/portal/voicegallery) or the [Hugging Face Edge-TTS Interface](https://huggingface.co/spaces/innoai/Edge-TTS-Text-to-Speech).

### How to Narrate Custom Writing

If any horny slags want to write their own smut and have it narrated to them, the Audio Factory is perfect because it is 100% uncensored. Since it runs strictly bare-metal on the Atom, no cloud provider (like OpenAI or Microsoft) will ever flag it or ban your account.

1. **Write the Story:** Write it in whatever app you prefer (Google Docs, Apple Pages, Obsidian).
2. **Export as EPUB:** The Audio Factory works best with `.epub` files because it automatically understands chapter breaks and pacing. 
   - *Google Docs:* `File -> Download -> EPUB Publication (.epub)`.
   - *Apple Pages:* `File -> Export To -> EPUB`.
3. **Upload & Generate:** Drop the `.epub` file into the TTS interface (`http://100.73.93.94:7860`), select a narrator, and hit Start. It will autonomously chew through the text and output a pristine, professional-grade Audiobook file.

---

## 🧠 Open WebUI & The Memory Engine

> *Your private, sovereign AI interface and automatic digital diary.*

### Access Points

| Connection Type | URL |
| :--- | :--- |
| **Tailscale IP** | `http://100.73.93.94:3000` |
| **MagicDNS** | `http://ai.atom.tailnet` |
| **Home WiFi** | `http://192.168.88.50:3000` |

### Permanent Memory Pipeline
You do **not** need to click "save" or manually export your chats. 

1. **The Trigger:** Every night at 11:59 PM, the `n8n` container silently wakes up.
2. **The Extraction:** It pulls down all raw chat logs from your private account securely via the internal Open WebUI server.
3. **The Synthesis:** It feeds that data into the bare-metal Ollama API (`llama3`) to extract core emotional states, key events, and actionable thoughts.
4. **The Vault:** It takes the pristine summary and physically writes it into the Atom's `/obsidian_vault` hard drive (e.g., `SJ_Diary_2026-06-05.md`).
5. **The Sync:** Syncthing instantly beams that new file to your laptop to view in the Obsidian app.

### The Core Profile (Tier 2 Memory) & Auto-Bake
The engine maintains a foundational document (`SJ_Core_Profile.md`) containing core demographic and psychological facts. 

> [!IMPORTANT]
> Every night at 3:00 AM, the engine checks yesterday's diary for any fundamental life changes. If it detects a major shift, it automatically overwrites `SJ_Core_Profile.md` and instantly fires an API request to **rebuild BOTH your `sj-diary` (Fast Chat) and `sj-diary-reasoning` (Deep Think) models on the fly**. This guarantees your Open WebUI models never go stale.

---

## 📱 The Walkie-Talkie (Ambient Intelligence)

> *Your direct, hands-free link to your private diary via Telegram.*

### Usage Guide
1. Open the Telegram app on your phone and open the private chat with your Diary Bot.
2. **Text Notes:** Type any text message and hit send. It will instantly log to your diary.
3. **Voice Notes:** While driving or walking, hold the microphone button to record a voice note. The Atom will instantly intercept the message and securely transcribe the audio using offline Whisper AI.

### Memory Synthesis & Silence Filter
Before saving, the Atom securely routes the raw text through your local `llama3` LLM to structure your thoughts into clean bullet points. 

> [!WARNING]
> **Silence Filter:** If it detects that the transcript is just wind noise or Whisper hallucination garbage (e.g., "Thanks for watching"), it will instantly incinerate the file to keep your vault pristine and text you a warning.

It appends the structured summary to today's `.md` file, hiding the messy transcript inside a collapsible `<details>` dropdown, and embeds hidden JSON psychological telemetry (`mood`, `stress`, `energy`).

> [!NOTE]
> **Zero-Trust Security:** The Walkie-Talkie engine is cryptographically locked to SJ's exact Telegram User ID. Your diary cannot be written to by anyone but you.

---

## 🌅 The Sunday Reflection (Weekly Synthesis)

> *The Atom connects your present to your past, without ever pinging your phone.*

This is a completely autonomous, silent pipeline built natively into the Walkie-Talkie engine. 

1. At exactly **8:00 PM every Sunday**, the Python engine wakes up.
2. It silently reads every single diary entry from the past **7 days**, plus historical echoes from exactly **30 days ago** and **365 days ago**.
3. The AI generates a customized Weekly Synthesis, identifying core emotional themes and reflecting on psychological growth.
4. The finalized Markdown file is silently dropped into your vault as `SJ_Weekly_Synthesis_[Date].md`.

---

## ✈️ Automated Flight Tracker (The Hunter)

> *Your autonomous background service for securing cheap weekend flights.*

### How it Works (Context-Aware)
The Flight Tracker is fully context-aware and tied to your private Diary vault. It **will not scan** or spam you unless you actively tell it you are looking for flights.

1. **The Intent Check:** Every 24 hours, before doing anything, it securely reads your latest journal entry and asks the local Ollama AI to determine if you are actively looking for a flight.
2. **The 4-Week Lock:** If intent is found, it extracts the date of that journal entry. It generates the precise dates for the **4 weekends following your journal entry**.
3. **The Hunt:** It checks Google Flights for Direct, Round-Trip flights under your threshold (currently **$300 NZD**). If it finds them, it pings your phone via Telegram. Since you are actively looking, it will ping you every 24 hours to ensure you don't miss sudden price drops.
4. **The Auto-Shutoff:** Once the real-world date passes the Sunday of the 4th weekend, the target window expires and the scanner automatically shuts down to prevent spam.
5. **The Manual Override:** If you buy a flight early or change your mind, simply type `#stopflights` or `#haltflights` anywhere in your newest journal entry. The scanner will detect the tag and instantly shut down.

### How to Modify Target Parameters
To change the destination or the price limit:
1. Open `~/Athena-Public/infrastructure/sj_atom/docker-compose-ai.yml` on the Atom.
2. Locate the `flight-scanner` service block at the bottom of the file.
3. Edit the `FLY_TO`, `FLY_FROM`, or `TARGET_PRICE` environment variables.
4. Run `sudo docker compose -f docker-compose-ai.yml up -d --build` to permanently lock in the new parameters.

---

## 🎬 Media Automation Stack (The Empire)

> *Sovereign media acquisition and serving. Request a movie → it appears on your TV.*

### Architecture
```
Telegram ← Seerr (notifications)
                ↓
         Radarr / Sonarr
                ↓
            Prowlarr (indexers)
                ↓
     qBittorrent ← [Gluetun VPN — optional]
                ↓
      /mnt/media/data/media/
                ↓
              Plex → TV/Phone/Browser
```

### How to Use The Stack (Daily Operation)

You do **not** need to manually download torrents or interact with Radarr/Sonarr. The entire pipeline is operated exclusively through Telegram and Jellyfin.

**1. Requesting Content (Telegram Bot)**
The fastest way to request media is via the autonomous Telegram Bot.
1. Open the private chat or shared group chat with the Seerr Bot in Telegram.
2. Type `/check <Movie or Show Title>` (e.g. `/check The Matrix`).
   > [!TIP]
   > **First Time Setup:** If the bot replies "No user configured", tap the **🔄 Switch User** button and select the main profile. It will permanently link your Telegram ID so you never have to do it again.
3. Tap the **1080p** or **4K** button underneath the poster.
4. The bot will autonomously route the request to Seerr, which triggers Radarr/Sonarr, which sends it to qBittorrent to download directly to the 11TB QNAP array.

*(Alternatively, you can request via the Seerr Web UI at `http://192.168.88.50:5055` or `http://seerr.atom.tailnet` via Tailscale).*

**2. Watching Content (Jellyfin)**
1. Open the **Jellyfin** app on your TV, phone, or browser.
   - **On Home WiFi:** Use `http://192.168.88.50:8096`
   - **Outside Network (Cellular/Travel):** You **must** activate the Tailscale VPN on your device first, then connect to `http://100.73.93.94:8096` or `http://jellyfin.atom.tailnet`
2. Log in with your standard Jellyfin username and password.
3. Once a requested download hits 100%, it will magically appear on your Jellyfin home screen.
4. Click play.

**3. Troubleshooting Stalled Downloads**
If a movie is taking hours and hasn't finished:
1. Open **qBittorrent** (`http://192.168.88.50:8088`). Check if the torrent has 0 seeders or is stuck on "Stalled".
2. If it is stalled, open **Radarr** or **Sonarr**, search for the title, click the manual "Search" tab, and explicitly pick a different torrent with more seeders.

### Service Map

| Service | Port | What It Does |
|---------|------|-------------|
| Jellyfin| 8096 | Primary sovereign media server |
| Plex | 32400 | Secondary media server (host network) |
| Radarr | 7878 | Movie automation |
| Sonarr | 8989 | TV show automation |
| Prowlarr | 9696 | Indexer management |
| Seerr | 5055 | Request management + Telegram |
| qBittorrent | 8088 | Download client |
| Gluetun | — | VPN kill-switch (optional — Mode B) |
| Recyclarr | — | TRaSH Guide quality sync (daily cron) |

### Deploy Commands
```bash
# First time: mount the media drive
sudo bash mount_media_drive.sh

# Deploy the stack
cd ~/Athena-Public/infrastructure/sj_atom
docker compose -f docker-compose-media.yml up -d

# Check status
docker compose -f docker-compose-media.yml ps

# Verify VPN (only if using Mode B)
docker exec gluetun curl -s ifconfig.me
```

### Critical Path Notes
- ⚠️ Plex uses `network_mode: host` for DLNA discovery. It is NOT on the Docker bridge network. Seerr must connect to Plex via the host's LAN IP (e.g., `http://192.168.x.x:32400`), not by container name.
- VPN is **optional** (Mode B in compose file). Stack runs out of the box in Mode A without VPN credentials.

### Full Setup Guide
See: `MEDIA_STACK_SETUP.md` for the complete post-deploy wiring walkthrough.

