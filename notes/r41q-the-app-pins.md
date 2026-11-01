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

## Forbidden

No merge, label, tag, release, issue filed or closed; no attribution trailer. No build on the Mac (the Mac
only downloaded and hashed archives); local runs on hasu block B alone, both lock names held per run;
kasumi not touched. No source of another implementation read. No engine module, golden, test or game
changed: the pin, one comment in `tools/build`, one ref dropped from `ci/games.conf` (R-r41q-2), one
sentence in `docs/ENGINE.md`, the README's two version statements, this note and its evidence. cub is cb19's and is not in this PR.

## Inputs verified

- Base: lair trunk `9a65bf54`, as the contract read it on 2026-10-31.
- The pair: wolf `v0.2.36` is tag object `86d61559` peeling to `5adf3d91`; lupin `v0.1.58` is tag object
  `dc4689e3` peeling to `6240efe5`; wolf-std `78b9d3cb` resolves. All read from the GitHub API.
- The digests: the release API's asset `digest` fields read in two passes (00:11:56Z and 00:11:57Z),
  identical, and equal row for row to the eleven-row table of r41's record (a `diff` of the two, empty).
  The six pinned archives downloaded fresh and hashed twice each: linux x86-64 on hasu, macOS arm64 and
  linux aarch64 on nomad (download and hash only), every read equal to the API
  (`notes/r41q-evidence/release-api-two-passes.txt`, `linux-x86_64-identities.txt`,
  `mac-hashed-archives.txt`). `wolf-toolchain.toml` is then held to the API passes by a script, not by
  eye: six digest rows, both versions, both revs, both `version_line`s and the std rev green; the same
  script reads trunk's file red.
- The identities, from the linux x86-64 archives on hasu: `wolf 0.2.36 (wolfgang, pin 5adf3d9)`, paired
  with lupin 0.1.58, pin a5378e3; `lupin 0.1.58 (wolf-interp, reference interpreter at pin a5378e3)`; the
  archive's `std/STD-REV` `78b9d3cbc41d51db44d18c40b6694403644d1c83`.
- 0.2.36's documented changes (its CHANGELOG): the five `va_*`/`VaList` and two argv prelude names may warn
  as W0304 on a shadowing declaration. A search of every `.lu` file in lair, pack, fugue, trail and yew
  finds none of the seven names declared. The std moves `2386522e` to `78b9d3cb` (sc72): the `std.list`
  mutators work in place with the signatures unchanged, the rest is new wrappers.
