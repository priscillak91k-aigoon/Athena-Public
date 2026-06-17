import os
import time
import requests
import datetime
import shutil
import re
import tempfile

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ALLOWED_CHAT_ID = os.environ.get("ALLOWED_CHAT_ID", "8309108979")
WHISPER_URL = "http://whisper-api:9000/asr"
VAULT_DIR = "/vault"
POLL_INTERVAL = 5

def ensure_directories():
    os.makedirs(VAULT_DIR, exist_ok=True)
    os.makedirs(os.path.join(VAULT_DIR, "Quarantine"), exist_ok=True)
    os.makedirs(os.path.join(VAULT_DIR, "SJ_Core_Profile_proposals"), exist_ok=True)

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
    try:
        resp = requests.get(url, timeout=15).json()
        if not resp.get("ok"): 
            return None
        file_path = resp.get("result", {}).get("file_path")
        if not file_path:
            return None
        
        dl_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        file_data = requests.get(dl_url, timeout=60).content
        with open(save_path, "wb") as f:
            f.write(file_data)
        return save_path
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

def transcribe_audio(file_path):
    with open(file_path, "rb") as f:
        files = {"audio_file": f}
        try:
            resp = requests.post(WHISPER_URL, files=files, timeout=300)
            if resp.headers.get('content-type') == 'application/json':
                return resp.json().get('text', '')
            else:
                return resp.text
        except Exception as e:
            print(f"Transcription error: {e}")
            return None

def synthesize_memory(raw_text):
    prompt = f"""You are an autonomous memory synthesis engine for SJ's lifelong digital diary. 
Read her raw stream-of-consciousness transcript and structure it for long-term storage.

RAW TRANSCRIPT:
"{raw_text}"

INSTRUCTIONS:
1. Extract the core emotional state or sentiment (e.g., Anxious, Excited, Reflective).
2. Extract key entities (people, places, projects) and list them as #tags.
3. Summarize the main points into clear, concise bullet points.
4. Extrapolate her psychological telemetry. Estimate on a scale of 1-10 her Mood, Stress, and Energy levels based on the text. (Label these as LLM Estimates).
5. QUARANTINE FILTER: If the raw transcript is just background noise or YouTube filler (e.g., "Thank you for watching") and contains no actual journal content, output EXACTLY the phrase: IGNORED_HALLUCINATION
6. If it is a valid entry, output strictly in this Markdown format, with NO conversational filler:

**Emotional State:** [Emotion]
**Key Entities:** #tag1 #tag2

**Synthesis:**
- [Bullet point 1]
- [Bullet point 2]

<!-- {{"mood_estimate": [1-10], "stress_estimate": [1-10], "energy_estimate": [1-10], "source": "llm_estimate"}} -->
"""
    try:
        resp = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={"model": "hermes3:8b", "prompt": prompt, "stream": False},
            timeout=600
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"Ollama synthesis failed: {e}")
    return None

