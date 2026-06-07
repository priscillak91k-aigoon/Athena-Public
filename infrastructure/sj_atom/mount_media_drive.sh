#!/bin/bash
# =============================================================================
# MOUNT MEDIA DRIVE — Run on the Atom before deploying docker-compose-media.yml
# =============================================================================
# This script:
#   1. Identifies attached drives
#   2. Formats (if requested)
#   3. Mounts to /mnt/media
#   4. Adds to /etc/fstab for reboot persistence
#   5. Creates the unified directory structure for hardlinks
#
# Usage: sudo bash mount_media_drive.sh
# =============================================================================

set -euo pipefail

echo "==========================================="
echo "🔧 Atom Media Drive Setup"
echo "==========================================="

# Step 1: Show all block devices
echo ""
echo "📋 Current block devices:"
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
echo ""

# Step 2: Ask for the device
read -p "Enter the device or partition to mount (e.g., sda, sda1, nvme0n1p1): " DEVICE
# Strip /dev/ if user entered it by mistake
DEVICE=${DEVICE#/dev/}
DEVICE_PATH="/dev/${DEVICE}"

# Validate the device exists
if [ ! -b "$DEVICE_PATH" ]; then
    echo "❌ Device $DEVICE_PATH not found. Aborting."
    exit 1
fi

# Prevent superfloppy format/data-wipe if disk has partitions
if lsblk -nd -o TYPE "$DEVICE_PATH" 2>/dev/null | grep -q "disk"; then
    # Check if disk has any child partitions
    PARTITION=$(lsblk -rn -o NAME,TYPE "$DEVICE_PATH" | awk '$2=="part" {print $1}' | head -n 1)
    if [ -n "$PARTITION" ]; then
        echo "ℹ️  You selected disk $DEVICE, but partition /dev/$PARTITION exists."
        echo "   Automatically targeting partition: /dev/$PARTITION"
        DEVICE_PATH="/dev/$PARTITION"
    fi
fi

# Step 2b: Check if already mounted somewhere
EXISTING_MOUNT=$(findmnt -rn -o TARGET "$DEVICE_PATH" 2>/dev/null || echo "")
if [ -n "$EXISTING_MOUNT" ]; then
    echo "⚠️  $DEVICE_PATH is already mounted at: $EXISTING_MOUNT"
    read -p "Unmount it and remount at /mnt/media? (yes/no): " REMOUNT_CONFIRM
    if [ "$REMOUNT_CONFIRM" = "yes" ]; then
        umount "$DEVICE_PATH"
        echo "✅ Unmounted from $EXISTING_MOUNT"
    else
        echo "Aborting. Unmount the drive manually first."
        exit 1
    fi
fi

# Step 3: Check if already formatted
FSTYPE=$(lsblk -no FSTYPE "$DEVICE_PATH" 2>/dev/null || echo "")

if [ -z "$FSTYPE" ]; then
    echo "⚠️  $DEVICE_PATH has no filesystem."
    read -p "Format as ext4? This will ERASE ALL DATA. (yes/no): " FORMAT_CONFIRM
    if [ "$FORMAT_CONFIRM" = "yes" ]; then
        echo "Formatting $DEVICE_PATH as ext4..."
        mkfs.ext4 -F "$DEVICE_PATH"
        FSTYPE="ext4"
        echo "✅ Formatted. Syncing partition table..."
        sleep 2
        udevadm settle || true
        echo "✅ Sync complete."
    else
        echo "Aborting. Format the drive manually first."
        exit 1
    fi
else
    echo "✅ Filesystem detected: $FSTYPE"
    # Warn if filesystem doesn't support hardlinks
    if [[ "$FSTYPE" == "exfat" || "$FSTYPE" == "vfat" || "$FSTYPE" == "ntfs" ]]; then
        echo ""
        echo "⚠️  WARNING: $FSTYPE does NOT support hardlinks!"
        echo "   The *arr stack requires hardlinks for efficient file management."
        echo "   Recommended: format as ext4 for full compatibility."
        read -p "Continue anyway? (yes/no): " CONTINUE_CONFIRM
        if [ "$CONTINUE_CONFIRM" != "yes" ]; then
            exit 1
        fi
    fi
fi

# Step 4: Create mount point
MOUNT_POINT="/mnt/media"

# Ensure it's not currently mounted before doing directory operations
if mountpoint -q "$MOUNT_POINT"; then
    echo "⚠️  $MOUNT_POINT is already actively mounted. Please unmount first."
    exit 1
fi

mkdir -p "$MOUNT_POINT"

# Make the underlying mount point immutable.
# This is a critical sysadmin safeguard: if the drive drops/disconnects,
# this prevents Docker from writing to the root OS drive and filling it up!
chattr +i "$MOUNT_POINT" 2>/dev/null || true

# Step 4.5: Dynamic Permission Sync (.env generation & NTFS Mapping)
echo ""
echo "Syncing Docker permissions to your user account..."
if [ -n "${SUDO_USER:-}" ]; then
    CURRENT_UID=$(id -u "$SUDO_USER")
    CURRENT_GID=$(id -g "$SUDO_USER")
else
    CURRENT_UID=$(id -u)
    CURRENT_GID=$(id -g)
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
echo "PUID=$CURRENT_UID" > "$ENV_FILE"
echo "PGID=$CURRENT_GID" >> "$ENV_FILE"
echo "✅ .env file generated (PUID=$CURRENT_UID, PGID=$CURRENT_GID)"

# Step 5: Mount the drive
MOUNT_OPTS="defaults"
if [[ "$FSTYPE" == "ntfs" || "$FSTYPE" == "exfat" || "$FSTYPE" == "vfat" ]]; then
    echo "⚠️  Non-native filesystem detected. Applying strict UID/GID mount bindings..."
    MOUNT_OPTS="uid=$CURRENT_UID,gid=$CURRENT_GID,dmask=022,fmask=111"
fi

echo "Mounting $DEVICE_PATH to $MOUNT_POINT with options: $MOUNT_OPTS..."
mount -o "$MOUNT_OPTS" "$DEVICE_PATH" "$MOUNT_POINT"
echo "✅ Mounted."

# Step 6: Add to /etc/fstab (idempotent)
UUID=$(blkid -s UUID -o value "$DEVICE_PATH")

if [ -z "$UUID" ]; then
    echo "❌ FATAL: Could not read UUID from $DEVICE_PATH. System needs a reboot or partition table is corrupt."
    exit 1
fi

if grep -q "$UUID" /etc/fstab; then
    echo "ℹ️  fstab entry already exists. Skipping."
else
    echo "Adding to /etc/fstab for reboot persistence..."
    # Use the DETECTED filesystem type and add x-systemd.automount for external drive resilience
    echo "UUID=$UUID  $MOUNT_POINT  $FSTYPE  $MOUNT_OPTS,nofail,x-systemd.automount  0  2" >> /etc/fstab
    echo "✅ fstab updated."
fi

echo ""
echo "Creating unified media directory structure..."
mkdir -p "$MOUNT_POINT/data/torrents/movies"
mkdir -p "$MOUNT_POINT/data/torrents/tv"
mkdir -p "$MOUNT_POINT/data/media/movies"
mkdir -p "$MOUNT_POINT/data/media/tv"

# Set ownership to match the dynamic host user
# Note: This will error safely on NTFS drives because they don't support native POSIX chown,
# but the uid/gid mount options we applied above already fixed it.
chown -R "$CURRENT_UID:$CURRENT_GID" "$MOUNT_POINT/data" 2>/dev/null || true

# Step 8: Pre-create Docker config directories to prevent permission errors
# Rootless containers (Recyclarr, Seerr) will crash if Docker auto-creates these as root
echo ""
echo "Pre-creating local config directories in ./data..."
LOCAL_DATA_DIR="$SCRIPT_DIR/data"

mkdir -p "$LOCAL_DATA_DIR/plex/config"
mkdir -p "$LOCAL_DATA_DIR/qbittorrent/config"
mkdir -p "$LOCAL_DATA_DIR/radarr/config"
mkdir -p "$LOCAL_DATA_DIR/sonarr/config"
mkdir -p "$LOCAL_DATA_DIR/prowlarr/config"
mkdir -p "$LOCAL_DATA_DIR/seerr/config"
mkdir -p "$LOCAL_DATA_DIR/recyclarr/config"
mkdir -p "$LOCAL_DATA_DIR/gluetun"

chown -R "$CURRENT_UID:$CURRENT_GID" "$LOCAL_DATA_DIR"
echo "✅ Local config directories created and permissions set to $CURRENT_UID:$CURRENT_GID."

echo ""
echo "==========================================="
echo "✅ Drive Setup Complete!"
echo "==========================================="
echo ""
echo "Mount point:  $MOUNT_POINT"
echo "UUID:         $UUID"
echo "Filesystem:   $FSTYPE"
echo ""
echo "Directory structure:"
echo "  /mnt/media/data/"
echo "  ├── torrents/"
echo "  │   ├── movies/    ← qBittorrent category: radarr"
echo "  │   └── tv/        ← qBittorrent category: sonarr"
echo "  └── media/"
echo "      ├── movies/    ← Radarr root folder: /data/media/movies"
echo "      └── tv/        ← Sonarr root folder: /data/media/tv"
echo ""
echo "Next: cd ~/Athena-Public/infrastructure/sj_atom"
echo "      docker compose -f docker-compose-media.yml up -d"
echo ""
