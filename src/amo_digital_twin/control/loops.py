from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, List


MeasureFn = Callable[[], float]
ActuateFn = Callable[[float], None]
ErrorFn = Callable[[float], float]


@dataclass
class FeedbackLogEntry:
    t: float
    measurement: float
    control: float
    error: float


@dataclass
class FeedbackResult:
    history: List[FeedbackLogEntry]


def run_scalar_feedback_loop(
    measure: MeasureFn,
    actuate: ActuateFn,
    error_fn: ErrorFn,
    initial_control: float,
    gain: float = 0.1,
    dt: float = 0.05,
    steps: int = 100,
) -> FeedbackResult:
    """
    Simple synchronous scalar feedback loop.

    - measure(): returns a scalar (e.g. power_mw)
    - actuate(u): sets a scalar control (e.g. motor angle_deg)
    - error_fn(y): maps measurement to error to be minimized
    """
    history: List[FeedbackLogEntry] = []
    u = initial_control

    for _ in range(steps):
        t0 = time.time()
        actuate(u)
        y = measure()
        e = error_fn(y)

        # simple "push uphill" sign-based rule
        direction = -1.0 if e > 0.0 else 1.0
        u += gain * direction

        history.append(FeedbackLogEntry(t=t0, measurement=y, control=u, error=e))

        time.sleep(dt)

    return FeedbackResult(history=history)
