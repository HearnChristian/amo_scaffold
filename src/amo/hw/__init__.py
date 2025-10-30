# Re-export capability protocols so callers import from amo.hw, not deep paths
from .interfaces import (
    Device, Channels, ClockConsumer,
    TunableFrequency, PhaseAdjustable, AmplitudeAdjustable,
    CommitRequired, Triggerable, Sweepable, ReadbackState
)

# Optional: expose the simulator here too for convenience
from .dds_sim import SimDDS  # noqa: F401
