#!/bin/bash

# ==============================================================================
# Automated Plex Media Server Provisioning Script for SJ's NVIDIA AI TOP (Ubuntu)
# ==============================================================================
# Author: Lobotto
# Date: 2026-05-18
# Description: Automates NVIDIA driver installation, Plex installation, and 
#              prepares the system for the QNAP NTFS RAID mount.
# ==============================================================================

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo -e "\e[31m❌ Please run this script as root (use sudo).\e[0m"
  exit 1
fi

echo -e "\e[36m🚀 Starting Lobotto Ubuntu Plex Provisioning Protocol...\e[0m\n"

# 1. Update and Install Prerequisites
echo -e "\e[33m⚡ Step 1: Updating system and installing dependencies...\e[0m"
apt update && apt upgrade -y
apt install -y curl gnupg software-properties-common ntfs-3g
echo -e "\e[32m✅ System updated and ntfs-3g installed.\e[0m\n"

# 2. Install NVIDIA Proprietary Drivers
echo -e "\e[33m⚡ Step 2: Installing NVIDIA Proprietary Drivers for NVENC...\e[0m"
ubuntu-drivers autoinstall
echo -e "\e[32m✅ NVIDIA drivers installed.\e[0m\n"

# 3. Install Plex Media Server
echo -e "\e[33m🎬 Step 3: Installing Plex Media Server from official repo...\e[0m"
# Add Plex GPG key
curl https://downloads.plex.tv/plex-keys/PlexSign.key | gpg --dearmor | tee /usr/share/keyrings/plex-archive-keyring.gpg >/dev/null
# Add repository
echo "deb [signed-by=/usr/share/keyrings/plex-archive-keyring.gpg] https://downloads.plex.tv/repo/deb public main" | tee /etc/apt/sources.list.d/plexmediaserver.list
# Install Plex
apt update
apt install -y plexmediaserver
echo -e "\e[32m✅ Plex Media Server installed. (Service runs securely as 'plex' user).\e[0m\n"

# 4. Prepare QNAP Mount Point
echo -e "\e[33m📁 Step 4: Preparing QNAP mount point...\e[0m"
mkdir -p /mnt/qnap
chown plex:plex /mnt/qnap
chmod 755 /mnt/qnap
echo -e "\e[32m✅ /mnt/qnap created and permissions set.\e[0m\n"

# 5. Enable Plex to start on boot
systemctl enable plexmediaserver
systemctl start plexmediaserver

echo -e "\e[36m🎉 Provisioning Script Complete!\e[0m"
echo -e "====================================================================="
echo -e "\e[31m⚠️  CRITICAL NEXT STEPS:\e[0m"
echo -e "1. Reboot the system to apply the NVIDIA drivers: \e[32msudo reboot\e[0m"
echo -e "2. Plug in the QNAP via \e[33mUSB-A\e[0m."
echo -e "3. Find the QNAP's UUID: \e[32msudo blkid\e[0m"
echo -e "4. Edit fstab: \e[32msudo nano /etc/fstab\e[0m"
echo -e "   Add this line (replace YOUR-UUID):"
echo -e "   \e[32mUUID=YOUR-UUID /mnt/qnap ntfs-3g defaults,nofail,uid=plex,gid=plex,umask=0022 0 0\e[0m"
echo -e "5. Mount it: \e[32msudo mount -a\e[0m"
echo -e "====================================================================="
