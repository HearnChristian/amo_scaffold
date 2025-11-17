from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Type, List

from .base import Device
from .mock import MockPowerMeter, MockMotor


@dataclass
class DeviceSpec:
    """
    Declarative description of one device, as read from config.

    Fields:
      - id: logical device ID
      - type: factory key (e.g. "mock_power_meter", "mock_motor")
      - model: human-readable model name
      - params: extra kwargs passed to the device class
    """

    id: str
    type: str
    model: str
    params: Dict[str, Any] = field(default_factory=dict)


class DeviceRegistry:
    """
    Maps simple string 'type' keys to concrete Device subclasses,
    and can build Device instances from DeviceSpec.
    """

    def __init__(self) -> None:
        self._types: Dict[str, Type[Device]] = {}

    def register(self, type_name: str, cls: Type[Device]) -> None:
        self._types[type_name] = cls

    def create(self, spec: DeviceSpec) -> Device:
        if spec.type not in self._types:
            raise KeyError(f"Unknown device type '{spec.type}' for id '{spec.id}'")
        cls = self._types[spec.type]
        # id and model are always passed; params override/extend
        kwargs = dict(spec.params)
        kwargs.setdefault("id", spec.id)
        kwargs.setdefault("model", spec.model)
        return cls(**kwargs)  # type: ignore[arg-type]


def default_registry() -> DeviceRegistry:
    """
    Pre-populated registry with built-in device types.
    """
    reg = DeviceRegistry()
    reg.register("mock_power_meter", MockPowerMeter)
    reg.register("mock_motor", MockMotor)
    # Later: reg.register("thorlabs_pm100", ThorlabsPM100), etc.
    return reg
