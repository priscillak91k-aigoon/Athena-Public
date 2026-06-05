#!/bin/bash
# Boot sequence for The Sovereign Engineer
# This script injects the Lobotto/Antigravity laws into the local LLM

echo "==========================================="
echo "⚡ Booting The Sovereign Engineer..."
echo "Injecting Core Identity and Directives into local Qwen model..."
echo "==========================================="

cd /home/sj/Athena-Public/infrastructure/sj_atom

OLLAMA_API_BASE=http://127.0.0.1:11434 ~/.local/bin/aider \
  --model ollama/the-engineer:latest \
  --yes \
  --no-auto-commits \
  docker-compose-*.yml
