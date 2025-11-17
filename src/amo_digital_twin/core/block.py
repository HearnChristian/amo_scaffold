from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Protocol

from .light import LightState


@dataclass
class Block:
    """
    Base class for all optical / hardware blocks.
    """

    id: str
    kind: str
    params: Dict[str, Any] = field(default_factory=dict)

    pose_world: Any | None = None  # reserved for 3D
    cad_uri: str | None = None     # reserved for 3D

    def forward(self, light: LightState, backend: "Backend") -> LightState:
        return light.copy()


class Backend(Protocol):
    name: str

    def apply(self, block: Block, light: LightState) -> LightState:
        ...
