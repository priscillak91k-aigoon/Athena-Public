<style>
  body {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    line-height: 1.7;
    color: #e2e8f0;
    max-width: 900px;
    margin: 0 auto;
    padding: 30px;
  }
  h1, h2, h3 {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #f8fafc;
    margin-top: 1.8em;
  }
  h1 { font-size: 2.2em; border-bottom: 2px solid #334155; padding-bottom: 10px; }
  h2 { font-size: 1.6em; border-bottom: 1px solid #1e293b; padding-bottom: 8px; }
  p, li { font-size: 1.05em; color: #cbd5e1; }
  strong { color: #38bdf8; font-weight: 600; }
  em { color: #94a3b8; }
  code {
    background-color: #1e293b !important;
    padding: 3px 6px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.9em;
    color: #f1f5f9;
  }
  blockquote {
    border-left: 4px solid #38bdf8;
    padding: 10px 15px;
    background-color: rgba(56, 189, 248, 0.05);
    margin-left: 0;
    font-style: italic;
    border-radius: 0 8px 8px 0;
  }
  hr { border: 0; border-top: 1px solid #334155; margin: 2.5em 0; }
</style>

# 📖 Sovereign Atom: Operations Manual

Welcome to the Atom's sovereign media infrastructure. This manual outlines how to operate the services from anywhere in the world without relying on cloud providers.

## 🌐 The Zero-Trust Network (Tailscale)
The Atom server is invisible to the public internet. To access any of the services below while away from your home WiFi, you **must** use Tailscale.

1. Install the **Tailscale** app on your phone, laptop, or tablet.
2. Log in with your authorized account.
3. Toggle the VPN to **Active**.
4. You can now use the `100.x` IP addresses or `.tailnet` domains exactly as if you were sitting in your living room.

---

## 🎧 Audiobookshelf (The Library)
*Your private, sovereign replacement for Audible.*

**Access URLs:**
- Tailscale IP: `http://100.73.93.94:13378`
- MagicDNS: `http://audio.atom.tailnet`
- Home WiFi: `http://192.168.88.50:13378`

**How to Use:**
1. Open the URL in your browser or download the official **Audiobookshelf App** (iOS/Android) and use the URL as the Server Address.
2. **Streaming:** Click any book and hit play. It will stream directly from the Atom to your device.
3. **Offline Listening:** Use the mobile app to "Download" a book to your phone before a flight or road trip.
4. **Progress Sync:** Your listening progress automatically syncs across all devices.

---

## 🏭 EdgeTTS (The Audiobook Generator)
*Your private factory for converting text/EPUBs into high-quality, human-like neural audio.*

**Access URLs:**
- Tailscale IP: `http://100.73.93.94:7860`
- MagicDNS: `http://tts.atom.tailnet`
- Home WiFi: `http://192.168.88.50:7860`

**How to Generate a Book:**
1. Obtain an `.epub` file of the book you want.
2. Open the EdgeTTS URL and drag your `.epub` into the upload box.
3. **CRITICAL SETTINGS:**
   - **Output Directory:** Change to exactly `/app/output`. *(If you forget this, the book will be lost in the matrix).*
   - **Worker Count:** Set between `5` and `8` for maximum speed.
   - **Voice:** Select your preferred narrator. (We recommend `en-GB-ThomasNeural` for a classic, deep storyteller vibe).
   - **Voice Rate/Pitch:** For a "sleep story" or older narrator feel, drop Rate to `-15` and Pitch to `-10`.
4. Hit **Start**.
5. You can close your laptop. The Atom will autonomously crunch the entire book in the background. Once finished, it will automatically drop the file into your Audiobookshelf library.

---

## 🎙️ Previewing Voices
Because the Generator processes massive files, it cannot preview voices directly. To test a voice before committing to a 10-hour generation:

- **Option A:** Use the [Microsoft Voice Gallery](https://speech.microsoft.com/portal/voicegallery) to test voices in real-time.
- **Option B:** Use the [Hugging Face Edge-TTS Interface](https://huggingface.co/spaces/innoai/Edge-TTS-Text-to-Speech) for an exact replica of the voice dropdown list.

---

## 🚀 The Pipeline: From Creation to Listening
This is the step-by-step workflow for turning a raw ebook into a streaming audiobook.

**Step 1: The Source Material**
- Download your desired book in `.epub` format to your laptop.

**Step 2: The Factory Floor (EdgeTTS)**
- Go to `http://100.73.93.94:7860`.
- Upload the `.epub` file.
- **Critical:** Set Output Directory to `/app/output`.
- **Optimization:** Set Worker Count to `5` (uses 5 CPU cores simultaneously).
- **Casting:** Select your voice (e.g., `en-GB-ThomasNeural`). For a "sleep story" vibe, tweak Rate to `-15` and Pitch to `-10`.
- Click **Start**. You can now close your laptop. The Atom will autonomously crunch the audio in the background.

**Step 3: The Handoff**
- Because we wired the Docker containers together, the moment the factory finishes generating the last chapter, the audio files are instantly teleported into Audiobookshelf's private `/audiobooks` folder on the Atom's hard drive.

**Step 4: The Library Scan (Audiobookshelf)**
- Go to `http://100.73.93.94:13378` (or open the app on your phone).
- The library usually scans automatically every 24 hours, but to see it instantly, click the **Scan** button in the top right corner of the dashboard.
- Audiobookshelf will detect the new files, search Google Books for the cover art and author bio, and package it into a beautiful interface.

**Step 5: The Stream**
- Tap the book cover and hit Play. 
- You are now streaming your own private, unmetered neural audiobook from the Atom to your device. 

---

## 🧠 Open WebUI & The Memory Engine
*Your private, sovereign AI interface and automatic digital diary.*

**Access URLs:**
- Tailscale IP: `http://100.73.93.94:3000`
- MagicDNS: `http://ai.atom.tailnet`

**How to Use the Digital Diary:**
1. Open the URL in your browser or phone.
2. Ensure you are logged into your isolated account (e.g., SJ's account).
3. At the top of the chat screen, click the dropdown and select the **`SJ Diary`** custom model.
4. Talk to it like a journal. It is programmed to listen, validate emotions, and extract core facts. It is also time-aware.

**How the Permanent Memory Works (Technical Breakdown):**
You do **not** need to click "save" or manually export your chats. 
1. **The Trigger:** Every night at 11:59 PM, the `n8n` container silently wakes up.
2. **The Extraction:** It fires an API request securely to the internal Open WebUI server (`http://host.docker.internal:3000/api/v1/chats/`) using SJ's exact JSON Web Token (JWT). This pulls down all raw chat logs from her private account for that specific day.
3. **The Synthesis (Ollama Brain):** It then takes that raw, messy JSON data and feeds it into the Atom's bare-metal Ollama API (`llama3`) with this exact cryptographic prompt:
   > *"You are an autonomous memory synthesis engine. Read the following raw chat logs from SJ's digital diary today. Extract the core emotional states, key events, and actionable thoughts. Format your output strictly as a clean Markdown journal entry with headers. Do not include any conversational filler."*
4. **The Vault:** Once the AI finishes thinking, it takes the pristine summary and physically writes it into the Atom's `/obsidian_vault` hard drive (e.g., `SJ_Diary_2026-06-05.md`).
5. **The Sync:** Syncthing instantly beams that new file to your laptop, where you can view it in the Obsidian app as a physical 3D Knowledge Graph.

**The Core Profile (Tier 2 Memory) & Auto-Bake Protocol:**
The engine maintains a foundational document (`SJ_Core_Profile.md`) containing your core demographic and psychological facts. 
1. Every night at 3:00 AM, the engine checks yesterday's diary for any fundamental life changes (e.g., new job, new relationship).
2. If it detects a major shift, it automatically overwrites `SJ_Core_Profile.md`.
3. **The Auto-Bake:** It then instantly sends an API request directly into the Ollama kernel to physically rebuild the `sj-diary` chat model, permanently baking the new facts into its neural weights. The Open WebUI model never goes stale and perfectly tracks your life trajectory.

**How to Test or Manually Run the Pipeline:**
If you don't want to wait until midnight, you can force the extraction at any time:
1. Open n8n (`http://100.73.93.94:5678`) and open the **SJ's Daily Memory Extractor** workflow.
2. Click **Execute Workflow** at the bottom of the screen.
3. The **Ollama Brain** node will say "Running..." and display a spinning loading icon. This can take a few minutes because the local processor is physically reading your entire day's chat log and writing a summary from scratch, entirely offline.
4. **How to know it worked:** When it finishes, a small green checkmark (✅) will appear on the top right of the Ollama node, and the final "Write to Obsidian Vault" node will execute instantly and turn green.
5. Check your Obsidian Vault—the new `.md` file will be sitting there waiting for you.

---

## 📱 The Walkie-Talkie (Ambient Intelligence)
*Your direct, hands-free link to your private diary via Telegram.*

**How to Use the Walkie-Talkie:**
1. Open the Telegram app on your phone and open the private chat with your Diary Bot.
2. **Text Notes:** Type any text message and hit send. It will instantly log to your diary.
3. **Voice Notes:** While driving or walking, hold the microphone button in Telegram to record a voice note, then send it.
4. The Atom will instantly intercept the message and securely transcribe the audio using its offline Whisper AI.
5. **Memory Synthesis & Silence Filter:** Before saving, the Atom securely routes the raw text through your local `llama3` LLM. The AI extracts the core emotion, detects key entities as `#tags`, and structures your raw thoughts into clean bullet points. If it detects that the transcript is just wind noise or Whisper AI hallucination garbage (e.g., "Thanks for watching"), it will instantly incinerate the file to keep your vault pristine and text you a warning.
6. It appends this highly structured summary to today's `.md` file in your Obsidian vault, hiding the messy raw transcript inside a collapsible `<details>` dropdown. It also embeds hidden JSON psychological telemetry (`mood`, `stress`, `energy`) at the bottom of the file for longitudinal tracking.
7. The bot will automatically reply `✅ Voice note transcribed, synthesized, and logged to vault.` to confirm it was captured.

**Zero-Trust Security:**
Because Telegram bots are technically public, the Walkie-Talkie engine is cryptographically locked to SJ's exact Telegram User ID. If anyone else on the internet guesses the bot's username and tries to send it a message, the server will instantly incinerate it. Your diary cannot be written to by anyone but you.

---

## 🌅 The Sunday Reflection (Weekly Synthesis)
*The Atom connects your present to your past, without ever pinging your phone.*

**How it Works:**
This is a completely autonomous, silent pipeline built natively into the Walkie-Talkie engine. You do not need to push any buttons.
1. At exactly **8:00 PM every Sunday**, the Python engine wakes up.
2. It silently reaches into your Obsidian Vault and reads every single diary entry from the past **7 days**.
3. It specifically hunts for `SJ_Diary_` files from exactly **30 days ago** and **365 days ago**.
4. It feeds all of this environmental and historical context into the bare-metal Ollama `llama3` processor.
5. The AI generates a customized, profoundly personal Weekly Synthesis. It identifies your core emotional themes of the week and reflects on your psychological growth by comparing your present state to your historical echoes.
6. The finalized Markdown file is silently dropped into your vault as `SJ_Weekly_Synthesis_[Date].md`.

**Graceful Degradation:**
If you did not write any diary entries this week, the system will simply skip the synthesis and go back to sleep. If historical echoes (T-30/T-365) don't exist yet, it will just summarize the current week.

---

*This manual is a living document and will be updated as new AI capabilities (Council of Minds, Ambient Intelligence) come online.*

---

## ✈️ Automated Flight Tracker (The Hunter)
*Your autonomous background service for securing cheap weekend flights.*

**How it Works:**
This is a completely "set it and forget it" microservice that runs autonomously in the dark.
1. The engine wakes up exactly **every 12 hours**.
2. It mathematically calculates the precise dates for **upcoming weekends 3, 4, 5, and 6** (skipping the immediate two weeks to avoid expensive last-minute pricing).
3. It securely proxies an API request to Google Flights to check the exact prices for **Direct, Round-Trip flights** between Dunedin (DUD) and Wellington (WLG).
4. If it detects a flight under your target threshold (currently **$300 NZD** total round-trip), it instantly pings your phone via the private Telegram bot with a direct booking link.
5. If no flights match the criteria, the engine stays completely silent and goes back to sleep to conserve your 250/month free API quota.

**How to Modify Target Parameters:**
If you ever need to change the destination or the price limit:
1. Open `~/Athena-Public/infrastructure/sj_atom/docker-compose-ai.yml` on the Atom.
2. Locate the `flight-scanner` service block at the bottom of the file.
3. Edit the `FLY_TO`, `FLY_FROM`, or `TARGET_PRICE` environment variables.
4. Run the standard boot sequence (`sudo docker compose -f docker-compose-ai.yml up -d --build`) to permanently lock in the new parameters.
