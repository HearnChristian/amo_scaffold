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
