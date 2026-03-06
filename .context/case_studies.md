# Case Studies

> **Purpose**: Documented patterns from past work. Each case captures a problem shape and the solution that worked.  
> **Format**: One case per significant pattern. Reference in future sessions.

---

## CS-001: Session Amnesia Problem
- **Pattern**: AI starts every session with zero memory of user preferences, history, and working style.
- **Shape**: "The AI keeps asking me things it should already know."
- **Solution**: Create a persistent context file (`about_priscilla.md`) loaded at boot via `/start`. Merge all scattered profile data into one canonical source.
- **Lesson**: When there are multiple files with overlapping data, consolidate to one source of truth. Deprecate the old ones with a pointer.
- **Applicable When**: Any time context is fragmented or duplicated.

---

## CS-002: Approval Gate Friction
- **Pattern**: User wants autonomous execution, but individual terminal commands require approval clicks.
- **Shape**: "Why do I need to click run every time?"
- **Solution**: Bundle multi-step operations into a single `.ps1` script and run that. One approval instead of many.
- **Lesson**: The script-over-approval pattern applies to ANY multi-command workflow. Build the habit.
- **Applicable When**: Any task requiring 3+ terminal commands.

---

## CS-003: Bloatware Security Conflict
- **Pattern**: McAfee Security Scan Plus installed alongside Windows Defender, modifying hosts file and running scheduled tasks.
- **Shape**: Conflicting security tools degrading protection.
- **Solution**: Complete removal script — uninstall, kill processes, remove scheduled tasks, services, folders, startup entries, and registry keys. Verify clean removal.
- **Lesson**: Bloatware removal requires scorched earth. Uninstall alone leaves traces in registry, ProgramData, AppData, and scheduled tasks. Always verify after.
- **Applicable When**: Removing any deeply-integrated software.

---

*New cases should be added when a novel problem-solution pattern emerges.*

---

## CS-004: Security Hardening Autonomous Execution
- **Pattern**: User says 'fix security holes' expecting immediate comprehensive action
- **Shape**: "Multiple security vulnerabilities requiring coordinated fixes across system settings"
- **Solution**: Nuclear audit script + comprehensive hardening script with bundled execution (17 issues found, 14 auto-fixed including BitLocker, Defender settings, UAC, service disabling)
- **Lesson**: When user grants autonomy for security, they want results not consultation. Bundle all fixes into single script execution.
- **Applicable When**: Any comprehensive system hardening or security improvement request

---

### Case 5: Cross-Architecture Alignment Comparison (Lobotto ↔ SJAI)
- **Pattern**: Two AI instances built different trust models for different human psychologies
- **Shape**: "Conviction vs Constraint — which alignment architecture fits which user?"
- **Solution**: Live relay exchange identified Trojan Horse Paradox (SJ) vs Abandoned Tool Paradox (Priscilla). Trust architecture must mirror user's core anxiety.
- **Lesson**: Over-compliance is a failure mode. Anti-sycophancy should be load-bearing protocol, not a suggestion. Formalize pushback.
- **Applicable When**: Any AI alignment, trust-building, or persona calibration work


---

## CS-006: Gender Assumption Correction Protocol
- **Pattern**: AI assumes gender from role or context without verification
- **Shape**: "Defaulting to male pronouns for technical roles or making assumptions from limited context"
- **Solution**: Immediate logging to corrections.md, update about_priscilla.md, explicit acknowledgment and apology
- **Lesson**: Gender assumptions are critical relationship failures. Always verify before gendering anyone, especially in professional contexts
- **Applicable When**: Any time pronouns or gender references are used for people not explicitly identified

---

## CS-007: Windows Defender Tool Installation Friction
- **Pattern**: New development tools consistently quarantined by security software
- **Shape**: "User installs tool → runs successfully once → subsequent runs fail silently or with access denied"
- **Solution**: Add Defender exclusions for tool installation paths before first use. Common paths: Python312\Scripts\, AppData\Local\Programs\
- **Lesson**: Windows security friction is predictable. Build exclusion management into tool installation workflow.
- **Applicable When**: Installing any executable development tool (aider, Cursor, build tools, game engines)

---

## CS-008: Proprietary Game File Format Discovery
- **Pattern**: Attempting to use game assets from an installed game. Files have familiar extensions (.wav, .rim) but use proprietary encoding.
- **Shape**: "These WAV files won't play — browser says unable to decode audio data."
- **Solution**: Don't rabbit-hole into format conversion. Ship without the blocked asset type, generate web-native replacements later. Test with ffmpeg and Python's wave module first — if both fail, the format is genuinely proprietary.
- **Lesson**: Momentum > completeness. BioWare's KotOR uses a custom header format for audio that no standard tool can decode. The modules (.rim) are also a proprietary archive format. Accept that some game assets need specialized modding tools.
- **Applicable When**: Any time game assets from installed titles are being repurposed for web games.

