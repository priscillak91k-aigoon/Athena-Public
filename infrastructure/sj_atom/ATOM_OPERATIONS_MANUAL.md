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
> **Previewing Voices:** You can test voices in real-time using the [Microsoft Voice Gallery](https://speech.microsoft.com/portal/voicegallery) or the [Hugging Face Edge-TTS Interface](https://huggingface.co/spaces/innoai/Edge-TTS-Text-to-Speech).

---

## 🧠 Open WebUI & The Memory Engine

> *Your private, sovereign AI interface and automatic digital diary.*

### Access Points

| Connection Type | URL |
| :--- | :--- |
| **Tailscale IP** | `http://100.73.93.94:3000` |
| **MagicDNS** | `http://ai.atom.tailnet` |

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
> Every night at 3:00 AM, the engine checks yesterday's diary for any fundamental life changes. If it detects a major shift, it automatically overwrites `SJ_Core_Profile.md` and instantly fires an API request to **rebuild the `sj-diary` chat model on the fly**. The Open WebUI model never goes stale.

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

### How it Works
1. The engine wakes up exactly **every 12 hours**.
2. It calculates the precise dates for **upcoming weekends 3, 4, 5, and 6**.
3. It checks Google Flights for Direct, Round-Trip flights between Dunedin (DUD) and Wellington (WLG).
4. If it detects a flight under your target threshold (currently **$300 NZD**), it pings your phone via the private Telegram bot.

### How to Modify Target Parameters
To change the destination or the price limit:
1. Open `~/Athena-Public/infrastructure/sj_atom/docker-compose-ai.yml` on the Atom.
2. Locate the `flight-scanner` service block at the bottom of the file.
3. Edit the `FLY_TO`, `FLY_FROM`, or `TARGET_PRICE` environment variables.
4. Run `sudo docker compose -f docker-compose-ai.yml up -d --build` to permanently lock in the new parameters.
