import time
import json
import pathlib
import yaml
from datetime import datetime
from typing import Dict, Any, List, Tuple

def new_run_dir(base: str = "data") -> pathlib.Path:
    # Use microseconds to avoid collisions; no printing here—let caller handle errors.
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    d = pathlib.Path(base) / ts
    d.mkdir(parents=True, exist_ok=False)  # fail if not writable so caller can report nicely
    return d

def save_params(run_dir: pathlib.Path, params: Dict[str, Any]) -> None:
    (run_dir / "params.json").write_text(json.dumps(params, indent=2))

def save_environment(run_dir: pathlib.Path, env: Dict[str, Any]) -> None:
    (run_dir / "environment.json").write_text(json.dumps(env, indent=2))

def load_recipe(path: str) -> list[dict]:
    with open(path, "r") as f:
        return yaml.safe_load(f) or []

def _iter_set_ops(steps: List[dict]):
    for step in steps:
        set_ops = step.get("set", {}) or {}
        for target, value in set_ops.items():
            yield step, target, value

def preflight(steps: List[dict], devices: Dict[str, Any], interlock_check, *, param_whitelist: dict | None = None) -> Tuple[bool, List[str]]:
    """
    Validate before executing:
      - target format 'device.param'
      - device exists
      - param exists if we have a whitelist (from registry metadata)
      - values respect interlock limits (for constants)
      - timing fields are numeric
    """
    issues: List[str] = []
    device_names = set(devices.keys())
    param_whitelist = param_whitelist or {}

    if not isinstance(steps, list):
        issues.append("Recipe root must be a list of steps.")
        return False, issues

    for _, target, value in _iter_set_ops(steps):
        if "." not in target:
            issues.append(f"Invalid target '{target}'. Use device.param (e.g., laser.power).")
            continue
        dev_name, param = target.split(".", 1)
        if dev_name not in device_names:
            issues.append(f"Unknown device '{dev_name}' in recipe.")
            continue
        allowed = param_whitelist.get(dev_name)
        if isinstance(allowed, (list, tuple, set)) and param not in allowed:
            issues.append(f"Unknown parameter '{param}' for device '{dev_name}'. Allowed: {sorted(allowed)}")
            continue
        cmd = {"device": dev_name, "action": "set", "param": param, "value": value}
        ok, why = interlock_check(cmd)
        if not ok:
            issues.append(f"{dev_name}.{param}={value} blocked: {why}")

    for step in steps:
        at_ms = step.get("at_ms")
        if at_ms is not None:
            try:
                float(at_ms)
            except Exception:
                issues.append(f"at_ms must be numeric; got '{at_ms}'")

    return (len(issues) == 0), issues

def execute_recipe(steps: list[dict], devices: Dict[str, Any], interlock_check) -> None:
    """Supports timed 'at', 'set', and 'status' steps with guards."""
    start = time.monotonic()
    for idx, step in enumerate(steps):
        at_ms = step.get("at_ms")
        if at_ms is not None:
            t_target = start + (float(at_ms) / 1000.0)
            while time.monotonic() < t_target:
                time.sleep(0.001)

        set_ops = step.get("set", {}) or {}
        for target, value in set_ops.items():
            if "." not in target:
                print(f"[step {idx}] SKIP invalid target '{target}' (use device.param).")
                continue
            dev_name, param = target.split(".", 1)
            dev = devices.get(dev_name)
            if dev is None:
                print(f"[step {idx}] SKIP unknown device '{dev_name}'.")
                continue
            cmd = {"device": dev_name, "action": "set", "param": param, "value": value}
            ok, why = interlock_check(cmd)
            if not ok:
                print(f"BLOCKED: {why}")
                continue
            try:
                dev.set(**{param: value})
            except Exception as e:
                print(f"[step {idx}] ERROR applying {dev_name}.{param}={value}: {e}")

        for name in step.get("status", []):
            dev = devices.get(name)
            if dev is None:
                print(f"[step {idx}] SKIP status for unknown device '{name}'.")
                continue
            try:
                st = dev.status()
                print(f"[status] {name}: {st}")
            except Exception as e:
                print(f"[step {idx}] ERROR status for '{name}': {e}")
