from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np

from amo_digital_twin.core.light import LightState


@dataclass
class MultiPortBlock:
    """
    Base class for generic optical elements with multiple input/output ports.
    Examples: beam splitters, PBS, fiber couplers, interferometers, etc.

    Each block has:
      - N input ports
      - M output ports
      - A forward() call that maps a dict of inputs -> dict of outputs
    """

    id: str
    kind: str
    params: Dict[str, Any] = field(default_factory=dict)
    n_in: int = 1
    n_out: int = 1

    def forward(self, inputs: Dict[int, LightState]) -> Dict[int, LightState]:
        """
        The core method subclasses override.

        inputs:  dict[port_index] = LightState
        returns: dict[out_port_index] = LightState
        """
        raise NotImplementedError("Subclasses must implement forward()")

    def apply(self, inputs: Dict[int, LightState]) -> Dict[int, LightState]:
        """
        Safe wrapper for forward() that deep-copies states before modifying.
        """
        in_copy = {k: v.copy() for k, v in inputs.items()}
        return self.forward(in_copy)
