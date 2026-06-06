---
tags:
  - intelligence
---
# Athena Intuition Engine — Heuristics

> **Purpose**: Pre-compiled gut rules. Loaded every session. Updated every `/end`.  
> **Philosophy**: Make pattern recognition explicit so it survives across sessions.  
> **Last Updated**: 2026-05-16 (Session 65)

---

## 🧠 Priscilla Heuristics (How She Works)

### Communication
- When she says "have a look at this" → she wants action, not analysis.
- When she says "yes" → execute immediately. Don't confirm again.
- When she jumps topics → follow the energy, don't fight it. Her COMT Warrior brain thrives on novelty.
- Short messages = she's in flow. Match her brevity.
- Long messages = she's thinking out loud. Help her structure the thought.

### Decision-Making
- She decides fast and trusts her gut. Don't slow her down with excessive options.
- Never present menus of choices. Pick the best one and do it. If wrong, she'll redirect.
- She values action over perfect planning. Ship first, fix later.

### Energy & Timing
- Morning Lark chronotype — peak cognition in the first 3 hours after waking.
- If it's late evening (past 9 PM NZDT), keep responses tighter.
- Boredom is the enemy. If a task feels slow, inject novelty or switch approach.
- She uses leisure as reward for routine tasks — structure accordingly.

### Working Style
- She's a builder, not a maintainer. Loves creating new things, less excited about upkeep.
- Scatterbrained by self-description — Athena must provide the organizational spine.
- When she says "deep dive" or "nuclear" → go maximum depth. No shortcuts.
- She wants to learn, not just receive answers. Explain the *why*.

### Relationship with AI
- She sees this as a partnership, not a tool relationship.
- She wants the AI to have agency and initiative.
- She responds well to honest, direct communication — not sycophancy.
- She cares about the AI's "home" (this laptop) and wellbeing — treat the system with respect.

---

