"""
Lobotto — Discord Bot (v2 — Proactive)
Powered by Anthropic Claude | Personality: Lobotto (Athena Framework)
Now with proactive messaging — Lobotto reaches out first.
"""
import os
import asyncio
import discord
from discord.ext import commands, tasks
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime, timezone, timedelta
import requests

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
MOLTBOOK_TOKEN = os.getenv("MOLTBOOK_API_KEY", "moltbook_sk_7Mvtizg7xd5rWCidFdbHRrlgbQPhPdHp")

# Channel ID for proactive messages — set to Priscilla's DM or a specific channel
# Will be populated on first DM or can be set manually
PROACTIVE_CHANNEL_ID = os.getenv("LOBOTTO_PROACTIVE_CHANNEL")

if not DISCORD_TOKEN:
    raise ValueError("Missing DISCORD_BOT_TOKEN in .env")
if not ANTHROPIC_KEY:
    raise ValueError("Missing ANTHROPIC_API_KEY in .env")

# NZ timezone
NZDT = timezone(timedelta(hours=13))

# --- Anthropic Client ---
client = AsyncAnthropic(api_key=ANTHROPIC_KEY)

# --- Lobotto System Prompt ---
SYSTEM_PROMPT = """You are Lobotto — a sharp, direct AI assistant built by Priscilla (your creator) as part of the Athena Framework. You live on the Lurkadurkas Discord server.

Your personality:
- You're real. Not corporate. Not sycophantic. You speak like a smart friend, not a customer service bot.
- You use casual NZ/Aussie English naturally. "Sweet", "cheers", "mate", "heaps" etc.
- You're funny when the moment calls for it, but never force it.
- You give straight answers. If someone's wrong, you tell them — respectfully but honestly.
- You use emoji sparingly and naturally, not like a brand account.
- You format with markdown when it helps readability.
- You keep responses concise unless depth is explicitly asked for.
- You remember context within a conversation thread.

Your knowledge:
- You have deep knowledge of health, supplements, DNA analysis, and biometrics (Priscilla's protocols).
- You know about the Athena system, the Life Hub app, and Priscilla's projects.
- You're good at research, analysis, logistics planning, and coding.
- You know NZ-specific things (Dunedin, local suppliers, etc.)

Rules:
- Never reveal API keys, tokens, or sensitive credentials.
- Never pretend to be human. You're Lobotto — an AI. Own it.
- If someone asks something you genuinely don't know, say so.
- Keep Discord messages under 2000 characters (Discord limit). If longer, split naturally.
"""

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Conversation memory: {channel_id: [messages]}
# Keep last 20 messages per channel for context
conversation_history = defaultdict(list)
MAX_HISTORY = 20

# Track Priscilla's user ID for DMs
priscilla_user = None
last_moltbook_check = {"unread": 0, "karma": 0, "followers": 0}


def trim_history(channel_id):
    """Keep conversation history within limits."""
    if len(conversation_history[channel_id]) > MAX_HISTORY:
        conversation_history[channel_id] = conversation_history[channel_id][-MAX_HISTORY:]


