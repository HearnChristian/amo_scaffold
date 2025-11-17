from __future__ import annotations

from dataclasses import dataclass

from .light import LightState
from .block import Block, Backend as BackendProto


@dataclass
class RayBackend(BackendProto):
    name: str = "RT"

    def apply(self, block: Block, light: LightState) -> LightState:
        if hasattr(block, "_apply_ray"):
            return block._apply_ray(light)  # type: ignore[attr-defined]
        return light.copy()
        
class PolarizationBackend(BackendProto):
    """
    Simple Jones-matrix backend (polarization only).
    """

    name: str = "POL"

    def apply(self, block: Block, light: LightState) -> LightState:
        if hasattr(block, "_apply_pol"):
            return block._apply_pol(light)  # type: ignore[attr-defined]
        return light.copy()
