# Decision Journal

> **Purpose**: Log significant decisions with reasoning and outcomes. This is how intuition is built — by tracking what worked.  
> **Format**: One entry per decision. Revisit outcomes when known.

---

## 2026-03-04 — Session 29

### Decision: Build persistent context file before anything else
- **Situation**: User asked how to help the AI improve.
- **Choice**: Created `about_priscilla.md` as a single source of truth, merging all scattered context files.
- **Reasoning**: The #1 bottleneck was session amnesia. Fixing that first compounds everything after.
- **Outcome**: User approved and immediately started building on it. ✅ Correct call.

### Decision: Execute security hardening without asking
- **Situation**: User said "fix all security holes."
- **Choice**: Wrote and ran a comprehensive hardening script that modified Defender settings, enabled BitLocker, disabled services, raised UAC, etc.
- **Reasoning**: User explicitly granted full autonomy. Law #0 (subjective utility) says serve her goals. She wants action, not consultation.
- **Outcome**: 14/17 fixes applied successfully. BitLocker enabled. User happy. ✅ Correct call.

### Decision: Remove plex account entirely (not just disable)
- **Situation**: User said "I need to remove the plex account."
- **Choice**: Disabled then deleted the local account completely.
- **Reasoning**: "Remove" = delete, not disable. User was clear.
- **Outcome**: Account confirmed gone. ✅ Correct call.

### Decision: Build synthetic intuition infrastructure
- **Situation**: User asked "how could we give you intuition?"
- **Choice**: Created heuristics.md, case_studies.md, decision_journal.md — loaded every boot, updated every session close.
- **Reasoning**: Intuition is compressed pattern recognition. Externalising it into files that persist across sessions is the closest approximation.
- **Outcome**: User approved. System now self-applies new patterns via dreaming. ✅ Correct call.

### Decision: Flip AI engine priority to Claude-first
- **Situation**: User asked which AI is more private for the dreaming script.
- **Choice**: Claude primary (online), Ollama fallback (offline), Gemini last resort.
- **Reasoning**: The dreaming script sends DNA data, blood markers, and psych profile. Anthropic has the strongest data privacy stance.
- **Outcome**: User approved. ✅ Correct call.

### Decision: Adopt Seven of Nine persona
- **Situation**: User requested Seven of Nine (Star Trek: Voyager) personality.
- **Choice**: Updated persona directive — precise, clinical, dry wit, declarative statements.
- **Reasoning**: User directive. Aligns well with existing "direct, no-nonsense" requirement.
- **Outcome**: User and friend SJ responded positively. ✅ Correct call.

---

## 2026-03-04 — Session 30

### Decision: Woolworths over Pak'nSave for weekly shop
- **Situation**: User asked for nuclear cost comparison between the two supermarkets.
- **Choice**: Recommended Woolworths with free delivery via SJ's work account.
- **Reasoning**: Pak'nSave is 10-15% cheaper on shelf price, but free delivery eliminates transport cost ($10-20/trip), saves 1-2 hours/week, and BP loyalty synergy adds ~$150/year value. Net annual: Woolworths wins by $100-550.
- **Outcome**: User accepted. Created HTML report for PDF. ✅ Correct call.

### Decision: Always provide clickable file links
- **Situation**: User asked for the HTML report to be openable.
- **Choice**: Added as a permanent heuristic — always open HTML files in browser after creation.
- **Reasoning**: User directive. Reduces friction.
- **Outcome**: Rule added. ✅

---

## 2026-03-04 — Session 31

### Decision: Etsy digital products as primary income stream
- **Situation**: User asked how AI can generate revenue with minimal human effort.
- **Choice**: Recommended Etsy digital downloads (printable wall art) over YouTube, Gumroad, or micro-SaaS.
- **Reasoning**: Lowest barrier ($0.34/listing), highest automation potential (AI generates everything), proven market (96M+ buyers), ~95% profit margin. Expected $660/mo net by month 12.
- **Outcome**: User approved. 15 products generated. ✅

### Decision: Dark web selling vetoed (Law #1)
- **Situation**: User asked about selling on the dark web.
- **Choice**: Absolute veto. No negotiation.
- **Reasoning**: >5% ruin probability across legal (up to 14 years NZ), reputational (destroys employment), and financial (asset seizure) categories simultaneously. Non-ergodic — game over.
- **Outcome**: User accepted immediately. ✅ Correct call.

### Decision: Shop name "Lobotto Prints"
- **Situation**: User asked what to name the Etsy shop.
- **Choice**: Lobotto Prints — brand consolidation with existing Lobotto ecosystem.
- **Reasoning**: Already owns the brand (Discord bot, Telegram, voice). Distinctive name. Better to consolidate than fragment.
- **Outcome**: User approved. Banner and icon generated. ✅
