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
