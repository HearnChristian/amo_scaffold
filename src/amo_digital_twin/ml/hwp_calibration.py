from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np

from amo_digital_twin.experiments.hwp_scan_hal import run_hwp_scan_hal
from amo_digital_twin.ml.fitters import fit_single_param_least_squares


TWIN_CONFIG_PATH = Path("configs/twin_params.json")


def hwp_model(
    angles_deg: np.ndarray,
    params: Dict[str, Any],
) -> np.ndarray:
    """
    Simple analytical model for transmitted power vs HWP angle.

    P(θ) = P0 * cos^2(2 * (θ + offset_deg))
    """
    P0 = float(params.get("P0", 1.0))
    offset_deg = float(params.get("offset_deg", 0.0))

    theta = np.deg2rad(angles_deg + offset_deg)
    return P0 * np.cos(2.0 * theta) ** 2


def load_twin_params() -> Dict[str, Any]:
    if not TWIN_CONFIG_PATH.exists():
        return {"blocks": {}}
    return json.loads(TWIN_CONFIG_PATH.read_text())


def save_twin_params(data: Dict[str, Any]) -> None:
    TWIN_CONFIG_PATH.write_text(json.dumps(data, indent=2, sort_keys=True))


def calibrate_hwp_offset(
    scan_step_deg: float = 10.0,
    noise_std_mw: float = 0.05,
) -> float:
    """
    Run a HWP scan via HAL, fit the offset_deg, and write it into
    configs/twin_params.json under blocks.hwp1.angle_offset_deg.

    Returns the fitted offset in degrees.
    """
    # 1) Run the HAL-based scan (this uses the current digital twin)
    data: List[Tuple[float, float, float]] = run_hwp_scan_hal(
        step_deg=scan_step_deg,
        noise_std_mw=noise_std_mw,
    )

    angles = np.array([d[0] for d in data], dtype=float)
    powers_meas = np.array([d[2] for d in data], dtype=float)  # use measured column

    # 2) Initial guess: P0 = max power, offset_deg ~ 0
    params: Dict[str, Any] = {
        "P0": float(powers_meas.max()),
        "offset_deg": 0.0,
    }

    # 3) Fit offset_deg using our generic fitter
    params = fit_single_param_least_squares(
        x=angles,
        y_meas=powers_meas,
        model_fn=hwp_model,
        params=params,
        key="offset_deg",
        lr=1e-4,
        iters=5000,
    )

    offset = float(params["offset_deg"])

    # 4) Write back into twin_params.json
    twin = load_twin_params()
    blocks = twin.setdefault("blocks", {})
    hwp_entry = blocks.setdefault("hwp1", {})
    hwp_entry["angle_offset_deg"] = offset
    save_twin_params(twin)

    return offset


def main() -> None:
    print("=== HWP calibration (offset) ===")
    offset = calibrate_hwp_offset()
    print(f"Fitted angle offset: {offset:.4f} deg")
    print(f"Updated {TWIN_CONFIG_PATH} with blocks.hwp1.angle_offset_deg")
