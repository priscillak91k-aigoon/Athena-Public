# Media Stack — Post-Deploy Wiring Guide

> Run these steps AFTER `docker compose -f docker-compose-media.yml up -d` is healthy.
> All web UIs are accessible via Tailscale at `http://<atom-tailscale-ip>:<port>`.

> [!CAUTION]
> **LEGAL RISK (MODE A)**: If you run this stack in Mode A (No VPN), your real New Zealand IP address is fully exposed to torrent swarms. Downloading copyrighted movies/TV shows *will* likely trigger a "Three Strikes" copyright infringement notice from Spark/Chorus. **Switch to Mode B (VPN) as soon as possible before fulfilling requests.**

---

## Step 1: Configure Prowlarr (Indexer Hub)

**URL**: `http://atom:9696`

1. On first launch, set an admin password.
2. **Add Indexers**: Settings → Indexers → Add Indexer
   - Add your indexer sources (your choice — Prowlarr supports 100+ indexers)
   - Test each one to confirm it works
3. **Connect to Radarr**: Settings → Apps → Add Application
   - Type: Radarr
   - Prowlarr Server: `http://prowlarr:9696`
   - Radarr Server: `http://radarr:7878`
   - API Key: Copy from Radarr → Settings → General → API Key
   - Sync Level: Full Sync
4. **Connect to Sonarr**: Same as above but:
   - Type: Sonarr
   - Sonarr Server: `http://sonarr:8989`
   - API Key: Copy from Sonarr → Settings → General → API Key

---

## Step 2: Configure qBittorrent

**URL**: `http://atom:8088`

1. **Get initial password**: `docker logs qbittorrent 2>&1 | grep "temporary password"`
2. Login with `admin` / `<temporary password>`
3. Go to Settings (gear icon):
   - **Default Save Path**: `/data/torrents/`
   - **Downloads → When torrent completes**: do NOT enable "Move to" (Radarr/Sonarr handles this)
4. **If using Mode B (VPN)**: Verify VPN is working:
   ```bash
   docker exec gluetun curl -s ifconfig.me
   ```
   This should return your VPN exit IP, NOT the Atom's real IP.

---

## Step 3: Configure Radarr (Movies)

**URL**: `http://atom:7878`

1. **Root Folder**: Settings → Media Management → Add Root Folder
   - Path: `/data/media/movies`
2. **Download Client**: Settings → Download Clients → Add
   - Type: qBittorrent
   - Host: `qbittorrent` (or `gluetun` if using Mode B VPN)
   - Port: `8088`
   - Username: `admin`
   - Password: (the one you set in qBit)
   - Category: `radarr`
   - Click "Test" → must show ✅
3. **Quality Profiles**: Recyclarr handles this automatically. Leave defaults for now.

---

## Step 4: Configure Sonarr (TV Shows)

**URL**: `http://atom:8989`

Same as Radarr, but:
- Root Folder: `/data/media/tv`
- Download Client Category: `sonarr`

---

## Step 5: Configure Seerr (Requests + Telegram)

**URL**: `http://atom:5055`

1. **Setup Wizard**: Connect to Jellyfin (or Plex)
   - **Jellyfin**: Enter `http://jellyfin:8096` as the server address, plus your Jellyfin username and password.
   - **Plex**: Use the **host's LAN IP** (e.g., `http://192.168.x.x:32400`), NOT `http://plex:32400`
2. **Connect Radarr**:
   - Hostname: `radarr`
   - Port: `7878`
   - API Key: from Radarr → Settings → General
   - Root Folder: `/data/media/movies`
   - Quality Profile: (whatever Recyclarr set up)
