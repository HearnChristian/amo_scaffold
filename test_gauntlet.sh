#!/usr/bin/env bash
set +e  # don't stop on errors; we want to see failures
proj_root="$(pwd)"

say() { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
run() {
  printf "\033[0;33m$ %s\033[0m\n" "$*"
  eval "$@"
  rc=$?
  printf "\033[2m(exit %d)\033[0m\n" "$rc"
  return 0
}

# 0) Activate env (if not already)
say "0) ensure venv active"
if [ -z "${VIRTUAL_ENV:-}" ]; then
  if [ -f ".venv/bin/activate" ]; then
    run "source .venv/bin/activate"
  else
    say "No .venv found — creating one + installing"
    run "python3 -m venv .venv"
    run "source .venv/bin/activate"
    run "pip install -e ."
  fi
fi

# 1) CLI misuse & parsing errors
say "1) CLI misuse & parsing"
run "amo set"
run "amo frobnicate"
run "amo set laser 0.1"
run "amo set laser.power waffles"
run "amo status camera"
run "amo set laser.flavor 123"
run "amo get laser.flavor"

# 2) Interlock & limits abuse
say '2) Interlocks'
run "amo set laser.power 0.9"
run "amo set laser.detune_mhz 9999"
run "amo set laser.detune_mhz NaN"
run "amo set laser.power -0.1"

# 3) Recipe loader/executor stress
say "3) Recipes: missing, empty, malformed, unknown device, over-limit, long wait"
run "amo run recipes/does_not_exist.yaml"

# empty recipe
run "printf '' > recipes/empty.yaml"
run "amo run recipes/empty.yaml"

# malformed yaml
cat > recipes/bad.yaml <<'YAML'
- at_ms: not_a_number
  set:
    laser.power:: 0.5
    laser.detune_mhz: "oops
YAML
run "amo run recipes/bad.yaml"

# bad device
cat > recipes/bad_device.yaml <<'YAML'
- at_ms: 0
  set:
    camera.exposure_ms: 10
YAML
run "amo run recipes/bad_device.yaml"

# over-limit values
cat > recipes/overlimit.yaml <<'YAML'
- at_ms: 0
  set:
    laser.power: 0.99
    laser.detune_mhz: 9999
  status: [laser]
- at_ms: 50
  set:
    laser.power: 0.2
  status: [laser]
YAML
run "amo run recipes/overlimit.yaml"

# long wait
cat > recipes/long_wait.yaml <<'YAML'
- at_ms: 0
  set:
    laser.power: 0.10
- at_ms: 1500
  status: [laser]
YAML
run "time amo run recipes/long_wait.yaml"

# 4) Filesystem & logging edge cases
say "4) Filesystem"
run "chmod -w data || true"
run "amo run recipes/empty.yaml"
run "chmod +w data || true"

run "rm -rf data"
run "amo run recipes/empty.yaml"
run "ls -1 data | tail -n 3"

# long nested path
run "mkdir -p 'recipes/very/long/path/with/many/segments/for/fun'"
run "cp recipes/empty.yaml 'recipes/very/long/path/with/many/segments/for/fun/demo.yaml'"
run "amo run 'recipes/very/long/path/with/many/segments/for/fun/demo.yaml'"

# 5) Concurrency / reentrancy
say "5) Concurrency"
run "( amo set laser.power 0.05 ) & ( amo set laser.detune_mhz -10 ) ; wait"
run "amo status laser"

# 6) Unicode & formatting
say "6) Unicode & formatting"
run "cp recipes/empty.yaml 'recipes/δemo.yaml'"
run "amo run 'recipes/δemo.yaml'"
run "amo set 'laser.power' 1e-1"
run "amo set 'laser.detune_mhz' ' -1.8e1 '"
run "amo status laser"

# 7) Case & extra dots
say "7) Case sensitivity & malformed target"
run "amo status Laser"
run "amo set laser.power.extra 0.1"

# 8) Environment tests (wrong cwd, path/venv)
say "8) Environment / cwd"
tmpdir="$(mktemp -d)"
run "cd '$tmpdir' && amo run recipes/empty.yaml"
run "cd '$proj_root'"

# 9) Wrap-up: list recent runs
say "9) Recent runs created"
run "ls -1 data | tail -n 10 || true"

say "DONE. Gauntlet complete."
