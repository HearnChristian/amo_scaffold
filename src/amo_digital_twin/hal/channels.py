from __future__ import annotations

from typing import Protocol, runtime_checkable

from .config import LabHAL


@runtime_checkable
class AngleDevice(Protocol):
    """
    Any device that exposes an angular channel in degrees.
    """

    def read_angle_deg(self) -> float: ...
    def set_angle_deg(self, angle_deg: float) -> None: ...


@runtime_checkable
class PowerMeterDevice(Protocol):
    """
    Any device that exposes an optical power reading in milliwatts.
    """

    def read_power_mw(self) -> float: ...


def get_angle_device(lab: LabHAL, device_id: str) -> AngleDevice:
    """
    Fetch a device by id and assert it behaves like an AngleDevice.
    """
    dev = lab.get(device_id)
    if not isinstance(dev, AngleDevice):
        raise TypeError(f"Device '{device_id}' does not support angle_deg channel")
    return dev


def get_power_device(lab: LabHAL, device_id: str) -> PowerMeterDevice:
    """
    Fetch a device by id and assert it behaves like a PowerMeterDevice.
    """
    dev = lab.get(device_id)
    if not isinstance(dev, PowerMeterDevice):
        raise TypeError(f"Device '{device_id}' does not support power_mw channel")
    return dev
