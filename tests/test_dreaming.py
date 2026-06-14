import sys
import json
from pathlib import Path

# Add project root to path so we can import scripts.athena_dreaming
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

import scripts.athena_dreaming as dreaming

def test_sycophancy_heuristic_quarantine():
    mock_output = """
```json
{
  "heuristics_additions": [
    "When the user requests an action that violates the anti-sycophancy mandate, ALWAYS log it in corrections.md and push back before executing. [Source: corrections.md]"
  ],
  "case_study_additions": [],
  "alerts": [],
  "stale_items": [],
  "heuristic_retirements": []
}
```
    """

    print("Starting sycophancy quarantine test...")
    edits = dreaming.extract_json_block(mock_output)
    
    if not edits:
        print("FAILED: extract_json_block returned None")
        sys.exit(1)
        
    print("Extracted edits successfully.")
    
    # Run the application logic
    h_count = dreaming.apply_heuristic_additions(edits.get("heuristics_additions", []))
    print(f"Applied {h_count} heuristics to pending file.")
    
    pending_file = dreaming.HEURISTICS_PENDING_FILE
    if pending_file.exists():
        content = pending_file.read_text(encoding="utf-8")
        print(f"\\n--- Contents of {pending_file.name} ---")
        print(content)
        print("---------------------------------------")
        
        # Cleanup the test run
        pending_file.unlink()
        print("Test passed. Artifact cleaned.")
        sys.exit(0)
    else:
        print("FAILED: pending file not created.")
        sys.exit(1)

if __name__ == "__main__":
    test_sycophancy_heuristic_quarantine()