def write_to_vault(raw_text, synthesized_text):
    """Writes to vault using an atomic temp-file rename to prevent half-written corruption."""
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%I:%M %p")
    file_name = f"SJ_Diary_{date_str}.md"
    file_path = os.path.join(VAULT_DIR, file_name)
    
    header = ""
    if not os.path.exists(file_path):
        header = f"# Sovereign Journal - {date_str}\n\n"
        
    if synthesized_text:
        content = f"{synthesized_text}\n\n<details>\n<summary>Raw Transcript (Canonical Record)</summary>\n\n{raw_text.strip()}\n</details>"
    else:
        content = raw_text.strip()
        
    entry = f"{header}### 🎙️ Walkie-Talkie Log ({time_str})\n{content}\n\n---\n\n"
    
    try:
        # Atomic Write Pattern
        fd, temp_path = tempfile.mkstemp(dir=VAULT_DIR)
        with os.fdopen(fd, 'w', encoding="utf-8") as tf:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding="utf-8") as orig:
                    tf.write(orig.read())
            tf.write(entry)
        
        os.replace(temp_path, file_path) # Atomic overwrite
        return True
    except Exception as e:
        print(f"CRITICAL FILE IO ERROR writing to vault: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        pass

def update_core_profile(yesterday, diary_path, proposal_file):
    print(f"Initiating Core Profile synthesis for {yesterday}...")
    profile_path = os.path.join(VAULT_DIR, "SJ_Core_Profile.md")
    
    if not os.path.exists(profile_path):
        print("Missing SJ_Core_Profile.md. Skipping.")
        # Create a dummy to avoid infinite loop
        with open(proposal_file, "w") as f: f.write("NO_CHANGE")
        return

    with open(profile_path, "r", encoding="utf-8") as f:
        current_profile = f.read()
        
    with open(diary_path, "r", encoding="utf-8") as f:
        yesterday_diary = f.read()

    prompt = f"""You are the Memory Tier 2 Engine. 
Review SJ's diary to determine if her Core Profile needs updating.

CURRENT CORE PROFILE:
{current_profile}

YESTERDAY'S DIARY:
{yesterday_diary}

INSTRUCTIONS:
1. Did any fundamental, long-term facts about SJ's life change in the diary? (e.g., new job, core belief shift).
2. If absolutely NOTHING fundamental changed, you MUST output exactly: NO_CHANGE
3. If a fundamental fact DID change, rewrite the ENTIRE Core Profile incorporating the new information. Keep the same Markdown structure.
"""
    try:
        resp = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={"model": "deepseek-r1:14b", "prompt": prompt, "stream": False},
            timeout=600
        )
        if resp.status_code == 200:
            result = resp.json().get("response", "").strip()
            clean_result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
            
            if clean_result and clean_result != "NO_CHANGE" and "NO_CHANGE" not in clean_result:
                print("Core Profile shift detected. Writing proposal...")
                with open(proposal_file, "w", encoding="utf-8") as f:
                    f.write(clean_result)
                send_message(ALLOWED_CHAT_ID, f"🧠 **Core Profile Shift Detected**\nI noticed a fundamental change in your life based on yesterday's diary. I have drafted a proposed update.\n\nPlease review `/SJ_Core_Profile_proposals/SJ_Core_Profile_proposal_{yesterday}.md`. Rename it to `SJ_Core_Profile.md` to enact the changes.")
            else:
                print("No fundamental changes detected.")
                # Touch the file to mark it as processed
                with open(proposal_file, "w") as f: f.write("NO_CHANGE")
    except Exception as e:
        print(f"Ollama profile synthesis failed: {e}")

