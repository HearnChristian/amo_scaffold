import time
import random
from typing import Dict, Any, Iterable
from .interfaces import (Device, Channels, ClockConsumer, TunableFrequency,
                         PhaseAdjustable, AmplitudeAdjustable, CommitRequired, ReadbackState)

class SimDDS(Device, Channels, ClockConsumer, TunableFrequency,
             PhaseAdjustable, AmplitudeAdjustable, CommitRequired, ReadbackState):
    def __init__(self, ref_clk_hz: float = 25e6, pll_mult: int = 20, n_ch: int = 4):
        self._ref = ref_clk_hz
        self._sys = ref_clk_hz * pll_mult
        self._f = [0.0] * n_ch
        self._p = [0.0] * n_ch
        self._a = [0.0] * n_ch

    # Device
    def id(self) -> str: return "sim:dds"
    def metadata(self) -> Dict[str, Any]:
        return {"type":"dds_sim","sysclk_Hz": self._sys, "channels": len(self._f)}
    def close(self) -> None: pass

    # Channels
    def channels(self) -> Iterable[int]: return range(len(self._f))

    # ClockConsumer
    def set_ref_clock(self, hz: float, pll_mult: int | None = None) -> None:
        self._ref = float(hz)
        if pll_mult is not None:
            self._sys = self._ref * int(pll_mult)

    # TunableFrequency
    def set_freq(self, ch: int, hz: float) -> None: self._f[ch] = float(hz)
    def get_freq(self, ch: int) -> float: return self._f[ch]

    # PhaseAdjustable
    def set_phase_deg(self, ch: int, deg: float) -> None: self._p[ch] = float(deg) % 360.0
    def get_phase_deg(self, ch: int) -> float: return self._p[ch]

    # AmplitudeAdjustable
    def set_amplitude(self, ch: int, frac: float) -> None:
        self._a[ch] = max(0.0, min(1.0, float(frac)))
    def get_amplitude(self, ch: int) -> float: return self._a[ch]

    # CommitRequired
    def apply_update(self) -> None: self._last_update = time.time()

    # ReadbackState
    def read_state(self) -> Dict[str, Any]:
        power = [self._a[i]**2 * (1.0 + 0.01*random.uniform(-1,1)) for i in range(len(self._a))]
        return {"t": self._last_update, "sysclk_Hz": self._sys,
                "ch":[{"f_Hz":self._f[i],"phase_deg":self._p[i],"amp":self._a[i],"power_est":power[i]}
                      for i in range(len(self._f))]}

    def set_frequency(self, ch: int, hz: float) -> None:
        self._f[ch] = float(hz)
    def get_frequency(self, ch: int) -> float:
        return self._f[ch]
    def set_phase(self, ch: int, deg: float) -> None:
        self._p[ch] = float(deg)
    def get_phase(self, ch: int) -> float:
        return self._p[ch]
