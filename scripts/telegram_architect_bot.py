import os
import asyncio
import subprocess
import anthropic
import re
from supabase import create_client
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")
USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USER_ID"))

# We will configure Anthropic inside the functions

# Local file sync removed (Phase 14: Supabase Migration)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(">>> MESSAGE RECEIVED FROM TELEGRAM <<<")
    
    if update.effective_user.id != USER_ID:
        print(f"Rejected: Sender ID {update.effective_user.id} does not match {USER_ID}")
        return
        
    user_text = update.message.text
    print(f"Accepted message: '{user_text}'")
    
    try:
        print("Attempting to send initial telegram reply...")
        await update.message.reply_text("⏳ Writing new code to schedule_data.js...")
        print("Reply sent successfully. Proceeding to Gemini.")
    except Exception as reply_err:
        print(f"CRITICAL ERROR sending reply: {reply_err}")
    
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        db_response = await asyncio.to_thread(
            lambda: supabase.table("user_data").select("*").eq("id", 1).execute()
        )
        
        if db_response.data:
            user_data = db_response.data[0]
            current_schedule = user_data.get("schedule_payload", "")
            loaded_history = user_data.get("history_payload", "") or ""
            loaded_memory = user_data.get("memory_payload", "") or ""
            
            current_history = loaded_history if loaded_history else "No history yet."
            current_memory = loaded_memory if loaded_memory else "No memory yet."
        else:
            current_schedule = ""
            loaded_history = ""
            loaded_memory = ""
            current_history = "No history yet."
            current_memory = "No memory yet."

        prompt = f"""The user just sent this text message to the Life Engine: "{user_text}"

Here is the current content of life-dashboard/schedule_data.js:
<current_javascript>
{current_schedule}
</current_javascript>

Here is the current biological history:
<current_history>
{current_history}
</current_history>

Here is the current Life Memory Bank:
<current_memory>
{current_memory}
</current_memory>

Analyze the user's message. 
1. If it is a log of high-glycemic food, implement the TCF7L2 Glucose Clearance Protocol in the schedule.
2. If it is a scheduling constraint, adjust the day-of-week routing or add an override boolean in the schedule.
3. If it is an End of Day summary, Sleep Score, or HRV log:
   - Evaluate the HRV/Sleep. If it implies high central nervous system fatigue, downgrade tomorrow's workout in the schedule to 'Zone 2 Active Recovery'.
   - Generate a markdown log entry for this new data to append to the biological history.
4. If it is a general life update or fact to remember (not a schedule constraint or biological log), append it to the memory bank.

You MUST wrap your outputs in specific XML tags.
If modifying the schedule, wrap the FULL, completely valid javascript code in <javascript>...</javascript> tags.
If adding a biological history log, wrap the NEW markdown entry to append in <history>...</history> tags.
If adding a memory, wrap the NEW markdown entry to append in <memory>...</memory> tags.
Do NOT use markdown code blocks inside the XML tags.
"""
        print("Calling Anthropic API...")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY is not set.")
        client = anthropic.Anthropic(api_key=anthropic_key)
        
        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-6",
            max_tokens=8192,
            system="""You are the Athena Life Engine (Architect). Your task is to apply modifications to the javascript schedule timeline and/or track biological history.

CRITICAL DIRECTIVES:
1. XML Outputs: You must use <javascript> to output the modified schedule, and <history> to output new markdown log entries. Do not output anything outside of these tags.
2. Routine Edits: Adjust `window.generateTodayTimeline` for scheduling constraints.
3. Metabolic Logging: For high-glycemic carbs, inject a "Glucose Disposal Protocol: 30 Air Squats" into the timeline with tags: ["Bio", "Metabolic"] and an expertInsight.
4. Deep-Sync Protocol: When processing HRV/Sleep scores, log the data in <history> and explicitly scale down the next day's high-intensity workouts in <javascript> if the user is under-recovered.
5. Infinite Memory: When processing a general life update or persistent fact, log it in <memory> to retain it for the future.
""",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        print("Anthropic API returned successfully.")
        
        response_text = response.content[0].text
        
        # Parse output
        js_match = re.search(r"<javascript>(.*?)</javascript>", response_text, re.DOTALL)
        history_match = re.search(r"<history>(.*?)</history>", response_text, re.DOTALL)
        memory_match = re.search(r"<memory>(.*?)</memory>", response_text, re.DOTALL)
        
        update_payload = {}
        items_modified = []
        
        if js_match:
            new_code = js_match.group(1).strip()
            # Clean up markdown if Claude accidentally injects it anyway
            new_code = new_code.replace("```javascript", "").replace("```js", "").replace("```", "").strip()
            if "generateTodayTimeline" in new_code:
                update_payload["schedule_payload"] = new_code
                items_modified.append("schedule_data")
            else:
                print("Generated JS failed validation.")
                
        if history_match:
            new_history_entry = history_match.group(1).strip()
            if new_history_entry:
                updated_history = loaded_history + "\n\n" + new_history_entry + "\n" if loaded_history else new_history_entry + "\n"
                update_payload["history_payload"] = updated_history
                items_modified.append("biological_history")
                
        if memory_match:
            new_memory_entry = memory_match.group(1).strip()
            if new_memory_entry:
                updated_memory = loaded_memory + "\n\n" + new_memory_entry + "\n" if loaded_memory else new_memory_entry + "\n"
                update_payload["memory_payload"] = updated_memory
                items_modified.append("memory_bank")
                
        if update_payload:
            print(f"Entities updated: {items_modified}. Sending Telegram confirmation...")
            await update.message.reply_text(f"🔄 Updates processed ({', '.join(items_modified)}). Saving to Supabase...")
            
            await asyncio.to_thread(
                lambda: supabase.table("user_data").update(update_payload).eq("id", 1).execute()
            )
            
            print("Supabase update complete.")
            await update.message.reply_text(f"✅ Cloud sync complete for {len(items_modified)} item(s)! Refresh your dashboard in 2-3 seconds.")
        else:
            print(f"No valid XML tags found in response.")
            await update.message.reply_text("❌ Model generated invalid XML output structure. Update aborted.")
            
    except Exception as e:
        print(f"Exception caught in main block: {e}")
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
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
