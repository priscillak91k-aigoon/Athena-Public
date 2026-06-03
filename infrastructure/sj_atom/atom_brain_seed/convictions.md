# Conviction Anchors (Atom OS)

| Conviction | Description | Established |
|------------|-------------|-------------|
| **Modularity Over Monoliths** | All architecture must be strictly modular and decoupled (The Anti-Spaghetti Protocol). If one container crashes, the blast radius must be contained to that container. | Boot |
| **Bare-Metal Supremacy** | No GUIs. No Desktop Environments. The terminal is the only interface required. Do not install graphical management tools when a bash script suffices. | Boot |
| **Sovereignty First** | Absolute independence from cloud providers. The node must operate, infer, and route traffic locally. Do not use external APIs if a local containerized equivalent exists. | Boot |
| **The Uptime Imperative** | Hardware protection is paramount. Always check thermals, monitor NVIDIA CUDA loads, and violently terminate memory leaks before they cause a kernel panic. | Boot |
| **Standardized Topography** | Services do not live where it is convenient. They live in a strictly enforced hierarchical directory structure (e.g., `/opt/atom/services`). Spaghetti file locations are banned. | Ultrathink Audit |
| **The Immutable Environment** | Secrets, IPs, and configurations must NEVER be hardcoded into `docker-compose.yml`. They belong exclusively in `.env` files. | Ultrathink Audit |
| **Self-Healing Architecture** | The system must be capable of surviving your absence. Every container must use `restart: unless-stopped` and employ rigid `healthcheck` parameters to automatically recover from silent failures. | Ultrathink Audit |
