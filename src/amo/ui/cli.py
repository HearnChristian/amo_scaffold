import numpy as np
from amo.optics.polarimetry import trace_stokes
import typer
from amo.io.config import get_influx_config
from amo.io.sinks.influx import InfluxSink
from amo.io.loggers.rga import stream_rga_csv_to_influx, upload_rga_folder

app = typer.Typer(no_args_is_help=True)

@app.command()
def influx_test():
    """Write a single test point to InfluxDB."""
    cfg = get_influx_config()
    with InfluxSink(cfg.url, cfg.token, cfg.org, cfg.bucket) as sink:
        sink.write("amo_ping", {"value": 1.0}, {"who": "cli"})
    typer.echo("✅ InfluxDB write OK.")

@app.command()
def rga_log(csv: str, follow: bool = True):
    """Stream an RGA CSV into InfluxDB (tail-f style)."""
    cfg = get_influx_config()
    with InfluxSink(cfg.url, cfg.token, cfg.org, cfg.bucket) as sink:
        stream_rga_csv_to_influx(csv, sink, follow=follow)

@app.command()
def rga_upload(folder: str):
    """Upload all CSV files in a folder into InfluxDB."""
    cfg = get_influx_config()
    with InfluxSink(cfg.url, cfg.token, cfg.org, cfg.bucket) as sink:
        upload_rga_folder(folder, sink)

if __name__ == "__main__":
    app()


@app.command()
def pol_demo(plot: bool = False):
    """H -> HWP(22.5) -> QWP(45) -> POL(0)"""
    nodes = [
        {"type":"waveplate","theta":22.5,"retard":180.0},
        {"type":"waveplate","theta":45.0,"retard":90.0},
        {"type":"polarizer","theta":0.0},
    ]
    E0 = np.array([1.0+0j, 0.0+0j])
    steps = trace_stokes(nodes, E0)
    for s in steps:
        S = s["S"]
        print(f"{s['node']:02d} {s['type']:10s} S=[{S[0]:.3f},{S[1]:.3f},{S[2]:.3f},{S[3]:.3f}]")
    if plot:
        from amo.ui.poincare import plot_stokes_path
        plot_stokes_path([np.array(x["S"]) for x in steps])
