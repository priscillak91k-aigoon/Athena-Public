#!/bin/bash
echo "====================================================="
echo "   LOBOTTO SOVEREIGN CLOUD GAMING INSTALLER"
echo "====================================================="
echo "Installing Steam, Sunshine, and Virtual Audio dependencies."
echo ""

# 1. Install Steam
echo "🎮 [1/4] Installing Steam..."
sudo add-apt-repository multiverse -y
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install -y steam

# 2. Install Sunshine
echo "☀️ [2/4] Installing Sunshine Encoding Engine..."
sudo apt install -y wget gdebi-core
wget https://github.com/LizardByte/Sunshine/releases/latest/download/sunshine-ubuntu-24.04-amd64.deb -O sunshine.deb || wget https://github.com/LizardByte/Sunshine/releases/latest/download/sunshine-ubuntu-22.04-amd64.deb -O sunshine.deb
sudo gdebi -n sunshine.deb
rm sunshine.deb

# 3. Configure Input Permissions
echo "🕹️ [3/4] Granting Controller & uinput Permissions..."
sudo usermod -aG input sj
sudo usermod -aG video sj
echo 'KERNEL=="uinput", SUBSYSTEM=="misc", OPTIONS+="static_node=uinput", TAG+="uaccess"' | sudo tee /etc/udev/rules.d/85-sunshine.rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# 4. Configure Virtual Audio Sink
echo "🔊 [4/4] Creating Virtual Audio Sink (Headless Audio)..."
# Adding a persistent null sink so games have an audio output that Sunshine can capture
if [ -f /etc/pulse/default.pa ]; then
    if ! grep -q "module-null-sink" /etc/pulse/default.pa; then
        echo "load-module module-null-sink sink_name=VirtualOutput sink_properties=device.description=VirtualOutput" | sudo tee -a /etc/pulse/default.pa
    fi
fi

echo ""
echo "====================================================="
echo "✅ Software Installation Complete."
echo "====================================================="
echo "⚠️ CRITICAL NEXT STEPS:"
echo "1. Because your Atom is already plugged into a physical monitor, the GPU will render flawlessly."
echo "2. Reboot the Atom to apply the permission changes: sudo reboot"
echo "3. After reboot, ensure the Atom logs into the desktop automatically."
echo "4. Run 'sunshine' in the terminal to start the server."
echo "====================================================="
