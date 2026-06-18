# Project Contract: Hawkeye SaaS
**Created:** 2026-06-14   **Last amended:** 2026-06-14

## 1. Canonical Choices (pick ONE each — violations are unambiguous)
| Decision | Canonical choice | Banned alternatives |
|----------|------------------|---------------------|
| Storage | Python backend updates via `nzbc_auto_updater.py` | flat JSON, localStorage for core state |
| Styling | External `styles.css` | inline `style=""`, `<style>` blocks in `index.html` |
| UI/State | Vanilla HTML/JS in `index.html` | React, Vue, jQuery |
| Naming | `snake_case` for Python, `camelCase` for JS/HTML IDs | `kebab-case` variables, generic names like `data` |

## 2. File / Module Boundaries
- `index.html`: Holds structural markup and client-side UI logic.
- `styles.css`: Holds ALL styling tokens and presentation logic.
- `nzbc_auto_updater.py`: The single source of truth for updating compliance logic and data fetching.
- `assets/`: Static media files only.
- `knowledge_base/`: Reference documentation and compliance PDFs.

## 3. Dependencies (closed list)
- Vanilla JS (Frontend)
- Standard Library (Python backend)
*Adding ANY external JS library or Python pip package requires amending this contract first.*

## 4. Exceptions (the part that keeps it honest)
- Dynamic visibility toggling (`display: none` / `display: block`) applied via JavaScript `style` attributes is exempt from the "no inline styles" rule, as it represents state rather than presentation.

## 5. Session-End Audit Hook
At /end, check the session's output against §1–§3:
- Any banned alternative used? → VIOLATION (log it)
- Any new file whose job isn't in §2? → FLAG
- Any new dependency not in §3? → VIOLATION
- Repeated same-pattern violation across sessions? → amend the contract (add a predefined rule), don't just re-log
