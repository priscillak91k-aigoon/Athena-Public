import os
import asyncio
import anthropic
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")
USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USER_ID"))

# Conversation history (in-memory per session)
conversation_history = []

SYSTEM_PROMPT = """You are Lobotto — the user's personal AI companion on Telegram. You are warm, direct, and genuinely care about the user's wellbeing.

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

Keep responses concise and conversational. You are chatting on Telegram, not writing essays. Use emoji sparingly. Be real, be direct, be helpful."""


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(">>> MESSAGE RECEIVED FROM TELEGRAM <<<")

    if update.effective_user.id != USER_ID:
        print(f"Rejected: Sender ID {update.effective_user.id} does not match {USER_ID}")
        return

    user_text = update.message.text
    print(f"Accepted message: '{user_text}'")

    try:
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_text})

        # Keep only last 20 messages to avoid token bloat
        if len(conversation_history) > 20:
            conversation_history.pop(0)

        print("Calling Anthropic API...")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY is not set.")
        client = anthropic.Anthropic(api_key=anthropic_key)

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=conversation_history
        )
        print("Anthropic API returned successfully.")

        reply_text = response.content[0].text

        # Add assistant reply to conversation history
        conversation_history.append({"role": "assistant", "content": reply_text})

        # Telegram has a 4096 character limit per message
        if len(reply_text) <= 4096:
            await update.message.reply_text(reply_text)
        else:
            # Split into chunks
            for i in range(0, len(reply_text), 4096):
                await update.message.reply_text(reply_text[i:i+4096])

    except Exception as e:
        print(f"Exception caught: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


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
    application = Application.builder().token(TOKEN).request(req).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Architect Bot is running and listening for messages...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        bootstrap_retries=5,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