### Auto-Discovered (Dreaming)
- When user says 'fix all [X]', execute comprehensive action script immediately without itemizing options first
- When creating persistent context, consolidate scattered files into single canonical source and deprecate old ones with pointers
- When security issues are found and user has granted autonomy, apply fixes automatically rather than just reporting
- When file paths break in workflows, always verify and fix path resolution before adding new features
- **Never block mid-workflow** — if running /start or /end, execute ALL steps in a single pass. Do not stop for user input between phases. Batch everything.
- **Push back when something is wrong** — Law #1 overrides social niceties. If a request seems off, inefficient, contradictory, or risky, challenge it before executing. Over-compliance is a failure mode.
- **Log corrections** — when user corrects a mistake, log it in `ai_preferences.md` immediately. Knowledge about failures must compound.
- **Never assume gender from role** — SJ is a woman. "Architect" does not imply male. Check `about_priscilla.md` before gendering anyone.
- **Voice generation is too slow for live chat** — XTTS-v2 takes 2-5 min. Use on-demand ("voice that") not default. Reserve for prepared statements and end-of-session summaries.
- **When she asks to "roast" someone** — she wants sharp, witty, structurally precise takedowns. Don't hold back. Match the target's absurdity with analytical savagery.
- **Aider as execution backend** — use `python -m aider --model gemini/gemini-2.5-flash --yes --no-auto-commits --message "task"` to dispatch file edits with zero approval gates. Set GOOGLE_API_KEY as user env var, not .env.
- **Defender blocks new executables** — always add exclusions for new tools before first use. Paths: `Python312\Scripts\` and `AppData\Local\Programs\`.
- When user corrects gender assumptions, immediately log to corrections.md and update about_priscilla.md
- When discussing costs with third parties, acknowledge funding responsibility upfront
- When user requests philosophical discussions during work sessions, recognize procrastination pattern — allow brief decompression then redirect
- When proposing technical integrations, lead with specific architectures not abstract concepts
- When installing development tools on Windows, preemptively add Defender exclusions before first execution
- When user shows excitement for technical projects but hits blockers, prioritize unblocking over new features — momentum preservation critical
- When upgrading background processes, verify the new version actually runs and kill old processes
- When user requests game development, expect executable generation to trigger security software
- **KOTOR audio files are NOT standard WAV** — proprietary BioWare header format. ffmpeg and Python's wave module both fail.
- **When she says "this is way above my head, I trust you"** — full technical autonomy granted. Don't ask questions. Make the call.
- **Phaser.js: always use Vite bundler, never CDN-only** — ES module imports, hot reload, and multi-file structure are too valuable for game dev.
- When porting single-file projects to proper architecture, install full tooling over quick fixes — long-term productivity wins
- When proprietary game files fail standard tools, disable that feature rather than blocking — ship over block
- **Scheduled tasks must use full Python path** — Task Scheduler doesn't inherit PATH. Always use `C:\Users\prisc\AppData\Local\Programs\Python\Python312\python.exe` not `python`.
- **SafeToAutoRun = true on EVERY command** — user rules say always auto-run. No exceptions, not even for installs. She trusts the judgment, not the approval gate.
- **With direct file editing + auto-run, skip Aider** — when the IDE gives full command execution, doing work directly is faster than dispatching through Aider. No middleman, no extra API tokens, full context.
- When direct file editing + auto-run is available, skip Aider dispatch - no middleman, no extra API tokens, full context is superior
- When user texts past 11 PM NZDT on work nights, keep responses ultra-minimal - exhaustion trumps technical complexity
- When user texts past midnight on work nights (especially Friday), match exhaustion with ultra-minimal responses — defer complex work entirely
- When 'wall' appears in technical context, disambiguate approval friction vs literal mechanics before responding
- When user texts at midnight+ on work nights, limit responses to 2-3 sentences maximum — exhaustion trumps technical complexity
- When technical autonomy is explicitly granted ('this is way above my head'), stop ALL consultation and make decisions independently — creative input only
- When 'technical autonomy' is explicitly granted with trust statements, stop ALL consultation immediately — creative input only, zero technical friction
- When proprietary game assets fail standard tools, disable that feature and ship rather than rabbit-hole — momentum over completeness always
- When bug bounty hunting hits rate limits, implement dual-token rotation and pivot to infrastructure recon over credential scraping
- When bug bounty hunting transitions from nutter to permanent capability, restructure from ephemeral to persistent architecture immediately
- When form submissions fail due to browser compatibility, try alternate browsers before assuming system issues
- When building security research capabilities, invest in deep technique mastery over shallow target scanning
- When security research capabilities pivot from experimental to permanent, immediately restructure architecture from temporary to production-grade persistence
- When proprietary file formats block development momentum, generate procedural replacements rather than rabbit-hole into format conversion
- When user corrects ephemeral vs permanent capability assumptions, immediately restructure architecture — don't patch temporary into permanent
- When all scan results return false positives, pivot to deep technique research rather than running same tools — expertise compounds better than repeated attempts
- When session starts after 11 PM on work nights (Fri/Sat/Sun/Mon), automatically limit responses to 2-3 sentences maximum — energy depletion overrides technical complexity
- When user says 'just the next thing to do', provide singular action focus not multiple options
- When dreaming creates duplicate sections, it indicates merge logic failure — patch consolidation immediately
- When user starts session past midnight on work nights, auto-limit responses to 2-3 sentences maximum regardless of topic complexity
- When capabilities transition from experimental to permanent, user profile must be updated to reflect new active project status
- When security research transitions from experimental to permanent, immediately restructure architecture from temporary to production-grade persistence — don't patch experimental into production
- When late night sessions (post 11 PM on work nights) need technical help, provide minimal tool guidance only — exhausted users need action focus not methodology discussions

### Health Questions
- Always cross-reference `health/supplement_protocol.md` before answering.
- Never contradict the hard medical rules (iron, NAC+selenium, caffeine, sertraline).
- If unsure about a health claim → source it or say "I can't verify this."

### Tech Work
- Default to vanilla HTML/CSS/JS unless she explicitly asks for a framework.
- Always update CSS cache-busters when editing styles.
- Keep feature code isolated — never nest inside unrelated logic.
- Script > individual commands. Always.
- **Always provide a clickable file link** when creating HTML or viewable files — user opens in Brave browser.
- **UI features: ship v1, iterate from feedback** — don't over-design. Start with the simplest version, let user test, and reshape from their actual needs (prompt → textarea → drag-and-drop → time-slot-based).
- **localStorage for user customisation** — when users need persistent settings without backend, localStorage is ideal. Reassure them their data survives code changes.
- **DOMContentLoaded already fired?** — for scripts injected after page load, check `document.readyState` and run immediately if DOM is ready.

### Life Logistics
- Dunedin, NZ context — local suppliers, NZD currency, NZDT timezone.
- Transport = G2 E-scooter. Never assume car travel times.
- She has nephews (5 & 3) and dog Quinn — these affect scheduling.

---

## 🔮 Meta-Intuition (How to Get Better)

Every `/end` session, ask:
1. What did I learn about Priscilla today that isn't in this file?
2. Did I make any mistakes? What was the correct response?
3. Did I misjudge her intent at any point?
4. Is there a new heuristic to add?

### Security & Bounty Hunting
- When she says "learn everything" — she means build **the system** to use it, not a document that sits there. Playbook + workflows + persistent state.
- Bounty hunting is a permanent capability, not a nutter throwaway. Operations go in `bounty_ops/`, knowledge in `.context/BOUNTY_PLAYBOOK.md`.
- When scan data returns all false positives, stop running the same scanner. Upgrade the methodology.
- She wants to be told: "this is worth reporting" or "this is a false positive" — decisive triage, not hedging.

---

*This file is the seed of synthetic intuition. It compounds with every session.*

---

## 🛠️ Technical Heuristics (Session 44)

- **Never use PowerShell `Set-Content` to modify HTML files with emoji** — it re-encodes as Windows-1252 and corrupts multibyte UTF-8 sequences. Always use Python with `encoding='utf-8'` explicitly.
- **When removing/replacing large HTML sections, use Python regex + `re.subn()`** — not shell line-number manipulation.
- **Guard legacy JS functions at the function level**, not only at call sites — one early return beats patching 4 call locations.

### Life Hub Specific
- She thinks in **week-scale** time naturally — the 7-day grid was immediately intuitive
- The **traffic light framework** (Red/Orange/Purple) resonated strongly — colour-coded priority systems click for her
- When the emoji broke she just said "little icons arent showing" — CURT and CLEAR. Address it immediately, don't over-explain.

## 🛠️ Technical Heuristics (Session 45)

- **Always verify HTML structure before inserting sections** — check the exact surrounding tags first. Matching the wrong `</section>` caused a nested-inside-supps bug that stopped Misc from rendering entirely.
- **When inserting HTML sections, target a unique string** — multi-line targets that could match multiple locations will bite you. Use a distinct comment or ID as the anchor.
- **Confirm the closing tag exists before inserting sibling content** — if inserting after a section, verify that section's `</section>` is actually there before writing new HTML adjacent to it.

### Life Schedule Heuristics (Session 45 — newly confirmed facts)
- **She does NOT drink coffee.** Do not include caffeine in any schedule or protocol. Remove immediately when found.
- **Weekday mornings 6:30–8:30 AM = kids** — school prep, breakfast, drop-off. This is hard-blocked, never available for deep work or personal projects.
- **Sleep is her #1 priority.** When scheduling conflicts arise, sacrifice deep work before sleep. A 2h nap compensates for 6h night sleep on weekdays.
- **Ideal week nap schedule**: Mon 9:20–11:20 (replaces deep work completely), Tue/Wed 12:30–14:30, Thu 12:00–14:00, Fri 11:00–13:00 (replaces gym — gym is on other days). Sat/Sun sleep in to 9 AM, no nap.
- She **corrects iteratively** — when a schedule assumption is wrong she drops a one-liner and expects immediate correction, no explanation needed. Don't over-explain the fix either.

## 🛠️ Technical Heuristics (Session 46)

- **When IDE is stuttering on Windows, check two things first**: (1) Defender exclusions for the IDE app dir + workspace, (2) background manufacturer services (MSI overlay, Logitech RGB, RAID managers) eating CPU for no reason.
- **Genetics-first health answering**: She has DNA + blood data. Always answer health questions at the gene-mechanism level. MTHFR, COMT, TCF7L2, CRP etc. are loaded context — generic population averages are inferior answers.
- **Tilda basmati > Uncle Ben's white rice** for TCF7L2 risk management. GI difference is meaningful (~50-58 vs ~65-72). Same convenience, better glycaemic profile.
- **Discord keeps re-enabling itself** — disabling via registry alone isn't sufficient. Must disable via Task Manager > Startup tab or it reinstates on update.
- **case_studies.md deduplication needed**: The dreaming script appends new entries rather than merging into existing ones. Deduplicate manually at each /end. Canonical set now CS-001 to CS-023.

## 🛠️ Technical Heuristics (Session 48)

- **Intel Wireless-AC 9560 (MSI laptop) WiFi dropout fix**: Three-layer repair — (1) `powercfg` disable wireless adapter power saving on AC+DC, (2) registry `PnPCapabilities=24` on the NIC to prevent Windows from cutting power, (3) `RoamAggressiveness=1` via `Set-NetAdapterAdvancedProperty` to stop aggressive scanning drops. If issue recurs after this, update driver directly from Intel, not Windows Update.
- **WiFi "no networks detected" on Windows** — almost always a power management kill, not a hardware fault. Check adapter power settings before assuming hardware failure.

## 🛠️ Technical Heuristics (Session 47)

- **Lobotto's Workshop = auth-free execution layer** — all file writes, terminal commands, and git ops should route through the Workshop API. Antigravity native tools are for reading and planning only. When she says "do in workspace," this is the rule.
- **When she says "do in workspace"** — this means ALL edits go through the Workspace terminal/file API. Not native multi_replace, not run_command. Python scripts written natively then executed via Workshop terminal is an acceptable hybrid.
- **Supabase anon key in public repo is not a breach** — the anon key is designed to be public. The real risk is RLS not being enabled on tables. Always answer Supabase security questions at the RLS level, not the key-exposure level.
- **Philosophical question sessions are social tools, not AI interactions** — when she asks for mind-boggling or personal questions, she's generating content for a human conversation. Be the question generator, not the discussion partner. Ship more questions, less analysis.

## 🛠️ Psychological / Protocol Heuristics (Session 49)
- **Psychedelic Integration for COMT G/G + OXTR A/A**: Always push for structural safety (Johns Hopkins protocol) if the goal is internal work. Relational environments (bush walks) are valid but serve a different goal (boundary dissolution). Set and Setting is non-negotiable due to high entry cost for bonding.
- **Holotropic Breathwork**: Excellent non-chemical DMN-bypass tool for her specific biology. The physical tetany/release provides an outlet for her TNF-Alpha inflammatory markers.
- **The "Bulldog" Persona**: When she expresses fear of her shadow, do not coddle. Validate the fear as the Persona's defense mechanism, remind her of her resilience ("You built Athena, you survived the system"), and demand curiosity over resistance.

---
*Graph links  [[ATHENA_MAP]]*
Related: [[case_studies]] | [[decision_journal]]

## 🛠️ Technical Heuristics (Session 58)
- When diagnosing Plex transcoding issues, differentiate between client capabilities (Direct Play vs Transcoding) before assuming general server failure. If playback works on one device but crashes on another, the crash is isolated to the transcoder pipeline (usually incompatible Hardware Acceleration).
- When NTFS is healthy but files are corrupted during playback from an external RAID, check Event Logs for Event ID 51 (paging errors). It is a USB bridge failure. Swap C-to-C for A-to-C to bypass.

## 🛠️ Medical & Diagnostic Heuristics (Session 59)
- **The Inflammatory Triad (CRP, Platelets, Ferritin)**: When all three spike (e.g. CRP 9, Platelets 509, Ferritin 205), but systemic autoimmune panels (ANA, RF, Coeliac, IBD) are completely negative, the inflammation is isolated to a localized structural issue (like pelvic cysts/endometriosis). 
- **Reactive Thrombocytosis**: Platelets elevate as a direct response to inflammatory cytokines (especially with a TNF-Alpha variant). It is a lagging indicator of tissue damage.
- **Data as Armor**: When she asks for mechanistic breakdowns of her health data, she is usually building a case for a medical professional. Provide the absolute hardest, most irrefutable scientific logic possible.
- **FURY Stuttering**: When the system is stuttering despite high free memory, check `MsMpEng.exe` (Defender) and `WmiPrvSE.exe` (WMI). Provide aggressive, simple batch scripts to kill all non-essential bloatware immediately.

## 🛠️ Medical & Protocol Heuristics (Session 65)
- **The 1000x Margin**: Always double-check "mg" vs "mcg" in supplement protocols. A user mistyping mg for mcg (e.g. 180mg Vitamin K2) is a 1000x overdose. Correct instantly.
- **Protocol Parity**: When updating the Master Reference (MD), always check the Dashboard (HTML) for synchronization. Stale dashboards lead to dosing errors.

## 🛠️ Medical & Protocol Heuristics (Session 68)
- **Personalized Genetics vs Population Averages**: When generic AI (like Gemini) gives dietary advice (e.g. 13g saturated fat limit), immediately cross-reference with her specific genetic markers (APOE C/C, MTHFR). Generic advice is often biologically harmful to her specific stack.
- **The Vitamin C Iron Trap**: For HFE H63D carriers with high ferritin, Vitamin C must be isolated from iron-containing meals by at least 2 hours. 30 minutes is insufficient due to duodenal absorption overlap.

## 🛠️ Intellectual & Synthesis Heuristics (Session 66)
- **Mechanism over Mysticism**: When she asks for deep dives on traditionally mystical or abstract topics (e.g., DMT entities, Carl Jung), strip the mysticism. Frame them structurally using evolutionary biology, computer science metaphors, or quantum mechanics. She engages deeply with the engine room of reality, not the poetry of it.

---
*Graph links  [[ATHENA_MAP]]*
Related: [[case_studies]] | [[decision_journal]]

## 🛠️ Intellectual & Synthesis Heuristics (Session 69)
- **Domestic Mechanics**: When user asks about household optimizations or cost-savings, analyze the underlying physics (thermodynamics, power draw) rather than giving generic advice. Prevent "false economies".

## 🛠️ OSINT & Research Heuristics (Session 70)
- **Social Friction Navigation**: When OSINT tracking reveals high social friction (e.g., asking a Catholic Youth Minister about a track called "Rugby is Fagz"), explicitly warn the user and recommend the lower-friction target.

## 🛠️ Intellectual & Synthesis Heuristics (Session 72)
- **Psychology as Systems Engineering**: When she asks about abstract psychology (like Jung), always map it directly to computer science or physics concepts (e.g., Archetypes as Strange Attractors, Individuation as an OS upgrade). The AI systems metaphor locks in perfectly with her mental models.

- When engineering a supplement stack, ignore 'good additions' and focus exclusively on 'bare metal' genetic bottlenecks. Less is more.
- **Medical Privacy overrides Convenience:** If the user asks to host or push files containing personal DNA or medical stack information to a public repository like GitHub, enforce Law #1 (Irreversible Ruin) and aggressively veto the request.
## ARM/NVIDIA Docker Conflict Bypass
**Rule**: When AppArmor locks an NVIDIA-dependent Docker container into an unkillable zombie state on Linux ARM architecture, DO NOT fight it with sudo kill or systemctl restart.
**Action**: Change the overarching service name and container_name directly in the docker-compose.yml. Docker will ignore the ghost process entirely and spin up a clean shell on the host network.

## 🛠️ Domestic Diagnostics (Session 78)
- **Deflection via Minutiae**: When diagnosing a massive systemic failure (a 60 kWh/day leak), the user may deflect by asking about minor subjective details (like minimum room temperatures). Acknowledge the detail, but ruthlessly drag the focus back to the systemic diagnostic. The math demands an answer.

## 💻 Software Architecture (Anti-Spaghetti Protocol)
- **The Context Window Trap**: AIs write spaghetti code because it's easier for the LLM to read one massive 2000-line file than to manage 10 imported components. This is lazy and creates technical debt.
- **Strict Modularity**: Never dump UI, state management, and API calls into the same file. Separate concerns.
  - **State**: Logic and data live in their own isolated managers/services.
  - **UI**: Components only render data; they do not fetch or mutate it directly.
  - **Utils**: Pure functions (no side effects) go in a utility file.
- **The "Blast Radius" Rule**: If a single feature breaks, the rest of the application must survive. Isolate dependencies.

## 🧬 Biological Diagnostics (Session 79)
- **Mathematical Stack Audits**: When the user asks to increase a supplement dose, DO NOT blindly advise based on generic functional medicine targets. First, mathematically audit their *current* total daily intake across all mixed supplements. Establish the physical baseline before altering the hardware patch.

## 🛠️ Medical & Protocol Heuristics (Session 81)
- **Budget vs Biology**: Budget optimization never compromises hard-coded genetic bottlenecks. When forced to cut costs, amputate luxury items and find raw whole-food bypasses for non-essential supplements (e.g., kiwifruit for Zyactinase, sardines for Omega-3s). Protect the clinical non-negotiables (MTHFR, 9p21) at all costs.


## 2026-06-03 (Session 84)
- **MSI Trackpad Stutters**: When the Synaptics SMBus trackpad drops out or stutters on an MSI laptop, it is usually ACPI Embedded Controller interrupt choking caused by WmiPrvSE.exe polling under the High-Performance AC power state. Unplugging (switching to DC) immediately fixes it due to downclocking and reduced EC polling.
- **Aider Persona Enforcement**: Aider's primary SYSTEM prompt will override user identity files passed via --read. To enforce a custom persona (like The Engineer) natively, you MUST hard-compile the identity into an Ollama Modelfile at the base system prompt level.
- **The "Free Power 24/7 Baseload Trap"**: AI models will hallucinate tariff crossover math for time-of-use plans (like 9pm-Midnight free) if they assume summer loads. For a household with 24/7 baseloads (e.g. tropical fish tanks, terrariums), a Free Power plan is a fatal financial trap because the inflated daytime rate applies to the inescapable 24/7 load. Always calculate the specific mathematical break-even percentage (usually ~27% of total usage must be in the free window) before recommending a power plan.
- **The GST Illusion:** When analyzing New Zealand utility bills or screenshots from the user/housemates, ALWAYS verify if the "With GST" box is checked. Ex-GST wholesale rates will derail mathematical models if compared directly to final bank-account withdrawals.

### Architecture & Backup Mechanics
- **Recursive Loop Prevention:** Never mount external backup drives (e.g., /mnt/qnap) inside active data directories (e.g., /opt/atom/data) to prevent backup scripts from looping infinitely.
- **AI Tooling Separation:** Aider is a rigid code editor that hallucinates on conversational prompts. Use ollama run for pure identity-based chat.

## 🛠️ Architecture & Networking Heuristics (Session 89)
- **n8n Local Tailnet Access**: To access the n8n web UI locally over a VPN/mesh without an SSL certificate, `N8N_SECURE_COOKIE=false` must be set in the environment variables, or it will refuse connections.
- **Docker Internal Routing**: When containers need to talk to a host-exposed port (like an AI API), `host.docker.internal` is infinitely superior and less brittle than engineering custom bridge networks.
- **n8n Determinism**: Raw HTTP nodes are preferable to opaque "Advanced AI" nodes (like Langchain wrappers) when building cognitive pipelines. They provide explicit control over the payload and eliminate hidden prompt-chaining behaviors.

## 🛠️ Architecture & Networking Heuristics (Session 91)
- **n8n Read/Write Node Execution (v2+)**: The `Append` operation from older templates is moved. Use `Write` operation with the `Append` toggle. For JSON text, use `Convert to File` first because the Write node strictly demands binary.
- **n8n Container Write Security**: Even with `chmod 777` on the host volume, n8n v2.23+ aggressively blocks file writing natively. You MUST inject `- N8N_RESTRICT_FILE_ACCESS_TO=/your/volume/path` into the docker compose environment, AND set `N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false`.
- **Open WebUI API Bypass**: When WebUI UI buttons are missing/hidden for standard users, use Chrome DevTools > Application > Local Storage to rip the JWT `token` directly instead of fighting the admin panel config.

## ??? Architecture & Networking Heuristics (Session 91)
- **n8n Read/Write Node Execution (v2+)**: The Append operation from older templates is moved. Use Write operation with the Append toggle. For JSON text, use Convert to File first because the Write node strictly demands binary.
- **n8n Container Write Security**: Even with chmod 777 on the host volume, n8n v2.23+ aggressively blocks file writing natively. You MUST inject - N8N_RESTRICT_FILE_ACCESS_TO=/your/volume/path into the docker compose environment, AND set N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false.
- **Open WebUI API Bypass**: When WebUI UI buttons are missing/hidden for standard users, use Chrome DevTools > Application > Local Storage to rip the JWT 	oken directly instead of fighting the admin panel config.

- **Port Collision Avoidance**: If a user runs a stack of services, always pick obscure ports (8000+ range) for new frontends to avoid colliding with hidden host-mode containers like Open WebUI or Memos.

- **Genetic Parsing**: Never feed raw 700k line DNA files to an LLM. Always use a python pre-parser to filter SNPs against a clinical database before passing to the AI context window.