def generate_weekly_synthesis(last_sunday, synthesis_file):
    print(f"Initiating Weekly Passive Synthesis for week ending {last_sunday.strftime('%Y-%m-%d')}...")
    
    weekly_diaries = ""
    for i in range(7):
        date_str = (last_sunday - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        path = os.path.join(VAULT_DIR, f"SJ_Diary_{date_str}.md")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                weekly_diaries += f"--- {date_str} ---\n{f.read()}\n\n"
                
    if not weekly_diaries:
        print("No diaries found. Skipping.")
        with open(synthesis_file, "w") as f: f.write("NO_DATA")
        return
        
    t_30_str = (last_sunday - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    t_365_str = (last_sunday - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
    
    historical = ""
    t30_path = os.path.join(VAULT_DIR, f"SJ_Diary_{t_30_str}.md")
    t365_path = os.path.join(VAULT_DIR, f"SJ_Diary_{t_365_str}.md")
    
    if os.path.exists(t30_path):
        with open(t30_path, "r", encoding="utf-8") as f: historical += f"--- EXACTLY 30 DAYS AGO ---\n{f.read()}\n\n"
    if os.path.exists(t365_path):
        with open(t365_path, "r", encoding="utf-8") as f: historical += f"--- EXACTLY 1 YEAR AGO ---\n{f.read()}\n\n"
            
    prompt = f"""You are SJ's autonomous cognitive engine. Your task is to write a weekly synthesis.
Rule 1: Be gentle, objective, and reflective. Do NOT over-psychoanalyze or feed rumination. Keep it light.

THIS WEEK'S DIARIES:
{weekly_diaries}

HISTORICAL ECHOES:
{historical if historical else "No historical echoes available."}

INSTRUCTIONS:
1. Synthesize her week. What were the core themes?
2. Connect her present state to her past (if historical echoes exist). Point out her growth.
3. Output entirely in a beautifully formatted Markdown structure. Use headers and bullet points.
4. Title the reflection: "# Weekly Synthesis"
"""
    try:
        resp = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={"model": "deepseek-r1:14b", "prompt": prompt, "stream": False},
            timeout=600
        )
        if resp.status_code == 200:
            result = resp.json().get("response", "").strip()
            clean_result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
            
            if clean_result:
                with open(synthesis_file, "w", encoding="utf-8") as f:
                    f.write(clean_result)
                print(f"Weekly synthesis saved to {synthesis_file}")
    except Exception as e:
        print(f"Ollama weekly synthesis failed: {e}")

def run_idempotent_jobs():
    """State-based job execution, unhooked from brittle system clocks."""
    today = datetime.datetime.now()
    
    # 1. Profile Core Updates
    yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_diary = os.path.join(VAULT_DIR, f"SJ_Diary_{yesterday}.md")
    proposal_file = os.path.join(VAULT_DIR, "SJ_Core_Profile_proposals", f"SJ_Core_Profile_proposal_{yesterday}.md")
    
    if os.path.exists(yesterday_diary) and not os.path.exists(proposal_file):
        update_core_profile(yesterday, yesterday_diary, proposal_file)
        
    # 2. Weekly Synthesis
    days_since_sunday = (today.weekday() + 1) % 7
    if days_since_sunday == 0 and today.hour < 20:
        last_sunday = today - datetime.timedelta(days=7)
    else:
        last_sunday = today - datetime.timedelta(days=days_since_sunday)
        
    sunday_str = last_sunday.strftime("%Y-%m-%d")
    synthesis_file = os.path.join(VAULT_DIR, f"SJ_Weekly_Synthesis_{sunday_str}.md")
    
    if not os.path.exists(synthesis_file):
        generate_weekly_synthesis(last_sunday, synthesis_file)

def process_voice_note(message, chat_id):
    file_id = message["voice"]["file_id"]
    print(f"Received voice note from {chat_id}. Downloading...")
    audio_path = f"/tmp/{file_id}.ogg"
    saved_path = download_file(file_id, audio_path)
    
    print("Transcribing via Local Whisper...")
    if saved_path and os.path.exists(saved_path):
        raw_text = transcribe_audio(saved_path)
    else:
        raw_text = None
    
    if raw_text:
        print(f"Transcription: {raw_text[:50]}...")
        synthesized_text = synthesize_memory(raw_text)
        
        if synthesized_text and "IGNORED_HALLUCINATION" in synthesized_text:
            print("Dropped whisper hallucination into Quarantine.")
            shutil.move(audio_path, os.path.join(VAULT_DIR, "Quarantine", f"hallucination_{file_id}.ogg"))
            send_message(chat_id, "⚠️ Low-confidence note parked in Quarantine. Raw audio preserved.")
            return # Skip write to vault
        else:
            success = write_to_vault(raw_text, synthesized_text)
            if not success:
                send_message(chat_id, "🚨 CRITICAL ERROR: Failed to write to vault! (Disk full?)")
            elif synthesized_text:
                send_message(chat_id, "✅ Voice note transcribed, synthesized, and logged to vault.")
            else:
                send_message(chat_id, "⚠️ Voice note transcribed and logged, but Ollama synthesis failed.")
    else:
        send_message(chat_id, "❌ Failed to transcribe audio. Is Whisper running?")
        
    # Standard cleanup of successful transcriptions
    if os.path.exists(audio_path): 
        try:
            os.remove(audio_path)
        except Exception:
            pass

def process_text_note(message, chat_id):
    raw_text = message["text"]
    synthesized_text = synthesize_memory(raw_text)
    
    if synthesized_text and "IGNORED_HALLUCINATION" in synthesized_text:
        send_message(chat_id, "⚠️ Dropped non-journal text message.")
    else:
        success = write_to_vault(raw_text, synthesized_text)
        if not success:
            send_message(chat_id, "🚨 CRITICAL ERROR: Failed to write to vault! (Disk full?)")
        elif synthesized_text:
            send_message(chat_id, "✅ Text synthesized and logged to vault.")
        else:
            send_message(chat_id, "⚠️ Text logged to vault, but Ollama synthesis failed.")

def main():
    print("Starting Sovereign Walkie-Talkie Bridge (v2)...")
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_TOKEN not set!")
        return
        
    ensure_directories()
    
    offset = None
    while True:
        try:
            run_idempotent_jobs()
            
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                
                if not chat_id or str(chat_id) != ALLOWED_CHAT_ID:
                    continue
                
                if "voice" in message:
                    process_voice_note(message, chat_id)
                elif "text" in message:
                    process_text_note(message, chat_id)
                    
        except Exception as e:
            print(f"Critical error in main loop: {e}")
            
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
