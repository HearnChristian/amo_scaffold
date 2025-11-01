import typer
import numpy as np
from amo.optics.polarimetry import trace_stokes
from amo.io.chain_loader import load_chain_json
from amo.run.chain_exec import run_chain

app = typer.Typer(no_args_is_help=True, help="Polarization tools")

@app.command("pol-demo")
def pol_demo(
    plot: bool = typer.Option(False, "--plot", help="Show Poincaré plot"),
):
    """H -> HWP(22.5) -> QWP(45) -> POL(0)"""
    nodes = [
        {"type": "waveplate", "theta": 22.5, "retard": 180.0},
        {"type": "waveplate", "theta": 45.0, "retard": 90.0},
        {"type": "polarizer", "theta": 0.0},
    ]
    E0 = np.array([1.0 + 0j, 0.0 + 0j])
    steps = trace_stokes(nodes, E0)
    for s in steps:
        S = s["S"]
        print(f"{s['node']:02d} {s['type']:10s} S=[{S[0]:.3f},{S[1]:.3f},{S[2]:.3f},{S[3]:.3f}]")
    if plot:
        from amo.ui.poincare import plot_stokes_path
        plot_stokes_path([np.array(x["S"]) for x in steps])

@app.command("pol-branch")
def pol_branch(
    config: str = typer.Argument(..., help="Path to chain JSON"),
    branch: str = typer.Option(None, "--branch", "-b", help="Choose 'T' or 'R' for PBS if not set in JSON"),
    plot: bool = typer.Option(False, "--plot", help="Show Poincaré plot"),
):
    """Run a JSON chain, selecting a PBS branch."""
    nodes, E0 = load_chain_json(config)
    steps = run_chain(nodes, E0, cli_branch=branch)
    for s in steps:
        S = s["S"]
        print(f"{s['node']:02d} {s['type']:10s} S=[{S[0]:.3f},{S[1]:.3f},{S[2]:.3f},{S[3]:.3f}]  {s.get('meta',{})}")
    if plot:
        from amo.ui.poincare import plot_stokes_path
        plot_stokes_path([np.array(x["S"]) for x in steps])

@app.command("pol-log")
def pol_log(
    config: str = typer.Argument(..., help="Path to chain JSON"),
    branch: str = typer.Option(None, "--branch", "-b", help="PBS branch if needed (T/R)"),
    data_dir: str = typer.Option("data", "--data-dir", help="Where to write JSONL logs"),
    plot: bool = typer.Option(False, "--plot", help="Show Poincaré plot"),
):
    """Run a chain, log each step via TwinLogger, optionally plot."""
    from amo.run.pol_runner import run_and_log
    nodes, E0 = load_chain_json(config)
    steps = run_and_log(nodes, E0, branch, log_root=data_dir)
    for s in steps:
        S = s["S"]
        print(f"{s['node']:02d} {s['type']:10s} S=[{S[0]:.3f},{S[1]:.3f},{S[2]:.3f},{S[3]:.3f}]  {s.get('meta',{})}")
    if plot:
        from amo.ui.poincare import plot_stokes_path
        plot_stokes_path([np.array(x["S"]) for x in steps])
    typer.echo(f"✅ Logged {len(steps)} steps to {data_dir}/dds_*.jsonl")

@app.command("pol-animate")
def pol_animate(
    config: str = typer.Argument(..., help="Path to chain JSON"),
    node: int = typer.Option(0, "--node", "-n", help="Index of node to sweep theta"),
    sweep: str = typer.Option("0:90:5", "--sweep", "-s", help="theta sweep spec start:stop:step_deg"),
    branch: str = typer.Option(None, "--branch", "-b", help="PBS branch if needed (T/R)"),
    interval_ms: int = typer.Option(120, "--interval-ms", help="Frame interval for animation"),
    after: int = typer.Option(-1, "--after", help="Plot Stokes after node index (use -1 for final)"),
):
    """Animate polarization by sweeping a node's theta."""
    from amo.ui.animate import animate_stokes
    nodes, E0 = load_chain_json(config)
    if not (0 <= node < len(nodes)):
        raise typer.BadParameter(f"node index {node} out of range (0..{len(nodes)-1})")
    try:
        start, stop, step = [float(x) for x in sweep.split(":")]
    except Exception:
        raise typer.BadParameter("sweep must be 'start:stop:step' in degrees")

    thetas = np.arange(start, stop + 1e-9, step)
    S_frames = []
    for th in thetas:
        nodes[node] = {**nodes[node], "theta": float(th)}
        steps = run_chain(nodes, E0, cli_branch=branch)
        idx = after if after != -1 else len(steps) - 1
        if not (0 <= idx < len(steps)):
            raise typer.BadParameter(f"--after {after} out of range for chain length {len(steps)}")
        S_frames.append(np.array(steps[idx]["S"]))
    animate_stokes(S_frames, interval_ms=interval_ms, title=f"Sweep theta@node{node} {start}:{stop}:{step}")

if __name__ == "__main__":
    app()
