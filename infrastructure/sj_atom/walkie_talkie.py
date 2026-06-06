import os
import time
import requests
import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WHISPER_URL = "http://whisper-api:9000/asr"
VAULT_DIR = "/vault"
POLL_INTERVAL = 5

def get_updates(offset):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 10, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=15)
        return response.json().get("result", [])
    except Exception as e:
        print(f"Error getting updates: {e}")
        return []

def download_file(file_id, save_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
    resp = requests.get(url).json()
    if not resp.get("ok"): return None
    file_path = resp["result"]["file_path"]
    
    dl_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
    file_data = requests.get(dl_url).content
    with open(save_path, "wb") as f:
        f.write(file_data)
    return save_path

def transcribe_audio(file_path):
    with open(file_path, "rb") as f:
        files = {"audio_file": f}
        try:
            resp = requests.post(WHISPER_URL, files=files)
            if resp.headers.get('content-type') == 'application/json':
                return resp.json().get('text', '')
            else:
                return resp.text
        except Exception as e:
            print(f"Transcription error: {e}")
            return None

def synthesize_memory(raw_text):
    prompt = f"""You are an autonomous memory synthesis engine for SJ's lifelong digital diary. 
Read her raw stream-of-consciousness transcript and structure it for long-term vector database storage.

RAW TRANSCRIPT:
"{raw_text}"

INSTRUCTIONS:
1. Extract the core emotional state or sentiment (e.g., Anxious, Excited, Reflective).
2. Extract key entities (people, places, projects) and list them as #tags.
3. Summarize the main points into clear, concise bullet points.
4. Output strictly in this Markdown format, with NO conversational filler:

**Emotional State:** [Emotion]
**Key Entities:** #tag1 #tag2

**Synthesis:**
- [Bullet point 1]
- [Bullet point 2]
"""
    try:
        resp = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=120
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"Ollama synthesis failed: {e}")
    return None

def write_to_vault(raw_text, synthesized_text):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%I:%M %p")
    file_name = f"SJ_Diary_{date_str}.md"
    file_path = os.path.join(VAULT_DIR, file_name)
    
    # Check if file exists to determine if we need a header
    header = ""
    if not os.path.exists(file_path):
        header = f"# Sovereign Journal - {date_str}\n\n"
        
    if synthesized_text:
        content = f"{synthesized_text}\n\n<details>\n<summary>Raw Transcript</summary>\n\n{raw_text.strip()}\n</details>"
    else:
        content = raw_text.strip()
        
    entry = f"{header}### 🎙️ Walkie-Talkie Log ({time_str})\n{content}\n\n---\n\n"
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(entry)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def main():
    print("Starting Sovereign Walkie-Talkie Bridge...")
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_TOKEN not set!")
        return
        
    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message", {})
            chat_id = message.get("chat", {}).get("id")
            
            if not chat_id: continue
            
            # ZERO-TRUST LOCKDOWN: Only accept messages from SJ
            if str(chat_id) != "8309108979":
                print(f"SECURITY BLOCK: Dropped unauthorized message from {chat_id}")
                continue
            # Handle Voice Notes
            if "voice" in message:
                file_id = message["voice"]["file_id"]
                print(f"Received voice note from {chat_id}. Downloading...")
                audio_path = f"/tmp/{file_id}.ogg"
                download_file(file_id, audio_path)
                
                print("Transcribing via Local Whisper...")
                raw_text = transcribe_audio(audio_path)
                
                if raw_text:
                    print(f"Transcription: {raw_text[:50]}...")
                    print("Synthesizing memory via Ollama...")
                    synthesized_text = synthesize_memory(raw_text)
                    write_to_vault(raw_text, synthesized_text)
                    send_message(chat_id, "✅ Voice note transcribed, synthesized, and logged to vault.")
                else:
                    send_message(chat_id, "❌ Failed to transcribe audio. Is Whisper running?")
                    
                if os.path.exists(audio_path): os.remove(audio_path)
            
            # Handle Text Notes
            elif "text" in message:
                raw_text = message["text"]
                print(f"Received text note: {raw_text[:50]}...")
                print("Synthesizing memory via Ollama...")
                synthesized_text = synthesize_memory(raw_text)
                write_to_vault(raw_text, synthesized_text)
                send_message(chat_id, "✅ Text synthesized and logged to vault.")
                
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
