#!/usr/bin/env bash
set -euo pipefail

sedi() { sed -i'' -e "$1" "$2"; }

echo "1) Clean __init__ and interlocks…"
mkdir -p src/amo/control
cat > src/amo/__init__.py <<'PY'
__all__ = ["hw", "twin", "__version__"]

from . import hw, twin

__version__ = "0.1.0"
PY

cat > src/amo/control/interlocks.py <<'PY'
from typing import Tuple

LIMITS: dict[str, Tuple[float, float]] = globals().get("LIMITS", {})

def check(cmd: dict) -> tuple[bool, str]:
    dev = cmd.get("device")
    action = cmd.get("action")

    if dev == "laser" and action == "set":
        param = cmd.get("param")
        value = cmd.get("value")
        key = f"{dev}.{param}"

        if key in LIMITS:
            lo, hi = LIMITS[key]
            try:
                v = float(value) if value is not None else None
            except (TypeError, ValueError):
                return False, f"Bad value for {key}: {value!r}"
            if v is None or not (lo <= v <= hi):
                return False, f"{key} must be within {lo}..{hi}, got {v}"

    return True, "ok"
PY

echo "2) Fix specific semicolon / one-liner spots…"
if grep -nq 'if dev is None: return' src/amo/main.py 2>/dev/null; then
  sedi 's/if dev is None: return/if dev is None:\
    return/' src/amo/main.py
fi
if grep -nq 'rec = {"evt": "pol_step"}; rec.update(s)' src/amo/run/pol_runner.py 2>/dev/null; then
  sedi 's/rec = {"evt": "pol_step"}; rec.update(s)/rec = {"evt": "pol_step"}\
        rec.update(s)/' src/amo/run/pol_runner.py
fi

echo "3) Patch type errors (only if present)…"
if grep -nEq 'self\._freq *= *None' src/amo/hw/dds_sim.py 2>/dev/null; then
  sedi 's/self\._freq *= *None/self._freq = 0.0/' src/amo/hw/dds_sim.py
fi
if grep -nEq 'self\._phase *= *None' src/amo/hw/dds_sim.py 2>/dev/null; then
  sedi 's/self\._phase *= *None/self._phase = 0.0/' src/amo/hw/dds_sim.py
fi
if grep -nEq 'self\._amp *= *None' src/amo/hw/dds_sim.py 2>/dev/null; then
  sedi 's/self\._amp *= *None/self._amp = 1.0/' src/amo/hw/dds_sim.py
fi
if grep -nq 'precision: str = 1.0' src/amo/io/sinks/influx.py 2>/dev/null; then
  sedi 's/precision: str = 1.0/precision: float = 1.0/' src/amo/io/sinks/influx.py
fi

echo "4) Run ruff + mypy…"
ruff check src tests --fix || true
mypy || true
