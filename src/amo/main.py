from __future__ import annotations
from typing import Any, Callable, cast

from amo.io.registry import REGISTRY
from amo.control import interlocks

def _known_devices_msg(devices: dict[str, Any]) -> str:
  return ", ".join(sorted(devices.keys()))

def _split_target_or_explain(target: str) -> tuple[str | None, str | None]:
  if "." not in target:
    print("Target must be 'device.param'")
    return None, None
  dev, param = target.split(".", 1)
  return dev, param

def build_devices() -> dict[str, Any]:
  devices: dict[str, Any] = {}
  for name, spec in REGISTRY.items():
    if not isinstance(spec, dict):
      continue
    drv_cls = spec.get("driver")
    if drv_cls is None:
      continue
    conn = spec.get("connect", {})
    d = drv_cls(**conn) if isinstance(conn, dict) and conn else drv_cls()
    connect = getattr(d, "connect", None)
    if callable(connect):
      cast(Callable[[], Any], connect)()
    devices[name] = d
  return devices

async def run_set(devices: dict[str, Any], target: str, value: float) -> None:
  dev, param = _split_target_or_explain(target)
  if dev is None or param is None:
    return
  if dev not in devices:
    print(f"Unknown device '{dev}'. {_known_devices_msg(devices)}")
    return
  cmd = {"device": dev, "action": "set", "param": param, "value": value}
  ok, why = interlocks.check(cmd)
  if not ok:
    print("BLOCKED:", why)
    return
  setter = getattr(devices[dev], "set", None)
  if callable(setter):
    cast(Callable[..., Any], setter)(**{param: value})

async def run_get(devices: dict[str, Any], target: str) -> None:
  dev, param = _split_target_or_explain(target)
  if dev is None or param is None:
    return
  if dev not in devices:
    print(f"Unknown device '{dev}'. {_known_devices_msg(devices)}")
    return
  getter = getattr(devices[dev], "get", None)
  if callable(getter):
    print(cast(Callable[[str], Any], getter)(param))
