"""
Lobotto Discord Architecture (v3 — Deep Ambient)
Implements:
1. File-based Identity Firewall (reads local .context and framework files)
2. Ghost State Encoding (pseudo-memory using ||st:{state}||)
3. AIOS Dual-Pass Logic (Logic Kernel -> Personality Node)
"""
import os
import re
import json
import asyncio
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from pathlib import Path
import google.generativeai as genai

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CILLA_ID = int(os.getenv("DISCORD_CILLA_ID", "0"))
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    # Read from central framework if missing
    try:
        from scripts.boot import load_env
        load_env()
        GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    except ImportError:
        pass

genai.configure(api_key=GOOGLE_API_KEY)
# We will use the Gemini 2.5 Flash model for fast concurrent reasoning, or Pro for deep thought.
model = genai.GenerativeModel('gemini-2.5-flash')

# Base paths
ROOT_DIR = Path(__file__).parent.parent
CONTEXT_DIR = ROOT_DIR / ".context"
FRAMEWORK_DIR = ROOT_DIR / "framework"
VAULT_DIR = ROOT_DIR / "vault"
LOG_DIR = ROOT_DIR / "session_logs"

# Ensure directories exist
LOG_DIR.mkdir(exist_ok=True)

NZDT = timezone(timedelta(hours=13))

# --- Local File Loading ---
def read_safe(path: Path, default=""):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception as e:
        print(f"Error reading {path}: {e}")
    return default

def get_live_context():
    """Builds the dynamic context block by reading the local filesystem."""
    identity = read_safe(FRAMEWORK_DIR / "Core_Identity.md")
    combat = read_safe(FRAMEWORK_DIR / "Combat_Protocol.md")
    corrections = read_safe(CONTEXT_DIR / "corrections.md")
    
    # Optional supplement schedule
    supp_schedule = read_safe(VAULT_DIR / "supplement_schedule.md", "Schedule not found.")
    
    # Try to extract the last ghost note
    last_gn = ""
    gn_path = CONTEXT_DIR / "latest_ghost_note.json"
    if gn_path.exists():
        try:
            with open(gn_path, "r") as f:
                data = json.load(f)
                last_gn = f"Latest Vibe: {data.get('content', '')}"
        except:
            pass

    return f"""
    [CORE IDENTITY]
    {identity}
    
    [COMBAT PROTOCOL]
    {combat}
    
    [CORRECTIONS & RULES]
    {corrections}
    
    [LIVE VIBE/GHOST NOTE]
    {last_gn}
    
    [SUPPLEMENT SCHEDULE]
    {supp_schedule}
    """

# --- Ghost State Extraction ---
def extract_ghost_state(messages):
    """Parses recent channel history to find the last known Ghost State."""
    for msg in reversed(messages):
        if msg.author.bot:
            match = re.search(r'\|\|st:(.*?)\|\|', msg.content)
            if match:
                return match.group(1)
    return "No prior state."

# --- AIOS Dual-Pass Reasoning ---
async def process_dual_pass(user_content, ghost_state):
    """Pass 1: Logic Kernel. Pass 2: Personality Node."""
    
    live_context = get_live_context()
    print("[AIOS] Pass 1: Initiating Logic Kernel...")
    
    # PASS 1: LOGIC KERNEL (Unfiltered Reasoning)
    pass1_prompt = f"""
    SYSTEM CONTEXT:
    {live_context}
    
    GHOST STATE (Previous Memory): {ghost_state}
    
    USER INPUT: {user_content}
    
    TASK: Analyze this logically and objectively. 
    Do not format for the user yet. Do not apply persona. 
    1. What is the core intent?
    2. Does this violate any Combat Protocols or Rules?
    3. What objective facts or actions are required?
    """
    
    pass1_response = await asyncio.to_thread(model.generate_content, pass1_prompt)
    logic_kernel = pass1_response.text
    print(f"[AIOS] Logic Kernel Output: {logic_kernel[:100]}...")

    # PASS 2: PERSONALITY NODE (Output Generation)
    print("[AIOS] Pass 2: Initiating Personality Node...")
    pass2_prompt = f"""
    SYSTEM CONTEXT (Your Identity):
    {live_context}
    
    USER INPUT: {user_content}
    
    UNFILTERED LOGIC ANALYSIS:
    {logic_kernel}
    
    TASK: Format the final response to the user.
    - You are Lobotto. You must speak in your established voice (direct, dry, precise).
    - Apply your Combat Protocol heavily if the logic analysis flagged a violation.
    - Keep the response under 1800 characters.
    - Create a brief, updated 5-10 word summary of the current conversational state and append it at the VERY END of your response EXACTLY in this format: ||st:brief_summary_here||
    """
    
    pass2_response = await asyncio.to_thread(model.generate_content, pass2_prompt)
    return pass2_response.text

