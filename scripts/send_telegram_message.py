"""Quick one-shot: send a message to Priscilla via Telegram and exit."""
import os, asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")
USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USER_ID"))

async def send():
    bot = Bot(token=TOKEN)
    msg = (
        "🔧 **Your Toolbox Links** 🔧\n\n"
        "Access from your phone (same WiFi):\n\n"
        "🏠 Life Hub: http://192.168.1.81:7337/\n"
        "🔧 Toolbox: http://192.168.1.81:7337/toolbox.html\n"
        "⚒ Workshop: http://192.168.1.81:7337/workshop.html\n\n"
        "All tools run locally in your browser — nothing uploaded anywhere."
    )
    await bot.send_message(chat_id=USER_ID, text=msg, parse_mode='Markdown')
    print("Message sent!")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(send())
