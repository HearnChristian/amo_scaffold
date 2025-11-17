from __future__ import annotations

from typing import List, Tuple, Dict, Any

import numpy as np

from amo_digital_twin.experiments.hwp_scan import run_hwp_scan


def hwp_model(
    angles_deg: np.ndarray,
    params: Dict[str, Any],
) -> np.ndarray:
    """
    Simple model for transmitted power vs HWP angle.

    We assume:
      P(θ) = P0 * cos^2(2 * (θ + offset))
    where:
      - P0 is approx the max power (here ~9.9 mW)
      - offset is an unknown angle error (deg) we want to fit
    """
    P0 = float(params.get("P0", 9.9))
    offset_deg = float(params.get("offset_deg", 0.0))

    theta = np.deg2rad(angles_deg + offset_deg)
    return P0 * np.cos(2.0 * theta) ** 2


def fit_offset(
    data: List[Tuple[float, float]],
    initial_offset_deg: float = 0.0,
) -> Dict[str, Any]:
    """
    Fit the HWP angle offset to the scan data using least squares.
    """
    angles = np.array([d[0] for d in data], dtype=float)
    powers = np.array([d[1] for d in data], dtype=float)

    # Initial params
    params: Dict[str, Any] = {
        "P0": float(powers.max()),
        "offset_deg": initial_offset_deg,
    }

    # Very small gradient descent, just to demonstrate the loop.
    lr = 1e-3  # learning rate
    iters = 2000

    for _ in range(iters):
        # Numerical gradient w.r.t. offset_deg
        eps = 1e-4
        y = hwp_model(angles, params)
        params_up = dict(params)
        params_up["offset_deg"] = params["offset_deg"] + eps
        y_up = hwp_model(angles, params_up)

        # d/d(offset) ~ (y_up - y) / eps
        grad = np.mean(2.0 * (y - powers) * (y_up - y) / eps)
        params["offset_deg"] -= lr * grad

    return params


def main() -> None:
    # In the future, this data will come from real hardware via the HAL.
    data = run_hwp_scan(step_deg=10.0)

    params = fit_offset(data, initial_offset_deg=5.0)
    P0 = params["P0"]
    offset = params["offset_deg"]

    print("=== HWP calibration demo ===")
    print(f"Fitted P0 (max power): {P0:.4f} mW")
    print(f"Fitted offset angle:  {offset:.4f} deg (should be ~0 for pure sim)")
