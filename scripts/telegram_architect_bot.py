import os
import asyncio
import subprocess
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")
USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USER_ID", 0))

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-pro")

SCHEDULE_FILE = os.path.join(os.path.dirname(__file__), "..", "life-dashboard", "schedule_data.js")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        return
        
    user_text = update.message.text
    
    await update.message.reply_text("⏳ Writing new code to schedule_data.js...")
    
    try:
        with open(SCHEDULE_FILE, "r") as f:
            current_schedule = f.read()

        prompt = f"""You are the Life Engine Architect. The user just sent a text message to update their life schedule.
Here is their message: "{user_text}"

Here is the current content of life-dashboard/schedule_data.js:
```javascript
{current_schedule}
```

Your task:
Modify the timeline logic inside `window.generateTodayTimeline` (or adjust habit pools) to accommodate this new constraint or override.
For date-specific overrides, add a boolean check (like `isMarch9Override` currently in the file) based on the date provided by the user, and push a specific timeline block for that condition.
Return the FULL, completely valid, updated javascript file.
Do NOT use markdown code blocks (no ```javascript). Just return the raw code.
Make sure you include everything so the file isn't truncated.
"""
        response = await asyncio.to_thread(model.generate_content, prompt)
        new_code = response.text.replace("```javascript", "").replace("```js", "").replace("```", "").strip()
        
        # Validate that it looks like js code containing the required function
        if "generateTodayTimeline" in new_code:
            with open(SCHEDULE_FILE, "w") as f:
                f.write(new_code)
                
            await update.message.reply_text("🔄 Code updated. Committing to GitHub and triggering deployment...")
            
            repo_cwd = os.path.dirname(SCHEDULE_FILE)
            # Commit and push
            subprocess.run(["git", "add", "schedule_data.js"], check=True, cwd=repo_cwd)
            subprocess.run(["git", "commit", "-m", f"Architect Bot Override: {user_text}"], check=True, cwd=repo_cwd)
            subprocess.run(["git", "push", "origin", "main"], check=True, cwd=repo_cwd)
            
            await update.message.reply_text("✅ Deployment triggered! Refresh your Netlify dashboard in 10-15 seconds.")
        else:
            await update.message.reply_text("❌ Model generated invalid code. Update aborted.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error during execution: {e}")

def main():
    if not TOKEN:
        print("TELEGRAM_ARCHITECT_TOKEN is not set in .env.")
        return
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Architect Bot is running and listening for instructions...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    import asyncio
    main()
