import csv
from typing import Any, Sequence, Iterable, Optional, Dict, Tuple
from amo.io.sinks.influx import InfluxSink
import time
import pathlib

# typing helpers
def _coerce_headers(h: Optional[Sequence[str]]) -> Sequence[str]:
    return list(h) if h is not None else []
def _coerce_values(v: Iterable[Any] | Sequence[Any]) -> Iterable[Any]:
    return list(v)

def parse_rga_csv_row(row: Dict[str, str]) -> Tuple[Dict[str, float], Dict[str, str]]:
    """Extract numeric RGA fields + static tags from one CSV row."""
    fields = {}
    for k, v in row.items():
        if not v:
            continue
        if k.startswith("amu_") or k in ("pressure_total", "temperature", "humidity"):
            try:
                fields[k] = float(v)
            except ValueError:
                pass
    tags = {"device": "rga_01", "station": "bake"}
    return fields, tags

def stream_rga_csv_to_influx(csv_path: str, sink: InfluxSink, follow: bool = True, sleep_s: float = 1.0):
    """Continuously stream a CSV file (like tail -f) into InfluxDB."""
    path = pathlib.Path(csv_path)
    with path.open() as f:
        reader = csv.DictReader(f)
        # stream existing rows
        for row in reader:
            fields, tags = parse_rga_csv_row(row)
            if fields:
                sink.write("rga", fields, tags)
        # follow mode
        if follow:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(sleep_s)
                    continue
                row = dict(zip(reader.fieldnames, line.strip().split(reader.dialect.delimiter)))
                fields, tags = parse_rga_csv_row(row)
                if fields:
                    sink.write("rga", fields, tags)

def upload_rga_folder(folder: str, sink: InfluxSink):
    """Upload all *.csv files in folder to InfluxDB."""
    for p in pathlib.Path(folder).glob("*.csv"):
        with p.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                fields, tags = parse_rga_csv_row(row)
                if fields:
                    sink.write("rga", fields, tags)
