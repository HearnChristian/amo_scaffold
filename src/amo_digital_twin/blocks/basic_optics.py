from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from ..core.block import Block
from ..core.light import LightState


@dataclass
class Laser(Block):
    """
    Simple linearly polarized laser.

    params:
      - power_mw
      - pol_angle_deg  (0° = x, 90° = y)
      - wavelength_m
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="laser", params=params)

    def _apply_pol(self, light: LightState) -> LightState:
        angle_deg = float(self.params.get("pol_angle_deg", 0.0))
        power_mw = float(self.params.get("power_mw", 1.0))
        wavelength_m = float(self.params.get("wavelength_m", 1064e-9))

        angle_rad = np.deg2rad(angle_deg)
        E = np.array([np.cos(angle_rad), np.sin(angle_rad)], dtype=np.complex128)

        out = light.copy()
        out.mode = "POL"
        out.wavelength_m = wavelength_m
        out.E = E
        out.dir = np.array([0.0, 0.0, 1.0])
        out.meta["power_mw"] = power_mw
        return out


@dataclass
class HalfWavePlate(Block):
    """
    Ideal half-wave plate.

    params:
      - angle_deg: fast axis angle in degrees.
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="hwp", params=params)

    def _apply_pol(self, light: LightState) -> LightState:
        out = light.copy()
        if out.E is None:
            return out

        angle_deg = float(self.params.get("angle_deg", 0.0))
        theta = np.deg2rad(angle_deg)

        c = np.cos(theta)
        s = np.sin(theta)
        R = np.array([[c, -s], [s, c]], dtype=np.complex128)
        J = R.T @ np.diag([1.0, -1.0]) @ R

        out.E = J @ out.E
        return out

@dataclass
class QuarterWavePlate(Block):
    """
    Ideal quarter-wave plate.

    params:
      - angle_deg: fast axis angle in degrees, measured from x axis.

    Physically:
      - angle ~45° turns linear polarization into circular.
      - angle ~0° or 90° adds a 90° phase shift between x and y.
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="qwp", params=params)

    def _apply_pol(self, light: LightState) -> LightState:
        out = light.copy()
        if out.E is None:
            return out

        angle_deg = float(self.params.get("angle_deg", 0.0))
        theta = np.deg2rad(angle_deg)

        # Jones for ideal QWP with fast axis at angle theta.
        # J = R(-θ) @ diag(1, i) @ R(θ)
        c = np.cos(theta)
        s = np.sin(theta)
        R = np.array([[c, -s], [s, c]], dtype=np.complex128)
        J_ret = np.diag([1.0 + 0.0j, 1.0j])
        J = R.T @ J_ret @ R

        out.E = J @ out.E
        return out

@dataclass
class GenericRetarder(Block):
    """
    Generic linear retarder.

    params:
      - angle_deg: fast axis angle in degrees (0° = x)
      - retardance_rad: phase delay in radians between fast and slow axes

    Special cases:
      - retardance_rad = pi   -> ideal half-wave plate (HWP)
      - retardance_rad = pi/2 -> ideal quarter-wave plate (QWP)
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="retarder", params=params)

    def _apply_pol(self, light: LightState) -> LightState:
        out = light.copy()
        if out.E is None:
            return out

        angle_deg = float(self.params.get("angle_deg", 0.0))
        retardance_rad = float(self.params.get("retardance_rad", 0.0))

        theta = np.deg2rad(angle_deg)

        # J = R(-θ) @ diag(1, e^{iδ}) @ R(θ)
        c = np.cos(theta)
        s = np.sin(theta)
        R = np.array([[c, -s], [s, c]], dtype=np.complex128)
        J_ret = np.diag([1.0 + 0.0j, np.exp(1j * retardance_rad)])
        J = R.T @ J_ret @ R

        out.E = J @ out.E
        return out

