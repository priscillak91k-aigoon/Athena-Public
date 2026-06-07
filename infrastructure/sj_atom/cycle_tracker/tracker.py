import os
import json
import logging
import datetime
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, Defaults

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
STATE_FILE = os.environ.get("STATE_FILE", "/context/.cycle_state.json")
NZT = pytz.timezone('Pacific/Auckland')
TONE = os.environ.get("TONE", "warm").lower()

# ============================================================================
# PHASE DEFINITIONS — Evidence-Based Cycle Syncing
# ============================================================================
# Sources: Cleveland Clinic, Healthline, NIH, Harvard Health
# Cycle model: 28-day average, 4-phase consumer framework
# Clinically, Follicular overlaps Menstrual (both start Day 1), but consumer
# trackers universally separate them for UX clarity.
# ============================================================================

WARM_PHASES = {
    1: {
        "name": "🩸 Menstrual Phase",
        "days": "Days 1–5",
        "msg": (
            "Hey lovely, your cycle has started again. Take it easy today. 🤍\n\n"
            "🔬 <b>What's going on:</b> Your hormones are at their quietest right now — "
            "estrogen and progesterone have both dipped. Your body is doing its "
            "natural reset.\n\n"
            "⚡ <b>How you might feel:</b> You may feel a bit more tired than usual, "
            "and you might want more time to yourself. That's completely okay — "
            "it's your body asking for rest, not weakness.\n\n"
            "🏋️ <b>Movement:</b> Gentle is the word — a walk, some yoga, or just "
            "stretching. If you feel like doing more, go for it. But there's no "
            "pressure to push through anything right now.\n\n"
            "🍽️ <b>Nourishment:</b> Iron-rich foods are your friend (think red meat, "
            "lentils, spinach). Pair them with something rich in vitamin C "
            "(kiwifruit, capsicum, citrus) to help your body absorb it. Stay hydrated. "
            "And if you're craving dark chocolate — that's actually your body asking "
            "for magnesium. Have some. 🍫\n\n"
            "💡 <b>A gentle reminder:</b> This is a beautiful time for reflection and "
            "quietness. You don't have to be 'on' right now."
        )
    },
    6: {
        "name": "🌱 Follicular Phase",
        "days": "Days 6–12",
        "msg": (
            "Good morning! You're entering your Follicular phase — things are "
            "about to feel a lot brighter. ✨\n\n"
            "🔬 <b>What's going on:</b> Estrogen is gently rising, and your body is "
            "building up fresh energy reserves.\n\n"
            "⚡ <b>How you might feel:</b> You'll probably notice your mind feels "
            "sharper and clearer. Ideas flow easier. Motivation starts to come "
            "back naturally — don't fight it, ride it.\n\n"
            "🏋️ <b>Movement:</b> Your body is ready for more now — resistance training, "
            "a good run, or anything that gets your heart going. Recovery is "
            "faster during this phase too, so push a little if it feels good.\n\n"
            "🍽️ <b>Nourishment:</b> Lean proteins and wholesome carbs will fuel the "
            "energy you're building. Great time to try that new recipe you've "
            "been saving.\n\n"
            "💡 <b>A gentle reminder:</b> This is your power window. If there's something "
            "big you've been putting off — a conversation, a project, a decision — "
            "now is the time."
        )
    },
    13: {
        "name": "🔥 Ovulatory Phase",
        "days": "Days 13–14",
        "msg": (
            "You're glowing — ovulation is here or just around the corner. 🌟\n\n"
            "🔬 <b>What's going on:</b> Estrogen is at its peak. There's a brief "
            "little spike of testosterone too, which adds to the confidence.\n\n"
            "⚡ <b>How you might feel:</b> This is often when you feel your most "
            "magnetic — more social, more articulate, more <i>you</i>. If you feel "
            "like you could take on the world today, that's real.\n\n"
            "🏋️ <b>Movement:</b> You're at your physical peak right now. If there's "
            "a workout you love, today is the day. Strength, cardio, whatever "
            "lights you up.\n\n"
            "🍽️ <b>Nourishment:</b> Anti-inflammatory foods (salmon, berries, leafy "
            "greens) support the hormonal shift that's coming next.\n\n"
            "💡 <b>A gentle reminder:</b> Enjoy this energy. Say yes to the social "
            "thing. Start the conversation. You're in your element."
        )
    },
    15: {
        "name": "🍂 Luteal Phase",
        "days": "Days 15–28",
        "msg": (
            "The Luteal phase is here. Time to slow down a little — and that's "
            "a good thing. 🍵\n\n"
            "🔬 <b>What's going on:</b> Progesterone is rising, and your body is "
            "naturally shifting gears. Your temperature goes up slightly too.\n\n"
            "⚡ <b>How you might feel:</b> You may feel things more deeply during this "
            "time — emotions might be closer to the surface, and that's perfectly "
            "natural. You might also notice you're hungrier than usual (your "
            "metabolism actually speeds up a little).\n\n"
            "🏋️ <b>Movement:</b> Moderate is your sweet spot — Pilates, swimming, a "
            "long walk. Your body is actually better at burning fat for fuel "
            "right now, so steady movement feels surprisingly good.\n\n"
            "🍽️ <b>Nourishment:</b> Honour your appetite — your body genuinely needs "
            "a bit more right now. Complex carbs and healthy fats help keep "
            "your mood steady. Calcium and Vitamin D are your allies. If bloating "
            "shows up, easing off salt and caffeine can help.\n\n"
            "💡 <b>A gentle reminder:</b> You're not slowing down because something is "
            "wrong. You're slowing down because your body is wise. Finish what's "
            "open, rest what can wait, and be kind to yourself."
        )
    }
}

