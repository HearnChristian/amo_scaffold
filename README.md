# AMO-Digital-Twin

Block-based optical digital twin with:

- LightState (canonical light representation)
- Blocks (laser, waveplates, mirrors, detectors)
- Backends (polarization, ray-tracing stub)
- HAL (hardware abstraction layer) stubs
- ML hooks for calibration and surrogates
- Viz stubs for future 3D engines

# AMO Digital Twin – V1 Checklist

## 1. Core model: Light + Blocks

- [ ] Implement `LightState` with:
  - [ ] Polarization (Jones vector or equivalent canonical rep)
  - [ ] Wavelength / frequency metadata
  - [ ] Intensity / power
  - [ ] Phase tracking (at least relative)
- [ ] Implement core optical blocks:
  - [ ] `Laser` (coherent source, configurable power, wavelength, polarization)
  - [ ] `Mirror` (reflection with orientation and phase)
  - [ ] `BeamSplitter` / `PBS` (polarizing beam splitter) with correct matrices
  - [ ] `Waveplate` (half-wave, quarter-wave, generic retarders)
  - [ ] `Polarizer`
  - [ ] `Detector` (intensity readout + noise model stub)
- [ ] Define a clean block interface:
  - [ ] `propagate(light_state: LightState) -> LightState | list[LightState]`
  - [ ] Metadata for ports (in/out labels, spatial index, etc.)
  - [ ] Unique IDs for each block instance (for mapping back to hardware)

## 2. Graph / circuit engine

- [ ] Graph representation of an optical circuit:
  - [ ] Node = block, edge = optical link
  - [ ] Support for multiple paths / branches
- [ ] Loader for graph configs:
  - [ ] JSON schema for circuits (e.g. `configs/circuit_mach_zehnder.json`)
  - [ ] Validation of configs with nice error messages
- [ ] Simulation engine:
  - [ ] Step-through mode (propagate light hop by hop)
  - [ ] One-shot mode (run full circuit and return detector readings)
  - [ ] Seedable randomness for reproducibility

## 3. Backends

- [ ] Polarization backend:
  - [ ] Jones / Mueller matrix implementation for all core blocks
  - [ ] Simple intensity-only mode for quick runs
- [ ] Ray-tracing backend (stub is fine for V1):
  - [ ] Data structures for rays / positions / angles
  - [ ] Pass-through “no-op” implementation that can be swapped later
- [ ] Backend selection:
  - [ ] Single flag / config option to pick backend
  - [ ] Consistent interface so the rest of the code is backend-agnostic

## 4. HAL (Hardware Abstraction Layer)

- [ ] Define HAL interfaces:
  - [ ] `LaserDriver` (set power, wavelength, on/off)
  - [ ] `WaveplateActuator` (set angle / retardance)
  - [ ] `StageController` (positioning)
  - [ ] `DetectorInterface` (read counts / voltage)
- [ ] Implement at least one **mock** HAL backend:
  - [ ] Simulated responses with noise
  - [ ] Deterministic seed for testing
- [ ] Clean mapping from graph blocks -> HAL devices:
  - [ ] One config file that maps block IDs to hardware IDs
  - [ ] Ability to run in “pure sim” (no hardware) vs “live hardware” mode

## 5. CLI (Command-Line Interface) tools

- [ ] `amo-run-graph-circuit`:
  - [ ] Arguments: `--config`, `--backend`, `--mode` (`sim`, `hardware`)
  - [ ] Prints detector outputs in a clean table
  - [ ] Non-zero exit codes on failure
- [ ] `amo-dump-graph`:
  - [ ] Load a config and print a human-readable description of the circuit
- [ ] `amo-sweep`:
  - [ ] Simple parameter sweep (e.g. scan waveplate angle, log detector output)
  - [ ] CSV output to `./data/` with timestamped filenames

## 6. Calibration + ML hooks

- [ ] Data logging:
  - [ ] Unified logger that writes inputs/outputs + metadata to disk
  - [ ] Configurable log level (quiet/verbose)
- [ ] Calibration routines (non-ML but ML-ready):
  - [ ] Basic parameter fitting routine (e.g. least-squares on detector data)
  - [ ] API for “surrogate model” prediction (function that can be patched later)
- [ ] ML integration hooks:
  - [ ] Clear abstraction where a learned model can replace a block/backend
  - [ ] Placeholder module (e.g. `ml/surrogates.py`) with stub classes

## 7. Visualization stubs

- [ ] Consistent “viz data” structure:
  - [ ] Positions and connections of blocks
  - [ ] Optional light-field / intensity along each edge
- [ ] Simple textual or ASCII visualization for v1:
  - [ ] Print graph with block names and connections
- [ ] Hooks for future 3D engine:
  - [ ] Function that exports graph + state into a JSON format usable by a 3D viewer

## 8. Testing & quality

- [ ] Unit tests:
  - [ ] `LightState` math
  - [ ] Each core block (mirror, waveplate, beam splitter, detector)
  - [ ] Circuit execution for a Mach–Zehnder interferometer
- [ ] Integration tests:
  - [ ] CLI runs successfully on a sample config
  - [ ] Mock HAL roundtrip (set params, get readings)
- [ ] Static checks:
  - [ ] `mypy` (static type checking) passes
  - [ ] `pytest` (unit tests) green locally and in CI
- [ ] Shell helpers:
  - [ ] `test_gauntlet.sh` runs lint + mypy + tests in one go

## 9. Documentation & onboarding

- [ ] README:
  - [ ] One-sentence pitch
  - [ ] Architecture diagram (even ASCII) of LightState → Blocks → Backends → HAL
  - [ ] Quickstart:
    - [ ] `git clone`
    - [ ] `pip install -e .`
    - [ ] `amo-run-graph-circuit configs/circuit_mach_zehnder.json`
  - [ ] “How to add a new block” section
- [ ] Example configs:
  - [ ] Mach–Zehnder
  - [ ] Simple polarization experiment
- [ ] Contribution guidelines:
  - [ ] Coding style
  - [ ] How to add new blocks/backends/HAL drivers
