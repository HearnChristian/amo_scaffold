import asyncio, os
from amo.ui.cli import build_parser
from amo.io.registry import REGISTRY
from amo.control import interlocks
from amo.run.runner import new_run_dir, save_params, save_environment, load_recipe, execute_recipe

def make_devices():
    devices = {}
    for name, spec in REGISTRY.items():
        drv_cls = spec["driver"]; conn = spec.get("connect", {})
        d = drv_cls(**conn) if conn else drv_cls()
        d.connect()
        devices[name] = d
    return devices

async def run_set(devices, target, value):
    dev, param = target.split(".", 1)
    cmd = {"device": dev, "action": "set", "param": param, "value": value}
    ok, why = interlocks.check(cmd)
    if not ok: print("BLOCKED:", why); return
    devices[dev].set(**{param: value}); print("OK")

async def run_get(devices, target):
    dev, param = target.split(".", 1)
    print(devices[dev].get(param))

async def run_status(devices, device):
    print(devices[device].status())

async def run_recipe(devices, path):
    steps = load_recipe(path)
    run_dir = new_run_dir()
    save_params(run_dir, {"recipe_path": path})
    save_environment(run_dir, {"cwd": os.getcwd()})
    execute_recipe(steps, devices, interlocks.check)
    print(f"Saved run to {run_dir}")

def cli_entry():
    parser = build_parser()
    args = parser.parse_args()
    devices = make_devices()
    if args.cmd == "set": asyncio.run(run_set(devices, args.target, args.value))
    elif args.cmd == "get": asyncio.run(run_get(devices, args.target))
    elif args.cmd == "status": asyncio.run(run_status(devices, args.device))
    elif args.cmd == "run": asyncio.run(run_recipe(devices, args.recipe_path))

if __name__ == "__main__":
    cli_entry()
