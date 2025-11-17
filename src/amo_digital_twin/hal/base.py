from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class Capability:
    """
    Describes one capability of a device.

    Example:
      name: "read_power_mw"
      kind: "read"
      units: "mW"
    """

    name: str
    kind: str  # "read" or "write"
    units: str | None = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Device:
    """
    Base class for hardware devices (or mocks).
    """

    id: str
    model: str
    capabilities: List[Capability] = field(default_factory=list)

    def info(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "model": self.model,
            "capabilities": [c.name for c in self.capabilities],
        }
