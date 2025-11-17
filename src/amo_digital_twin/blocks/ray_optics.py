from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from ..core.block import Block
from ..core.light import LightState


@dataclass
class RaySource(Block):
    """
    Simple ray source: creates a bundle of parallel rays along +z.
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="ray_source", params=params)

    def _apply_ray(self, light: LightState) -> LightState:
        n = int(self.params.get("n_rays", 16))
        wavelength_m = float(self.params.get("wavelength_m", 1064e-9))
        power_mw = float(self.params.get("power_mw", 10.0))

        # Grid of rays in xy, all along +z
        r = np.linspace(-1.0, 1.0, int(np.sqrt(n)))
        xv, yv = np.meshgrid(r, r)
        pos = np.stack([xv.ravel(), yv.ravel(), np.zeros_like(xv).ravel()], axis=1)
        dir_vec = np.tile(np.array([0.0, 0.0, 1.0]), (pos.shape[0], 1))
        wl = np.full((pos.shape[0], 1), wavelength_m)
        power = np.full((pos.shape[0], 1), power_mw / pos.shape[0])

        rays = np.concatenate([pos, dir_vec, wl, power], axis=1)

        out = light.copy()
        out.mode = "RT"
        out.rays = rays
        out.wavelength_m = wavelength_m
        return out
