import numby as np
import numpy as np

def rot(theta_deg: float) -> np.ndarray:
    t = np.deg2rad(theta_deg); c,s = np.cos(t), np.sin(t)
    return np.array([[c, -s],[s, c]], dtype=complex)

def jones_waveplate(theta_deg: float, retard_deg: float) -> np.ndarray:
    R = rot(theta_deg); Rm = rot(-theta_deg)
    phi = np.deg2rad(retard_deg)
    Jd = np.array([[1.0, 0.0],[0.0, np.exp(1j*phi)]], dtype=complex)
    return R @ Jd @ Rm

def jones_polarizer(theta_deg: float) -> np.ndarray:
    R = rot(theta_deg); Rm = rot(-theta_deg)
    P = np.array([[1.0,0.0],[0.0,0.0]], dtype=complex)
    return R @ P @ Rm

def apply_chain(jones_chain, E0: np.ndarray) -> np.ndarray:
    E = E0.astype(complex)
    for J in jones_chain: E = J @ E
    return E

def stokes(E: np.ndarray) -> np.ndarray:
    Ex,Ey = E[0], E[1]
    S0 = (np.abs(Ex)**2 + np.abs(Ey)**2).real
    S1 = (np.abs(Ex)**2 - np.abs(Ey)**2).real
    S2 = (2*np.real(Ex*np.conj(Ey))).real
    S3 = (-2*np.imag(Ex*np.conj(Ey))).real
    return np.array([S0,S1,S2,S3], dtype=float)

def trace_stokes(nodes, E0: np.ndarray):
    out, E = [], E0.astype(complex)
    for i, n in enumerate(nodes):
        t = n.get("type")
        if t == "waveplate":
            J = jones_waveplate(n["theta"], n["retard"])
        elif t == "polarizer":
            J = jones_polarizer(n["theta"])
        else:
            raise ValueError(f"unknown node type: {t}")
        E = J @ E
        out.append({"node": i, "type": t, "S": stokes(E).tolist()})
    return out
