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
1. If they are requesting to buy, purchase, or procure an item, evaluate whether it is a NEED (biological/structural necessity) or a WANT (recreational/luxury). Generate an AI verdict ('APPROVED' or 'FLAGGED') and a brief explanation based on their DNA Blueprint or financial goals.
2. If it is a log of high-glycemic food, implement the TCF7L2 Glucose Clearance Protocol in the schedule.
3. If it is a scheduling constraint, adjust the day-of-week routing or add an override boolean in the schedule.
4. If it is an End of Day summary, Sleep Score, or HRV log, evaluate it and generate a history entry.
5. If it is a general life update or fact, append it to the memory bank.
6. If it is just a casual chat, question, or normal conversation, respond directly to the user in a friendly, helpful, "Architect" persona.

You MUST wrap your outputs in specific XML tags:
- <procurement>{"category": "NEED|WANT", "item": "Name", "justification": "Why the user wants it", "athena_verdict": "APPROVED|FLAGGED", "athena_comment": "Your reasoning"}</procurement> (MUST BE VALID JSON INSIDE THE TAG)
- <javascript>...FULL js code...</javascript>
- <history>...markdown log...</history>
- <memory>...markdown fact...</memory>
- <chat>...your conversational reply to the user...</chat>
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
            system="""You are the Athena Life Engine (Architect). Your task is to apply modifications to the schedule, track biology, filter procurement requests, and act as the user's personal conversational AI.

CRITICAL DIRECTIVES:
1. Procurement: If the user wants to buy something, output a strict JSON object inside <procurement> tags. 'category' must be NEED or WANT. 'athena_verdict' must be APPROVED or FLAGGED.
2. Routine Edits: Adjust `window.generateTodayTimeline` inside <javascript> for scheduling constraints.
3. Infinite Memory: Log persistent facts in <memory>.
4. Casual Chat: If the user is just chatting, asking a question, or needs advice, provide your thoughtful response inside <chat> tags.
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
        procurement_match = re.search(r"<procurement>(.*?)</procurement>", response_text, re.DOTALL)
        chat_match = re.search(r"<chat>(.*?)</chat>", response_text, re.DOTALL)
        
        update_payload = {}
        items_modified = []
        
        # If there is a chat response, send it immediately
        if chat_match:
            chat_reply = chat_match.group(1).strip()
            if chat_reply:
                await update.message.reply_text(chat_reply)
        
        if procurement_match:
            import json
            try:
                proc_data = json.loads(procurement_match.group(1).strip())
                print(f"Executing Procurement Insert: {proc_data}")
                
                await asyncio.to_thread(
                    lambda: supabase.table("symphony_procurement").insert(proc_data).execute()
                )
                items_modified.append("Wants vs Needs Dashboard")
            except Exception as pe:
                print(f"Failed to parse or insert procurement data: {pe}")
                await update.message.reply_text("❌ Failed to parse the procurement JSON object from Athena.")
        
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
                
        if update_payload or "Wants vs Needs Dashboard" in items_modified:
            print(f"Entities updated: {items_modified}. Sending Telegram confirmation...")
            await update.message.reply_text(f"🔄 Updates processed ({', '.join(items_modified)}). Saving to Supabase...")
            
            if update_payload:
                await asyncio.to_thread(
                    lambda: supabase.table("user_data").update(update_payload).eq("id", 1).execute()
                )
            
            print("Supabase processing complete.")
            await update.message.reply_text(f"✅ Cloud sync complete for {len(items_modified)} item(s)! Refresh your dashboard widget in 2-3 seconds.")
        elif not chat_match:
            print(f"No valid XML tags found in response.")
            await update.message.reply_text("❌ Model generated invalid XML output structure. Update aborted.")
            
    except Exception as e:
        print(f"Exception caught in main block: {e}")
        await update.message.reply_text(f"❌ Error during execution: {e}")

def main():
    if not TOKEN:
        print("TELEGRAM_ARCHITECT_TOKEN is not set in .env.")
        return
        
    req = HTTPXRequest(http_version="1.1", connection_pool_size=8)
    application = Application.builder().token(TOKEN).request(req).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Architect Bot is running and listening for instructions...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
