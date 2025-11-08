import time, math
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from amo.hw.dds_sim import SimDDS

# --- device
d = SimDDS()
CH = 0

# --- history buffers
N = 300  # number of points shown
xs = deque(maxlen=N)
yf = deque(maxlen=N)   # frequency (Hz)
yp = deque(maxlen=N)   # phase (deg)
ya = deque(maxlen=N)   # amplitude (0..1)
yP = deque(maxlen=N)   # power estimate

t0 = time.time()

# --- figure
fig, axs = plt.subplots(2, 2, figsize=(10, 6))
(ax_f, ax_p), (ax_a, ax_P) = axs
lines = {
    "f": ax_f.plot([], [])[0],
    "phase": ax_p.plot([], [])[0],
    "amp": ax_a.plot([], [])[0],
    "power": ax_P.plot([], [])[0],
}
ax_f.set_title("Frequency (Hz)")
ax_p.set_title("Phase (deg)")
ax_a.set_title("Amplitude (0–1)")
ax_P.set_title("Power (arb)")

for ax in (ax_f, ax_p, ax_a, ax_P):
    ax.grid(True, alpha=0.3)

# stable y-lims for known ranges
ax_p.set_ylim(0, 360)
ax_a.set_ylim(0, 1.05)

def update(i):
    # simple param trajectories
    freq = 1_000_000 + 800_000 * math.sin(i * 0.05)
    phase = (i * 7.0) % 360.0
    amp = 0.5 + 0.45 * math.sin(i * 0.07)
    amp = max(0.0, min(1.0, amp))

    # push to device and read back
    d.set_frequency(CH, freq)
    d.set_phase(CH, phase)
    d.set_amplitude(CH, amp)
    d.apply_update()
    s = d.read_state()
    ch0 = s["ch"][CH]
    now = time.time() - t0

    xs.append(now)
    yf.append(ch0["f_Hz"])
    yp.append(ch0["phase_deg"])
    ya.append(ch0["amp"])
    yP.append(ch0["power_est"])

    # set data
    lines["f"].set_data(xs, yf)
    lines["phase"].set_data(xs, yp)
    lines["amp"].set_data(xs, ya)
    lines["power"].set_data(xs, yP)

    # x-lims follow the newest data
    for ax in (ax_f, ax_p, ax_a, ax_P):
        if xs:
            ax.set_xlim(xs[0], xs[-1] if xs[-1] > xs[0] else xs[0] + 1.0)

    # dynamic y-lims for frequency/power
    if yf:
        lo, hi = min(yf), max(yf)
        pad = 0.05 * max(1.0, hi - lo)
        ax_f.set_ylim(lo - pad, hi + pad)
    if yP:
        lo, hi = min(yP), max(yP)
        pad = 0.1 * max(1.0, hi - lo)
        ax_P.set_ylim(lo - pad, hi + pad)

    return tuple(lines.values())

ani = FuncAnimation(fig, update, interval=50, blit=False)
plt.tight_layout()
plt.show()
