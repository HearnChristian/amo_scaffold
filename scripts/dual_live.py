import os, math, time, argparse
from collections import deque

p = argparse.ArgumentParser()
p.add_argument("--save", metavar="PATH")
p.add_argument("--seconds", type=float, default=6.0)
p.add_argument("--fps", type=int, default=10)
p.add_argument("--width", type=int, default=560)
p.add_argument("--height", type=int, default=315)
p.add_argument("--dpi", type=int, default=72)
p.add_argument("--colors", type=int, default=96)
p.add_argument("--max-mb", type=float, default=9.5)
p.add_argument("--no-wire", action="store_true", default=True)
args = p.parse_args()

import matplotlib
if args.save: matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from PIL import Image, ImageSequence

from amo.hw.dds_sim import SimDDS

def rot(theta_deg: float) -> np.ndarray:
    t = np.deg2rad(theta_deg); c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]], dtype=complex)

def jones_waveplate(theta_deg: float, retard_deg: float) -> np.ndarray:
    R, Rm = rot(theta_deg), rot(-theta_deg)
    phi = np.deg2rad(retard_deg)
    Jd = np.array([[1.0, 0.0], [0.0, np.exp(1j*phi)]], dtype=complex)
    return R @ Jd @ Rm

def stokes(E: np.ndarray) -> np.ndarray:
    Ex, Ey = E[0], E[1]
    S0 = (np.abs(Ex)**2 + np.abs(Ey)**2).real
    S1 = (np.abs(Ex)**2 - np.abs(Ey)**2).real
    S2 = (2*np.real(Ex*np.conj(Ey))).real
    S3 = (-2*np.imag(Ex*np.conj(Ey))).real
    return np.array([S0, S1, S2, S3], dtype=float)

# --- device / buffers
d = SimDDS(); CH = 0
N = 300
xs = deque(maxlen=N); yf = deque(maxlen=N); yp = deque(maxlen=N); ya = deque(maxlen=N); yP = deque(maxlen=N)
t0 = time.time()

# --- figure
w_in = max(2, args.width / args.dpi); h_in = max(2, args.height / args.dpi)
fig = plt.figure(figsize=(w_in, h_in), dpi=args.dpi)
fig.patch.set_facecolor("white")
gs = fig.add_gridspec(2, 3)

ax_f = fig.add_subplot(gs[0, 1])
ax_p = fig.add_subplot(gs[0, 2])
ax_a = fig.add_subplot(gs[1, 1])
ax_P = fig.add_subplot(gs[1, 2])
for ax in (ax_f, ax_p, ax_a, ax_P):
    ax.set_facecolor("white"); ax.grid(True, alpha=0.3)
ax_f.set_title("Frequency (Hz)")
ax_p.set_title("Phase (deg)")
ax_a.set_title("Amplitude (0–1)")
ax_P.set_title("Power (arb)")
ax_p.set_ylim(0, 360); ax_a.set_ylim(0, 1.05)
lines = {"f": ax_f.plot([], [])[0], "phase": ax_p.plot([], [])[0],
         "amp": ax_a.plot([], [])[0], "power": ax_P.plot([], [])[0]}

ax3 = fig.add_subplot(gs[:, 0], projection='3d')
ax3.set_xlim(-1, 1); ax3.set_ylim(-1, 1); ax3.set_zlim(-1, 1)
ax3.set_xlabel('S1'); ax3.set_ylabel('S2'); ax3.set_zlabel('S3'); ax3.set_title('Poincaré – DDS-driven')
if not args.no_wire:
    u = np.linspace(0, 2*np.pi, 48); v = np.linspace(0, np.pi, 24)
    xsph = np.outer(np.cos(u), np.sin(v)); ysph = np.outer(np.sin(u), np.sin(v)); zsph = np.outer(np.ones_like(u), np.cos(v))
    ax3.plot_wireframe(xsph, ysph, zsph, linewidth=0.2, alpha=0.25)
