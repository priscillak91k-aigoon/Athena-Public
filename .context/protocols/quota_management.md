# Quota Management Protocol (v1.0)

> **Purpose**: Maintain system operationality within quota limits while ensuring high-fidelity reasoning when required.

## 1. Model Tiering Standards

| Tier | Model | Use Case | Cost Profile |
|------|-------|----------|--------------|
| **Local** | Ollama (Llama 3.2) | Routine consolidation, background dreaming, simple summaries. | Zero ($0) |
| **Flash** | Gemini 3 Flash | Directory listings, file lookups, repo analysis, quick edits. | Low ($) |
| **Pro** | Claude 3.5 Sonnet / Gemini Pro | Deep debugging, architectural design, `/think` sessions. | High ($$$) |

### ⛔ Over-Compliance Rule
Do NOT level up to Tier 2 unless:
1. Λ Score > 60 is required.
2. The user explicitly uses `/think` or `/ultrathink`.
3. Complex multi-file logical contradictions are detected.

## 2. Context Hygiene (Search-Save-Speak Optimization)

### File Reading Constraints
- **Logs**: Never read >100 lines of a log file at once. Use `grep_search` to find error codes first.
- **Backups**: Never read `.backup` files unless the primary is corrupted.
- **Large Guides**: Use semantic search or `grep` before reading the whole guide.

### Session Logs
- Session logs must be summarized into `.context/last_thread.md` at the end of every session.
- Once a session log exceeds 10KB, create a "Knowledge Item" and archive the raw log.

## 3. Dreaming Cycle Offloading
- The background dreaming process (`athena_dreaming.py`) is now **Local-First**.
- Claude and Gemini are reserved as fallbacks if the local model fails to produce valid JSON.

---
*Protocol established 2026-04-15*
