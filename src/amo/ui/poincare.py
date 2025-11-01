import numpy as np
import matplotlib.pyplot as plt

def plot_stokes_path(S_list):
    """S_list: iterable of [S0,S1,S2,S3]"""
    pts = []
    for S in S_list:
        S0 = S[0] if S[0] != 0 else 1.0
        pts.append(np.array(S[1:4], dtype=float) / float(S0))
    pts = np.array(pts)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # unit sphere wireframe
    u = np.linspace(0, 2*np.pi, 64)
    v = np.linspace(0, np.pi, 32)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x, y, z, linewidth=0.3, alpha=0.3)

    # path
    ax.plot(pts[:,0], pts[:,1], pts[:,2], marker='o')
    ax.set_xlabel('S1')
    ax.set_ylabel('S2')
    ax.set_zlabel('S3')
    ax.set_title('Poincaré Path')
    plt.show()