CLINICAL_PHASES = {
    1: {
        "name": "Menstrual Phase",
        "days": "Days 1–5",
        "msg": (
            "<b>State:</b> Hormonal baseline. Estrogen and progesterone are at their lowest.\n\n"
            "<b>Effects:</b> Reduced energy levels, potential fatigue.\n\n"
            "<b>Action:</b> Focus on rest, low-intensity movement (walking, yoga), and iron-rich foods combined with Vitamin C for absorption."
        )
    },
    6: {
        "name": "Follicular Phase",
        "days": "Days 6–12",
        "msg": (
            "<b>State:</b> Estrogen rising.\n\n"
            "<b>Effects:</b> Increased cognitive clarity, energy, and motivation.\n\n"
            "<b>Action:</b> Optimal window for high-intensity training, project initiation, and complex tasks."
        )
    },
    13: {
        "name": "Ovulatory Phase",
        "days": "Days 13–14",
        "msg": (
            "<b>State:</b> Estrogen peak, accompanied by a minor testosterone spike.\n\n"
            "<b>Effects:</b> Peak physical and verbal performance.\n\n"
            "<b>Action:</b> Prioritise high-output activities, strength training, and social engagements."
        )
    },
    15: {
        "name": "Luteal Phase",
        "days": "Days 15–28",
        "msg": (
            "<b>State:</b> Progesterone rising. Core body temperature increases.\n\n"
            "<b>Effects:</b> Metabolism increases by ~3-5% (30-120 kcal/day). Potential for decreased insulin sensitivity and increased systemic inflammation.\n\n"
            "<b>Action:</b> Transition to moderate, steady-state exercise. Increase complex carbohydrate and healthy fat intake. Monitor for signs of fatigue."
        )
    }
}

PHASES = CLINICAL_PHASES if TONE == "clinical" else WARM_PHASES

# Sorted phase transition days for lookup
PHASE_DAYS = sorted(PHASES.keys())


def load_state():
    """Load cycle state from disk. Merges with defaults to prevent key-amnesia."""
    default_state = {"anchor_date": "2026-06-08"}
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                default_state.update(data)
    except (FileNotFoundError, json.JSONDecodeError):
        save_state(default_state)
    return default_state


def save_state(state):
    """Atomic write: write to .tmp then replace to prevent corruption on crash."""
    tmp_file = STATE_FILE + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(state, f, indent=4)
    os.replace(tmp_file, STATE_FILE)


def get_current_day(anchor_date_str):
    """Calculate the current cycle day (1-28) from the anchor date."""
    try:
        anchor_date = datetime.datetime.strptime(anchor_date_str, "%Y-%m-%d").date()
    except ValueError:
        logger.error(f"Invalid anchor_date format: {anchor_date_str}. Resetting to today.")
        return 1

    today = datetime.datetime.now(NZT).date()
    days_elapsed = (today - anchor_date).days

    if days_elapsed < 0:
        return 1

    return (days_elapsed % 28) + 1


def get_phase_for_day(day):
    """Determine which phase a given cycle day falls in."""
    current_phase_start = PHASE_DAYS[0]
    for start_day in PHASE_DAYS:
        if day >= start_day:
            current_phase_start = start_day
        else:
            break
    return PHASES[current_phase_start]


