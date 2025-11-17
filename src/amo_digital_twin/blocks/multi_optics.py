from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

import numpy as np

from amo_digital_twin.core.multiblock import MultiPortBlock
from amo_digital_twin.core.light import LightState


@dataclass
class Source(MultiPortBlock):
    """
    Simple laser-like source as a multi-port block.

    Treat as 1-input (dummy) / 1-output block so it fits
    the GraphPipeline logic. The input is ignored.
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="source", params=params, n_in=1, n_out=1)

    def forward(self, inputs: Dict[int, LightState]) -> Dict[int, LightState]:
        power_mw = float(self.params.get("power_mw", 10.0))
        wavelength_m = float(self.params.get("wavelength_m", 1064e-9))
        pol_angle_deg = float(self.params.get("pol_angle_deg", 0.0))

        theta = np.deg2rad(pol_angle_deg)
        E = np.array([np.cos(theta), np.sin(theta)], dtype=np.complex128)

        # Scale amplitude so |E|^2 = power_mw
        norm = np.vdot(E, E).real
        if norm > 0:
            E = E * np.sqrt(power_mw / norm)

        ls = LightState()
        ls.mode = "POL"
        ls.E = E
        ls.wavelength_m = wavelength_m
        ls.meta["power_mw"] = power_mw

        return {0: ls}


@dataclass
class MirrorMP(MultiPortBlock):
    """
    Multi-port mirror (1 in, 1 out).
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="mirror_mp", params=params, n_in=1, n_out=1)

    def forward(self, inputs: Dict[int, LightState]) -> Dict[int, LightState]:
        inp = inputs.get(0)
        if inp is None:
            return {0: None}

        out = inp.copy()
        R = float(self.params.get("reflectivity", 1.0))

        # amplitude scaling by sqrt(R), add π phase flip on reflection
        if out.E is not None:
            out.E = -np.sqrt(R) * out.E

        # update power metadata if present; otherwise derive from |E|^2
        if "power_mw" in out.meta:
            out.meta["power_mw"] = R * float(out.meta["power_mw"])
        else:
            if out.E is not None:
                out.meta["power_mw"] = float(np.vdot(out.E, out.E).real)

        return {0: out}


@dataclass
class PowerDetectorMP(MultiPortBlock):
    """
    Power detector as a multi-port block (1 in, 1 out pass-through).

    Computes power from the Jones vector and stores in meta["power_mw"].
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="power_detector_mp", params=params, n_in=1, n_out=1)

    def forward(self, inputs: Dict[int, LightState]) -> Dict[int, LightState]:
        inp = inputs.get(0)
        if inp is None:
            return {0: None}

        out = inp.copy()
        if out.E is not None:
            power = float(np.vdot(out.E, out.E).real)
            out.meta["power_mw"] = power
        return {0: out}
