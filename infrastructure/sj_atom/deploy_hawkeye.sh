#!/bin/bash

echo "==========================================================="
echo "🦅 Deploying Hawkeye Vision Engine (llama3.2-vision:90b)"
echo "==========================================================="
echo "Note: Running the massive 90B model because the GB10 Superchip"
echo "has 128GB of unified memory."

# Ensure Ollama is running before pulling
if ! systemctl is-active --quiet ollama && ! docker ps | grep -q ollama; then
    echo "[!] Ollama doesn't appear to be running. Please start your AI stack first."
    exit 1
fi

echo "[*] Pulling vision model... (This is ~55GB, so grab a coffee)"
# We use docker exec if Ollama is containerized, otherwise bare metal
if docker ps | grep -q "ollama"; then
    docker exec -it ollama ollama pull llama3.2-vision:90b
else
    ollama pull llama3.2-vision:90b
fi

echo "[*] Pre-loading model into memory to verify..."
if docker ps | grep -q "ollama"; then
    docker exec -it ollama ollama run llama3.2-vision:90b "Describe what a blueprint looks like in one sentence."
else
    ollama run llama3.2-vision:90b "Describe what a blueprint looks like in one sentence."
fi

echo "==========================================================="
echo "✅ Vision Engine Online. Return to FURY for WebUI setup."
echo "==========================================================="
