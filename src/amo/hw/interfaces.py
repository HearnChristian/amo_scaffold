from typing import Protocol, Dict, Any, Iterable, Optional


class Device(Protocol):
    def id(self) -> str:
        ...

    def metadata(self) -> Dict[str, Any]:
        ...

    def close(self) -> None:
        ...


class Channels(Protocol):
    def channels(self) -> Iterable[int]:
        ...


class ClockConsumer(Protocol):
    def set_ref_clock(self, hz: float, pll_mult: Optional[int] = None) -> None:
        ...


class TunableFrequency(Protocol):
    def set_freq(self, ch: int, hz: float) -> None:
        ...

    def get_freq(self, ch: int) -> float:
        ...


class PhaseAdjustable(Protocol):
    def set_phase_deg(self, ch: int, deg: float) -> None:
        ...

    def get_phase_deg(self, ch: int) -> float:
        ...


class AmplitudeAdjustable(Protocol):
    def set_amplitude(self, ch: int, frac: float) -> None:  # 0..1
        ...

    def get_amplitude(self, ch: int) -> float:
        ...


class CommitRequired(Protocol):
    def apply_update(self) -> None:  # latch buffered writes
        ...


class Triggerable(Protocol):
    def arm(self) -> None:
        ...

    def trigger(self) -> None:
        ...


class Sweepable(Protocol):
    def config_freq_sweep(self, ch: int, start_hz: float,
                          stop_hz: float, rate_hz_per_s: float) -> None:
        ...

    def start_sweep(self, ch: int) -> None:
        ...

    def stop_sweep(self, ch: int) -> None:
        ...


class ReadbackState(Protocol):
    def read_state(self) -> Dict[str, Any]:
        ...
