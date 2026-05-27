#!/bin/bash
# SJ's Sovereign Server Bootstrap Script
# OS: Ubuntu 24.04 LTS (NVIDIA Kernel)

set -e # Exit immediately if a command fails

echo "==========================================="
echo "⚡ Bootstrapping SJ's Super-Node..."
echo "==========================================="

echo "[0/3] Purging old Docker repository conflicts..."
sudo rm -f /etc/apt/sources.list.d/docker.list
sudo rm -f /etc/apt/keyrings/docker.gpg
sudo rm -f /etc/apt/keyrings/docker.asc

echo "[1/3] Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

echo "[2/3] Installing Docker & Docker Compose..."
# Remove old conflicting packages just in case
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove -y $pkg; done

# Add Docker's official GPG key
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add current user to docker group so sudo isn't needed for docker compose
sudo usermod -aG docker $USER

echo "[3/3] Installing NVIDIA Container Toolkit for AI hardware acceleration..."
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

echo "==========================================="
echo "✅ Bootstrap Complete!"
echo "CRITICAL: You must log out of the computer and log back in for the Docker permissions to apply."
echo "Once logged back in, you can run the Docker compose files."
echo "==========================================="
