from __future__ import annotations

from amo_digital_twin.core.light import LightState
from amo_digital_twin.core.backend import PolarizationBackend
from amo_digital_twin.core.pipeline import Pipeline
from amo_digital_twin.blocks.basic_optics import (
    Laser,
    HalfWavePlate,
    QuarterWavePlate,
    Polarizer,
    Mirror,
    NeutralDensityFilter,
    PowerDetector,
)


def build_demo_pipeline() -> Pipeline:
    pipe = Pipeline()
    pipe.add(Laser("laser1", power_mw=10.0, pol_angle_deg=0.0, wavelength_m=1064e-9))
    pipe.add(NeutralDensityFilter("nd1", optical_density=0.3))  # ~50% power
    pipe.add(HalfWavePlate("hwp1", angle_deg=22.5))
    pipe.add(Polarizer("pol1", axis_deg=0.0, efficiency=1.0))
    pipe.add(Mirror("m1", reflectivity=0.99))
    pipe.add(PowerDetector("pd1"))
    return pipe


def main() -> None:
    backend = PolarizationBackend()
    pipe = build_demo_pipeline()

    light_in = LightState()
    light_out = pipe.run(light_in, backend)

    pd = pipe.by_id("pd1")
    reading = pd.params.get("last_reading_mw", None)

    print("=== AMO Digital Twin demo ===")
    print(f"Final wavelength: {light_out.wavelength_m*1e9:.1f} nm")
    print(f"Detector reading: {reading} mW")
    print(f"Final polarization (Jones): {light_out.E}")


if __name__ == "__main__":
    main()
