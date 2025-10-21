from amo.devices.simulators import SimLaser

REGISTRY = {
    "laser": {
        "driver": SimLaser,
        "connect": {},
        "metadata": {"vendor": "SIM", "model": "SimLaser"},
    },
}
