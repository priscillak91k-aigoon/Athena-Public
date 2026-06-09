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
5. SILENCE FILTER: If the raw transcript is just background noise or YouTube filler (e.g., "Thank you for watching", "Subscribe to my channel") and contains no actual journal content, output EXACTLY the phrase: IGNORED_HALLUCINATION
6. If it is a valid entry, output strictly in this Markdown format, with NO conversational filler:

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
            json={"model": "deepseek-r1:8b", "prompt": prompt, "stream": False},
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
            json={"model": "deepseek-r1:8b", "prompt": prompt, "stream": False},
            timeout=300
        )
        if resp.status_code == 200:
            result = resp.json().get("response", "").strip()
            if result != "NO_CHANGE" and "NO_CHANGE" not in result:
                print("Core Profile updated. Writing to vault...")
                with open(profile_path, "w", encoding="utf-8") as f:
                    f.write(result)
                    
                # THE AUTO-BAKE PROTOCOL
                print("Re-baking the sj-diary model dynamically...")
                modelfile_payload = f"FROM deepseek-r1:8b\nSYSTEM \"\"\"You are SJ's lifelong autonomous AI companion.\nBelow is her foundational Core Profile. You must never forget these facts.\n\n{result}\"\"\""
                try:
                    requests.post(
                        "http://host.docker.internal:11434/api/create", 
                        json={"name": "sj-diary:latest", "modelfile": modelfile_payload}, 
                        timeout=120
                    )
                    print("sj-diary model successfully updated in Open WebUI.")
                except Exception as ex:
                    print(f"Failed to auto-bake model: {ex}")
            else:
                print("No fundamental changes detected. Core Profile remains unchanged.")
    except Exception as e:
        print(f"Ollama profile synthesis failed: {e}")

def generate_weekly_synthesis():
    print("Initiating Weekly Passive Synthesis...")
    today = datetime.datetime.now()
    
    # 1. Gather the last 7 days of diaries
    weekly_diaries = ""
    for i in range(7):
        date_str = (today - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        path = os.path.join(VAULT_DIR, f"SJ_Diary_{date_str}.md")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                weekly_diaries += f"--- {date_str} ---\n{f.read()}\n\n"
                
    if not weekly_diaries:
        print("No diaries found for the week. Skipping synthesis.")
        return
        
    # 2. Gather historical context (T-30, T-365)
    t_30_str = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    t_365_str = (today - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
    
    historical = ""
    t30_path = os.path.join(VAULT_DIR, f"SJ_Diary_{t_30_str}.md")
    t365_path = os.path.join(VAULT_DIR, f"SJ_Diary_{t_365_str}.md")
    
    if os.path.exists(t30_path):
        with open(t30_path, "r", encoding="utf-8") as f:
            historical += f"--- EXACTLY 30 DAYS AGO ---\n{f.read()}\n\n"
    if os.path.exists(t365_path):
        with open(t365_path, "r", encoding="utf-8") as f:
            historical += f"--- EXACTLY 1 YEAR AGO ---\n{f.read()}\n\n"
            
    # 3. Ask Ollama to synthesize
    prompt = f"""You are SJ's autonomous cognitive engine. Your task is to write a profound, deeply personal Weekly Reflection for her.

THIS WEEK'S DIARIES:
{weekly_diaries}

HISTORICAL ECHOES:
{historical if historical else "No historical echoes available."}

INSTRUCTIONS:
1. Synthesize her week. What were the core emotional themes?
2. Connect her present state to her past (if historical echoes exist). Point out her growth, resilience, or recurring patterns.
3. Output entirely in a beautifully formatted Markdown structure. Use headers and bullet points.
4. Do not include conversational filler.
5. Title the reflection: "# Weekly Synthesis"
"""
    try:
        resp = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={"model": "deepseek-r1:8b", "prompt": prompt, "stream": False},
            timeout=300
        )
        if resp.status_code == 200:
            result = resp.json().get("response", "").strip()
            
            # Save silently to the vault
            synthesis_filename = f"SJ_Weekly_Synthesis_{today.strftime('%Y-%m-%d')}.md"
            with open(os.path.join(VAULT_DIR, synthesis_filename), "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Weekly synthesis saved to {synthesis_filename}")
    except Exception as e:
        print(f"Ollama weekly synthesis failed: {e}")

def main():
    print("Starting Sovereign Walkie-Talkie Bridge...")
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_TOKEN not set!")
        return
        
    # Run the profile updater daily at 3:00 AM
    schedule.every().day.at("03:00").do(update_core_profile)
    
    # Run the passive weekly synthesis every Sunday at 8:00 PM
    schedule.every().sunday.at("20:00").do(generate_weekly_synthesis)
    
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
                    
                    if synthesized_text == "IGNORED_HALLUCINATION":
                        print("Dropped whisper hallucination.")
                        send_message(chat_id, "⚠️ Dropped empty audio/background noise.")
                    else:
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
