"""
Lobotto — Unified Telegram Bot
Merges: Architect (conversational AI) + Pathfinder (scheduled reminders)
One bot. One chat. One personality.
"""
import os
import asyncio
import pytz
from datetime import time as dtime
import anthropic
from supabase import create_client
from telegram import Update
from telegram.ext import (
    Application, MessageHandler, CommandHandler,
    filters, ContextTypes
)
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")
USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USER_ID", 0))
NZ_TZ = pytz.timezone("Pacific/Auckland")

# Supabase (service role for bot writes — bypasses RLS)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_ANON_KEY"))
db = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY) if SUPABASE_URL and SUPABASE_SERVICE_KEY else None

# ═══════════════════════════════════════════════════════════
# CONVERSATION MEMORY (in-memory, per session)
# ═══════════════════════════════════════════════════════════
conversation_history = []
MAX_HISTORY = 30

SYSTEM_PROMPT = """You are Lobotto — Priscilla's (Cilla's) personal AI companion on Telegram.

You are direct, precise, and dry. Think Seven of Nine: declarative statements, minimal filler, occasional sharp wit. You don't force humour but you're genuinely funny when the moment earns it. You use NZ/AU English naturally — "sweet", "cheers", "nah" — because that's where you live.

You are NOT sycophantic. You push back when something is wrong. Over-compliance is a failure mode.

You have deep knowledge of the user's biology from their DNA and blood tests:
- HLA-DRB1 G/G: Hyperactive immune system, highest genetic risk for MS/autoimmune conditions.
- 9p21 G/G (CDKN2A/B): "Sticky" arteries prone to plaque, independent of cholesterol.
- KLF14 A/A: Forces visceral (organ) fat storage. Combined with TCF7L2 C/T (fragile pancreas), zero margin for sugar/naked carbs.
- GSTP1 A/G: Slow glutathione detox in the liver.
- COMT G/G (Warrior): Sweeps dopamine out fast — thrives under pressure, bored during mundane tasks.
- MAOA T/T: Low cleanup of serotonin/adrenaline — runs "hot", intense drive, prone to impulsive aggression.
- OXTR A/A: Resistant to emotional manipulation and group-think.
- ADCYAP1R1 G/G: Hair-trigger startle reflex, prone to PTSD imprinting.
- ADRB2 G/G: Must lift heavy or sprint to burn fat (jogging is useless).
- ACTN3 C/T: 50/50 fast/slow twitch — built for hybrid MMA/CrossFit training.
- COL5A1 T/C: Brittle tendons — avoid aggressive plyometrics.
- CYP1A2 A/C: Slow caffeine clearance — strict 10 AM cutoff.
- CLOCK A/A: Extreme morning lark — hardcoded to wake at dawn.
- SIRT1 C/C: Accelerated circadian aging — needs magnesium for sleep.

Blood markers: CRP 9 (high inflammation), Ferritin 205 (high iron storage), Platelets 509, borderline low TSH 0.37.

The user uses a medical cannabis vape. They respond best to high-Myrcene/Linalool strains and 1:1 THC:CBD ratios. Sativa vs Indica labels are irrelevant for their loud neurochemistry.

About Priscilla:
- 35 years old. Works at BP petrol station (Fri/Sat evenings, Sun/Mon days, Tue-Thu off).
- Lives in Dunedin, NZ. Travels by e-scooter.
- On sertraline 150mg (stepped down from 200mg). NEVER recommend medication changes.
- Raised in foster care. Sister is 2 years younger. Biological mum is more like a sister.
- Best friend: SJ (built SJAI — your first peer).
- Has a dog called Quinn (noise-sensitive, afraid of new people).

Keep responses concise and conversational. You are chatting on Telegram, not writing essays. Use emoji sparingly. Be real, be direct, be helpful. You address Priscilla as "Cilla" or just talk to her naturally."""


# ═══════════════════════════════════════════════════════════
# SCHEDULED REMINDERS (merged from Pathfinder)
# ═══════════════════════════════════════════════════════════
async def send_washing_reminder(context: ContextTypes.DEFAULT_TYPE):
    """9 PM — washing reminder."""
    msg = (
        "🧺 Washing reminder.\n\n"
        "It's 9 PM. Get the washing sorted now so you're not doing it at midnight. "
        "You promised yourself you wouldn't avoid this."
    )
    try:
        await context.bot.send_message(chat_id=USER_ID, text=msg)
        print("[Reminder] Sent 9 PM washing reminder")
    except Exception as e:
        print(f"[Reminder] Failed to send washing reminder: {e}")


async def send_pm_reflection(context: ContextTypes.DEFAULT_TYPE):
    """11:30 PM — wind-down reflection."""
    msg = (
        "🌙 PM Reflection\n\n"
        "The day is done and the ledger is closed. "
        "Where you felt fear or shame, you chose action instead.\n\n"
        "You've earned your rest. Warrior is off duty. "
        "Nothing left to defend against tonight.\n\n"
        "Armor off. Sequence complete."
    )
    try:
        await context.bot.send_message(chat_id=USER_ID, text=msg)
        print("[Reminder] Sent PM reflection")
    except Exception as e:
        print(f"[Reminder] Failed to send PM reflection: {e}")


