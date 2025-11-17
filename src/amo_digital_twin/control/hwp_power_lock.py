from __future__ import annotations

from typing import Tuple

from amo_digital_twin.core.light import LightState
from amo_digital_twin.core.backend import PolarizationBackend
from amo_digital_twin.core.pipeline import Pipeline
from amo_digital_twin.blocks.basic_optics import (
    Laser,
    HalfWavePlate,
    Polarizer,
    PowerDetector,
)
from amo_digital_twin.hal.config import load_lab_hal
from amo_digital_twin.hal.channels import get_angle_device, get_power_device
from amo_digital_twin.control.loops import run_scalar_feedback_loop


def build_pipeline() -> Pipeline:
    pipe = Pipeline()
    pipe.add(Laser("laser1", power_mw=10.0, pol_angle_deg=0.0, wavelength_m=1064e-9))
    pipe.add(HalfWavePlate("hwp1", angle_deg=0.0))
    pipe.add(Polarizer("pol1", axis_deg=0.0, efficiency=1.0))
    pipe.add(PowerDetector("pd1"))
    return pipe


def make_loop_functions(
    target_power_mw: float = 9.0,
) -> Tuple[callable, callable, callable]:
    """
    Build measure, actuate, error_fn for the HWP power-lock loop.
    """
    backend = PolarizationBackend()
    pipe = build_pipeline()
    lab = load_lab_hal("configs/hal_lab_example.json")
    motor = get_angle_device(lab, "hwp_motor")
    pm = get_power_device(lab, "pm1")

    def measure() -> float:
        # sync twin HWP with motor
        hwp = pipe.by_id("hwp1")
        hwp.params["angle_deg"] = motor.read_angle_deg()
        pipe.run(LightState(), backend)

        pd = pipe.by_id("pd1")
        power_sim = float(pd.params.get("last_reading_mw", 0.0))

        pm.reading_mw = power_sim
        return pm.read_power_mw()

    def actuate(angle_deg: float) -> None:
        motor.set_angle_deg(angle_deg)

    def error_fn(measured_power: float) -> float:
        # positive error means "too low"
        return target_power_mw - measured_power

    return measure, actuate, error_fn


def main() -> None:
    measure, actuate, error_fn = make_loop_functions(target_power_mw=9.5)

    result = run_scalar_feedback_loop(
        measure=measure,
        actuate=actuate,
        error_fn=error_fn,
        initial_control=0.0,
        gain=0.5,
        dt=0.1,
        steps=40,
    )

    print("t,measurement_mw,error")
    for entry in result.history:
        print(f"{entry.t:.3f},{entry.measurement:.4f},{entry.error:.4f}")
