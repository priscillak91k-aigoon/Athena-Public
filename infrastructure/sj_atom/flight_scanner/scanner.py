import os
import time
import requests
import schedule
from datetime import datetime, timedelta

# Environment Variables
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
FLY_FROM = os.getenv("FLY_FROM", "DUD")
FLY_TO = os.getenv("FLY_TO", "WLG")
TARGET_PRICE = int(os.getenv("TARGET_PRICE", "300"))

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def get_next_weekends():
    weekends = []
    today = datetime.now()
    # Find next Friday
    days_ahead = 4 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_friday = today + timedelta(days=days_ahead)
    
    # Generate next 4 weekends (Friday to Sunday)
    for i in range(4):
        outbound = next_friday + timedelta(weeks=i)
        inbound = outbound + timedelta(days=2)
        weekends.append((outbound.strftime("%Y-%m-%d"), inbound.strftime("%Y-%m-%d")))
    return weekends

def check_flights():
    if not SERPAPI_KEY:
        print("SERPAPI_KEY is missing. Skipping flight check.")
        return

    print(f"Scanning Google Flights for {FLY_FROM} to {FLY_TO} under ${TARGET_PRICE} NZD...")
    weekends = get_next_weekends()
    found_flights = False
    message = f"🚨 <b>CHEAP WEEKEND FLIGHT ALERT!</b> 🚨\n\nFound Google Flights from {FLY_FROM} to {FLY_TO} under ${TARGET_PRICE} NZD:\n\n"

    for outbound_date, return_date in weekends:
        params = {
            "engine": "google_flights",
            "departure_id": FLY_FROM,
            "arrival_id": FLY_TO,
            "outbound_date": outbound_date,
            "return_date": return_date,
            "type": "1", # Round trip
            "stops": "1", # 1 = Nonstop only in Google Flights
            "currency": "NZD",
            "api_key": SERPAPI_KEY
        }
        try:
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            best_flights = data.get("best_flights", [])
            for flight in best_flights:
                price = flight.get("price")
                if price and price <= TARGET_PRICE:
                    found_flights = True
                    flights_info = flight.get("flights", [{}])[0]
                    airline = flights_info.get("airline", "Unknown Airline")
                    link = data.get("search_metadata", {}).get("google_flights_url", "https://flights.google.com")
                    message += f"✈️ <b>${price} NZD</b> - {outbound_date} to {return_date} ({airline})\n<a href='{link}'>Book on Google Flights</a>\n\n"
                    break # Only alert the best one per weekend to avoid spam
            
        except Exception as e:
            print(f"Error checking {outbound_date}: {e}")
            
    if found_flights:
        print("Alert sent!")
        send_telegram_alert(message)
    else:
        print("No flights found under target price.")

if __name__ == "__main__":
    print("Flight Scanner Engine Booting (Google Flights via SerpApi)...")
    check_flights()
    schedule.every(12).hours.do(check_flights)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
