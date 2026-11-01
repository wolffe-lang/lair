# r41q — lair to wolf 0.2.36 / lupin 0.1.58

_The engine's half of r41q (the apps, the games and the docs to the published pair). The games' `lair.pin`
bumps follow in their own repositories once this merges._

## Prediction

Written before the first change (2026-11-01, base `9a65bf54`).

- `wolf-toolchain.toml` moves to wolf **0.2.36** (`v0.2.36`, tag object `86d61559` peeling to `5adf3d91`),
  lupin **0.1.58** (`v0.1.58` at `6240efe5`, spec pin `a5378e3`) and the std the 0.2.36 archive bundles,
  wolf-std **`78b9d3cb`**. `tools/fetch-toolchain` accepts all three pinned archives by digest on the hosts
  CI runs (linux x86-64, macOS arm64); `tools/lib-toolchain.sh` accepts `wolf 0.2.36 (wolfgang, pin
  5adf3d9)` and `lupin 0.1.58 (wolf-interp, reference interpreter at pin a5378e3)` (both read from the
  archives on hasu before the change) and `STD-REV` `78b9d3cb`.
- The engine's Linux leg stays green with nothing else moved: fmt clean (0.2.36's only formatter change is
  for a malformed first item), **86 checked tests, zero SKIPs**, both builds under `--deny-warnings` (the
  new prelude names `VaList`, `va_start`, `va_arg`, `va_copy`, `va_end`, `env_arg0` and `env_args_bytes`
  are declared nowhere in the engine or the games, so no W0304), the PCM goldens unchanged, the sound and
  input rows, both selftests.
- pack on this engine (`tier pr`'s `pack` job: pack's trunk with this checkout staged as its `.lair`)
  stays green at the new pin: its tests with zero SKIPs, both builds, the selftest, the **39 golden
  directories byte for byte**, the eight pty rows.
- What does not move: the release tier keeps `WOLF_MIDEND=0`. wolf-lang#940 (the mid-end miscompile of
  pack's key path) is fixed by s270 at `d2753b48`, which is 24 commits after the 0.2.36 tag, so this pin
  still carries the fault. The `wolf.pkg` path-dependency gap (`docs/ENGINE.md`) is unchanged: the
  reproducer re-run at 0.2.36 on hasu answers `E0301` in `pkg://eng/tier/tier.lu`, as at 0.2.35, so the
  symlink shape stays.
- The plant: lair's trunk with one hex digit of the linux x86-64 wolf digest changed, on
  `r41q-plant-lair-digest` (a draft PR). It goes red in `tier pr` at the step `the pinned toolchain, by
  digest` with `fetch-toolchain: REFUSED`, in both the `linux` and the `pack` jobs.
