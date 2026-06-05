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

**How the Permanent Memory Works:**
You do **not** need to click "save" or manually export your chats. 
1. **The Chat:** You talk to the AI normally throughout the day.
2. **The Extraction:** Every night at 11:59 PM, an autonomous background robot (`n8n`) silently wakes up. It pulls your raw chat logs for the day and feeds them to the Atom's bare-metal processor.
3. **The Synthesis:** The AI automatically extracts the key events, facts, and emotional states, stripping away the conversational fluff.
4. **The Vault:** It writes a pristine Markdown file (e.g., `SJ_Diary_2026-06-05.md`) directly into the Atom's `/obsidian_vault` hard drive.
5. **The Sync:** Syncthing instantly beams that new file to your laptop, where you can view it in the Obsidian app as a physical 3D Knowledge Graph.

---

*This manual is a living document and will be updated as new AI capabilities (Council of Minds, Ambient Intelligence) come online.*
