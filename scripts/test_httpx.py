import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")

async def main():
    print("Testing asyncio and httpx raw getUpdates...")
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            payload = {"timeout": 30, "limit": 100}
            print("Sending request...", url)
            resp = await client.post(url, json=payload, timeout=40)
            print("SUCCESS:", resp.status_code, resp.text)
        except Exception as e:
            print("FAILED:", type(e), e)

if __name__ == "__main__":
    asyncio.run(main())