@dataclass
class PolarizationRotator(Block):
    """
    Pure polarization rotator.

    params:
      - angle_deg: rotation angle applied to the polarization state.

    This rotates the Jones vector by a real 2D rotation, without adding
    differential phase (unlike a retarder).
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="pol_rotator", params=params)

    def _apply_pol(self, light: LightState) -> LightState:
        out = light.copy()
        if out.E is None:
            return out

        angle_deg = float(self.params.get("angle_deg", 0.0))
        theta = np.deg2rad(angle_deg)

        c = np.cos(theta)
        s = np.sin(theta)
        R = np.array([[c, -s], [s, c]], dtype=np.complex128)

        out.E = R @ out.E
        return out

@dataclass
class GlobalPhase(Block):
    """
    Global phase shifter.

    params:
      - phase_rad: global phase in radians

    This does not change power or polarization, only the overall phase of E.
    Useful for interference / multi-path simulations later.
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="global_phase", params=params)

    def _apply_pol(self, light: LightState) -> LightState:
        out = light.copy()
        if out.E is None:
            return out

        phase_rad = float(self.params.get("phase_rad", 0.0))
        out.E = np.exp(1j * phase_rad) * out.E
        # power |E|^2 is unchanged; meta["power_mw"] left as-is
        return out

@dataclass
class JonesElement(Block):
    """
    Arbitrary Jones matrix element.

    params:
      - matrix: 2x2 complex-like array (nested lists acceptable), applied as:
          E_out = matrix @ E_in

    Example usage in code:
      JonesElement(
          "j1",
          matrix=[[1.0, 0.0], [0.0, 1.0j]],
      )

    Note:
      Parameters must be JSON-serializable if you want to dump configs;
      you can store complex numbers as [real, imag] pairs if needed and
      convert to complex inside this block.
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="jones", params=params)

    def _apply_pol(self, light: LightState) -> LightState:
        out = light.copy()
        if out.E is None:
            return out

        raw_mat = self.params.get("matrix", None)
        if raw_mat is None:
            # No-op if no matrix provided
            return out

        M = np.array(raw_mat, dtype=np.complex128).reshape(2, 2)
        out.E = M @ out.E
        return out


@dataclass
class NeutralDensityFilter(Block):
    """
    Neutral density filter (attenuator).

    params:
      - optical_density: OD value, where T = 10^(-OD) is the intensity transmission.

    This scales the field amplitude by sqrt(T) and the stored power by T,
    without changing polarization.
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="nd_filter", params=params)

    def _apply_pol(self, light: LightState) -> LightState:
        out = light.copy()
        od = float(self.params.get("optical_density", 0.0))
        T = 10.0 ** (-od)  # intensity transmission

        if out.E is not None:
            out.E = np.sqrt(T) * out.E

        power = out.meta.get("power_mw")
        if power is not None:
            out.meta["power_mw"] = T * power

        return out

@dataclass
class Mirror(Block):
    """
    Simple mirror that flips z-direction.

    params:
      - reflectivity [0,1]
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="mirror", params=params)

    def _apply_pol(self, light: LightState) -> LightState:
        out = light.copy()
        R = float(self.params.get("reflectivity", 0.999))

        if out.E is not None:
            out.E = np.sqrt(R) * out.E
        if out.dir is not None:
            d = out.dir
            out.dir = np.array([d[0], d[1], -d[2]])
        power = out.meta.get("power_mw")
        if power is not None:
            out.meta["power_mw"] = R * power
        return out


@dataclass
class PowerDetector(Block):
    """
    Simple power detector.

    Stores last reading in params["last_reading_mw"].
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="power_detector", params=params)

    def _apply_pol(self, light: LightState) -> LightState:
        out = light.copy()
        power = out.meta.get("power_mw", None)
        self.params["last_reading_mw"] = power
        return out
class Polarizer(Block):
    """
    Ideal linear polarizer.

    params:
      - axis_deg: transmission axis angle in degrees (0° = x, 90° = y)
      - efficiency: scalar [0,1] (throughput for aligned pol.)
    """

    def __init__(self, id: str, **params: Any) -> None:
        super().__init__(id=id, kind="polarizer", params=params)

    def _apply_pol(self, light: LightState) -> LightState:
        out = light.copy()
        if out.E is None:
            return out

        axis_deg = float(self.params.get("axis_deg", 0.0))
        eff = float(self.params.get("efficiency", 1.0))

        theta = np.deg2rad(axis_deg)
        # Unit vector along transmission axis
        a = np.array([np.cos(theta), np.sin(theta)], dtype=np.complex128)

        # Project E onto axis and scale
        amp = np.vdot(a, out.E)  # inner product
        out.E = eff * amp * a

        # Update power estimate (proportional to |E|^2)
        power = out.meta.get("power_mw")
        if power is not None:
            # Transmission is |projection|^2 times efficiency
            trans = float(np.vdot(out.E, out.E).real)
            out.meta["power_mw"] = power * trans

        return out
