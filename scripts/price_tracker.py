import os
import json
import asyncio
import re
from telegram import Bot
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Using Aegis bot token
USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USER_ID", 0))

WATCHLIST_PATH = Path(__file__).parent.parent / ".context" / "state" / "price_watchlist.json"

def clean_price(price_str):
    """Extracts the first valid floating point number from a string."""
    match = re.search(r'[\d,]+\.\d{2}', price_str)
    if match:
        return float(match.group().replace(',', ''))
    return None

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Run in background
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

async def check_prices():
    if not WATCHLIST_PATH.exists():
        print("Watchlist not found.")
        return

    with open(WATCHLIST_PATH, 'r') as f:
        data = json.load(f)

    bot = Bot(token=TOKEN)
    alerts = []
    
    print("Initializing headless browser...")
    driver = setup_driver()

    try:
        for item in data.get('items', []):
            try:
                name = item['name']
                url = item['url']
                store = item['store']
                target = item['target_price']
                selector = item['css_selector']

                print(f"Checking {name} at {store}...")
                driver.get(url)
                
                # Wait up to 10 seconds for the element to appear
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                current_price = clean_price(element.text)
                print(f"  Found price: ${current_price}")
                
                if current_price and current_price <= target:
                    alerts.append(
                        f"🚨 **SALE ALERT** 🚨\n\n"
                        f"**{name}** has dropped to **${current_price}** at {store}!\n"
                        f"(Your target was ${target})\n\n"
                        f"[Buy it here]({url})"
                    )
                    
            except Exception as e:
                print(f"Error checking {name}: {e}")
    finally:
        driver.quit()

    if alerts:
        message = "\n\n---\n\n".join(alerts)
        await bot.send_message(chat_id=USER_ID, text=message, parse_mode='Markdown')
        print(f"Sent {len(alerts)} alerts to Telegram.")
    else:
        print("No items met their target price. No alerts sent.")

if __name__ == "__main__":
    asyncio.run(check_prices())
