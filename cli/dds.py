#!/usr/bin/env python3
import argparse
from amo.hw.dds_sim import SimDDS
from amo.twin.logger import TwinLogger

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ch", type=int, required=True)
    ap.add_argument("--f", type=float, required=True, help="frequency Hz")
    ap.add_argument("--p", type=float, default=0.0, help="phase degrees")
    ap.add_argument("--a", type=float, default=1.0, help="amplitude 0..1")
    args = ap.parse_args()

    dds = SimDDS()
    log = TwinLogger()

    try:
        dds.set_freq(args.ch, args.f)
        dds.set_phase_deg(args.ch, args.p)
        dds.set_amplitude(args.ch, args.a)
        dds.apply_update()
        log.record({
            "device": dds.id(),
            "op": "set",
            "channel": args.ch,
            "freq_Hz": args.f,
            "phase_deg": args.p,
            "amplitude": args.a,
            "state": dds.read_state(),
            "caps": ["TunableFrequency","PhaseAdjustable","AmplitudeAdjustable","CommitRequired"]
        })
    finally:
        dds.close()

if __name__ == "__main__":
    main()
