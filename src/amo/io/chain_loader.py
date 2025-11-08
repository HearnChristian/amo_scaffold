from __future__ import annotations
import json
import numpy as np
from typing import Any, Dict, List, Tuple

def _parse_complex(s: str) -> complex:
    try:
        return complex(s)
    except Exception as e:
        raise ValueError(f"Invalid complex string: {s!r}") from e

def _parse_input(inp: Any) -> np.ndarray:
    if inp is None or inp == "H":
        return np.array([1.0+0j, 0.0+0j])
    if inp == "V":
        return np.array([0.0+0j, 1.0+0j])
    if isinstance(inp, dict):
        Ex = _parse_complex(str(inp.get("Ex", "1+0j")))
        Ey = _parse_complex(str(inp.get("Ey", "0+0j")))
        return np.array([Ex, Ey], dtype=complex)
    raise ValueError(f"Unsupported input spec: {inp!r}")

def _validate_node(n: Dict[str, Any]) -> Dict[str, Any]:
    t = n.get("type")
    if t not in {"waveplate", "polarizer", "pbs"}:
        raise ValueError(f"Unsupported node type: {t!r} (allowed: waveplate, polarizer, pbs)")
    if t == "waveplate":
        if "theta" not in n or "retard" not in n:
            raise ValueError("waveplate requires 'theta' and 'retard' (degrees)")
        return {"type":"waveplate", "theta": float(n["theta"]), "retard": float(n["retard"])}
    if t == "polarizer":
        if "theta" not in n:
            raise ValueError("polarizer requires 'theta' (degrees)")
        return {"type":"polarizer", "theta": float(n["theta"])}
    if t == "pbs":
        theta = float(n.get("theta", 0.0))
        branch = n.get("branch")
        if branch not in {"T","R",None}:
            raise ValueError("pbs 'branch' must be 'T', 'R', or omitted (choose later via CLI)")
        return {"type":"pbs", "theta": theta, "branch": branch}
    return n

def load_chain_json(path: str) -> Tuple[List[Dict[str, Any]], np.ndarray]:
    with open(path, "r") as f:
        data = json.load(f)
    nodes_in = data.get("nodes")
    if not isinstance(nodes_in, list) or not nodes_in:
        raise ValueError("JSON must contain non-empty 'nodes' list")
    nodes = [_validate_node(n) for n in nodes_in]
    E0 = _parse_input(data.get("input"))
    return nodes, E0
