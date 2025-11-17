from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any, Optional

from .block import Block, Backend
from .light import LightState


Hook = Callable[[Block, LightState], None]


@dataclass
class Pipeline:
    """
    Ordered list of blocks.
    """

    blocks: List[Block] = field(default_factory=list)

    def run(
        self,
        light_in: LightState,
        backend: Backend,
        hooks: Optional[Dict[str, Hook]] = None,
    ) -> LightState:
        light = light_in.copy()
        hooks = hooks or {}

        for block in self.blocks:
            light = backend.apply(block, light)
            if block.id in hooks:
                hooks[block.id](block, light)
        return light

    def add(self, block: Block) -> None:
        self.blocks.append(block)

    def by_id(self, block_id: str) -> Block:
        for b in self.blocks:
            if b.id == block_id:
                return b
        raise KeyError(f"Block '{block_id}' not found")