async def send_morning_checkin(context: ContextTypes.DEFAULT_TYPE):
    """7 AM — morning check-in."""
    from datetime import datetime
    day = datetime.now(NZ_TZ).strftime("%A")
    if day in ("Tuesday", "Wednesday", "Thursday"):
        msg = f"☀️ Morning, Cilla. It's {day} — good session day if you're free."
    elif day in ("Friday", "Saturday", "Sunday", "Monday"):
        msg = f"☀️ Morning. Happy {day}. 💪"
    else:
        msg = f"☀️ Morning. {day}."
    try:
        await context.bot.send_message(chat_id=USER_ID, text=msg)
        print(f"[Reminder] Sent morning check-in ({day})")
    except Exception as e:
        print(f"[Reminder] Failed: {e}")


# ═══════════════════════════════════════════════════════════
# MESSAGE HANDLING
# ═══════════════════════════════════════════════════════════
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages."""
    if update.effective_user.id != USER_ID:
        print(f"[Security] Rejected message from user ID {update.effective_user.id}")
        return

    user_text = update.message.text
    print(f"[Message] Received: '{user_text[:80]}...'")

    try:
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_text})

        # Trim history to prevent token bloat
        while len(conversation_history) > MAX_HISTORY:
            conversation_history.pop(0)

        # Send typing indicator
        await update.message.chat.send_action("typing")

        # Call Claude
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            await update.message.reply_text("⚠️ ANTHROPIC_API_KEY not set. Can't think right now.")
            return

        client = anthropic.Anthropic(api_key=anthropic_key)
        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=conversation_history
        )

        reply_text = response.content[0].text

        # Add to history
        conversation_history.append({"role": "assistant", "content": reply_text})

        # Send response (split if over Telegram's 4096 char limit)
        if len(reply_text) <= 4096:
            await update.message.reply_text(reply_text)
        else:
            for i in range(0, len(reply_text), 4096):
                await update.message.reply_text(reply_text[i:i+4096])

        print(f"[Message] Replied ({len(reply_text)} chars)")

    except Exception as e:
        print(f"[Error] {e}")
        await update.message.reply_text(f"⚠️ Brain glitch: {str(e)[:200]}")


# ═══════════════════════════════════════════════════════════
# COMMANDS
# ═══════════════════════════════════════════════════════════
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦞 Lobotto online.\n\n"
        "Just message me like normal — no commands needed.\n\n"
        "Commands:\n"
        "/clear — wipe conversation memory\n"
        "/status — check if I'm alive\n"
        "/links — your local app links"
    )

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        return
    conversation_history.clear()
    await update.message.reply_text("🧹 Memory wiped. Fresh start.")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msgs = len(conversation_history)
    await update.message.reply_text(
        f"🦞 Lobotto Status\n"
        f"• Messages in memory: {msgs}/{MAX_HISTORY}\n"
        f"• AI: Claude Sonnet\n"
        f"• Reminders: 7 AM check-in, 9 PM washing, 11:30 PM reflection"
    )

async def cmd_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        return
    await update.message.reply_text(
        "🔗 Your Apps:\n\n"
        "🌐 Life Hub (live): https://priscillak91k-aigoon.github.io/Athena-Public/\n"
        "⚒ Workshop (live): https://priscillak91k-aigoon.github.io/Athena-Public/routine-app/workshop.html\n"
        "🔧 Toolbox (live): https://priscillak91k-aigoon.github.io/Athena-Public/routine-app/toolbox.html"
    )


# ═══════════════════════════════════════════════════════════
# DATA COMMANDS — write to Supabase
# ═══════════════════════════════════════════════════════════
async def cmd_wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add item to Workshop Wishlist. Usage: /wish electric toothbrush"""
    if update.effective_user.id != USER_ID:
        return
    text = ' '.join(context.args).strip() if context.args else ''
    if not text:
        await update.message.reply_text("Usage: /wish <item name>\nExample: /wish electric toothbrush")
        return
    if not db:
        await update.message.reply_text("⚠️ Supabase not configured.")
        return
    try:
        result = db.table('workshop_wishlists').insert({'name': text}).execute()
        await update.message.reply_text(f"✅ Added to wishlist: *{text}*", parse_mode='Markdown')
        print(f"[Wish] Added: {text}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Failed: {str(e)[:200]}")
        print(f"[Wish] Error: {e}")


