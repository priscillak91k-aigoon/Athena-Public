# Project Contract: [project name]
**Created:** [date]   **Last amended:** [date]

## 1. Canonical Choices (pick ONE each — violations are unambiguous)
| Decision | Canonical choice | Banned alternatives |
|----------|------------------|---------------------|
| Storage | [e.g. Supabase] | [e.g. localStorage, flat JSON, IndexedDB] |
| Styling | [e.g. external styles.css] | [e.g. inline style=, <style> blocks] |
| State mgmt | [one] | [the rest] |
| Naming | [e.g. snake_case files, camelCase vars] | — |

## 2. File / Module Boundaries
- What lives where. e.g. "all DB calls go through db.py — no raw queries elsewhere."
- One sentence per boundary. If a file's job isn't listed, that's a flag.

## 3. Dependencies (closed list)
- Approved libraries only. Adding one = amend the contract first, not after.

## 4. Exceptions (the part that keeps it honest)
- Named, legitimate edge cases. e.g. "dynamic display:none toggles exempt from styling rule."
- Anything outside this list that breaks §1 is a real violation, not noise.

## 5. Session-End Audit Hook
At /end, check the session's output against §1–§3:
- Any banned alternative used? → VIOLATION (log it)
- Any new file whose job isn't in §2? → FLAG
- Any new dependency not in §3? → VIOLATION
- Repeated same-pattern violation across sessions? → amend the contract (add a predefined rule), don't just re-log
