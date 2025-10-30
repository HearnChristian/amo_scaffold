cat > src/amo/__init__.py <<'EOF'
__all__ = ["hw", "twin"]
from .twin import TwinLogger  # convenience re-export
EOF

cat > src/amo/hw/__init__.py <<'EOF'
from .interfaces import (
    Device, Channels, ClockConsumer,
    TunableFrequency, PhaseAdjustable, AmplitudeAdjustable,
    CommitRequired, Triggerable, Sweepable, ReadbackState
)
from .dds_sim import SimDDS
EOF

cat > src/amo/twin/__init__.py <<'EOF'
from .logger import TwinLogger
EOF