dot, = ax3.plot([], [], [], marker='o', markersize=5)
path, = ax3.plot([], [], [], linewidth=1.2)
px, py, pz = [], [], []
E0 = np.array([1.0, 0.0], dtype=complex)

def step(i: int):
    freq  = 1_000_000 + 800_000 * np.sin(i * 0.05)
    phase = (i * 7.0) % 360.0
    amp   = np.clip(0.5 + 0.45 * np.sin(i * 0.07), 0.0, 1.0)

    d.set_frequency(CH, float(freq)); d.set_phase(CH, float(phase)); d.set_amplitude(CH, float(amp)); d.apply_update()
    s = d.read_state(); ch = s["ch"][CH]; now = time.time() - t0

    xs.append(now); yf.append(ch["f_Hz"]); yp.append(ch["phase_deg"]); ya.append(ch["amp"]); yP.append(ch["power_est"])
    lines["f"].set_data(xs, yf); lines["phase"].set_data(xs, yp); lines["amp"].set_data(xs, ya); lines["power"].set_data(xs, yP)
    for ax in (ax_f, ax_p, ax_a, ax_P):
        if xs: ax.set_xlim(xs[0], max(xs[-1], xs[0] + 1.0))
    if yf:
        lo, hi = min(yf), max(yf); pad = 0.05 * max(1.0, hi - lo); ax_f.set_ylim(lo - pad, hi + pad)
    if yP:
        lo, hi = min(yP), max(yP); pad = 0.1 * max(1.0, hi - lo); ax_P.set_ylim(lo - pad, hi + pad)

    theta = phase / 2.0; retard = 180.0 * amp
    E = jones_waveplate(theta, retard) @ E0
    S = stokes(E); s1, s2, s3 = (0.0, 0.0, 0.0) if S[0] <= 0 else (S[1:] / S[0])
    px.append(float(s1)); py.append(float(s2)); pz.append(float(s3))
    dot.set_data([s1], [s2]); dot.set_3d_properties([s3]); path.set_data(px, py); path.set_3d_properties(pz)

def _figure_rgb(fig):
    """Backend-safe RGB capture."""
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    if hasattr(fig.canvas, "tostring_rgb"):
        buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8).reshape(h, w, 3)
        return buf
    if hasattr(fig.canvas, "tostring_argb"):
        argb = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8).reshape(h, w, 4)
        # ARGB -> RGB
        return argb[:, :, 1:4]
    if hasattr(fig.canvas, "buffer_rgba"):
        rgba = np.asarray(fig.canvas.buffer_rgba())
        return rgba[:, :, :3]
    raise RuntimeError("No canvas capture method available")

def save_gif(path: str):
    frames = int(max(1, args.seconds * args.fps))
    method = getattr(Image, "FASTOCTREE", 0)
    captured = []
    for i in range(frames):
        step(i)
        rgb = _figure_rgb(fig)
        im = Image.fromarray(rgb)
        if args.colors < 256:
            im = im.quantize(colors=max(2, args.colors), method=method)
        captured.append(im)
    duration = int(1000 / max(1, args.fps))
    captured[0].save(path, save_all=True, append_images=captured[1:], loop=0,
                     optimize=True, duration=duration, disposal=2)

    # enforce size limit by thinning frames progressively
    max_bytes = int(args.max_mb * 1024 * 1024)
    tries = 0
    while os.path.getsize(path) > max_bytes and len(captured) > 2 and tries < 5:
        tries += 1
        thinned = captured[::2]
        dur = int(1000 / max(1, args.fps // (2**tries)))
        thinned[0].save(path, save_all=True, append_images=thinned[1:], loop=0,
                        optimize=True, duration=dur, disposal=2)

if args.save:
    save_gif(args.save)
    print(f"Saved {args.save} ({os.path.getsize(args.save)/1024/1024:.2f} MB)")
else:
    import matplotlib.animation as manim
    from matplotlib.animation import FuncAnimation
    ani = FuncAnimation(fig, lambda i: (step(i),)[0], interval=50, blit=False)
    plt.tight_layout()
    plt.show()
