from __future__ import annotations
from typing import Dict, Any, List
import numpy as np
from amo.twin.logger import TwinLogger
from amo.run.chain_exec import run_chain

def run_and_log(nodes: List[Dict[str, Any]], E0: np.ndarray, branch: str | None, log_root: str = "data"):
    steps = run_chain(nodes, E0, cli_branch=branch)
    log = TwinLogger(log_root)
    for s in steps:
        rec = {"evt": "pol_step"}
        rec.update(s)
        log.record(rec)
    log.record({"evt": "pol_summary", "n_steps": len(steps)})
    return steps