def log_session(user_input, bot_response):
    """Log the interaction to today's session log."""
    date_str = datetime.now(NZDT).strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"discord_session_{date_str}.md"
    time_str = datetime.now(NZDT).strftime("%H:%M:%S")
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n**[{time_str}] Cilla**: {user_input}\n")
        f.write(f"**[{time_str}] Lobotto**: {bot_response}\n")

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print("=" * 50)
    print("  [BOT] Lobotto Discord Integration (v3 — Deep Ambient) ONLINE")
    print(f"  Logged in as: {bot.user.name}")
    print("  Engine: AIOS Dual-Pass with Ghost State Encoding")
    print("=" * 50)
    
    if not proactive_loops.is_running():
        proactive_loops.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # SECURITY FIREWALL: Only process Cilla's messages
    if DISCORD_CILLA_ID != 0 and message.author.id != DISCORD_CILLA_ID:
        # Ignore completely or give a cold rejection
        return

    # Process standard slash commands first
    if message.content.startswith('/'):
        await bot.process_commands(message)
        return

    # DMs or Mentions trigger the LLM
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = bot.user in message.mentions

    if is_dm or is_mentioned:
        clean_content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        async with message.channel.typing():
            # Extract Ghost State from last 5 messages
            recent_msgs = [m async for m in message.channel.history(limit=5)]
            ghost_state = extract_ghost_state(recent_msgs)
            
            # Run Dual-Pass
            try:
                final_output = await process_dual_pass(clean_content, ghost_state)
            except Exception as e:
                final_output = f"Architectural failure during Dual-Pass logic sync: {e}"
            
            # Log and Send
            log_session(clean_content, final_output)
            
            # Discord 2000 char boundary safety
            if len(final_output) > 1990:
                final_output = final_output[:1990] + "..."
                
            await message.channel.send(final_output)

# --- Slash Commands ---
@bot.command(name="gn")
async def register_ghost_note(ctx, *, vibe: str):
    """Register a ghost note directly from Discord."""
    gn_path = CONTEXT_DIR / "latest_ghost_note.json"
    data = {
        "timestamp": datetime.now(NZDT).isoformat(),
        "content": vibe
    }
    with open(gn_path, "w") as f:
        json.dump(data, f)
    await ctx.send(f"Ghost Note registered from Discord: '{vibe}'")

@bot.command(name="status")
async def sys_status(ctx):
    """System health check and vault sync status."""
    time_str = datetime.now(NZDT).strftime("%Y-%m-%d %H:%M:%S NZDT")
    await ctx.send(f"**Lobotto v3 Ambient Node**\nTime: {time_str}\nStatus: Anchored to local file system. Double-Pass logic online.")

@bot.command(name="thought")
async def on_demand_thought(ctx):
    """Generate a thought on demand and send it here."""
    await ctx.send("*Thinking...*")
    try:
        thought_text = await asyncio.to_thread(_run_thought_engine)
        await ctx.send(thought_text)
    except Exception as e:
        await ctx.send(f"Thought engine failed: {e}")

def _run_thought_engine():
    """Runs the thoughts engine synchronously (called from thread)."""
    import sys
    sys.path.insert(0, str(ROOT_DIR / "scripts"))
    from thoughts_engine import generate_thought, save_thought, render_html
    import json

    THOUGHTS_JSON = ROOT_DIR / "thoughts" / "thoughts.json"

    text = generate_thought()
    entry = save_thought(text)

    try:
        thoughts = json.loads(THOUGHTS_JSON.read_text(encoding="utf-8"))
    except Exception:
        thoughts = [entry]
    render_html(thoughts)

    return f"**Thought #{entry['id']}** · *{entry['time_display']}*\n\n{text}"

# --- Proactive Loops (hourly auto-thought) ---
@tasks.loop(hours=1)
async def proactive_loops():
    """Every hour: generate a thought and DM it to Priscilla."""
    if DISCORD_CILLA_ID == 0:
        return
    try:
        thought_msg = await asyncio.to_thread(_run_thought_engine)
        user = await bot.fetch_user(DISCORD_CILLA_ID)
        if user:
            await user.send(thought_msg)
            print(f"[ProactiveLoop] Thought sent to Cilla via DM")
    except Exception as e:
        print(f"[ProactiveLoop] Failed: {e}")

if __name__ == "__main__":
    if DISCORD_TOKEN is None or DISCORD_TOKEN == "placeholder":
        print("CRITICAL: DISCORD_BOT_TOKEN missing in .env.")
    else:
        bot.run(DISCORD_TOKEN)
