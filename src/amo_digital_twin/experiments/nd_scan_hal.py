from __future__ import annotations

from typing import List, Tuple

from amo_digital_twin.core.light import LightState
from amo_digital_twin.core.backend import PolarizationBackend
from amo_digital_twin.core.pipeline import Pipeline
from amo_digital_twin.blocks.basic_optics import (
    Laser,
    NeutralDensityFilter,
    PowerDetector,
)
from amo_digital_twin.hal.config import load_lab_hal
from amo_digital_twin.hal.channels import get_power_device


def build_nd_pipeline(od_guess: float) -> Pipeline:
    """
    Simple pipeline: Laser -> ND -> PD
    """
    pipe = Pipeline()
    pipe.add(Laser("laser1", power_mw=10.0, pol_angle_deg=0.0, wavelength_m=1064e-9))
    nd = NeutralDensityFilter("nd1", optical_density=od_guess)
    pipe.add(nd)
    pipe.add(PowerDetector("pd1"))
    return pipe


def run_nd_scan_hal(
    od_guess: float = 0.3,
    noise_std_mw: float = 0.05,
) -> Tuple[float, float, float]:
    """
    Run a single ND measurement via HAL.

    Returns (power_in_mw, power_sim_out_mw, power_meas_out_mw).
    """
    backend = PolarizationBackend()
    pipe = build_nd_pipeline(od_guess=od_guess)

    # Input power from laser params (design)
    laser = pipe.by_id("laser1")
    power_in = float(laser.params.get("power_mw", 10.0))

    # Load HAL, get power meter
    lab = load_lab_hal("configs/hal_lab_example.json")
    pm = get_power_device(lab, "pm1")

    # Run sim
    light_in = LightState()
    pipe.run(light_in, backend)

    pd = pipe.by_id("pd1")
    power_sim = float(pd.params.get("last_reading_mw", 0.0))

    # Add measurement noise
    import numpy as np

    if noise_std_mw > 0.0:
        power_meas = float(np.random.normal(loc=power_sim, scale=noise_std_mw))
    else:
        power_meas = power_sim

    pm.reading_mw = power_meas

    return power_in, power_sim, pm.read_power_mw()


def main() -> None:
    pin, psim, pmeas = run_nd_scan_hal(od_guess=0.3, noise_std_mw=0.05)
    print("power_in_mw,power_sim_out_mw,power_meas_out_mw")
    print(f"{pin:.4f},{psim:.4f},{pmeas:.4f}")
