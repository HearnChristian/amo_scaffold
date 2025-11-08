from __future__ import annotations
from typing import Dict, Any, List
import numpy as np
from amo.optics.polarimetry import jones_waveplate, jones_polarizer, stokes
from amo.devices.optics import PBS

def run_chain(nodes: List[Dict[str, Any]], E0: np.ndarray, cli_branch: str | None = None) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    E = E0.astype(complex)
    for i, n in enumerate(nodes):
        t = n["type"]
        if t == "waveplate":
            J = jones_waveplate(n["theta"], n["retard"])
            E = J @ E
            out.append({"node": i, "type": t, "S": stokes(E).tolist(),
                        "meta": {"theta": n["theta"], "retard": n["retard"]}})
        elif t == "polarizer":
            J = jones_polarizer(n["theta"])
            E = J @ E
            out.append({"node": i, "type": t, "S": stokes(E).tolist(),
                        "meta": {"theta": n["theta"]}})
        elif t == "pbs":
            pbs = PBS(theta_deg=n.get("theta", 0.0))
            ET, ER = pbs.route(E)
            PT, PR = stokes(ET)[0], stokes(ER)[0]
            branch = n.get("branch") or cli_branch
            if branch not in {"T","R"}:
                raise ValueError(f"PBS at node {i} needs a branch ('T' or 'R'). Pass --branch T|R or set in JSON.")
            E = ET if branch == "T" else ER
            out.append({"node": i, "type": t, "S": stokes(E).tolist(),
                        "meta": {"theta": n.get("theta", 0.0), "branch": branch,
                                 "PT": float(PT), "PR": float(PR)}})
        else:
            raise ValueError(f"Unknown node type: {t}")
    return out
