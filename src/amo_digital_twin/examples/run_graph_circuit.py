from __future__ import annotations

import sys
import json

from amo_digital_twin.blocks.beam_splitters import NPBS50, PBS
from amo_digital_twin.blocks.multi_optics import Source, MirrorMP, PowerDetectorMP
from amo_digital_twin.core.graph_pipeline import GraphPipeline
from amo_digital_twin.core.multiblock import MultiPortBlock
from amo_digital_twin.core.light import LightState


TYPE_MAP = {
    "laser": Source,
    "source": Source,
    "npbs50": NPBS50,
    "pbs": PBS,
    "mirror": MirrorMP,
    "power_detector": PowerDetectorMP,
}


def build_block(bconf: dict) -> MultiPortBlock:
    btype = bconf["type"]
    bid = bconf["id"]
    params = bconf.get("params", {})
    if btype not in TYPE_MAP:
        raise KeyError(f"Unknown block type '{btype}' in graph config")
    cls = TYPE_MAP[btype]
    return cls(id=bid, **params)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: amo-run-graph-circuit <config.json>")
        raise SystemExit(1)

    config_path = sys.argv[1]
    with open(config_path, "r") as f:
        cfg = json.load(f)

    gp = GraphPipeline()

    # Build blocks
    for b in cfg["blocks"]:
        blk = build_block(b)
        gp.add_block(blk)

    # Build connections: [src_block, src_port, dst_block, dst_port]
    for c in cfg["connections"]:
        src_id, src_port, dst_id, dst_port = c
        gp.connect(src_id, int(src_port), dst_id, int(dst_port))

    # Seed source input with a dummy LightState (ignored by Source)
    inputs = {"laser1": {0: LightState()}}

    outputs = gp.run(inputs)

    print("=== Graph circuit outputs ===")
    for blk_id, ports in outputs.items():
        for port_idx, ls in ports.items():
            if ls is None:
                continue
            power = ls.meta.get("power_mw", None)
            print(f"{blk_id}[{port_idx}]: power_mW={power}, E={ls.E}")
