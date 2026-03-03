"""
Lobotto — Discord Bot
Powered by Anthropic Claude | Personality: Lobotto (Athena Framework)
"""
import os
import asyncio
import discord
from discord.ext import commands
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

if not DISCORD_TOKEN:
    raise ValueError("Missing DISCORD_BOT_TOKEN in .env")
if not ANTHROPIC_KEY:
    raise ValueError("Missing ANTHROPIC_API_KEY in .env")

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


# --- Events ---
@bot.event
async def on_ready():
    print("=" * 50)
    print("  [BOT] Lobotto is ONLINE")
    print(f"  Logged in as: {bot.user.name}")
    print(f"  Servers: {', '.join(g.name for g in bot.guilds)}")
    print("  AI Backend: Anthropic Claude")
    print("=" * 50)
    # Set status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="@Lobotto to chat"
        )
    )


@bot.event
async def on_message(message):
    # Ignore own messages
    if message.author == bot.user:
        return

    # Ignore other bots
    if message.author.bot:
        return

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
    await ctx.send(
        f"**🤖 Lobotto Status**\n"
        f"• Uptime: Since boot\n"
        f"• AI Backend: Anthropic Claude\n"
        f"• Channels with context: {channels_tracked}\n"
        f"• Messages in memory: {total_messages}\n"
        f"• Latency: {round(bot.latency * 1000)}ms"
    )


# --- Launch ---
if __name__ == "__main__":
    print("Starting Lobotto Discord Bot...")
    bot.run(DISCORD_TOKEN)
