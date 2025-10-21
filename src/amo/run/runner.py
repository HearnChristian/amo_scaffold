import time, json, pathlib, yaml
from typing import Dict, Any

def new_run_dir(base: str = "data") -> pathlib.Path:
    d = pathlib.Path(base) / time.strftime("%Y%m%d_%H%M%S")
    d.mkdir(parents=True, exist_ok=True)
    return d

def save_params(run_dir: pathlib.Path, params: Dict[str, Any]) -> None:
    (run_dir / "params.json").write_text(json.dumps(params, indent=2))

def save_environment(run_dir: pathlib.Path, env: Dict[str, Any]) -> None:
    (run_dir / "environment.json").write_text(json.dumps(env, indent=2))

def load_recipe(path: str) -> list[dict]:
    with open(path, "r") as f:
        return yaml.safe_load(f) or []

def execute_recipe(steps: list[dict], devices: Dict[str, Any], interlock_check) -> None:
    start = time.monotonic()
    for step in steps:
        at_ms = step.get("at_ms")
        if at_ms is not None:
            t_target = start + (float(at_ms) / 1000.0)
            while time.monotonic() < t_target:
                time.sleep(0.001)

        for target, value in step.get("set", {}).items():
            dev_name, param = target.split(".", 1)
            cmd = {"device": dev_name, "action": "set", "param": param, "value": value}
            ok, why = interlock_check(cmd)
            if not ok:
                print(f"BLOCKED: {why}")
                continue
            devices[dev_name].set(**{param: value})

        for name in step.get("status", []):
            print(f"[status] {name}: {devices[name].status()}")
