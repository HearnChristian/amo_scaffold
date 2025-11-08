import numpy as np

def rot(theta_deg: float) -> np.ndarray:
    t = np.deg2rad(theta_deg)
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]], dtype=complex)

def jones_waveplate(theta_deg: float, retard_deg: float) -> np.ndarray:
    R = rot(theta_deg)
    Rm = rot(-theta_deg)
    phi = np.deg2rad(retard_deg)
    Jd = np.array([[1.0, 0.0], [0.0, np.exp(1j * phi)]], dtype=complex)
    return R @ Jd @ Rm

def jones_polarizer(theta_deg: float) -> np.ndarray:
    R = rot(theta_deg)
    Rm = rot(-theta_deg)
    P = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    return R @ P @ Rm

def apply_chain(jones_chain, E0: np.ndarray) -> np.ndarray:
    E = E0.astype(complex)
    for J in jones_chain:
        E = J @ E
    return E