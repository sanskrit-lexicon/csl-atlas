import json
from datetime import datetime, timezone
import subprocess

def write_source(out_path: str, script: str, stage: int) -> None:
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    except Exception:
        commit = "unknown"
    
    data = {
        "stage": stage,
        "commit": commit,
        "utc_iso": datetime.now(timezone.utc).isoformat(),
        "script": script
    }
    with open(f"{out_path}.source.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
