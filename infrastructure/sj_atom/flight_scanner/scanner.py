import os
import time
import requests
import schedule
import hashlib
import json
import re
import html
from datetime import datetime, timedelta

# Environment Variables
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
FLY_FROM = os.getenv("FLY_FROM", "DUD")
FLY_TO = os.getenv("FLY_TO", "WLG")
try:
    TARGET_PRICE = int(os.getenv("TARGET_PRICE", "300"))
except ValueError:
    TARGET_PRICE = 300

STATE_FILE = os.path.join(os.path.dirname(__file__), ".flight_phase.json")

# --- STATE MANAGEMENT ---
def load_state():
    default_state = {"is_hunting": False, "phase_start_date": None, "last_processed_entry_hash": None}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    default_state.update(loaded)
                    return default_state
        except Exception:
            pass
    return default_state

def save_state(state):
    tmp_file = STATE_FILE + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(state, f)
    os.replace(tmp_file, STATE_FILE)

# --- NOTIFICATIONS ---
def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

# --- TIME & SCHEDULING ---
def get_next_weekends(start_date_str):
    if not start_date_str:
        return []
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    except ValueError:
        return []

    weekends = []
    days_ahead = 4 - start_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_friday = start_date + timedelta(days=days_ahead)
    
    for i in range(2, 6):
        outbound = next_friday + timedelta(weeks=i)
        inbound = outbound + timedelta(days=2)
        cutoff = inbound + timedelta(days=1)
        if cutoff > datetime.now():
            weekends.append((outbound.strftime("%Y-%m-%d"), inbound.strftime("%Y-%m-%d")))
    return weekends

