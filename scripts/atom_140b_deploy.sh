#!/bin/bash

# ==============================================================================
# ATOM NODE DEPLOYMENT PAYLOAD: SOVEREIGN 100B+ LLM
# Target Architecture: ARM64 (Nvidia Grace / GB10 Superchip)
# ==============================================================================
# Description: Compiles llama.cpp from source for ARM64 and pulls down a massive
# frontier-class GGUF model. Configures a systemd daemon to run it in the background.
# ==============================================================================

set -e

echo ">>> INITIATING ATOM SOVEREIGN LLM DEPLOYMENT"

# Check for root
if [ "$EUID" -ne 0 ]; then
  echo "CRITICAL: This payload must be run as root. Use sudo ./atom_140b_deploy.sh"
  exit 1
fi

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------
# Target: Qwen3.5 122B A10B (Mixture of Experts)
# Claude's recommendation for absolute accuracy ceiling on a single ATOM node.
# The MoE architecture means only ~10B parameters fire per token, unlocking 15-20 tok/s.
MODEL_REPO="unsloth/Qwen3.5-122B-A10B-GGUF"
MODEL_FILE="*Q4_K_M*.gguf" # Uses wildcard to pull all shards
INSTALL_DIR="/opt/llama.cpp"
MODEL_DIR="/opt/models"
PORT=8080

echo ">>> TARGET MODEL: $MODEL_REPO ($MODEL_FILE)"

# ------------------------------------------------------------------------------
# 1. DEPENDENCIES
# ------------------------------------------------------------------------------
echo ">>> UPDATING APT AND INSTALLING DEPENDENCIES"
apt-get update
apt-get install -y build-essential cmake git python3-pip python3-venv curl

# ------------------------------------------------------------------------------
# 2. COMPILE LLAMA.CPP FOR ARM64 (GRACE SUPERCHIP)
# ------------------------------------------------------------------------------
echo ">>> CLONING AND COMPILING LLAMA.CPP FOR ARM64"
if [ -d "$INSTALL_DIR" ]; then
    echo "Directory $INSTALL_DIR exists. Pulling latest..."
    cd $INSTALL_DIR
    git pull
else
    git clone https://github.com/ggml-org/llama.cpp.git $INSTALL_DIR
    cd $INSTALL_DIR
fi

# Grace Superchips benefit from NEON/SVE instructions. GGML_NATIVE=ON optimizes for the host architecture.
cmake -B build -DGGML_NATIVE=ON 
cmake --build build --config Release -j$(nproc)

# ------------------------------------------------------------------------------
# 3. ACQUIRE THE MODEL
# ------------------------------------------------------------------------------
echo ">>> ACQUIRING MODEL (THIS WILL TAKE A WHILE...)"
mkdir -p $MODEL_DIR
cd $MODEL_DIR

# Install huggingface-cli
pip3 install -U "huggingface_hub[cli]" --break-system-packages

echo ">>> PULLING $MODEL_FILE FROM $MODEL_REPO"
huggingface-cli download $MODEL_REPO $MODEL_FILE --local-dir $MODEL_DIR --local-dir-use-symlinks False

# ------------------------------------------------------------------------------
# 4. SYSTEMD DAEMON CONFIGURATION
# ------------------------------------------------------------------------------
echo ">>> CONFIGURING SYSTEMD DAEMON (atom-llm.service)"

cat <<EOF > /etc/systemd/system/atom-llm.service
[Unit]
Description=Atom Sovereign LLM Server (llama.cpp)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
# --ctx-size 32768: 32K context window
# --threads 20: Maps to the Grace CPU cores for steady background inference
ExecStart=$INSTALL_DIR/build/bin/llama-server --model $MODEL_DIR/Q4_K_M/Qwen3.5-122B-A10B-Q4_K_M-00001-of-00003.gguf --alias sovereign-llm --port $PORT --ctx-size 32768 --threads 20 -fa on
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload and enable
systemctl daemon-reload
systemctl enable atom-llm.service
systemctl restart atom-llm.service

echo "=============================================================================="
echo "DEPLOYMENT COMPLETE."
echo "Model is being served at: http://localhost:$PORT"
echo "Check status via: systemctl status atom-llm.service"
echo "View logs via: journalctl -u atom-llm.service -f"
echo "=============================================================================="
