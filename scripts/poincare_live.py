import sys, numpy as np, matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.animation import FuncAnimation

def rot(theta_deg):
    t=np.deg2rad(theta_deg); c,s=np.cos(t),np.sin(t)
    return np.array([[c,-s],[s,c]], dtype=complex)

def jones_waveplate(theta_deg, retard_deg):
    R=rot(theta_deg); Rm=rot(-theta_deg)
    phi=np.deg2rad(retard_deg)
    Jd=np.array([[1.0,0.0],[0.0,np.exp(1j*phi)]], dtype=complex)
    return R @ Jd @ Rm

def stokes(E):
    Ex,Ey = E[0],E[1]
    S0=(np.abs(Ex)**2+np.abs(Ey)**2).real
    S1=(np.abs(Ex)**2-np.abs(Ey)**2).real
    S2=(2*np.real(Ex*np.conj(Ey))).real
    S3=(-2*np.imag(Ex*np.conj(Ey))).real
    return np.array([S0,S1,S2,S3])

# generate Stokes path by sweeping a half-wave plate (retard=180°)
E0 = np.array([1.0,0.0], dtype=complex)  # horizontal
thetas = np.linspace(0,180,181)
pts = []
E = E0
for th in thetas:
    J = jones_waveplate(th, 180.0)
    E = J @ E0
    S = stokes(E)
    s = S[1:]/max(S[0], 1e-12)  # normalize to unit Poincaré sphere
    pts.append(s)
pts = np.array(pts)  # (N,3)

fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim(-1,1); ax.set_ylim(-1,1); ax.set_zlim(-1,1)
ax.set_xlabel('S1'); ax.set_ylabel('S2'); ax.set_zlabel('S3'); ax.set_title('Poincaré Sphere – HWP sweep')

# unit sphere wireframe
u = np.linspace(0,2*np.pi,60); v = np.linspace(0,np.pi,30)
xs = np.outer(np.cos(u), np.sin(v))
ys = np.outer(np.sin(u), np.sin(v))
zs = np.outer(np.ones_like(u), np.cos(v))
ax.plot_wireframe(xs, ys, zs, linewidth=0.2, alpha=0.25)

dot, = ax.plot([], [], [], marker='o', markersize=6)
path, = ax.plot([], [], [], linewidth=1.5)

xs,ys,zs = [],[],[]
def update(i):
    xs.append(pts[i,0]); ys.append(pts[i,1]); zs.append(pts[i,2])
    dot.set_data([pts[i,0]],[pts[i,1]])
    dot.set_3d_properties([pts[i,2]])
    path.set_data(xs, ys)
    path.set_3d_properties(zs)
    return dot, path

ani = FuncAnimation(fig, update, frames=len(pts), interval=40, blit=True, repeat=True)

if len(sys.argv) > 1 and sys.argv[1] == "--save":
    ani.save("poincare.gif", writer="pillow", fps=25)
else:
    plt.show()
