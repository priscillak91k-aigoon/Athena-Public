# Active Projects

## 1. The 5 Sovereign Stacks (Microservice Rollout)
**Status**: In Progress
**Objective**: Build and deploy the decoupled Docker microservices to finalize the Atom's architecture.

### Remaining Stacks:
- [ ] **AI-Interface**: Deploy Open-WebUI via Docker, using `network_mode: host` to point directly to the bare-metal Ollama instance on `localhost:11434`.
- [ ] **Vault**: Deploy secure, local storage containers (e.g., Nextcloud).
- [ ] **Media**: Deploy Jellyfin/Plex via Docker without NVIDIA hooks (CPU decoding).
- [ ] **Audio**: Deploy the audio generation server.
- [ ] **Guardian**: Deploy Pi-hole/AdGuard Home for network-wide telemetry blocking.

---
*Note: Any completed stacks should be marked with an `[x]` and logged in the session journal.*