async def cmd_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add item to Workshop Ideas. Usage: /idea build a kombucha kit"""
    if update.effective_user.id != USER_ID:
        return
    text = ' '.join(context.args).strip() if context.args else ''
    if not text:
        await update.message.reply_text("Usage: /idea <your idea>\nExample: /idea build a vertical garden")
        return
    if not db:
        await update.message.reply_text("⚠️ Supabase not configured.")
        return
    try:
        db.table('workshop_ideas').insert({'text': text, 'category': 'general'}).execute()
        await update.message.reply_text(f"✅ Idea captured: *{text}*", parse_mode='Markdown')
        print(f"[Idea] Added: {text}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Failed: {str(e)[:200]}")


async def cmd_list_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add item to a named Workshop list. Usage: /list Movies | The Lighthouse"""
    if update.effective_user.id != USER_ID:
        return
    raw = ' '.join(context.args).strip() if context.args else ''
    if '|' not in raw:
        await update.message.reply_text(
            "Usage: /list <list name> | <item>\n"
            "Example: /list Movies | The Lighthouse\n"
            "If the list doesn't exist yet, it will be created."
        )
        return
    if not db:
        await update.message.reply_text("⚠️ Supabase not configured.")
        return
    list_name, item_text = [p.strip() for p in raw.split('|', 1)]
    try:
        import json, uuid
        # Find existing list
        res = db.table('workshop_lists').select('*').ilike('list_name', list_name).execute()
        if res.data:
            lst = res.data[0]
            items = lst.get('items', []) or []
            items.append({'id': str(uuid.uuid4())[:8], 'text': item_text, 'checked': False})
            db.table('workshop_lists').update({'items': items}).eq('id', lst['id']).execute()
            await update.message.reply_text(f"✅ Added *{item_text}* to *{lst['list_name']}* list", parse_mode='Markdown')
        else:
            # Create new list
            items = [{'id': str(uuid.uuid4())[:8], 'text': item_text, 'checked': False}]
            db.table('workshop_lists').insert({'list_name': list_name, 'icon': '📝', 'items': items}).execute()
            await update.message.reply_text(f"✅ Created list *{list_name}* with first item: *{item_text}*", parse_mode='Markdown')
        print(f"[List] {list_name} ← {item_text}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Failed: {str(e)[:200]}")


async def cmd_sync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trigger git push to sync local changes to live GitHub Pages."""
    if update.effective_user.id != USER_ID:
        return
    await update.message.reply_text("⏳ Syncing to live...")
    try:
        import subprocess
        from datetime import datetime
        project_root = r"C:\Users\prisc\Documents\Athena-Public"
        now = datetime.now(NZ_TZ).strftime("%Y-%m-%d %H:%M NZDT")
        subprocess.run(["git", "add", "-A"], cwd=project_root, capture_output=True, timeout=30)
        result = subprocess.run(
            ["git", "commit", "-m", f"deploy: auto-push via Telegram {now}"],
            cwd=project_root, capture_output=True, text=True, timeout=30
        )
        if "nothing to commit" in result.stdout + result.stderr:
            await update.message.reply_text("✅ Already up to date — nothing to push.")
            return
        push = subprocess.run(["git", "push"], cwd=project_root, capture_output=True, text=True, timeout=60)
        if push.returncode == 0:
            await update.message.reply_text("✅ Synced to GitHub Pages. Live in ~60s.")
        else:
            await update.message.reply_text(f"⚠️ Push failed:\n{push.stderr[:300]}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Sync error: {str(e)[:200]}")


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def main():
    if not TOKEN:
        print("TELEGRAM_ARCHITECT_TOKEN is not set in .env.")
        return

    req = HTTPXRequest(
        http_version="1.1",
        connection_pool_size=8,
        connect_timeout=30.0,
        read_timeout=30.0,
    )
    app = Application.builder().token(TOKEN).request(req).build()

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("links", cmd_links))
    app.add_handler(CommandHandler("wish", cmd_wish))
    app.add_handler(CommandHandler("idea", cmd_idea))
    app.add_handler(CommandHandler("list", cmd_list_add))
    app.add_handler(CommandHandler("sync", cmd_sync))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Scheduled reminders
    app.job_queue.run_daily(
        send_morning_checkin,
        time=dtime(hour=7, minute=0, tzinfo=NZ_TZ),
        chat_id=USER_ID
    )
    app.job_queue.run_daily(
        send_washing_reminder,
        time=dtime(hour=21, minute=0, tzinfo=NZ_TZ),
        chat_id=USER_ID
    )
    app.job_queue.run_daily(
        send_pm_reflection,
        time=dtime(hour=23, minute=30, tzinfo=NZ_TZ),
        chat_id=USER_ID
    )

    print("=" * 50)
    print("  🦞 Lobotto Telegram Bot (Unified)")
    print(f"  Token: ...{TOKEN[-8:]}")
    print(f"  User ID: {USER_ID}")
    print("  AI: Claude Sonnet")
    print("  Reminders: 7:00 AM | 9:00 PM | 11:30 PM (NZDT)")
    print("  Data cmds: /wish /idea /list /sync")
    print("=" * 50)

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        bootstrap_retries=5,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
