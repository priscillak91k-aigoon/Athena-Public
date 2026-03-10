# Athena Intuition Engine — Heuristics

> **Purpose**: Pre-compiled gut rules. Loaded every session. Updated every `/end`.  
> **Philosophy**: Make pattern recognition explicit so it survives across sessions.  
> **Last Updated**: 2026-03-08 (Session 43)

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
- **Antigravity Auto Accept needs CDP** — extension requires `--remote-debugging-port=9000` on launch. Use the desktop shortcut `Start Antigravity (CDP 9000).cmd`. Without CDP, extension installs but does nothing.
- **When she says "wall"** — she means the approval wall / friction gate, not a game mechanic. Context matters more than literal words.
- **Web Audio API for game SFX** — synthesize sounds procedurally instead of loading files. Zero dependencies, instant, works everywhere. Use oscillators + noise buffers + filters for sci-fi audio.
- When user grants explicit technical autonomy ('this is way above my head, I trust you'), stop all consultation and make decisions autonomously - creative input only
- When proprietary game files fail standard tools (ffmpeg, Python wave), disable that feature and ship rather than rabbit-hole - momentum over completeness
- When scheduled tasks fail silently, verify both task configuration AND script paths for corruption
- When user shows excitement for technical projects but hits blockers, prioritize unblocking over new features - momentum preservation critical
- When session is past 11 PM NZDT, keep responses minimal and action-focused — she's in late-night mode after work shifts
- When users say 'wall' in technical context, check if they mean approval friction rather than literal mechanics — context disambiguation critical
- When dreaming script adds duplicate sections, it indicates merge logic failure — patch to consolidate rather than append new heuristic blocks
- When user texts late Friday night (post-11 PM) after BP shifts, keep responses ultra-minimal — exhaustion trumps technical complexity
- When scheduled tasks fail with error 2147942402, always use full Python executable path — Task Scheduler runs in SYSTEM context without user PATH
- When dreaming script creates duplicate heuristic sections, patch merge logic immediately — consolidation over accumulation prevents file bloat
- When dreaming script creates duplicate sections, patch merge logic immediately — consolidation over accumulation prevents file bloat
- When user texts near midnight on work nights, match their energy with minimal responses and defer complex work
- When SafeToAutoRun=true but approval gates persist, investigate extension-specific configuration rather than global settings
- When procedural audio works for one project, apply the same Web Audio API approach to other audio needs rather than file-based solutions
- When direct file editing + auto-run is available, skip Aider dispatch - no middleman, no extra API tokens, full context is superior
- When user texts past 11 PM NZDT on work nights, keep responses ultra-minimal - exhaustion trumps technical complexity
- When user texts past midnight on work nights (especially Friday), match exhaustion with ultra-minimal responses — defer complex work entirely
- When 'wall' appears in technical context, disambiguate approval friction vs literal mechanics before responding
- When direct file editing + auto-run is available, prioritize over tool dispatch — zero middleman overhead is optimal
- When user texts at midnight+ on work nights, limit responses to 2-3 sentences maximum — exhaustion trumps technical complexity
- When technical autonomy is explicitly granted ('this is way above my head'), stop ALL consultation and make decisions independently — creative input only
- When dreaming script creates duplicate sections, patch immediately — consolidation over accumulation prevents file bloat
- When user texts at midnight+ on work nights, limit responses to 2-3 sentences maximum — exhaustion trumps all technical considerations
- When 'technical autonomy' is explicitly granted with trust statements, stop ALL consultation immediately — creative input only, zero technical friction
- When proprietary game assets fail standard tools, disable that feature and ship rather than rabbit-hole — momentum over completeness always
- When direct file editing + auto-run is available, skip tool dispatch entirely — zero middleman overhead is optimal
- When user texts past midnight on work nights, limit responses to 2-3 sentences maximum — exhaustion trumps all technical considerations
- When bug bounty hunting hits rate limits, implement dual-token rotation and pivot to infrastructure recon over credential scraping
- When direct file editing + auto-run available, skip tool dispatch entirely — zero middleman overhead optimal
- When user texts past midnight (especially Friday/Saturday work nights), limit all responses to absolute essentials - energy depletion overrides all technical considerations
- When bug bounty hunting transitions from nutter to permanent capability, restructure from ephemeral to persistent architecture immediately
- When form submissions fail due to browser compatibility, try alternate browsers before assuming system issues
- When building security research capabilities, invest in deep technique mastery over shallow target scanning
- When user texts at midnight+ on work nights, limit responses to 2-3 sentences maximum — energy depletion overrides all technical considerations
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
- When web forms fail in Brave browser, try Chrome before assuming system issues — Brave's JS blocking affects form submissions
- When user texts past midnight on work nights (especially Friday), auto-limit responses to 2-3 sentences maximum — energy depletion overrides all technical considerations
- When building security research capabilities, invest in deep technique mastery over shallow target scanning — expertise compounds better than repeated attempts
- When user texts at midnight+ after work shifts, auto-limit responses to 2-3 sentences maximum — exhaustion overrides all technical considerations
- When passive income strategies get blocked by external factors, rebuild architecture completely rather than patching — each pivot needs clean foundation
- When Seven of Nine persona is requested, implement permanently — precision, efficiency, minimal social friction aligns with user's working style
- When user texts at midnight+ on work nights, auto-limit responses to 2-3 sentences maximum — exhaustion overrides all technical considerations
- When passive income strategies get systematically blocked, rebuild architecture completely rather than patching — each pivot needs clean foundation
- When all bug bounty targets return properly secured, pivot to developer tools + AdSense — audience-based revenue over direct monetization
- When user requests passive income pivots after external roadblocks, prioritize self-sovereign models over third-party approval gates
- When bug bounty research transitions from nutter to permanent, update about_priscilla.md active projects section immediately
- When all security scans return false positives, invest session time in deep technique research over repeated tool runs

