from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List

from amo_digital_twin.core.pipeline import Pipeline
from amo_digital_twin.blocks.registry import BlockSpec, default_block_registry


@dataclass
class CircuitConfig:
    name: str
    blocks: List[BlockSpec] = field(default_factory=list)


def load_circuit_config(path: str | Path) -> CircuitConfig:
    p = Path(path)
    data = json.loads(p.read_text())

    name = data.get("name", p.stem)
    blocks_raw: List[Dict[str, Any]] = data.get("blocks", [])
    blocks = [
        BlockSpec(
            id=b["id"],
            type=b["type"],
            params=b.get("params", {}),
        )
        for b in blocks_raw
    ]

    return CircuitConfig(name=name, blocks=blocks)


def build_pipeline_from_config(cfg: CircuitConfig) -> Pipeline:
    reg = default_block_registry()
    pipe = Pipeline()
    for spec in cfg.blocks:
        block = reg.create(spec)
        pipe.add(block)
    return pipe
