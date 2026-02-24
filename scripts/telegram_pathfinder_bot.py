import os
import pytz
from datetime import time
import asyncio
from telegram import Update
from telegram.ext import Application, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_PATHFINDER_TOKEN")
USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USER_ID", 0))

async def send_9pm_washing_reminder(context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🧺 **Washing Reminder** 🧺\n\n"
        "It is 9:00 PM. Time to get the washing sorted so you aren't doing it at midnight! You promised yourself you wouldn't avoid this."
    )
    await context.bot.send_message(chat_id=USER_ID, text=message, parse_mode='Markdown')

async def send_pm_reflection(context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🌙 **THE PM REFLECTION** 🌙\n\n"
        "_"
        "The day is done, and the ledger is closed. I have proven today that I am capable of overcoming my own avoidance. Where I felt fear or shame, I chose action instead.\n\n"
        "I have earned my rest. I am allowing my nervous system to power down fully. The Warrior is off duty. There is nothing left to defend against tonight. I am safe, I am on track, and I have kept the promise to my future self.\n\n"
        "Armor off. Sequence complete."
        "_"
    )
    await context.bot.send_message(chat_id=USER_ID, text=message, parse_mode='Markdown')

async def send_welcome(context: ContextTypes.DEFAULT_TYPE):
    message = "🧭 **Pathfinder Online**\n\nI am running in the background. My sole directive is to ensure critical life reminders breach your phone screen, regardless of website connectivity."
    await context.bot.send_message(chat_id=USER_ID, text=message, parse_mode='Markdown')

def main():
    if not TOKEN:
        print("TELEGRAM_PATHFINDER_TOKEN is not set in .env.")
        return
        
    application = Application.builder().token(TOKEN).build()
    nz_tz = pytz.timezone('Pacific/Auckland')
    
    # 9 PM Washing Reminder
    application.job_queue.run_daily(
        send_9pm_washing_reminder, 
        time=time(hour=21, minute=0, tzinfo=nz_tz),
        chat_id=USER_ID
    )

    # 11:30 PM PM Reflection
    application.job_queue.run_daily(
        send_pm_reflection, 
        time=time(hour=23, minute=30, tzinfo=nz_tz),
        chat_id=USER_ID
    )

    # Boot Notification (fires 5 seconds after boot)
    application.job_queue.run_once(send_welcome, 5)

    print("Pathfinder Reminder Bot is running in the background...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
