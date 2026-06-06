import os
import time
import requests
import datetime
import schedule

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
4. Extrapolate her psychological telemetry. Estimate on a scale of 1-10 her Mood, Stress, and Energy levels based on the text.
5. Output strictly in this Markdown format, with NO conversational filler:

**Emotional State:** [Emotion]
**Key Entities:** #tag1 #tag2

**Synthesis:**
- [Bullet point 1]
- [Bullet point 2]

<!-- {"mood": [1-10], "stress": [1-10], "energy": [1-10]} -->
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

def update_core_profile():
    print("Initiating daily Core Profile synthesis...")
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    diary_path = os.path.join(VAULT_DIR, f"SJ_Diary_{yesterday}.md")
    # For now, looking in the vault directly, assuming we move the seed file here or it syncs here
    profile_path = os.path.join(VAULT_DIR, "SJ_Core_Profile.md")
    
    # If there's no diary from yesterday or no profile, we can't update
    if not os.path.exists(diary_path) or not os.path.exists(profile_path):
        print("Missing diary or profile. Skipping Core Profile update.")
        return

    with open(profile_path, "r", encoding="utf-8") as f:
        current_profile = f.read()
        
    with open(diary_path, "r", encoding="utf-8") as f:
        yesterday_diary = f.read()

    prompt = f"""You are the Memory Tier 2 Engine. Your job is to update SJ's Core Profile based on her latest diary entry.

CURRENT CORE PROFILE:
{current_profile}

YESTERDAY'S DIARY:
{yesterday_diary}

INSTRUCTIONS:
1. Did any fundamental, long-term facts about SJ's life change in the diary? (e.g., new job, new relationship, major health event, moved cities, core belief shift).
2. If absolutely NOTHING fundamental changed, you MUST output exactly: NO_CHANGE
3. If a fundamental fact DID change, rewrite the ENTIRE Core Profile incorporating the new information. Keep the same Markdown structure.
"""
    try:
        resp = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=300
        )
        if resp.status_code == 200:
            result = resp.json().get("response", "").strip()
            if result != "NO_CHANGE" and "NO_CHANGE" not in result:
                print("Core Profile updated. Writing to vault...")
                with open(profile_path, "w", encoding="utf-8") as f:
                    f.write(result)
            else:
                print("No fundamental changes detected. Core Profile remains unchanged.")
    except Exception as e:
        print(f"Ollama profile synthesis failed: {e}")

def main():
    print("Starting Sovereign Walkie-Talkie Bridge...")
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_TOKEN not set!")
        return
        
    # Run the profile updater daily at 3:00 AM
    schedule.every().day.at("03:00").do(update_core_profile)
    
    offset = None
    while True:
        schedule.run_pending()
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
