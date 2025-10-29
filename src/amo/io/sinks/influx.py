from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS, WriteOptions
from contextlib import AbstractContextManager
from typing import Mapping, Optional
import time

class InfluxSink(AbstractContextManager):
    """Reusable context manager for writing points to InfluxDB."""
    def __init__(self, url: str, token: str, org: str, bucket: str,
                 synchronous: bool = True, batch_size: int = 5000,
                 flush_interval_ms: int = 1000):
        self._client = InfluxDBClient(url=url, token=token, org=org)
        wo = SYNCHRONOUS if synchronous else WriteOptions(
            batch_size=batch_size, flush_interval=flush_interval_ms,
            jitter_interval=200, retry_interval=1000
        )
        self._write = self._client.write_api(write_options=wo)
        self._org, self._bucket = org, bucket

    def write(self, measurement: str, fields: Mapping[str, float],
              tags: Optional[Mapping[str, str]] = None,
              timestamp_ns: Optional[int] = None):
        p = Point(measurement)
        if tags:
            for k, v in tags.items():
                p = p.tag(k, v)
        for k, v in fields.items():
            p = p.field(k, float(v))
        p = p.time(timestamp_ns or time.time_ns())
        self._write.write(bucket=self._bucket, org=self._org, record=p)

    def close(self):
        try:
            self._write.flush()
        finally:
            self._client.close()

    def __exit__(self, *exc):
        self.close()
