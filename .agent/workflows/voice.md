---
description: Generate audio using Lobotto's voice (cloned from Priscilla's voice via XTTS-v2)
created: 2026-02-28
---

// turbo-all

# /voice — Lobotto Voice Generation

## Setup (Already Complete)
- **Voice Reference**: `session_logs/voice_reference.wav` (Priscilla's cloned voice)
- **Model**: XTTS-v2 (Coqui TTS) on CUDA
- **Speed Correction**: 1.35x atempo (XTTS generates slightly slow)

## Quick Use

// turbo
1. Run the voice generation script:
```powershell
python scripts/voice_gen.py "Your text here" output_filename.wav
```

## Manual Use (for custom speed)
```powershell
python scripts/voice_gen.py "Your text here" output_filename.wav 1.5
```

## Important Notes
- **Always use this voice** for all Lobotto audio output
- Reference WAV must exist at `session_logs/voice_reference.wav`
- Requires: PyTorch (CUDA), coqui-tts, ffmpeg
- First run downloads ~1.87GB model (cached after)
- Generation takes ~2-5 min depending on text length

## Files
| File | Purpose |
|------|---------|
| `scripts/voice_gen.py` | Reusable voice generation script |
| `session_logs/voice_reference.wav` | Priscilla's voice sample (source) |
| `session_logs/lobotto_intro_final.wav` | Lobotto's intro to Athena |
| `session_logs/lobotto_song_final.wav` | Silly beep-boop song |
| `session_logs/lobotto_dirty_song.wav` | Adult humor song |

#workflow #voice #lobotto
