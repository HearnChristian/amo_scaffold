from __future__ import annotations

from dataclasses import dataclass

from .base import Device, Capability


@dataclass
class MockPowerMeter(Device):
    """
    Mock power meter.
    """

    reading_mw: float = 0.0

    def __init__(self, id: str = "mock_pm", model: str = "mock") -> None:
        caps = [Capability(name="read_power_mw", kind="read", units="mW")]
        super().__init__(id=id, model=model, capabilities=caps)

    def read_power_mw(self) -> float:
        return float(self.reading_mw)


@dataclass
class MockMotor(Device):
    """
    Mock motorized rotation stage.
    """

    angle_deg: float = 0.0

    def __init__(self, id: str = "mock_motor", model: str = "mock") -> None:
        caps = [
            Capability(name="read_angle_deg", kind="read", units="deg"),
            Capability(name="set_angle_deg", kind="write", units="deg"),
        ]
        super().__init__(id=id, model=model, capabilities=caps)

    def read_angle_deg(self) -> float:
        return float(self.angle_deg)

    def set_angle_deg(self, angle_deg: float) -> None:
        self.angle_deg = float(angle_deg)
