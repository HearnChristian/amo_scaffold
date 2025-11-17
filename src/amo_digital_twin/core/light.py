from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Dict, Any, Optional

import numpy as np


ModeType = Literal["POL", "RT"]  # "POL": polarization only, "RT": simple ray


@dataclass
class LightState:
    """
    Canonical representation of light as it flows between blocks.

    - mode="POL": use Jones vector E (Ex, Ey) and direction dir.
    - mode="RT": later, use rays array.
    """

    mode: ModeType = "POL"

    wavelength_m: float = 1064e-9
    meta: Dict[str, Any] = field(default_factory=dict)

    E: Optional[np.ndarray] = None  # complex, shape (2,)
    dir: Optional[np.ndarray] = None  # real, shape (3,)

    rays: Optional[np.ndarray] = None  # placeholder for ray mode

    def copy(self) -> "LightState":
        return LightState(
            mode=self.mode,
            wavelength_m=float(self.wavelength_m),
            meta=dict(self.meta),
            E=None if self.E is None else self.E.copy(),
            dir=None if self.dir is None else self.dir.copy(),
            rays=None if self.rays is None else self.rays.copy(),
        )
# Convention for rays:
# rays: shape (N, 8)
# columns = [x, y, z, dx, dy, dz, wavelength_m, power_mw]

    def is_polarization_mode(self) -> bool:
        return self.mode == "POL"

    def is_ray_mode(self) -> bool:
        return self.mode == "RT"