- What waits for this pin, read from `notes/`, the README, the open issues and `tools/`:
  - `WOLF_MIDEND=0` (wolf-lang#940): fixed by s270 at wolf-lang `d2753b48`, 24 commits past `5adf3d91`
    (the compare API), so it is not in 0.2.36. Kept; the comment now names the issue and the condition
    for dropping it. Listed for the first pin that carries s270.
  - The package form (`docs/ENGINE.md`): the reproducer at 0.2.36 still answers E0301
    (`notes/r41q-evidence/dep-sibling-0.2.36.log`). Kept; the sentence re-dated.
  - lair#15 (the OSS sound adapter wants a wolf-std ioctl surface): sc72 adds no ioctl. Still waiting.
  - Nothing else in lair names 0.2.36 or "the next pin".
- **R-r41q-1, the release tier's switch at 0.2.36:** (A) keep `WOLF_MIDEND=0` until a pin carries s270;
  (B) drop it now. Recommend and implemented (A): the fix is not in the pinned compiler.
- **The prediction was wrong about what the `pack` job runs.** The gauntlet's first run staged pack at
  **`cb00` (`59cef80`)**, not trunk: `ci/games.conf` named `cb00 trunk`, and pack's `cb00` branch was
  merged on 2026-10-25 (pack#25) but never deleted, so `ci/stage-game` has taken it first on every lair
  run since, 46 commits behind pack trunk `27848095`.
- **R-r41q-2, `ci/games.conf`:** (A) drop the merged `cb00`, so this PR's `pack` job runs pack's trunk on
  the engine under test at the new pin; (B) leave the line and list pack's stale branch for deletion.
  Recommend and implemented (A): the pin must be proved on the game as it is, and the line's own comment
  now says a ref leaves at its merge. (Deleting pack's merged branches is the orchestrator's, listed.)
- **The prediction's pack counts were `cb00`'s.** pack's trunk on this engine at 0.2.36 holds **190
  tests** (zero SKIPs), **77 goldens** byte for byte (38 cases on both tiers, and the art) and **ten pty
  rows**, not the 39 goldens and eight rows the prediction copied from lair's own `ci.yml` header. That
  header now says what the job holds without counts that go stale as pack grows (the 2026-11-01 figures in
  parentheses). The README's and `docs/ENGINE.md`'s 39-and-eight sentences record the extraction as it
  was measured then, and stay.
- **R-r41q-3, the plant's base:** (A) trunk plus one changed digest digit (the gate every pin passes);
  (B) this branch plus the same. Recommend and implemented (A), the lane rules' "base + a break the fix
  never contains".
- README read against the change: the two version statements refreshed in a README-only commit; the
  test count (86) is re-read from this head's runs, below.

## Evidence index

- `1e31b61` the prediction (this note's first section), before any change.
- `e544862` `wolf-toolchain.toml`: wolf 0.2.36, lupin 0.1.58, std `78b9d3cb`, and the second pin's
  paragraph.
- `4395bc6` `tools/build`: the `WOLF_MIDEND=0` comment names wolf-lang#940 and why 0.2.36 keeps it.
- `e8eff7e` `notes/r41q-evidence/`: the two API passes, the archive hashes, the identities and the
  dep-sibling log.
- `3f5eff6` `docs/ENGINE.md`: the dependency gap re-measured at 0.2.36.
- `4310339` README only: the pinned pair.
- `0616699` `ci/games.conf`: pack's trunk, not the merged `cb00` (R-r41q-2).
- `7dff887` `.github/workflows/ci.yml`: the `pack` job's header comment names what trunk's leg holds.
- The gauntlet at the final head, on hasu block B (`/home/mfwolffe/lanes/r41q/bin/gauntlet-lair.sh`, its
  log under `/home/mfwolffe/lanes/r41q/logs/`): the head asserted, the pin proved against the API
  passes, the planner's and the memory gate's tests (CI's `plan-test`), the image `localhost/r41q-pack-ci:fbee7e864f7dbee6` built from `ci/Containerfile`,
  `tools/fetch-toolchain`, `tools/check-linux` in the container (CPUs 6-11), then pack's trunk staged
  with this checkout as its `.lair` (`ci/stage-game`), its toolchain fetched and its `check-linux` run
  with `LAIR_UNPINNED=1` (job-wide, as CI's `pack` job sets it). Every step prints `END <step>
  exit=N`; the wrapper stops at the first nonzero one. The END lines and the counts are in the PR body.
  A first run at `37fdb9df` went red at `pack-fetch-toolchain` by the gauntlet's own fault (it set
  `LAIR_UNPINNED=1` on the container run only) after the engine leg was green (86 passed, 0 SKIP); that
  run is what showed the `cb00` staging.
- The plant: lair#25, branch `r41q-plant-lair-digest`, commit `6678266` on trunk `9a65bf54`. Its red
  `tier pr` run is cited in the PR body.

## Done-when

The PR is open at its final head with `tier pr` green there, `Footprint: cross-cutting` (a pin), the audit
run once and passing but for the labelled `tier full`, which the orchestrator labels and watches. The
games follow once this merges: `lair.pin` in fugue, trail and pack (pack's own `wolf-toolchain.toml`
too), each its own PR on its own branch. Nothing to close or file from lair. For the orchestrator: pack
still carries its merged `cb00` branch and the merged lanes' plant branches; none is read by lair's CI
after R-r41q-2.
