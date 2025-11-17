from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Type, List

from .basic_optics import (
    Laser,
    HalfWavePlate,
    QuarterWavePlate,
    GenericRetarder,
    PolarizationRotator,
    GlobalPhase,
    JonesElement,
    Polarizer,
    Mirror,
    NeutralDensityFilter,
    PowerDetector,
)
from amo_digital_twin.core.block import Block


@dataclass
class BlockSpec:
    """
    Declarative description of one block in a circuit.

    Fields:
      - id: unique block id in the circuit
      - type: registry key (e.g. "laser", "hwp", "polarizer")
      - params: kwargs passed to the block constructor
    """

    id: str
    type: str
    params: Dict[str, Any] = field(default_factory=dict)


class BlockRegistry:
    """
    Maps simple string 'type' keys to Block subclasses,
    and builds Block instances from BlockSpec.
    """

    def __init__(self) -> None:
        self._types: Dict[str, Type[Block]] = {}

    def register(self, type_name: str, cls: Type[Block]) -> None:
        self._types[type_name] = cls

    def create(self, spec: BlockSpec) -> Block:
        if spec.type not in self._types:
            raise KeyError(f"Unknown block type '{spec.type}' for id '{spec.id}'")
        cls = self._types[spec.type]
        kwargs = dict(spec.params)
        kwargs.setdefault("id", spec.id)
        return cls(**kwargs)  # type: ignore[arg-type]


def default_block_registry() -> BlockRegistry:
    reg = BlockRegistry()
    reg.register("laser", Laser)
    reg.register("hwp", HalfWavePlate)
    reg.register("qwp", QuarterWavePlate)
    reg.register("retarder", GenericRetarder)
    reg.register("pol_rotator", PolarizationRotator)
    reg.register("global_phase", GlobalPhase)
    reg.register("jones", JonesElement)
    reg.register("polarizer", Polarizer)
    reg.register("mirror", Mirror)
    reg.register("nd", NeutralDensityFilter)
    reg.register("power_detector", PowerDetector)
    return reg
