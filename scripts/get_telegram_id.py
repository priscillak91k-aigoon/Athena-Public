import os
import asyncio
from telegram import Bot

async def get_chat_id():
    token = "8143458051:AAHpAmyEDb6dmWhcF2t8jsF5vOzTTbKvT1w"
    bot = Bot(token)
    
    print("Connecting to Telegram...")
    try:
        updates = await bot.get_updates()
        if not updates:
            print("\nNo messages found! Please send a message like 'Start' to your bot on Telegram.")
            print("After sending the message, rerun this script.")
        else:
            for update in updates:
                if update.message:
                    chat_id = update.message.chat.id
                    username = update.message.chat.username
                    first_name = update.message.chat.first_name
                    print(f"\nSUCCESS! Found a message from:")
                    print(f"Name: {first_name} (@{username})")
                    print(f"Chat ID: {chat_id}")
                    print(f"\nAdd this Chat ID to your .env file as TELEGRAM_CHAT_ID={chat_id}")
                    break
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_chat_id())
