import asyncio, os
import yaml
from amo.ui.cli import build_parser
from amo.io.registry import REGISTRY
from amo.control import interlocks
from amo.run.runner import new_run_dir, save_params, save_environment, load_recipe, execute_recipe, preflight

def make_devices():
    devices = {}
    for name, spec in REGISTRY.items():
        drv_cls = spec["driver"]; conn = spec.get("connect", {})
        d = drv_cls(**conn) if conn else drv_cls()
        d.connect()
        devices[name] = d
    return devices

def _known_devices_msg(devices):
    return "Known devices: " + ", ".join(sorted(devices.keys())) if devices else "No devices are registered."

def _allowed_params_for(device_name: str):
    meta = REGISTRY.get(device_name, {}).get("metadata", {})
    params = meta.get("params")
    return set(params) if isinstance(params, (list, tuple, set)) else None

def _split_target_or_explain(target: str):
    if "." not in target:
        print(f"Invalid target '{target}'. Use the format device.param (e.g., laser.power).")
        return None, None
    return target.split(".", 1)

async def run_set(devices, target, value):
    dev, param = _split_target_or_explain(target)
    if dev is None: return
    if dev not in devices:
        print(f"Unknown device '{dev}'. {_known_devices_msg(devices)}")
        return
    allowed = _allowed_params_for(dev)
    if allowed is not None and param not in allowed:
        print(f"Unknown parameter '{param}' for device '{dev}'. Allowed: {sorted(allowed)}")
        return
    cmd = {"device": dev, "action": "set", "param": param, "value": value}
    ok, why = interlocks.check(cmd)
    if not ok:
        print("BLOCKED:", why); return
    try:
        devices[dev].set(**{param: value})
        print("OK")
    except Exception as e:
        print(f"Error applying {dev}.{param}={value}: {e}")

async def run_get(devices, target):
    dev, param = _split_target_or_explain(target)
    if dev is None: return
    if dev not in devices:
        print(f"Unknown device '{dev}'. {_known_devices_msg(devices)}")
        return
    allowed = _allowed_params_for(dev)
    if allowed is not None and param not in allowed:
        print(f"Unknown parameter '{param}' for device '{dev}'. Allowed: {sorted(allowed)}")
        return
    try:
        val = devices[dev].get(param)
        if val is None:
            print(f"{dev}.{param} is not a known readable parameter (returned None).")
        else:
            print(val)
    except Exception as e:
        print(f"Error reading {dev}.{param}: {e}")

async def run_status(devices, device):
    if device not in devices:
        print(f"Unknown device '{device}'. {_known_devices_msg(devices)}")
        return
    try:
        print(devices[device].status())
    except Exception as e:
        print(f"Error fetching status for '{device}': {e}")

async def run_recipe(devices, path):
    # Load recipe with friendly errors
    try:
        steps = load_recipe(path)
    except FileNotFoundError:
        print(f"Recipe not found: {path}")
        return
    except yaml.YAMLError as e:
        print(f"YAML error in '{path}': {e}")
        return

    # Build param whitelist for preflight from registry metadata
    param_whitelist = {
        name: set(spec.get("metadata", {}).get("params", []))
        for name, spec in REGISTRY.items()
        if isinstance(spec.get("metadata", {}).get("params"), (list, tuple, set))
    }

    # Preflight validation
    ok, issues = preflight(steps, devices, interlocks.check, param_whitelist=param_whitelist)
    if not ok:
        print("Recipe validation failed:")
        for msg in issues:
            print(" -", msg)
        return

    # Create run dir + save metadata with friendly permission handling
    try:
        run_dir = new_run_dir()
    except PermissionError:
        print("Cannot create run directory under 'data/'. Check folder permissions (write access required).")
        return

    save_params(run_dir, {"recipe_path": path})
    save_environment(run_dir, {"cwd": os.getcwd()})
    execute_recipe(steps, devices, interlocks.check)
    print(f"Saved run to {run_dir}")

def cli_entry():
    parser = build_parser()
    args = parser.parse_args()
    devices = make_devices()
    if args.cmd == "set":
        asyncio.run(run_set(devices, args.target, args.value))
    elif args.cmd == "get":
        asyncio.run(run_get(devices, args.target))
    elif args.cmd == "status":
        asyncio.run(run_status(devices, args.device))
    elif args.cmd == "run":
        asyncio.run(run_recipe(devices, args.recipe_path))

if __name__ == "__main__":
    cli_entry()
