import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

import scripts.athena_dreaming as dreaming

def promote_heuristics():
    pending_file = dreaming.HEURISTICS_PENDING_FILE
    live_file = dreaming.HEURISTICS_FILE
    
    if not pending_file.exists():
        print("No pending heuristics found.")
        return

    content = pending_file.read_text(encoding="utf-8")
    lines = content.splitlines()
    
    heuristics_to_promote = [line for line in lines if line.strip().startswith("- ")]
    
    if not heuristics_to_promote:
        print("No heuristics found to promote.")
        return
        
    print(f"Found {len(heuristics_to_promote)} heuristics to promote:")
    for h in heuristics_to_promote:
        print(f"  {h}")
        
    # Promote them by appending directly to the live heuristics file
    current_live = live_file.read_text(encoding="utf-8") if live_file.exists() else ""
    
    # We append to the Auto-Discovered section
    marker = "## ⚡ Situational Heuristics"
    auto_header = "### Auto-Discovered (Dreaming)"
    new_entries = "\\n".join(heuristics_to_promote)
    
    if auto_header in current_live and marker in current_live:
        marker_idx = current_live.find(marker)
        auto_idx = current_live.rfind(auto_header, 0, marker_idx)
        if auto_idx != -1:
            insert_point = current_live.rfind("\\n", auto_idx, marker_idx)
            updated = current_live[:insert_point] + "\\n" + new_entries + current_live[insert_point:]
        else:
            updated = current_live.replace(marker, f"{auto_header}\\n{new_entries}\\n\\n{marker}")
    elif marker in current_live:
        updated = current_live.replace(marker, f"{auto_header}\\n{new_entries}\\n\\n{marker}")
    else:
        updated = current_live + f"\\n\\n{auto_header}\\n{new_entries}\\n"
        
    live_file.write_text(updated, encoding="utf-8")
    
    print(f"\\nSuccessfully promoted {len(heuristics_to_promote)} heuristics to live file.")
    pending_file.unlink()
    print("Pending heuristics file cleared.")

if __name__ == "__main__":
    promote_heuristics()
