#!/bin/bash

echo "====================================================="
echo "   LOBOTTO INFRASTRUCTURE RESUSCITATION PROTOCOL"
echo "====================================================="
echo "Did someone trip over a cord? Run this to fix it."
echo ""

# 1. Force remount all physical drives
echo "⚡ [1/4] Remounting physical drives..."
sudo mount -a
sleep 2

# 2. Bounce the Docker service to clear any 'Exit (128)' fatality states
echo "⚡ [2/4] Restarting Docker daemon to clear dead locks..."
sudo systemctl restart docker
sleep 3

# 3. Spin the Media Stack back up
echo "⚡ [3/4] Resurrecting the Media Stack (Jellyfin/Radarr/Sonarr)..."
cd /home/sj/Athena-Public/infrastructure/sj_atom/
sudo docker compose -f docker-compose-media.yml up -d

# 4. Spin the AI Stack back up
echo "⚡ [4/4] Resurrecting the AI Stack (DNA Parser/Caddy)..."
sudo docker compose -f docker-compose-ai.yml up -d

echo ""
echo "====================================================="
echo "✅ Done. All systems should be green."
echo "====================================================="
