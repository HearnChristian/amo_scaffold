from __future__ import annotations

import sys

from amo_digital_twin.core.light import LightState
from amo_digital_twin.core.backend import PolarizationBackend
from amo_digital_twin.core.circuit_config import load_circuit_config, build_pipeline_from_config


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: amo-run-circuit <config_path.json>")
        raise SystemExit(1)

    config_path = sys.argv[1]
    cfg = load_circuit_config(config_path)
    pipe = build_pipeline_from_config(cfg)

    backend = PolarizationBackend()
    light_out = pipe.run(LightState(), backend)

    try:
        pd = pipe.by_id("pd1")
        reading = pd.params.get("last_reading_mw", None)
    except KeyError:
        reading = None

    print(f"=== Circuit: {cfg.name} ===")
    print(f"Config: {config_path}")
    print(f"Final wavelength: {light_out.wavelength_m * 1e9:.2f} nm")
    print(f"Detector 'pd1' reading: {reading} mW")
    print(f"Final Jones E: {light_out.E}")
