#!/bin/bash
# Phase 5: Zero-Trust Automated Backup Script
# Syncs Docker state and cognitive air-gap to the QNAP array
# 
# To install as a nightly cron job at 3:00 AM:
# run `sudo crontab -e` and add the following line:
# 0 3 * * * /home/sj/infrastructure/sj_atom/backup_to_qnap.sh >> /var/log/qnap_backup.log 2>&1

set -e

BACKUP_DEST="/mnt/qnap/atom_backups/$(date +%Y-%m-%d)"
LATEST_LINK="/mnt/qnap/atom_backups/latest"
INFRA_DIR="/home/sj/Athena-Public/infrastructure/sj_atom"
CONTEXT_DIR="/home/sj/context"

echo "[$(date)] Starting Phase 5 QNAP Backup..."

# 1. Stop all stateful containers to prevent database corruption during rsync
echo "[$(date)] Halting docker containers for safe snapshot..."
cd $INFRA_DIR
docker compose -f docker-compose-vault.yml stop
docker compose -f docker-compose-ai.yml stop

# 2. Rsync the data
echo "[$(date)] Rsyncing infrastructure /data..."
mkdir -p "$BACKUP_DEST/infrastructure"
rsync -aP --delete "$INFRA_DIR/data/" "$BACKUP_DEST/infrastructure/"

echo "[$(date)] Rsyncing cognitive air-gap /context..."
mkdir -p "$BACKUP_DEST/context"
if [ -d "$CONTEXT_DIR" ]; then
    rsync -aP --delete "$CONTEXT_DIR/" "$BACKUP_DEST/context/"
else
    echo "[WARNING] $CONTEXT_DIR not found. Skipping air-gap backup."
fi

# Update latest symlink
ln -sfn "$BACKUP_DEST" "$LATEST_LINK"

# 3. Restart the containers
echo "[$(date)] Restarting docker containers..."
docker compose -f docker-compose-vault.yml start
docker compose -f docker-compose-ai.yml start

echo "[$(date)] Backup complete!"
