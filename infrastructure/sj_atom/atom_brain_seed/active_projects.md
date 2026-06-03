# Active Projects

## 1. The 5 Sovereign Stacks (Microservice Rollout)
**Status**: In Progress
**Objective**: Build and deploy the decoupled Docker microservices to finalize the Atom's architecture.

### Remaining Stacks:
- [x] **AI-Interface**: Deploy Open-WebUI via Docker, using `network_mode: host` to point directly to the bare-metal Ollama instance on `localhost:11434`.
- [x] **Vault**: Deploy secure, local storage containers (e.g., Nextcloud).
- [x] **Media**: Deploy Jellyfin/Plex via Docker without NVIDIA hooks (CPU decoding).
- [x] **Audio**: Deploy the audio generation server.
- [x] **Guardian**: Deploy Pi-hole/AdGuard Home for network-wide telemetry blocking.

### Phase 5 Directives:
- [x] **Zero-Trust Reverse Proxy**: Deployed Caddy with automatic Tailscale HTTPS.
- [x] **Automated Backups**: Created `backup_to_qnap.sh` for nightly air-gap syncing to `/mnt/qnap`.

---
*Note: Any completed stacks should be marked with an `[x]` and logged in the session journal.*