# --- JOURNAL PARSING ---
def get_latest_journal_entry():
    journal_path = "/context/journal.md"
    if not os.path.exists(journal_path):
        journal_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".context", "journal.md")
        
    if not os.path.exists(journal_path):
        print(f"Journal not found at {journal_path}.")
        return None
        
    try:
        with open(journal_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        entries = content.split("\n## ")
        if not entries:
            return None
        return entries[-1].strip()
    except Exception as e:
        print(f"Error reading journal: {e}")
        return None

def ask_ollama_intent(entry):
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    if not os.getenv("IN_DOCKER"):
        ollama_url = "http://localhost:11434"
        
    truncated_entry = entry[:2000]
    prompt = f"Analyze the following journal entry. Does the user express an active, current intent to look for, buy, or book a flight? Answer with a single word: YES or NO.\n\nEntry:\n{truncated_entry}"
    
    payload = {"model": "llama3", "prompt": prompt, "stream": False}
    try:
        response = requests.post(f"{ollama_url}/api/generate", json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "").strip().upper()
    except Exception as api_err:
        print(f"Failed to reach Ollama: {api_err}. Falling back to keyword search.")
        return "YES" if "flight" in entry.lower() and any(k in entry.lower() for k in ["look", "want", "trip", "buy"]) else "NO"

def process_journal_intent():
    state = load_state()
    latest_entry = get_latest_journal_entry()
    
    if not latest_entry:
        return state
        
    entry_hash = hashlib.md5(latest_entry.encode("utf-8")).hexdigest()
    if state.get("last_processed_entry_hash") == entry_hash:
        return state
        
    state["last_processed_entry_hash"] = entry_hash
    
    first_line = latest_entry.split('\n')[0]
    match = re.search(r'\b(20\d{2}-\d{2}-\d{2})\b', first_line)
    journal_date_str = match.group(1) if match else datetime.now().strftime("%Y-%m-%d")
    
    if "#stopflights" in latest_entry.lower() or "#haltflights" in latest_entry.lower():
        print("Manual halt trigger detected.")
        state["is_hunting"] = False
        save_state(state)
        return state
        
    result = ask_ollama_intent(latest_entry)
    if "YES" in result:
        print(f"New flight intent detected! Activating Hunting Phase from {journal_date_str}.")
        state["is_hunting"] = True
        state["phase_start_date"] = journal_date_str
    else:
        print("New journal entry has no flight intent. Hunting Phase remains unchanged.")
        
    save_state(state)
    return state

# --- FLIGHT DATA PROCESSING ---
def fetch_serpapi_flights(outbound_date, return_date):
    params = {
        "engine": "google_flights",
        "departure_id": FLY_FROM,
        "arrival_id": FLY_TO,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "type": "1",
        "stops": "1",
        "currency": "NZD",
        "api_key": SERPAPI_KEY
    }
    response = requests.get("https://serpapi.com/search", params=params, timeout=20)
    response.raise_for_status()
    return response.json()

def sanitize_and_sort_flights(data):
    best = data.get("best_flights")
    best_flights = best if isinstance(best, list) else []
    
    other = data.get("other_flights")
    other_flights = other if isinstance(other, list) else []
    
    all_flights = best_flights + other_flights
    
    valid_flights = []
    seen = set()
    for flight in all_flights:
        if not isinstance(flight, dict):
            continue
            
        try:
            price_val = float(flight.get("price"))
        except (ValueError, TypeError):
            continue
            
        if price_val > TARGET_PRICE:
            continue
            
        flights_list = flight.get("flights") or []
        flights_info = flights_list[0] if flights_list else {}
        airline_raw = flights_info.get("airline") or "Unknown Airline"
        airline = html.escape(str(airline_raw))
        
        uniq_key = flight.get("flight_token", "")
        if not uniq_key:
            dep_airport = flights_info.get("departure_airport") or {}
            departure_time = dep_airport.get("time", "")
            uniq_key = f"{airline}_{price_val}_{departure_time}"
            
        if uniq_key not in seen:
            seen.add(uniq_key)
            flight["_safe_price"] = price_val
            flight["_safe_airline"] = airline
            valid_flights.append(flight)
            
    valid_flights.sort(key=lambda x: x.get("_safe_price", 0))
    return valid_flights[:3]

def format_weekend_message(outbound_date, return_date, top_flights, search_url):
    if not top_flights:
        return ""
        
    link_raw = search_url or "https://flights.google.com"
    link = html.escape(str(link_raw), quote=True)
    msg = f'📅 <b>{outbound_date} to {return_date}</b> - <a href="{link}">Search</a>\n'
    
    for flight in top_flights:
        price_display = flight.get("_safe_price", 0)
        if isinstance(price_display, float) and price_display.is_integer():
            price_display = int(price_display)
            
        airline = flight.get("_safe_airline", "Unknown Airline")
        msg += f'✈️ ${price_display} NZD ({airline})\n'
    return msg + "\n"

# --- CORE ENGINE ---
def check_flights():
    state = process_journal_intent()
    if not state.get("is_hunting"):
        print("Hunting Phase is inactive. Sleeping.")
        return

    weekends = get_next_weekends(state.get("phase_start_date"))
    if not weekends:
        print("Intent active but all target weekends have passed. Auto-shutting down Hunting Phase.")
        state["is_hunting"] = False
        save_state(state)
        return

    if not SERPAPI_KEY:
        print("SERPAPI_KEY is missing. Skipping flight check.")
        return

    print(f"Scanning Google Flights for {FLY_FROM} to {FLY_TO} under ${TARGET_PRICE} NZD...")
    found_flights = False
    message = f"🚨 <b>CHEAP WEEKEND FLIGHT ALERT!</b> 🚨\n\nFound Google Flights from {FLY_FROM} to {FLY_TO} under ${TARGET_PRICE} NZD:\n\n"

    for outbound_date, return_date in weekends:
        try:
            data = fetch_serpapi_flights(outbound_date, return_date)
            top_flights = sanitize_and_sort_flights(data)
            
            if top_flights:
                found_flights = True
                search_url = data.get("search_metadata", {}).get("google_flights_url")
                message += format_weekend_message(outbound_date, return_date, top_flights, search_url)
                
            time.sleep(2)
            
        except requests.exceptions.HTTPError as http_err:
            if getattr(http_err.response, "status_code", 0) == 429:
                print("SerpApi quota exhausted!")
                message += "⚠️ <i>Warning: SerpApi free tier quota exhausted. Scans paused until quota resets.</i>\n"
                found_flights = True
                break
            print(f"HTTP Error checking {outbound_date}: {http_err}")
        except Exception as e:
            print(f"Error checking {outbound_date}: {e}")
            
    if found_flights:
        print("Alert sent!")
        send_telegram_alert(message)
    else:
        print("No flights found under target price.")

if __name__ == "__main__":
    print("Flight Scanner Engine Booting (Google Flights via SerpApi)...")
    try:
        check_flights()
    except Exception as e:
        print(f"Boot check failed: {e}")
        
    schedule.every(24).hours.do(check_flights)
    
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print(f"Daemon execution error: {e}")
        time.sleep(60)
