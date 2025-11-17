from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List

from .base import Device
from .registry import DeviceSpec, default_registry


@dataclass
class LabHAL:
    """
    Container for a set of devices instantiated from config.
    """

    devices: Dict[str, Device] = field(default_factory=dict)

    def get(self, device_id: str) -> Device:
        try:
            return self.devices[device_id]
        except KeyError:
            raise KeyError(f"Device '{device_id}' not found in LabHAL.")


def load_lab_hal(config_path: str | Path) -> LabHAL:
    """
    Load a LabHAL from a JSON config.

    Schema:
      {
        "devices": [
          { "id": "...", "type": "...", "model": "...", "params": {...} },
          ...
        ]
      }
    """
    path = Path(config_path)
    data = json.loads(path.read_text())

    specs_raw: List[Dict[str, Any]] = data.get("devices", [])
    specs: List[DeviceSpec] = [
        DeviceSpec(
            id=sr["id"],
            type=sr["type"],
            model=sr.get("model", sr["id"]),
            params=sr.get("params", {}),
        )
        for sr in specs_raw
    ]

    reg = default_registry()
    devices: Dict[str, Device] = {}
    for spec in specs:
        dev = reg.create(spec)
        devices[spec.id] = dev

    return LabHAL(devices=devices)
