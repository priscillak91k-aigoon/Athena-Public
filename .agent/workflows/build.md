---
description: Command Center dispatch — Antigravity routes work through Aider or Cursor as needed
---

// turbo-all

# /build — Command Center Dispatch

> **Philosophy**: Cilla talks to Antigravity. Antigravity decides the execution path.
> **Rule**: Minimize friction. Maximize autonomy. One approval max.

## Dispatch Logic

When the user requests building/coding work:

### Step 1: Classify the Work

| Type | Route | Why |
|------|-------|-----|
| File edits (create, modify, delete) | **Direct** — Antigravity edits files | Zero friction, no terminal needed |
| Context-heavy work (health, Athena, research) | **Direct** — Antigravity handles | Only I have Athena context |
| Multi-file code generation | **Aider dispatch** | One approval, zero friction execution |
| Terminal commands (build, test, install) | **Aider or direct** | Aider if chaining multiple steps |
| Visual prototyping / composer mode | **Cursor instructions** | Write exact instructions for Cursor agent |

### Step 2: Execute

#### Route A: Direct (Default)
- Edit files directly using code editing tools
- No terminal, no approval gates
- This handles 70%+ of all work

#### Route B: Aider Dispatch
// turbo
When multi-step file operations or code generation is needed:

```powershell
$env:GOOGLE_API_KEY = [System.Environment]::GetEnvironmentVariable('GOOGLE_API_KEY', 'User'); python -m aider --model gemini/gemini-2.5-flash --yes --no-auto-commits --message "<DETAILED_INSTRUCTIONS>"
```

**Rules for Aider dispatch:**
- Always run from the project directory (use `--file` to scope if needed)
- `--yes` flag = no approval gates inside Aider
- `--no-auto-commits` = don't mess with git automatically
- Put ALL instructions in a single `--message` — one approval click total
- After Aider completes, verify the output

#### Route C: Cursor Handoff (Rare)
When visual AI composer is specifically needed:
- Output: Exact natural language instructions to paste into Cursor's Composer
- Format: Step-by-step, scoped to specific files
- User opens Cursor, pastes instructions, Cursor builds

### Step 3: Verify
- After any dispatch, review the changes
- Run tests if applicable
- Report results back to user

## Quick Reference

```
User says: "build X"  →  I assess  →  Direct edit / Aider / Cursor
User says: "fix X"    →  I assess  →  Direct edit (usually)
User says: "create X" →  I assess  →  Direct edit or Aider for large scope
User says: "vibe"     →  Cursor handoff with detailed instructions
```

---

# workflow #build #dispatch #command-center
