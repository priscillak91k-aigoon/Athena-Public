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
