#!/bin/bash
# Phase 5: Zero-Trust Automated Backup Script (v2 - True Failsafe)
# Syncs infrastructure state and cognitive air-gap to the QNAP array
# using restic for encrypted, deduplicated, immutable snapshots.
# 
# To install as an hourly cron job:
# run `sudo crontab -e` and add the following line:
# 0 * * * * /home/sj/Athena-Public/infrastructure/sj_atom/backup_to_qnap.sh >> /var/log/qnap_backup.log 2>&1

set -e

# NOTE: Set this password in your environment or keep it hardcoded for an air-gapped node
export RESTIC_PASSWORD="sovereign_atom_secure"
REPO_DEST="/mnt/qnap/atom_backups_restic"

INFRA_DIR="/home/sj/Athena-Public/infrastructure/sj_atom/data"
CONTEXT_DIR="/home/sj/context"

echo "[$(date)] Starting Phase 5 Restic Backup..."

# 1. Initialize repo if it doesn't exist
if [ ! -f "$REPO_DEST/config" ]; then
    echo "[$(date)] Initializing restic repository at $REPO_DEST..."
    mkdir -p "$REPO_DEST"
    restic init --repo "$REPO_DEST"
fi

# 2. Perform live, zero-downtime backup
echo "[$(date)] Backing up infrastructure data ($INFRA_DIR)..."
restic -r "$REPO_DEST" backup "$INFRA_DIR"

if [ -d "$CONTEXT_DIR" ]; then
    echo "[$(date)] Backing up cognitive air-gap ($CONTEXT_DIR)..."
    restic -r "$REPO_DEST" backup "$CONTEXT_DIR"
else
    echo "[WARNING] $CONTEXT_DIR not found. Skipping air-gap backup."
fi

# 3. Prune old snapshots (Retention Policy: Keep last 24 hourly, last 7 daily, last 4 weekly, last 12 monthly)
echo "[$(date)] Pruning old snapshots..."
restic -r "$REPO_DEST" forget --keep-hourly 24 --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune

echo "[$(date)] Backup complete! No containers were harmed (or stopped) in the making of this snapshot."
