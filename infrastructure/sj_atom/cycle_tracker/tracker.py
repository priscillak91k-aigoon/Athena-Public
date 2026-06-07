import os
import json
import logging
import datetime
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
STATE_FILE = "/context/.cycle_state.json"
NZT = pytz.timezone('Pacific/Auckland')

# ============================================================================
# PHASE DEFINITIONS — Evidence-Based Cycle Syncing
# ============================================================================
# Sources: Cleveland Clinic, Healthline, NIH, Harvard Health
# Cycle model: 28-day average, 4-phase consumer framework
# Clinically, Follicular overlaps Menstrual (both start Day 1), but consumer
# trackers universally separate them for UX clarity.
# ============================================================================

PHASES = {
    1: {
        "name": "🩸 Menstrual Phase",
        "days": "Days 1–5",
        "msg": (
            "Your cycle has begun.\n\n"
            "🔬 *What's happening:* Estrogen and progesterone are at their lowest. "
            "The uterine lining is shedding.\n\n"
            "⚡ *Energy & Mood:* Expect lower energy, potential cramps, and fatigue. "
            "Some people feel introspective or withdrawn — this is normal.\n\n"
            "🏋️ *Exercise:* Gentle movement only — walking, yoga, stretching. "
            "Don't force high-intensity work if your body says no.\n\n"
            "🍽️ *Nutrition:* Prioritise iron-rich foods (red meat, lentils, spinach) "
            "to replenish what's lost. Stay hydrated. Magnesium-rich foods "
            "(dark chocolate, nuts) may help with cramps.\n\n"
            "💡 *Tip:* This is a rest-and-reflect window. Don't schedule big social "
            "commitments if you can avoid it."
        )
    },
    6: {
        "name": "🌱 Follicular Phase",
        "days": "Days 6–12",
        "msg": (
            "You've entered the Follicular phase.\n\n"
            "🔬 *What's happening:* Estrogen is steadily rising. Your brain is "
            "producing more FSH, maturing a new egg.\n\n"
            "⚡ *Energy & Mood:* Mental clarity and focus are increasing. "
            "Motivation and optimism tend to peak. Creativity is high.\n\n"
            "🏋️ *Exercise:* Your body can handle more intensity now — resistance "
            "training, HIIT, and endurance work are well-tolerated. "
            "Rising estrogen supports muscle recovery.\n\n"
            "🍽️ *Nutrition:* Lean proteins and complex carbs to fuel the energy "
            "surge. Great time to experiment with new recipes or meal prep.\n\n"
            "💡 *Tip:* This is your power window. Schedule important meetings, "
            "deep work sessions, and challenging projects here."
        )
    },
    13: {
        "name": "🔥 Ovulatory Phase",
        "days": "Days 13–14",
        "msg": (
            "Ovulation is approaching (or occurring today).\n\n"
            "🔬 *What's happening:* Estrogen peaks. A surge of luteinising hormone "
            "(LH) triggers egg release. Testosterone also spikes briefly.\n\n"
            "⚡ *Energy & Mood:* This is typically your highest-energy window. "
            "Confidence, sociability, and verbal fluency tend to peak.\n\n"
            "🏋️ *Exercise:* Peak physical performance. Go hard if it feels right — "
            "strength training, intense cardio, competitive activities.\n\n"
            "🍽️ *Nutrition:* Anti-inflammatory foods (salmon, berries, leafy greens) "
            "support the hormonal transition that's about to happen.\n\n"
            "💡 *Tip:* Capitalise on this peak state for social events, "
            "presentations, or anything requiring confidence."
        )
    },
    15: {
        "name": "🍂 Luteal Phase",
        "days": "Days 15–28",
        "msg": (
            "The Luteal phase has begun.\n\n"
            "🔬 *What's happening:* Progesterone is rising sharply. Your body is "
            "preparing for potential implantation. Basal body temperature increases.\n\n"
            "⚡ *Energy & Mood:* Energy gradually winds down. You may notice "
            "increased appetite, fluid retention, and mood shifts (irritability, "
            "anxiety). These are progesterone effects, not personal failings.\n\n"
            "🏋️ *Exercise:* Moderate intensity is ideal — steady-state cardio, "
            "Pilates, swimming. Your body shifts toward fat oxidation, so "
            "endurance work can feel surprisingly good.\n\n"
            "🍽️ *Nutrition:* Resting metabolic rate increases (~100-300 cal/day). "
            "Honour the hunger — complex carbs and healthy fats help stabilise "
            "mood. Calcium and Vitamin D may reduce PMS symptoms. "
            "Reduce salt, caffeine, and alcohol if bloating is an issue.\n\n"
            "💡 *Tip:* Start pacing yourself. Wrap up big projects rather than "
            "starting new ones. Prioritise sleep — your body needs more of it now."
        )
    }
}

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
            f"🔔 *Cycle Update — Day {current_day}*\n\n"
            f"*{phase['name']} ({phase['days']})*\n\n"
            f"{phase['msg']}"
        )
        try:
            await context.bot.send_message(
                chat_id=CHAT_ID, text=msg, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send daily notification: {e}")


# ============================================================================
# TELEGRAM COMMAND HANDLERS
# ============================================================================

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset the cycle anchor to today. Triggered by /reset or texting 'period'."""
    if str(update.message.chat_id) != str(CHAT_ID):
        return

    today_str = datetime.datetime.now(NZT).date().strftime("%Y-%m-%d")
    save_state({"anchor_date": today_str})

    await update.message.reply_text(
        f"✅ Cycle anchor reset to today ({today_str}). You are now on Day 1."
    )

    # Send the Day 1 phase info immediately
    phase = PHASES[1]
    info_msg = f"*{phase['name']} ({phase['days']})*\n\n{phase['msg']}"
    await update.message.reply_text(info_msg, parse_mode="Markdown")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current cycle day and phase. Triggered by /status or any text."""
    if str(update.message.chat_id) != str(CHAT_ID):
        return

    state = load_state()
    current_day = get_current_day(state["anchor_date"])
    phase = get_phase_for_day(current_day)

    msg = (
        f"📊 *Cycle Status*\n\n"
        f"Anchor Date: {state['anchor_date']}\n"
        f"Current Day: *Day {current_day}*\n"
        f"Current Phase: *{phase['name']}*\n\n"
        f"_Send \"period\" or /reset when your next cycle begins._"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free-text messages. 'period'/'reset'/'started' resets; else status."""
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower().strip()
    if any(keyword in text for keyword in ["reset", "started", "period"]):
        await reset_command(update, context)
    else:
        await status_command(update, context)


def main():
    if not TOKEN or not CHAT_ID:
        logger.error("FATAL: TELEGRAM_TOKEN and TELEGRAM_CHAT_ID must be set!")
        return

    app = Application.builder().token(TOKEN).build()

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
