---
description: Instantly save a memory mid-session without breaking flow
---

# /remember — Instant Memory Capture

When the user types `#remember` followed by any text, or says "remember that...", do the following:

// turbo-all

## Steps:

1. Extract the fact or preference from the user's message
2. Determine which file it belongs in:
   - **Personal fact** (about Priscilla, family, life) → append to `.context/about_priscilla.md`
   - **Working pattern** (how she likes things done) → append to `.context/heuristics.md`
   - **Technical lesson** (code pattern, mistake, fix) → append to `.context/case_studies.md`
   - **Decision** (choice made with reasoning) → append to `.context/decision_journal.md`
3. Append to the appropriate section of the target file
4. Respond with: "🧠 Remembered: [brief summary] → [filename]"

## Format for appending:
- Add under the most relevant existing section header
- Prefix with `- ` (markdown list item)
- Include date if time-sensitive

## Example:
```
User: #remember Quinn is scared of the vacuum cleaner
Response: 🧠 Remembered: Quinn is scared of the vacuum → about_priscilla.md
```

## Important:
- Do NOT create a new file for each memory
- Do NOT ask for confirmation — just write it
- Keep the response to one line — don't break the user's flow
