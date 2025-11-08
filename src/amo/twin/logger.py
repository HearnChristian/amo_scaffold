import json
import time
from pathlib import Path
from typing import Dict, Any

class TwinLogger:
    def __init__(self, root="data"):
        Path(root).mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        self._fp = open(Path(root)/f"dds_{ts}.jsonl", "a", buffering=1)

    def record(self, event: Dict[str, Any]) -> None:
        event["t_wall"] = time.time()
        self._fp.write(json.dumps(event) + "\n")
