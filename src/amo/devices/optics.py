from __future__ import annotations
import numpy as np
from typing import Tuple
from amo.optics.polarimetry import rot, jones_waveplate, jones_polarizer, stokes

class Waveplate:
    """
    Generic waveplate.
    theta_deg: optic axis angle (deg) w.r.t. x
    retard_deg: retardance (e.g., 180 for HWP, 90 for QWP)
    """
    def __init__(self, theta_deg: float, retard_deg: float):
        self.theta = float(theta_deg)
        self.retard = float(retard_deg)

    def jones(self) -> np.ndarray:
        return jones_waveplate(self.theta, self.retard)

    def apply(self, E: np.ndarray) -> np.ndarray:
        return self.jones() @ E

class Polarizer:
    """
    Ideal linear polarizer transmitting along angle theta_deg.
    """
    def __init__(self, theta_deg: float):
        self.theta = float(theta_deg)

    def jones(self) -> np.ndarray:
        return jones_polarizer(self.theta)

    def apply(self, E: np.ndarray) -> np.ndarray:
        return self.jones() @ E

class PBS:
    """
    Ideal polarizing beamsplitter oriented by theta_deg.
    Splits the input into two ports:
      - T (transmit) projects onto axis at theta_deg
      - R (reflect) projects onto orthogonal axis at theta_deg + 90
    A simple phase for reflection can be included (default +i).
    """
    def __init__(self, theta_deg: float = 0.0, reflect_phase: complex = 1j):
        self.theta = float(theta_deg)
        self._phiR = reflect_phase

        R  = rot(self.theta)
        Rm = rot(-self.theta)
        P0   = np.array([[1.0, 0.0],[0.0, 0.0]], dtype=complex)  # projector onto x
        P90  = np.array([[0.0, 0.0],[0.0, 1.0]], dtype=complex)  # projector onto y
        self._PT = R @ P0  @ Rm     # transmit projector
        self._PR = R @ P90 @ Rm     # reflect projector

    def route(self, E: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Return (E_T, E_R)."""
        ET = self._PT @ E
        ER = self._phiR * (self._PR @ E)
        return ET, ER

    def power(self, E: np.ndarray) -> Tuple[float, float]:
        ET, ER = self.route(E)
        ST, SR = stokes(ET), stokes(ER)
        return float(ST[0]), float(SR[0])  # S0 is total intensity
