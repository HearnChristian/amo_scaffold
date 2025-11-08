import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# keep a module-level handle so GC doesn't kill the animation
_anim_handle = None

def animate_stokes(sweep_S_list, interval_ms=100, title="Poincaré Animation"):
    """
    sweep_S_list: list of [S0,S1,S2,S3] over time (frames)
    """
    pts = []
    for S in sweep_S_list:
        S0 = S[0] if S[0] != 0 else 1.0
        pts.append(np.array(S[1:4], dtype=float) / float(S0))
    pts = np.array(pts)

    if len(pts) < 2:
        raise ValueError("Need at least 2 frames to animate (check your --sweep range)")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # unit sphere wireframe
    u = np.linspace(0, 2*np.pi, 64)
    v = np.linspace(0, np.pi, 32)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x, y, z, linewidth=0.3, alpha=0.25)

    # animated artists
    dot, = ax.plot([], [], [], marker='o', linestyle='None')
    path, = ax.plot([], [], [], linewidth=1.5)

    ax.set_xlim(-1,1)
    ax.set_ylim(-1,1)
    ax.set_zlim(-1,1)
    ax.set_xlabel('S1')
    ax.set_ylabel('S2')
    ax.set_zlabel('S3')
    ax.set_title(title)

    xs, ys, zs = [], [], []

    def init():
        dot.set_data([], [])
        dot.set_3d_properties([])
        path.set_data([], [])
        path.set_3d_properties([])
        return dot, path

    def update(frame):
        xs.append(pts[frame,0])
        ys.append(pts[frame,1])
        zs.append(pts[frame,2])
        dot.set_data([pts[frame,0]], [pts[frame,1]])
        dot.set_3d_properties([pts[frame,2]])
        path.set_data(xs, ys)
        path.set_3d_properties(zs)
        return dot, path

    global _anim_handle
    _anim_handle = FuncAnimation(fig, update, init_func=init,
                                 frames=len(pts), interval=interval_ms,
                                 blit=False, repeat=True)
    plt.show()
    return _anim_handle
