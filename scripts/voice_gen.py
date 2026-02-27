"""
Lobotto Voice Generator — Reusable script for generating voice-cloned audio.
Uses XTTS-v2 with Priscilla's voice sample.

Usage:
  python voice_gen.py "Text to speak" output_filename.wav
"""
import os
import sys
import torch
from TTS.api import TTS

# Ensure ffmpeg is on PATH
ffmpeg_path = r"C:\Users\prisc\AppData\Local\Microsoft\WinGet\Links"
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] = ffmpeg_path + ";" + os.environ["PATH"]

REFERENCE_WAV = r"c:\Users\prisc\Documents\Athena-Public\session_logs\voice_reference.wav"
OUTPUT_DIR = r"c:\Users\prisc\Documents\Athena-Public\session_logs"

def generate_voice(text, output_filename, speed=1.35):
    """Generate voice-cloned audio from text."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading XTTS-v2 on {device}...")
    
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    
    raw_path = os.path.join(OUTPUT_DIR, f"_raw_{output_filename}")
    final_path = os.path.join(OUTPUT_DIR, output_filename)
    
    print("Generating speech...")
    tts.tts_to_file(
        text=text,
        speaker_wav=REFERENCE_WAV,
        language="en",
        file_path=raw_path
    )
    
    # Speed up to normal tempo
    import subprocess
    subprocess.run([
        "ffmpeg", "-y", "-i", raw_path,
        "-filter:a", f"atempo={speed}",
        final_path
    ], capture_output=True)
    
    # Clean up raw file
    os.remove(raw_path)
    print(f"Saved to: {final_path}")
    return final_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python voice_gen.py \"Text to speak\" output.wav")
        sys.exit(1)
    
    text = sys.argv[1]
    output = sys.argv[2]
    speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.35
    generate_voice(text, output, speed)
