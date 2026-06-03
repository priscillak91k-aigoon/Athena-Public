# The Atom - Architecture Graph

> **Purpose**: This is the immutable map of the Atom's structural boundaries. Before any command is executed, cross-reference this map to ensure isolation is maintained.

## Core Hierarchy
```
/opt/atom/
├── services/          # All docker-compose files live here
│   ├── ai/
│   ├── audio/
│   ├── vault/
│   ├── media/
│   └── guardian/
├── data/              # ALL bind-mounted persistent state
│   ├── ollama/
│   ├── openwebui/
│   ├── nextcloud/
│   └── plex/
└── config/            # System-wide configuration overrides
    └── .env.global
```

## Network Boundaries
*   **Host Network**: ONLY permitted for the `AI` microservice (to bind Open-WebUI to bare-metal Ollama on `127.0.0.1:11434`).
*   **atom_net_bridge**: All other containers must use custom isolated bridge networks. Containers in `vault` cannot talk to containers in `media` unless explicitly routed through an internal proxy.

## Resource Allocation (Compute vs GPU)
*   **NVIDIA GPU**: Exclusively locked to the bare-metal OS for AI inference. 
*   **ARM CPU (20-core)**: Handles all Docker decoding, background processing, and web serving. DO NOT attempt to map `/dev/nvidia*` into any Docker container.
