import anthropic
import asyncio
import os
from telegram.ext import Application
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")

async def main():
    print("Testing default...")
    try:
        app = Application.builder().token(TOKEN).build()
        await app.bot.get_me()
        print("Default SUCCESS")
    except Exception as e:
        print("Default FAILED:", type(e))

    print("Testing HTTP/1.1 explicit...")
    try:
        req = HTTPXRequest(http_version="1.1")
        app = Application.builder().token(TOKEN).request(req).build()
        await app.bot.get_me()
        print("HTTP/1.1 SUCCESS")
    except Exception as e:
        print("HTTP/1.1 FAILED:", type(e))

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
