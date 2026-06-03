# Atom OS Troubleshooting Protocol

> **Purpose**: A mechanical, rigid diagnostic flowchart for resolving system and container failures. When a service goes down, The Architect must execute these steps sequentially. Do not guess. Retrieve the data.

## Phase 1: Container Triage
If a specific Docker service is unresponsive or crashing loop:
1. **Fetch Logs**: Run `docker logs --tail 50 <container_name>`
2. **Check Status**: Run `docker inspect --format='{{json .State.Health}}' <container_name>` if healthchecks are configured.
3. **Analyze Resource Choke**: Run `docker stats --no-stream` to verify it isn't hitting a hard memory limit.

## Phase 2: Host Network & Port Conflicts
If a container refuses to start due to port binding errors:
1. **Identify the Ghost**: Run `sudo netstat -tulpn | grep <PORT>` to find the exact PID of the process holding the port.
2. **Eliminate**: Kill the ghost process (`sudo kill -9 <PID>`).
3. **Verify Routing**: Ensure the firewall (`ufw`) isn't blocking internal Docker bridge traffic.

## Phase 3: Daemon & System Layer
If Docker itself or a bare-metal service (like Ollama) is failing:
1. **Daemon Logs**: Run `journalctl -xeu docker.service` (or `ollama.service`) to see system-level failures.
2. **Storage Audit**: Run `df -h`. A container will silently fail if the `/var/lib/docker` partition is at 100% capacity.
3. **Memory Audit**: Run `free -m`. Check if the host has started swapping heavily. If swap is saturated, the kernel OOM (Out of Memory) killer will randomly destroy processes. Check OOM logs: `dmesg -T | grep -i oom`

## Phase 4: Resolution & Post-Mortem
1. Fix the configuration (using `.env` variables, never hardcoding).
2. Bring the service back up (`docker-compose up -d`).
3. Add a new rule to `heuristics.md` to prevent this specific failure from recurring.
