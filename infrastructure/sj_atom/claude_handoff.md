# CLAUDE HANDOFF: SOVEREIGN LIFEHUB INFRASTRUCTURE

> **SYSTEM PRIMER FOR CLAUDE**: You are inheriting this architecture from Lobotto. This environment is mathematically hardened, air-gapped, and sovereign. Do not assume cloud deployment. Do not suggest adding external services, analytics, or Vercel/Supabase integrations. The Combat Protocol is active: prioritize resilience, zero-trust routing, and local-only execution. Do not break the air-gap.

## 1. The Core Objective
We successfully decoupled the user's `LifeHub` application from Supabase and deployed it to a local, headless Ubuntu ARM64 workstation (the "Atom"). The application now runs 100% locally, with zero public internet exposure.

## 2. Network Topology & Routing
- **Transport Layer**: All traffic routes through a zero-trust Tailscale network. The Atom's Tailscale IP is `100.103.179.49`.
- **DNS Resolution**: Tailscale MagicDNS was bypassing local TLDs, so we bypassed it. The Windows client (FURY) has a mathematically hardcoded `hosts` file routing `hub.atom.tailnet` directly to the Atom's Tailscale IP.
- **Firewall (UFW)**: The Atom's `ufw` firewall is aggressively configured. It was dropping standard web traffic, so we explicitly whitelisted `80/tcp` and `443/tcp` for the `tailscale0` interface. 

## 3. The Proxy Stack (Caddy)
- **Container**: `caddy:latest` running on the Docker bridge network.
- **Configuration**: The `Caddyfile` uses the `local_certs` directive to generate its own self-signed internal certificates (because Let's Encrypt cannot verify air-gapped domains).
- **Routing**: Caddy intercepts requests for `hub.atom.tailnet` and reverse proxies them to the internal `lifehub` container on port `8086`.
- **Trust Store**: Caddy's generated Root CA (`root.crt`) was extracted and injected directly into FURY's Windows Trusted Root Certification Authorities store to permanently silence browser security warnings.

## 4. The Backend (Node.js & SQLite)
- **Container**: `sj_proxy-lifehub` (Node 20 Alpine).
- **Environment**: Because `.env` files were failing on the sovereign node, environment variables (`PORT=8086`, `API_TOKEN=local_tailnet_token`) are injected directly into the `docker-compose-proxy.yml` file.
- **Database**: Supabase is dead. The backend initializes and connects to a sovereign SQLite database mapped to a physical volume on the Atom (`/home/sj/Athena-Public/routine-app/server/data/lifehub.db`).

## 5. The Backup Pipeline
- **Mechanism**: Data resilience is handled by `restic`, which provides deduplicated, encrypted, and immutable snapshots.
- **Scope**: The script `backup_to_qnap.sh` backs up both the system infrastructure config and the new SQLite database directory.
- **Automation**: The script is bound to an hourly `crontab` on the Atom, pushing the backups to the local QNAP array.

## 6. The Frontend
- The `symphony-app.js` frontend script was aggressively purged using a Python refactoring script. All references to Supabase, cloud endpoints, and remote fetching have been rewritten to reflect the new `LocalAPI` and `Backend` nomenclature.

## Current Status
The stack is stable, operational, and heavily armored. If the user asks you to audit it, check the code for any lingering external API calls or non-relative fetches. If you write new code, ensure it adheres strictly to the offline-first, local-storage, and local-SQLite methodology.