async def daily_check(context: ContextTypes.DEFAULT_TYPE):
    """Called once daily at 9:00 AM NZT by the JobQueue."""
    state = load_state()
    current_day = get_current_day(state["anchor_date"])
    logger.info(f"Daily Check: Cycle Day {current_day}")

    # Only send a notification on phase transition days
    if current_day in PHASES:
        phase = PHASES[current_day]
        msg = (
            f"🔔 <b>Cycle Update — Day {current_day}</b>\n\n"
            f"<b>{phase['name']} ({phase['days']})</b>\n\n"
            f"{phase['msg']}"
        )
        try:
            await context.bot.send_message(
                chat_id=CHAT_ID, text=msg, parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to send daily notification: {e}")


# ============================================================================
# TELEGRAM COMMAND HANDLERS
# ============================================================================

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset the cycle anchor to today. Triggered by /reset or texting 'period'."""
    logger.info(f"Received reset command from chat_id: {update.message.chat_id}")
    if str(update.message.chat_id) != str(CHAT_ID):
        logger.warning(f"Unauthorized chat_id {update.message.chat_id} tried to reset. Expected {CHAT_ID}.")
        return

    today_str = datetime.datetime.now(NZT).date().strftime("%Y-%m-%d")
    save_state({"anchor_date": today_str})

    if TONE == "clinical":
        await update.message.reply_text(f"Cycle anchor reset. Current day: 1.")
    else:
        await update.message.reply_text(f"Got it — I've noted today ({today_str}) as Day 1. 🤍")

    # Send the Day 1 phase info immediately
    phase = PHASES[1]
    info_msg = f"<b>{phase['name']} ({phase['days']})</b>\n\n{phase['msg']}"
    await update.message.reply_text(info_msg, parse_mode="HTML")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current cycle day and phase. Triggered by /status or any text."""
    logger.info(f"Received status command from chat_id: {update.message.chat_id}")
    if str(update.message.chat_id) != str(CHAT_ID):
        logger.warning(f"Unauthorized chat_id {update.message.chat_id} tried to get status. Expected {CHAT_ID}.")
        return

    state = load_state()
    current_day = get_current_day(state["anchor_date"])
    phase = get_phase_for_day(current_day)

    if TONE == "clinical":
        msg = (
            f"<b>Status Report</b>\n\n"
            f"Anchor Date: {state['anchor_date']}\n"
            f"Current Day: <b>{current_day}</b>\n"
            f"Phase: <b>{phase['name']}</b>\n\n"
            f'<i>Send "reset" or "period" to re-anchor cycle.</i>'
        )
    else:
        msg = (
            f"📊 <b>How you're tracking</b>\n\n"
            f"Last period started: {state['anchor_date']}\n"
            f"Today: <b>Day {current_day}</b>\n"
            f"Phase: <b>{phase['name']}</b>\n\n"
            f'<i>Just send "period" or /reset when your next one begins.</i>'
        )
    await update.message.reply_text(msg, parse_mode="HTML")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free-text messages. 'period'/'reset'/'started' resets; else status."""
    if not update.message or not update.message.text:
        return

    logger.info(f"Received text '{update.message.text}' from chat_id: {update.message.chat_id}")

    text = update.message.text.lower().strip()
    if any(keyword in text for keyword in ["reset", "started", "period"]):
        await reset_command(update, context)
    else:
        await status_command(update, context)


def main():
    if not TOKEN or not CHAT_ID:
        logger.error("FATAL: TELEGRAM_TOKEN and TELEGRAM_CHAT_ID must be set!")
        return

    defaults = Defaults(tzinfo=NZT)
    app = Application.builder().token(TOKEN).defaults(defaults).build()

    # Register command handlers
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("start", status_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # Schedule the daily phase-check using PTB's native JobQueue (APScheduler)
    # This is the correct v20+ pattern — no manual asyncio loop needed.
    job_queue = app.job_queue
    check_time = datetime.time(hour=9, minute=0, second=0, tzinfo=NZT)
    job_queue.run_daily(
        daily_check,
        time=check_time,
        days=(0, 1, 2, 3, 4, 5, 6),
        name="cycle_daily_check"
    )
    logger.info(f"Scheduled daily cycle check at 09:00 NZT")

    logger.info("Cycle Tracker is booting up...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
