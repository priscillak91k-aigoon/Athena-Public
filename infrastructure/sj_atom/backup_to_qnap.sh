#!/bin/bash
# Phase 5: Zero-Trust Automated Backup Script (v2 - True Failsafe)
# Syncs infrastructure state and cognitive air-gap to the QNAP array
# using restic for encrypted, deduplicated, immutable snapshots.
# 
# To install as an hourly cron job:
# run `sudo crontab -e` and add the following line:
# 0 * * * * /home/sj/Athena-Public/infrastructure/sj_atom/backup_to_qnap.sh >> /var/log/qnap_backup.log 2>&1

set -e

# Load environment for Telegram Tokens
if [ -f "/home/sj/Athena-Public/.env" ]; then
    export $(grep -v '^#' /home/sj/Athena-Public/.env | xargs)
fi

notify_failure() {
    echo "[$(date)] 🚨 CRITICAL ERROR: Backup script failed on line $1"
    if [ -n "$TELEGRAM_ARCHITECT_TOKEN" ] && [ -n "$TELEGRAM_ALLOWED_USER_ID" ]; then
        # -s for silent, -o /dev/null to discard response body, preventing token leak in logs
        curl -s -o /dev/null -X POST "https://api.telegram.org/bot${TELEGRAM_ARCHITECT_TOKEN}/sendMessage" \
            -d chat_id="${TELEGRAM_ALLOWED_USER_ID}" \
            -d text="🚨 CRITICAL: Restic backup of Sovereign Vault FAILED. Check logs immediately." || true
    fi
}

trap 'notify_failure $LINENO' ERR

# RESTIC_PASSWORD must be set in .env. The previous key was compromised.
if [ -z "$RESTIC_PASSWORD" ]; then
    echo "🚨 ERROR: RESTIC_PASSWORD not found in .env. Halting backup."
    notify_failure $LINENO
    exit 1
fi
REPO_DEST="/mnt/qnap/atom_backups_restic"

INFRA_DIR="/home/sj/Athena-Public/infrastructure/sj_atom/data"
DB_DIR="/home/sj/Athena-Public/routine-app/server/data"
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

if [ -d "$DB_DIR" ]; then
    echo "[$(date)] Backing up SQLite database ($DB_DIR)..."
    restic -r "$REPO_DEST" backup "$DB_DIR"
else
    echo "[WARNING] $DB_DIR not found. Skipping database backup."
fi

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

# Dead-Man's Switch: Ping Healthchecks.io on absolute success
if [ -n "$HEALTHCHECK_URL" ]; then
    # Timeout 10s, retry up to 3 times, silence output.
    curl -m 10 --retry 3 -s -o /dev/null "$HEALTHCHECK_URL" || echo "[$(date)] WARNING: Healthcheck ping failed to transmit."
fi
