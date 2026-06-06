import os
import time
import requests
import schedule
from datetime import datetime, timedelta

# Environment Variables
TEQUILA_API_KEY = os.getenv("TEQUILA_API_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
FLY_FROM = os.getenv("FLY_FROM", "DUD") # Default Dunedin
FLY_TO = os.getenv("FLY_TO", "WLG") # Default Wellington
TARGET_PRICE = int(os.getenv("TARGET_PRICE", "150")) # Default 150 NZD
DATE_RANGE_DAYS = int(os.getenv("DATE_RANGE_DAYS", "30")) # Look 30 days ahead

TEQUILA_ENDPOINT = "https://api.tequila.kiwi.com/v2/search"

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing. Cannot send alert.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def check_flights():
    if not TEQUILA_API_KEY:
        print("TEQUILA_API_KEY is missing. Skipping flight check.")
        return

    print(f"Checking flights from {FLY_FROM} to {FLY_TO} under ${TARGET_PRICE} NZD...")
    
    today = datetime.now()
    date_to = today + timedelta(days=DATE_RANGE_DAYS)
    
    headers = {"apikey": TEQUILA_API_KEY}
    params = {
        "fly_from": FLY_FROM,
        "fly_to": FLY_TO,
        "date_from": today.strftime("%d/%m/%Y"),
        "date_to": date_to.strftime("%d/%m/%Y"),
        "curr": "NZD",
        "price_to": TARGET_PRICE,
        "limit": 5,
        "sort": "price"
    }

    try:
        response = requests.get(TEQUILA_ENDPOINT, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        flights = data.get("data", [])
        if not flights:
            print(f"No flights found under ${TARGET_PRICE}.")
            return

        message = f"🚨 <b>CHEAP FLIGHT ALERT!</b> 🚨\n\nFound flights from {FLY_FROM} to {FLY_TO} under ${TARGET_PRICE} NZD:\n\n"
        
        for flight in flights:
            price = flight["price"]
            airline = flight["route"][0]["airline"]
            departure = flight["local_departure"].split("T")[0]
            link = flight["deep_link"]
            message += f"✈️ <b>${price} NZD</b> - {departure} ({airline})\n<a href='{link}'>Book Here</a>\n\n"

        print("Alert sent!")
        send_telegram_alert(message)

    except Exception as e:
        print(f"Error checking flights: {e}")

if __name__ == "__main__":
    print("Flight Scanner Engine Booting...")
    # Run once on startup to verify
    check_flights()
    
    # Schedule to run every 12 hours
    schedule.every(12).hours.do(check_flights)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
