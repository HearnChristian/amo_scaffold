.PHONY: setup test lint type influx rga_log rga_upload

setup:
\tpython -m pip install -U pip
\tpip install influxdb-client typer pyyaml jsonschema pytest ruff mypy

test:
\tpytest -q || true

lint:
\truff check .

type:
\tmypy src || true

influx:
\tamo influx_test

rga_log:
\tamo rga_log data/bake/latest.csv --follow True

rga_upload:
\tamo rga_upload data/bake
