LIMITS = {
    "laser.power": (0.0, 0.25),
    "laser.detune_mhz": (-200.0, 200.0),
}

def check(cmd: dict) -> tuple[bool, str]:
    dev = cmd.get("device"); action = cmd.get("action")
    if dev == "laser" and action == "set":
        param = cmd.get("param"); value = cmd.get("value")
        key = f"{dev}.{param}"
        if key in LIMITS:
            lo, hi = LIMITS[key]
            try:
                v = float(value)
            except Exception:
                return False, f"value for {key} must be numeric"
            if not (lo <= v <= hi):
                return False, f"{key} must be within {lo}..{hi}, got {v}"
    return True, "ok"
