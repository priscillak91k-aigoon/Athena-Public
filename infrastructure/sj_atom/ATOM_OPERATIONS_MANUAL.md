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

*This manual is a living document and will be updated as new AI capabilities (Council of Minds, Obsidian Vault) come online.*
