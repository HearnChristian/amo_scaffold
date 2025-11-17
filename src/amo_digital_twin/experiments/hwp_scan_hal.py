from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

import numpy as np

from amo_digital_twin.core.light import LightState
from amo_digital_twin.core.backend import PolarizationBackend
from amo_digital_twin.core.pipeline import Pipeline
from amo_digital_twin.blocks.basic_optics import (
    Laser,
    HalfWavePlate,
    Polarizer,
    Mirror,
    PowerDetector,
)
from amo_digital_twin.hal.config import load_lab_hal
from amo_digital_twin.hal.channels import get_angle_device, get_power_device


TWIN_CONFIG_PATH = Path("configs/twin_params.json")


def load_hwp_offset_deg() -> float:
    """
    Load hwp1.angle_offset_deg from the twin params config, if present.
    """
    if not TWIN_CONFIG_PATH.exists():
        return 0.0

    data = json.loads(TWIN_CONFIG_PATH.read_text())
    blocks = data.get("blocks", {})
    hwp = blocks.get("hwp1", {})
    return float(hwp.get("angle_offset_deg", 0.0))


def build_pipeline() -> Pipeline:
    """
    Build a pipeline whose HWP angle we'll slave to an angle device,
    with an optional calibrated offset.
    """
    pipe = Pipeline()
    pipe.add(Laser("laser1", power_mw=10.0, pol_angle_deg=0.0, wavelength_m=1064e-9))

    offset_deg = load_hwp_offset_deg()
    hwp = HalfWavePlate("hwp1", angle_deg=0.0)
    hwp.params["angle_offset_deg"] = offset_deg
    pipe.add(hwp)

    pipe.add(Polarizer("pol1", axis_deg=0.0, efficiency=1.0))
    pipe.add(Mirror("m1", reflectivity=0.99))
    pipe.add(PowerDetector("pd1"))
    return pipe


def run_hwp_scan_hal(
    start_deg: float = 0.0,
    stop_deg: float = 180.0,
    step_deg: float = 10.0,
    noise_std_mw: float = 0.0,
) -> List[Tuple[float, float, float]]:
    """
    HWP scan using HAL-like devices.

    Returns list of (angle_cmd_deg, power_sim_mw, power_meas_mw).
    """
    backend = PolarizationBackend()
    pipe = build_pipeline()

    # Load devices from config and view them through channel abstractions
    lab = load_lab_hal("configs/hal_lab_example.json")
    motor = get_angle_device(lab, "hwp_motor")
    pm = get_power_device(lab, "pm1")

    angles = np.arange(start_deg, stop_deg + 1e-9, step_deg)

    results: List[Tuple[float, float, float]] = []

    for ang in angles:
        # Command angle channel
        motor.set_angle_deg(float(ang))

        # Sync digital twin block to hardware state + offset
        hwp_block = pipe.by_id("hwp1")
        offset_deg = float(hwp_block.params.get("angle_offset_deg", 0.0))
        motor_angle = motor.read_angle_deg()
        hwp_block.params["angle_deg"] = motor_angle + offset_deg

        # Run sim
        light_in = LightState()
        pipe.run(light_in, backend)

        # “True” sim power from PD
        pd = pipe.by_id("pd1")
        power_sim = float(pd.params.get("last_reading_mw", 0.0))

        # Feed sim power into power channel + noise
        if noise_std_mw > 0.0:
            noisy = float(np.random.normal(loc=power_sim, scale=noise_std_mw))
        else:
            noisy = power_sim

        pm.reading_mw = noisy  # MockPowerMeter field; real devices would measure
        power_meas = pm.read_power_mw()

        results.append((float(ang), power_sim, float(power_meas)))

    return results


def main() -> None:
    data = run_hwp_scan_hal(step_deg=10.0, noise_std_mw=0.05)

    print("angle_deg,power_sim_mw,power_meas_mw")
    for ang, ps, pm in data:
        print(f"{ang:.1f},{ps:.4f},{pm:.4f}")
