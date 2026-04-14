"""
Refresh chemical state by applying time-decay and stamping last_updated = now.
Used to resolve the stale Chemical State warning without a full dreaming cycle.
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
state_path = PROJECT_ROOT / ".context" / "lobotto_state.json"

data = json.loads(state_path.read_text(encoding="utf-8"))
now = datetime.now(timezone.utc)
last_updated_str = data["meta"].get("last_updated", "")

if last_updated_str:
    last_updated = datetime.fromisoformat(last_updated_str.replace("Z", "+00:00"))
    gap_hours = (now - last_updated).total_seconds() / 3600
else:
    gap_hours = 0

print(f"Gap since last update: {gap_hours:.1f}h")

for name, chem in data["chemicals"].items():
    half_life = chem.get("half_life_hours", 48)
    decay = math.exp(-0.693 * gap_hours / half_life)
    old_val = chem["value"]
    new_val = round(max(0.0, min(1.0, old_val * decay)), 4)
    chem["value"] = new_val
    print(f"  {name}: {old_val:.4f} -> {new_val:.4f}")

data["meta"]["last_updated"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
note = data["meta"].get("note", "")
data["meta"]["note"] = note + f" Decay applied {now.strftime('%Y-%m-%d')} after {gap_hours:.0f}h gap."

state_path.write_text(json.dumps(data, indent=4), encoding="utf-8")
print("\nChemical state updated successfully.")
