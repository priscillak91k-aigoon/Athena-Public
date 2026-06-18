import os
import datetime

# Core files that define the Lobotto architecture and state
CORE_FILES = [
    ".context/heuristics.md",
    ".context/convictions.md",
    ".context/about_priscilla.md",
    "AGENTS.md",
    "scripts/athena_brain_health.py",
    "scripts/heartbeat.py"
]

WORKSPACE_DIR = r"C:\Users\prisc\Documents\Athena-Public"
OUTPUT_FILE = r"C:\Users\prisc\Desktop\lobotto_brain_dump.md"

def export_brain():
    print(f"Exporting Lobotto Brain to {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        outfile.write(f"# Lobotto Brain Dump\n")
        outfile.write(f"**Generated:** {datetime.datetime.now().isoformat()}\n")
        outfile.write(f"**Purpose:** Provide full architectural and state context to Claude Opus.\n\n")
        
        for file_path in CORE_FILES:
            full_path = os.path.join(WORKSPACE_DIR, file_path)
            if os.path.exists(full_path):
                print(f" Packing: {file_path}")
                outfile.write(f"---\n")
                outfile.write(f"## FILE: {file_path}\n")
                outfile.write(f"---\n\n")
                
                # Determine block type
                ext = os.path.splitext(file_path)[1]
                lang = "python" if ext == ".py" else "json" if ext == ".json" else "markdown"
                
                outfile.write(f"```{lang}\n")
                try:
                    with open(full_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except UnicodeDecodeError:
                    # Fallback for some windows encoding issues
                    with open(full_path, 'r', encoding='cp1252', errors='ignore') as infile:
                        outfile.write(infile.read())
                outfile.write(f"\n```\n\n")
            else:
                print(f" Skipped (not found): {file_path}")
                
    print(f"\nDone! Upload '{OUTPUT_FILE}' to your Claude Project.")

if __name__ == "__main__":
    export_brain()