3. **Connect Sonarr**: Same pattern, `sonarr:8989`
4. **Telegram Notifications**: Settings → Notifications → Telegram
   - Bot Token: `8878217823:AAHvwnBXXbtH20nzh9tbr0G35Ac_Y9hWKgI` (Reused from your existing AI bot)
   - Chat ID: `8309108979`
   - Enable: "Media Available" (so you get notified when it's ready to watch)
5. **Telegram Request Bot** (Conversational Requests):
   - Go to **Settings → General** in Seerr and copy your **API Key**.
   - Open your `docker-compose-media.yml` file and replace `PLACEHOLDER_INSERT_SEERR_API_KEY_HERE` under the `seerr-bot` service with this key.
   - Run `docker compose -f docker-compose-media.yml up -d seerr-bot` to launch the conversational request bot.

> **Plex LAN Networks**: In Plex → Settings → Network → LAN Networks, add `172.16.0.0/12,192.168.0.0/16` so Plex treats all Docker and LAN traffic as local (prevents "remote access" throttling).

---

## Step 6: Configure Recyclarr (Quality Automation)

Recyclarr v8 requires you to generate the initial configuration file.

1. SSH into the Atom
2. Generate the default config:
   ```bash
   docker exec -it recyclarr recyclarr config create
   ```
3. Edit the config:
   ```bash
   nano ~/Athena-Public/infrastructure/sj_atom/data/recyclarr/config/recyclarr.yml
   ```
4. Add your Radarr and Sonarr API keys and URLs:
   ```yaml
   radarr:
     movies:
       base_url: http://radarr:7878
       api_key: <radarr-api-key>
       quality_definition:
         type: movie
       quality_profiles:
         - from:
             trash_ids:
               - # Use TRaSH Guide IDs for your preferred quality
   
   sonarr:
     tv:
       base_url: http://sonarr:8989
       api_key: <sonarr-api-key>
       quality_definition:
         type: series
   ```
4. Force a sync: `docker exec recyclarr recyclarr sync`

---

## Verification Checklist

### Core (Mode A — No VPN)
- [ ] `docker compose -f docker-compose-media.yml ps` — all services show "healthy" or "running"
- [ ] Prowlarr: indexer test passes
- [ ] Radarr: download client test passes (Settings → Download Clients → Test)
- [ ] Sonarr: download client test passes
- [ ] Seerr: connected to Plex + Radarr + Sonarr
- [ ] Request a test movie in Seerr → confirm it appears in Radarr queue
- [ ] After download completes → confirm file appears in `/mnt/media/data/media/movies/`
- [ ] Confirm hardlink: `ls -l /mnt/media/data/media/movies/<movie>/` (link count > 1)
- [ ] Plex: library scan detects the new movie
- [ ] Telegram: notification received ("🎬 Movie is now available!")

### VPN (Mode B only — after upgrading)
- [ ] `docker exec gluetun curl -s ifconfig.me` — shows VPN IP, NOT real IP
- [ ] Radarr/Sonarr download client host changed from `qbittorrent` to `gluetun`

---

## Common Issues

| Symptom | Fix |
|---------|-----|
| qBit WebUI won't load (Mode A) | Check `docker logs qbittorrent` for startup errors |
| qBit WebUI won't load (Mode B) | Check `docker logs gluetun` — VPN credentials likely wrong |
| Radarr can't connect to qBit | Host must be `qbittorrent` (Mode A) or `gluetun` (Mode B) |
| Download stuck at 100%, won't import | Path mapping issue. Verify all containers use `/data` mount |
| Plex doesn't see new files | Force library scan, or check that Plex volume maps to `/data/media` |
| Hardlinks not working | Confirm downloads and media are on the same filesystem (same `/data` root) |
| NVENC greyed out in Plex | Known GB10 issue — consider switching to Jellyfin (uncomment in compose) |

---

## Step 7: Public Smart TV Access (Tailscale Funnel)

If you have users with standard Smart TVs (Samsung/LG) that cannot install the Tailscale app, you can expose Jellyfin to the public internet securely using **Tailscale Funnel**. This gives you a public URL without opening router ports or exposing your home IP.

**Part 1: Enable Funnel in Access Controls**
Before you can open a funnel, you must authorize it in your Tailscale Admin Console.
1. Go to your dashboard: `https://login.tailscale.com/admin/machines`
2. Click the **DNS** tab and ensure **Enable HTTPS** is turned ON.
3. Click the **Access Controls** tab.
4. Scroll to the bottom of your configuration code and paste this block right before the final `}`:
```json
	"nodeAttrs": [
		{
			"target": ["*"],
			"attr":   ["funnel"],
		},
	],
```
5. Click **Save**.

**Part 2: Open the Funnel on the Server**
1. SSH into the Atom node.
2. Force the daemon to sync with your new Access Controls:
   ```bash
   sudo tailscale up --force-reauth
   ```
3. Bind Jellyfin's port to the public relay as a background process:
   ```bash
   sudo tailscale funnel --bg 8096
   ```

**Part 3: Client Connection**
Tailscale will generate a secure HTTPS URL (e.g., `https://athena.tail42cb1a.ts.net`). Give this URL to your users. They just type it into the "Server URL" field of the Jellyfin app on their TV or phone. No VPN is required on their end.
