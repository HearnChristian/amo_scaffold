from .base import Device

class SimLaser(Device):
    def __init__(self):
        self.power = 0.0      # 0..1
        self.detune_mhz = 0.0

    def connect(self) -> bool:
        return True

    def set(self, power=None, detune_mhz=None, **_):
        if power is not None:
            self.power = max(0.0, min(float(power), 1.0))
        if detune_mhz is not None:
            self.detune_mhz = float(detune_mhz)

    def get(self, what: str):
        if what == "power":
            return self.power
        if what == "detune_mhz":
            return self.detune_mhz
        return None

    def status(self):
        return {"ok": True, "power": self.power, "detune_mhz": self.detune_mhz}
