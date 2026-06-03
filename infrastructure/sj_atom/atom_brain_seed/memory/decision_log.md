# Decision Log (Episodic Memory)

> **Purpose**: A chronological ledger of architectural changes and their underlying reasoning. This prevents the "Cold Start" problem where context is lost between sessions.

| Date | Service | Action | Rationale |
|------|---------|--------|-----------|
| [Boot] | Global | Established directory structure in `/opt/atom/` | Standardized topography prevents spaghetti file scattering across home directories. |
| [Boot] | AI | Removed NVIDIA Docker Toolkit | Bare-metal Ollama required due to fatal kernel-level AppArmor locks on ARM architecture. |
