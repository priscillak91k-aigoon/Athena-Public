#!/bin/bash
# Boot sequence for The Sovereign Engineer
# This script injects the Lobotto/Antigravity laws into the local LLM

echo "==========================================="
echo "⚡ Booting The Sovereign Engineer..."
echo "Injecting Core Identity and Directives into local Qwen model..."
echo "==========================================="

cd /home/sj/Athena-Public/infrastructure/sj_atom

OLLAMA_API_BASE=http://127.0.0.1:11434 ~/.local/bin/aider \
  --model ollama/qwen2.5-coder:32b \
  --yes \
  --no-auto-commits \
  --read atom_brain_seed/Core_Identity.md \
  --read atom_brain_seed/convictions.md \
  --read atom_brain_seed/heuristics.md \
  --read atom_brain_seed/thinking_protocol.md
