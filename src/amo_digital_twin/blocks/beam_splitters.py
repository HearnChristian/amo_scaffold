from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import numpy as np

from amo_digital_twin.core.multiblock import MultiPortBlock
from amo_digital_twin.core.light import LightState


@dataclass
class NPBS50(MultiPortBlock):
    """
    50/50 non-polarizing beam splitter.
    Two inputs, two outputs.
    """

    def __init__(self, id: str, **params):
        super().__init__(id=id, kind="npbs50", params=params, n_in=2, n_out=2)

    def forward(self, inputs: Dict[int, LightState]) -> Dict[int, LightState]:
        E_in0 = inputs.get(0)
        E_in1 = inputs.get(1)

        # Transmission & reflection amplitude coefficients
        t = 1 / np.sqrt(2)
        r = 1j / np.sqrt(2)  # typical π/2 phase for reflection

        out = {}

        # Out port 0 (towards "transmitted" direction from port 0)
        if E_in0:
            E0 = E_in0.copy()
            E0.E = t * E0.E
        else:
            E0 = None

        # Out port 1 (towards "reflected" direction)
        if E_in0:
            E1 = E_in0.copy()
            E1.E = r * E1.E
        else:
            E1 = None

        # Merge contributions from port 1 as well (if present)
        if E_in1:
            if E0:
                E0.E += r * E_in1.E
            else:
                E0 = E_in1.copy()
                E0.E = r * E0.E

            if E1:
                E1.E += t * E_in1.E
            else:
                E1 = E_in1.copy()
                E1.E = t * E1.E

        return {0: E0, 1: E1}
@dataclass
class PBS(MultiPortBlock):
    """
    Polarizing beam splitter:
      - transmits the component along +x (H)
      - reflects the component along +y (V)
    """

    def __init__(self, id: str, **params):
        super().__init__(id=id, kind="pbs", params=params, n_in=1, n_out=2)

    def forward(self, inputs: Dict[int, LightState]) -> Dict[int, LightState]:
        inp = inputs.get(0)
        if inp is None:
            return {0: None, 1: None}

        # Jones vector [Hx, Hy]
        H = inp.copy()
        V = inp.copy()

        # Transmission: keep x, zero y
        H.E = inp.E * 1
        H.E[1] = 0

        # Reflection: keep y, zero x, and add reflection phase
        V.E = inp.E * 1
        V.E[0] = 0
        V.E[1] = 1j * V.E[1]

        return {0: H, 1: V}