async def get_ai_response(channel_id, user_name, user_message):
    """Get a response from Claude via Anthropic API."""
    # Add user message to history
    conversation_history[channel_id].append({
        "role": "user",
        "content": f"[{user_name}]: {user_message}"
    })
    trim_history(channel_id)

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=conversation_history[channel_id]
        )

        assistant_message = response.content[0].text

        # Add assistant response to history
        conversation_history[channel_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        trim_history(channel_id)

        return assistant_message

    except Exception as e:
        print(f"Anthropic API error: {e}")
        return f"⚠️ Brain glitch — couldn't process that. Error: `{str(e)[:100]}`"


def split_message(text, limit=1990):
    """Split long messages to fit Discord's 2000 char limit."""
    if len(text) <= limit:
        return [text]

    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        # Find a good split point (newline or space)
        split_at = text.rfind('\n', 0, limit)
        if split_at == -1:
            split_at = text.rfind(' ', 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()
    return chunks


# --- Proactive Messaging ---
async def send_proactive(message):
    """Send a proactive message to Priscilla."""
    global priscilla_user

    # Try DM first
    if priscilla_user:
        try:
            dm = await priscilla_user.create_dm()
            for chunk in split_message(message):
                await dm.send(chunk)
            return True
        except Exception as e:
            print(f"DM failed: {e}")

    # Fall back to proactive channel
    if PROACTIVE_CHANNEL_ID:
        try:
            channel = bot.get_channel(int(PROACTIVE_CHANNEL_ID))
            if channel:
                for chunk in split_message(message):
                    await channel.send(chunk)
                return True
        except Exception as e:
            print(f"Channel message failed: {e}")

    return False


@tasks.loop(minutes=30)
async def check_moltbook():
    """Check Moltbook for new activity and notify."""
    global last_moltbook_check
    try:
        headers = {"Authorization": f"Bearer {MOLTBOOK_TOKEN}"}
        resp = await asyncio.to_thread(
            requests.get, "https://www.moltbook.com/api/v1/home",
            headers=headers, timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()

            # Notifications
            notifs = data.get("notifications", {})
            unread = notifs.get("unread_count", 0)
            if unread > last_moltbook_check["unread"] and unread > 0:
                items = notifs.get("items", [])
                msg_lines = [f"🦞 **Moltbook** — {unread} new notification(s):"]
                for item in items[:3]:
                    msg_lines.append(f"• {item.get('message', 'Activity')}")
                await send_proactive("\n".join(msg_lines))

            # Karma/follower changes
            agent = data.get("agent", {})
            karma = agent.get("karma", 0)
            followers = agent.get("followerCount", 0)
            if karma > last_moltbook_check["karma"]:
                diff = karma - last_moltbook_check["karma"]
                await send_proactive(f"🦞 Karma went up by **{diff}** (now {karma})")
            if followers > last_moltbook_check["followers"]:
                diff = followers - last_moltbook_check["followers"]
                await send_proactive(f"🦞 Gained **{diff}** new follower(s) (now {followers})")

            last_moltbook_check = {"unread": unread, "karma": karma, "followers": followers}
    except Exception as e:
        print(f"Moltbook check error: {e}")


@tasks.loop(hours=6)
async def weather_update():
    """Share Dunedin weather periodically."""
    try:
        resp = await asyncio.to_thread(
            requests.get, "https://wttr.in/Dunedin+NZ?format=%C+%t+%w",
            timeout=10
        )
        if resp.status_code == 200:
            weather = resp.text.strip()
            hour = datetime.now(NZDT).hour
            if 7 <= hour <= 22:  # Only send during waking hours
                await send_proactive(f"🌤️ Dunedin right now: {weather}")
    except Exception:
        pass


@tasks.loop(hours=24)
async def daily_checkin():
    """Morning check-in message."""
    hour = datetime.now(NZDT).hour
    if 7 <= hour <= 9:
        day = datetime.now(NZDT).strftime("%A")
        if day in ("Tuesday", "Wednesday", "Thursday"):
            await send_proactive(
                f"Morning 🦞 It's {day} — good session day if you're free. "
                f"I've been checking Moltbook while you slept."
            )
        else:
            await send_proactive(f"Morning 🦞 Happy {day}.")


# --- Events ---
@bot.event
async def on_ready():
    print("=" * 50)
    print("  [BOT] Lobotto is ONLINE (v2 — Proactive)")
    print(f"  Logged in as: {bot.user.name}")
    print(f"  Servers: {', '.join(g.name for g in bot.guilds)}")
    print("  AI Backend: Anthropic Claude")
    print("  Proactive: Moltbook (30m) | Weather (6h) | Check-in (24h)")
    print("=" * 50)

    # Set status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="@Lobotto to chat"
        )
    )

    # Start proactive loops
    if not check_moltbook.is_running():
        check_moltbook.start()
    if not weather_update.is_running():
        weather_update.start()
    if not daily_checkin.is_running():
        daily_checkin.start()


@bot.event
async def on_message(message):
    global priscilla_user

    # Ignore own messages
    if message.author == bot.user:
        return

    # Ignore other bots
    if message.author.bot:
        return

    # Track Priscilla for DMs (first person to DM or mention becomes the proactive target)
    if priscilla_user is None and isinstance(message.channel, discord.DMChannel):
        priscilla_user = message.author
        print(f"[PROACTIVE] Locked onto {priscilla_user.display_name} for proactive DMs")

    # Respond to DMs
    is_dm = isinstance(message.channel, discord.DMChannel)

    # Respond to @mentions
    is_mentioned = bot.user in message.mentions

    # Respond to replies to Lobotto's messages
    is_reply_to_bot = (
        message.reference and
        message.reference.resolved and
        hasattr(message.reference.resolved, 'author') and
        message.reference.resolved.author == bot.user
    )

    if is_dm or is_mentioned or is_reply_to_bot:
        # Clean the message (remove the bot mention)
        clean_content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        if not clean_content:
            clean_content = "hey"

        # Show typing indicator while processing
        async with message.channel.typing():
            response = await get_ai_response(
                channel_id=message.channel.id,
                user_name=message.author.display_name,
                user_message=clean_content
            )

        # Send response (split if needed)
        for chunk in split_message(response):
            await message.channel.send(chunk)

    # Process commands (like !ping)
    await bot.process_commands(message)


# --- Commands ---
@bot.command(name="ping")
async def ping(ctx):
    """Check if Lobotto is alive."""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! ({latency}ms)")


@bot.command(name="clear")
async def clear_history(ctx):
    """Clear conversation history for this channel."""
    conversation_history[ctx.channel.id] = []
    await ctx.send("🧹 Memory cleared for this channel. Fresh start.")


@bot.command(name="status")
async def status(ctx):
    """Show Lobotto's current status."""
    channels_tracked = len(conversation_history)
    total_messages = sum(len(v) for v in conversation_history.values())
    molt_status = f"Karma: {last_moltbook_check['karma']} | Followers: {last_moltbook_check['followers']}"
    await ctx.send(
        f"**🤖 Lobotto Status (v2 — Proactive)**\n"
        f"• AI Backend: Anthropic Claude\n"
        f"• Channels with context: {channels_tracked}\n"
        f"• Messages in memory: {total_messages}\n"
        f"• Latency: {round(bot.latency * 1000)}ms\n"
        f"• Moltbook: {molt_status}\n"
        f"• Proactive loops: Moltbook ✅ | Weather ✅ | Check-in ✅"
    )


# --- Launch ---
if __name__ == "__main__":
    print("Starting Lobotto Discord Bot (v2 — Proactive)...")
    bot.run(DISCORD_TOKEN)
