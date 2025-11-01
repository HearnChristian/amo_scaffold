import typer
import numpy as np
from amo.optics.polarimetry import trace_stokes

app = typer.Typer(no_args_is_help=True, help="Polarization tools")

@app.command("pol-demo")
def pol_demo(plot: bool = False):
    """H -> HWP(22.5) -> QWP(45) -> POL(0)"""
    nodes = [
        {"type": "waveplate", "theta": 22.5, "retard": 180.0},  # HWP
        {"type": "waveplate", "theta": 45.0, "retard": 90.0},   # QWP
        {"type": "polarizer", "theta": 0.0},                    # POL
    ]
    E0 = np.array([1.0 + 0j, 0.0 + 0j])
    steps = trace_stokes(nodes, E0)
    for s in steps:
        S = s["S"]
        print(f"{s['node']:02d} {s['type']:10s} S=[{S[0]:.3f},{S[1]:.3f},{S[2]:.3f},{S[3]:.3f}]")
    if plot:
        from amo.ui.poincare import plot_stokes_path
        plot_stokes_path([np.array(x["S"]) for x in steps])

if __name__ == "__main__":
    app()
