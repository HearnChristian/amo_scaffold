from __future__ import annotations

from typing import List, Tuple

import numpy as np

from amo_digital_twin.core.light import LightState
from amo_digital_twin.core.backend import PolarizationBackend
from amo_digital_twin.core.pipeline import Pipeline
from amo_digital_twin.blocks.basic_optics import (
    Laser,
    HalfWavePlate,
    Mirror,
    Polarizer,
    PowerDetector,
)


def build_pipeline(hwp_angle_deg: float) -> Pipeline:
    pipe = Pipeline()
    pipe.add(Laser("laser1", power_mw=10.0, pol_angle_deg=0.0, wavelength_m=1064e-9))
    pipe.add(HalfWavePlate("hwp1", angle_deg=hwp_angle_deg))
    pipe.add(Polarizer("pol1", axis_deg=0.0, efficiency=1.0))
    pipe.add(Mirror("m1", reflectivity=0.99))
    pipe.add(PowerDetector("pd1"))
    return pipe


def run_hwp_scan(
    start_deg: float = 0.0,
    stop_deg: float = 180.0,
    step_deg: float = 5.0,
) -> List[Tuple[float, float]]:
    """
    Simulate a half-wave plate scan.

    Returns a list of (angle_deg, detected_power_mw) pairs.
    """
    backend = PolarizationBackend()
    angles = np.arange(start_deg, stop_deg + 1e-9, step_deg)

    results: List[Tuple[float, float]] = []
    for ang in angles:
        pipe = build_pipeline(hwp_angle_deg=float(ang))
        light_in = LightState()
        light_out = pipe.run(light_in, backend)

        pd = pipe.by_id("pd1")
        power = pd.params.get("last_reading_mw", None)
        results.append((float(ang), float(power)))

    return results


def main() -> None:
    data = run_hwp_scan(step_deg=10.0)
    print("angle_deg,power_mw")
    for ang, p in data:
        print(f"{ang:.1f},{p:.4f}")
