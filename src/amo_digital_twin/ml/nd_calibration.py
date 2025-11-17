from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

import numpy as np

from amo_digital_twin.experiments.nd_scan_hal import run_nd_scan_hal


TWIN_CONFIG_PATH = Path("configs/twin_params.json")


def load_twin_params() -> Dict[str, Any]:
    if not TWIN_CONFIG_PATH.exists():
        return {"blocks": {}}
    return json.loads(TWIN_CONFIG_PATH.read_text())


def save_twin_params(data: Dict[str, Any]) -> None:
    TWIN_CONFIG_PATH.write_text(json.dumps(data, indent=2, sort_keys=True))


def calibrate_nd_optical_density(
    od_guess: float = 0.3,
    noise_std_mw: float = 0.05,
    repeats: int = 10,
) -> float:
    """
    Estimate ND optical density from repeated measurements.

    For each run, we measure (P_in, P_out_meas), compute T = P_out / P_in,
    average T, and set OD = -log10(T).
    """
    Ts = []
    for _ in range(repeats):
        pin, _psim, pmeas = run_nd_scan_hal(
            od_guess=od_guess,
            noise_std_mw=noise_std_mw,
        )
        if pin <= 0.0:
            continue
        Ts.append(pmeas / pin)

    if not Ts:
        raise RuntimeError("No valid ND measurements for calibration.")

    T_avg = float(np.mean(Ts))
    if T_avg <= 0.0:
        raise RuntimeError(f"Non-positive transmission {T_avg}")

    od_est = -np.log10(T_avg)

    twin = load_twin_params()
    blocks = twin.setdefault("blocks", {})
    nd_entry = blocks.setdefault("nd1", {})
    nd_entry["optical_density"] = od_est
    save_twin_params(twin)

    return od_est


def main() -> None:
    print("=== ND filter calibration (optical density) ===")
    od = calibrate_nd_optical_density()
    print(f"Estimated optical density: {od:.4f}")
    print(f"Updated {TWIN_CONFIG_PATH} with blocks.nd1.optical_density")