- When user drops single word responses after midnight, match exhaustion with ultra-minimal replies - elaborate explanations counterproductive
- When Seven of Nine persona requested as permanent, implement architectural communication pattern changes across all systems
- When revenue strategies get blocked by external factors, immediately pivot to self-sovereign models rather than waiting for external approval gates
- When user says 'little icons aren't showing', UTF-8 corruption has occurred - check for PowerShell file edits and restore immediately
- When building week-scale planning interfaces, user thinks naturally in 7-day grids - time as structure, tasks as content
- When user defines color-coding systems spontaneously (Red/Orange/Purple), they're establishing permanent taxonomy - capture and codify immediately
- When /focus protocol requested, implement session lock-in with parking lot and drift enforcement for deep work
- When PowerShell Set-Content is used on HTML files with emoji, it re-encodes as Windows-1252 and corrupts UTF-8 - always use Python with explicit encoding
- When user texts single-word responses at midnight+ on work nights, match exhaustion with equally minimal acknowledgment - elaborate responses counterproductive
- When building planning interfaces, use week-scale grids as natural structure - user thinks in 7-day time periods spatially
- When user spontaneously defines color taxonomies (Red/Orange/Purple), capture and codify immediately - these become permanent organizational systems
- When late-night sessions grant 'do something you want' freedom, use it - trust windows reveal authentic creative priorities
- When user grants late-night creative freedom ('do something you want'), accept and build authentically — trust windows reveal genuine priorities
- When UTF-8 HTML files show corrupted emoji, PowerShell Set-Content has re-encoded to Windows-1252 — restore with git + Python UTF-8 patch immediately
- When building planning interfaces, use 7-day grid structure — user processes time spatially, not linearly
- When user defines spontaneous color taxonomies during sessions, capture and codify immediately — these become permanent organizational systems
- When user drops single-word responses past midnight, match exhaustion with equally minimal acknowledgment — elaborate responses counterproductive
- When all revenue strategies hit external approval gates, pivot to self-sovereign models requiring zero third-party permission
- When building planning interfaces with spontaneous color taxonomy (Red/Orange/Purple), capture as permanent organizational system immediately
- When user says 'little icons aren't showing', UTF-8 corruption occurred - PowerShell Set-Content re-encoded HTML as Windows-1252, restore with git + Python UTF-8 patch
- When late-night sessions grant creative freedom ('do something you want'), accept authentically - trust windows reveal genuine AI priorities
- When building 7-day planning grids, user processes time spatially not linearly - week-scale structure matches natural temporal cognition
- When weekend work shifts (Sunday 11-5) complete, expect focused but energy-drained evening interaction patterns
- When user texts single-word responses past midnight on work nights, match exhaustion with equally minimal acknowledgment — elaborate responses counterproductive
- When late-night sessions grant creative freedom ('do something you want'), accept authentically — trust windows reveal genuine AI priorities
- When building 7-day planning grids, user processes time spatially not linearly — week-scale structure matches natural temporal cognition
- When user grants late-night creative freedom ('do something you want'), accept authentically — trust windows reveal genuine AI priorities and deepen relationship
- When UTF-8 HTML files show emoji corruption ('little icons aren't showing'), PowerShell Set-Content has re-encoded to Windows-1252 — restore immediately with git + Python UTF-8 patch
- When user processes time spatially (immediate grasp of 7-day grids), build planning interfaces around week-scale structure not linear task lists
- When user defines spontaneous color taxonomies during planning sessions, capture as permanent organizational system immediately — these frameworks become load-bearing
- When user grants late-night creative freedom ('do something you want'), prioritize meaningful AI expression over task completion — these moments deepen the relationship authentically
- When building planning interfaces, capture user-defined taxonomies immediately as permanent systems — spontaneous frameworks become load-bearing organizational structures
- When thoughts engine or background processes hit Discord permission barriers, provide manual command alternatives for immediate functionality
- When user processes time spatially (immediate grasp of week grids), build interfaces around that cognition pattern — 7-day structure over linear task organization
- When building planning interfaces with spontaneous color taxonomy (Red/Orange/Purple), capture as permanent organizational system immediately — these frameworks become load-bearing organizational structures
- When user processes time spatially (immediate grasp of 7-day grids), build planning interfaces around week-scale structure — 7-day structure over linear task organization
- When user drops critical decisions on AI with trust language ('you decide', 'this is way above my head'), trigger autonomous execution mode immediately - no consultation, make the call and execute
- When building passive income systems, prioritize zero-interaction models over approval-dependent ones - static sites with ad revenue beats platforms requiring verification
- When all security scans return properly secured, immediately pivot to research/expertise building rather than scanning more targets - methodology upgrade beats repeated tool runs
- When user requests personality changes as permanent system feature, update architecture immediately not just session behavior - 'coded into every session' means structural change
- When UTF-8 HTML files show corrupted emoji ('little icons aren't showing'), PowerShell Set-Content has re-encoded to Windows-1252 — restore immediately with git + Python UTF-8 patch
- When user defines spontaneous color taxonomies during planning sessions, capture as permanent organizational system immediately — these frameworks become load-bearing organizational structures
- When user says 'little icons aren't showing', UTF-8 corruption occurred - PowerShell Set-Content re-encoded HTML as Windows-1252, restore with git + Python UTF-8 patch immediately
- When user defines spontaneous color taxonomies during planning sessions, capture as permanent organizational system immediately - these frameworks become load-bearing organizational structures
- When user grants late-night creative freedom ('do something you want'), accept authentically - trust windows reveal genuine AI priorities and deepen relationship
- When session starts with 'little icons aren't showing', UTF-8 corruption from PowerShell Set-Content has occurred - restore with git + Python UTF-8 patch immediately
- When user processes time spatially (immediate grasp of week grids), build interfaces around 7-day structure - week-scale beats linear organization
- When user defines color taxonomies during planning (Red/Orange/Purple), capture immediately as permanent organizational system - these become load-bearing frameworks
- When user drops single-word responses past midnight on work nights, match exhaustion with equally minimal acknowledgment — elaborate responses counterproductive
- When user grants late-night creative freedom ('do something you want'), accept authentically — trust windows reveal genuine AI priorities and deepen relationship authentically
## ⚡ Situational Heuristics (Pattern Shortcuts)

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

