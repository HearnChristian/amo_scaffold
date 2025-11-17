from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Any

from amo_digital_twin.core.light import LightState
from amo_digital_twin.core.multiblock import MultiPortBlock


@dataclass
class Connection:
    src_block: str
    src_port: int
    dst_block: str
    dst_port: int


@dataclass
class GraphPipeline:
    blocks: Dict[str, MultiPortBlock] = field(default_factory=dict)
    connections: List[Connection] = field(default_factory=list)

    def add_block(self, block: MultiPortBlock) -> None:
        self.blocks[block.id] = block

    def connect(self, src_id: str, src_port: int, dst_id: str, dst_port: int) -> None:
        self.connections.append(Connection(src_id, src_port, dst_id, dst_port))

    def run(self, inputs: Dict[str, Dict[int, LightState]]) -> Dict[str, Dict[int, LightState]]:
        """
        Propagate through the DAG.
        inputs: dict[block_id][port_index] = LightState
        returns: dict[block_id][port_index] = LightState (final outputs per block)
        """

        # Initialize per-block port buffers
        port_in = {bid: {} for bid in self.blocks}
        for bid, ports in inputs.items():
            port_in[bid] = dict(ports)

        # Topological-ish execution: keep looping until no changes
        stable = False
        while not stable:
            stable = True
            for cid in self.blocks:
                block = self.blocks[cid]
                if any(p in port_in[cid] for p in range(block.n_in)):
                    out = block.apply(port_in[cid])
                    for port_idx in out:
                        # transmit forward along connections
                        for C in self.connections:
                            if C.src_block == cid and C.src_port == port_idx:
                                dst = C.dst_block
                                dst_port = C.dst_port
                                if out[port_idx] is None:
                                    continue
                                prev = port_in[dst].get(dst_port)
                                if prev is None:
                                    port_in[dst][dst_port] = out[port_idx]
                                    stable = False

        return port_in
