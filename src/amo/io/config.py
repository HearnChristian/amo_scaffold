from dataclasses import dataclass
import os

@dataclass(frozen=True)
class InfluxConfig:
    url: str
    org: str
    bucket: str
    token: str

def get_influx_config() -> InfluxConfig:
    """Read InfluxDB connection info from environment variables."""
    return InfluxConfig(
        url=os.getenv("AMO_INFLUX_URL", "http://localhost:8086"),
        org=os.getenv("AMO_INFLUX_ORG", "amo"),
        bucket=os.getenv("AMO_INFLUX_BUCKET", "amo_dev"),
        token=os.environ["AMO_INFLUX_TOKEN"],  # required; raises if missing
    )
