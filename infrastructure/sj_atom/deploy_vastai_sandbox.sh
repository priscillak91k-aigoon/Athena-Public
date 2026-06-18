#!/bin/bash

echo "==========================================================="
echo "WARNING: VAST.AI DEPLOYMENT SANDBOX CHECK"
echo "==========================================================="
echo ""
echo "This script is locked to prevent catastrophic sovereign data loss."
echo ""
echo "Vast.ai gives anonymous internet users raw Docker access to this machine."
echo "If you run this on the same physical OS that holds the Obsidian vault,"
echo "you are violating Law #1 (Irreversible Ruin)."
echo ""
echo "If you have already moved your Sovereign data off this node, OR if this is"
echo "running inside a sandboxed Proxmox VM with PCIe passthrough for the GB10,"
echo "you may proceed."
echo ""
echo "To unlock this installation, you must edit this script and change"
echo "I_HAVE_SANDBOXED_MY_DATA=false to true."
echo "==========================================================="

I_HAVE_SANDBOXED_MY_DATA=false

if [ "$I_HAVE_SANDBOXED_MY_DATA" = false ]; then
    echo "ERROR: Data sandbox not confirmed. Halting installation."
    exit 1
fi

echo "[*] Data sandbox confirmed. Proceeding with Vast.ai Host setup..."

# 1. Disable apt-daily to prevent host updates dropping renter jobs
sudo systemctl stop apt-daily.timer
sudo systemctl disable apt-daily.timer
sudo systemctl stop apt-daily-upgrade.timer
sudo systemctl disable apt-daily-upgrade.timer

# 2. Check for XFS partition (Vast.ai requires XFS for strict disk quotas)
if ! df -T | grep -q "xfs"; then
    echo "[!] WARNING: No XFS partition detected. Renters may fill your drive and crash the host."
    echo "[!] It is highly recommended to mount /var/lib/docker on a dedicated XFS partition."
fi

# 3. Pull the Vast daemon installer
# Note: In a real deployment, the user must paste their unique URL from the Vast.ai console here.
echo "[*] You must log into Vast.ai/host to get your unique installation command."
echo "Example: wget https://vast.ai/install_host.sh; chmod +x install_host.sh; ./install_host.sh --api-key YOUR_KEY"

echo "==========================================================="
echo "Node ready for Vast.ai. Ensure port forwarding (e.g., 40000-40050)"
echo "is configured on your home router pointing to this machine's IP."
echo "==========================================================="
