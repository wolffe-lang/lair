# cb00 — the engine: `lair` extracted from pack, pack re-pinned, cub's scaffold (M-CB0)

Lane cb00 of track 19 (the cub track, ruling #130 R-CB-4; the planning repo's `sprints/lair/cub/00-the-engine/
cb00-the-engine.md`), Fable, crawl 54, 2026-10-25. Three repositories, three pull requests, merged in this
order: lair (this one: the engine), then pack (re-pinned to it), then cub (the scaffold on it). The bar for
the extraction was zero: every pack golden byte-identical, every pty row green on both hosts, the perf
within pk03's numbers; it was met at the first try on both hosts. cub's own note (`notes/cb00-the-engine.md`
in cub) carries the cb01 draft. This repository was the licences and a README (`4d0805b`).

## 1. What this pass does

- **The split** (item 1; `docs/ENGINE.md`, `7690e1f`): engine = `grid`, `tier`, `draw`, `term`, `input`,
  `clock`, `replay`, `world`, `headless`, `probe`, the tools and the planner; game = the simulation, the
  sprite table, the key vocabulary, the frame, the cards, every number. Nothing is in both repositories; the
  rule that decided a case: a function that decides a cell's glyph or colour for a creature is the game's,
  one that puts a cell on a grid, turns a grid into bytes, reads bytes into keys, waits or writes a frame is
  the engine's. R-cb00-2 (A): each game owns its sheets, the engine owns the draw calls.
- **The engine as a wolf package** (item 2; `972c8c3` to `e8c7b25`): pack's `grid` (with the terminal model),
  `clock` and `term` moved whole (`term.message` takes the program's name); `tier` kept the tiers, detection,
  the dialect, `nearest_index` and a `blend` generalised from pk03's dusk arithmetic (the same integer
  operations in the same order; the dusk goldens prove it), and gave the sprite table back to pack; `input`
  became the terminal's decoder (arrows, the four Shift+arrows as keys of their own, Esc, Ctrl-C, Enter,
  Backspace, Tab, every printable byte as a character key) and took pack's held-key model (`Hold`) from
  `sim`; `replay` reads and writes the `.pk` file with the game's **vocabulary** (`Vocab`: key names by
  number, numeric event words), so pack's file is byte for byte what it was and cub's words are its own;
  `world` kept the noise, the hash, the density and the forest's cover and gave pack its path and rates;
  new `draw` (text in a style, fill, frame, a sprite blitted from rows, the cards' text fitting), `headless`
  (the frame formats, a capture through the model, the diff property) and `probe` (the glyph-width probe);
  `src/lair.lu` is the engine's own binary (`--selftest` on the shipped tier, `--apply`, `--version`);
  `src/wolf.pkg` declares the capabilities (`fs`, `env`, `exec`, `net`: what `std.term` and `std.signal`
  reach). 61 unit tests moved or written; `docs/REPLAY.md` moved and rewritten for the engine.
- **The tools** (`f0a872e`, `b13831a`, `ff0eb7d`, `36e7db3`): pack's tools as the engine's, run from lair's
  own checkout or from a game's staged `.lair/`; `tools/lib-root.sh` finds the game's root above `.lair` by
  name (never through `..`, which a lane's symlinked `.lair` resolves out of the game), the game's name from
  the one entry under `src/`, and checks `.lair/LAIR-REV` against the game's `lair.pin`, refusing a mismatch
  unless `LAIR_UNPINNED=1` says loudly that another engine is meant (lair's own CI; a lane); the knobs are
  `LAIR_*`; the pty runner keeps the engine's five rows and loads a game's own from `tests/pty_rows.py` by
  path; `perf` and `pty` read `tests/lair.conf` for the bench's and the rows' arguments; the toolchain pin
  (`wolf-toolchain.toml`) is the engine's and serves every game.
- **CI** (`5355efb`, `ff0eb7d`): the planner reads its pull-request jobs from `# tier: pr` marks in the
  workflow (so one planner serves lair's workflow and each game's), and its test reads the jobs from the
  workflow it runs against; lair's workflow runs the planner's test, the Linux leg (fmt, the tests, both
  builds, `lair --selftest`) and **pack on this engine** — pack cloned at the first ref of `ci/games.conf`
  that exists (its re-pin branch while it is in flight, then trunk), this checkout staged as its `.lair`,
  pack's whole Linux leg run (its tests, builds, selftest, 39 goldens, eight rows) — in `tier pr`; the macOS
  leg in `tier full`. The decoder plant is seen red there as pack's `held-run` row (section 6).
- **The pin** (item 3; pack `526908f`, `dc341f6`; cub `bf7d2e1`): `lair.pin` is the engine's commit on one
  line; `tools/fetch-lair` fetches that commit's tree into `.lair/` (a lane's local clone by `LAIR_GIT`),
  refuses a fetched commit that is not the pin and a staged tree the game's module symlinks cannot find,
  and writes `.lair/LAIR-REV`; `src/<module> -> ../.lair/src/<module>` for each engine module, so the
  compiler sees one package and `use grid` reads as it did. R-cb00-1 (A) the commit fetched as a tree,
  R-cb00-3 (A) the symlinked modules: section 4.
- **pack re-pinned** (item 3; pack `526908f` to `4148524`): `src/` lost grid, tier, term, input, clock,
  replay, world (4,684 of its own source lines remain of 6,826; 2,084 of tests), the tools, `ci/` and
  `docs/REPLAY.md`; gained `sprites` (the table and the palette's keyframes, what stayed of tier),
  `controls` (pack's key numbers over the engine's decoder, the replay words) and `trail` (the path and the
  spawn and deer rates over the engine's noise); `sim` takes the held-key model from `input` and the path
  from `trail`; `art` draws its cards' text and frames through `draw`; `pack.lu` runs the headless, apply
  and probe paths from the engine and maps the decoder's keys through `controls` (the title's text mode is a
  flag of the loop's now). Every one of the 39 golden directories byte-identical on both hosts, every one
  of the eight pty rows green on both hosts, the perf within pk03's numbers (section 3), 135 unit tests
  (pack's 74 and the engine's 61) on the checked machine. The workflow stages the engine first in every
  job; the docs and the README say where things live now.
- **cub's scaffold** (item 4; cub `bf7d2e1` to `3a6235a`): cub's note.

## 2. How it was tested

| what | where | result |
|---|---|---|
| lair: `wolf fmt --check`; 61 unit tests on the checked machine, 0 SKIP; both tiers built; `lair --selftest` on the release binary (`tools/check`) | nomad | green |
| pack on the engine: fmt; 135 tests, 0 SKIP; both tiers; `pack --selftest`; **39 goldens byte-identical**; eight pty rows | nomad (`notes/cb00-evidence/pack-goldens-pty-perf-nomad.txt`); kasumi CPUs 4-7 in the container, the engine staged from GitHub by `tools/fetch-lair` (`pack-check-linux-and-perf-kasumi.txt`) | green both; every golden `ok` at the first try on both hosts |
| pack's perf gate on the engine | nomad; kasumi | within pk03's numbers (section 3) |
| cub on the engine: fmt; 75 tests; both tiers; `cub --selftest`; 17 golden directories; the engine's five pty rows | nomad; kasumi (cub's `notes/cb00-evidence/check-linux-kasumi.txt`) | green both, the goldens written on nomad and byte-identical on kasumi |
| the planner's test and the memory gate's test | nomad, against lair's, pack's and cub's workflows | green |
| the pin refused: `lair.pin` at the stub commit staged from a local clone | nomad, a scratch clone of pack | `fetch-lair: REFUSED — src/clock points at nothing in the staged engine` |
| the plants (item 5) | three draft PRs | red, section 6 |

Three faults the proof caught that reading did not:

1. **The engine's modules cannot be a package dependency** at wolf 0.2.35: a `wolf.pkg` path dependency's
   child modules cannot import their own siblings (E0301 inside the dependency from the consumer's build),
   and `wolf test` in the consumer rejects a test that imports the dependency. Measured before the first
   change (`notes/cb00-evidence/prediction.md`, the reproducer in `probes/dep-sibling/`); the symlinked
   module directories are the shape until it is answered (R-cb00-3).
2. **The pin plant found the dangling-link check blind.** `tools/fetch-lair` looked for dangling symlinks
   with `src/*/`, a glob a dangling link never matches, so a pin at the stub passed the fetch step and died
   at the planner; `src/*` sees them, and the plant's second run is red at the fetch step as the contract
   names. `tools/build` had the same glob.
3. **The decoder plant found the pack job's environment.** `LAIR_UNPINNED=1` was set on the leg's step
   alone, so the toolchain step before it refused the unpinned engine; the whole job carries it now.
   And a lane's symlinked `.lair` found `lib-root.sh` resolving the game's root through `..`, which the
   kernel follows out of the game into the lane directory: the root is the name above `.lair` now.

The prediction (`notes/cb00-evidence/prediction.md`, `22a5740`), scored:

| | predicted | measured | |
|---|---|---|---|
| 1 pack source lines moving | about 2,750 of 6,826 (40 percent); about 800 of 2,620 test lines | 2,142 of pack's source lines left it (6,826 to 4,684, with `sprites`, `controls` and `trail` added back) and the engine holds 3,190 lines of module source (the moved code plus `draw`, `headless`, `probe` and the vocabulary); 536 test lines left pack (2,620 to 2,084), the engine has 967 | miss on the count both ways: the moved code grew a third in the engine (the generic decoder, the vocabulary, the new modules) and pack kept more than predicted (the sprite table is 560 lines, not 500; the key mapping and the rates came back as new modules) |
| 2 goldens changing | none | none: 39 directories `ok` on nomad and kasumi at the first run | hit |
| 3 the pin tooling's size | fetch-lair about 90 lines of sh, the root helper about 30, the config about 20, the rows about 330 | fetch-lair 54 lines, lib-root.sh 51, lair.conf 14, pty_rows.py 310 | hit within a third |
| 4 render at 200x60 | within 10 percent of pk03's 146/143 (nomad) and 215/215 (kasumi); the same bytes | nomad 146 / 145 us, kasumi 215 / 213 us; 14,580 / 8,182 bytes a frame | hit |
| 5 pack imports touched | about 35 `use` lines, about 420 qualified references | 20 `use` lines changed in pack.lu, art.lu, sim.lu and the tests; the qualified references renamed by module came to about 380 (`tier.` to `sprites.` 60 sites, `world.path` and the rates to `trail.` 14, `input.KEY_*` to `controls.` 30, the held-key model 11, the tests' the rest) | hit on the order, high on the `use` count |

## 3. Measurements

Release binaries, mid-end off (pack's R-pk00-5 stands; `tools/build` carries the switch). kasumi: CPUs 4-7
in the container under the shared lock (`~/lanes/cb00/leg.sh`: check-linux then perf; the lock waited 3.5
minutes on ld02b's gauntlet, then the leg took 96 seconds); nomad: load 1.5 to 3 with the maintainer's
servers up, every build and row behind the memory gate (never refused this lane).

| measurement | kasumi (Linux x86-64) | nomad (macOS arm64) | pk03's, before the move |
|---|---|---|---|
| pack render + diff, 80x24 rich, avg / p99 / max, 300 frames, a dozen shadows and three deer from row 900 | 36 / 66 / 86 us | 25 / 52 / 59 us | 38 / 71 / 92; 27 / 55 / 341 |
| 80x24 plain | 35 / 59 / 67 us | 25 / 42 / 50 us | 36 / 58 / 65; 25 / 42 / 46 |
| 200x60 rich | 215 / 402 / 436 us | 146 / 291 / 315 us | 215 / 404 / 468; 146 / 297 / 314 |
| 200x60 plain | 213 / 348 / 368 us | 145 / 249 / 263 us | 215 / 366 / 377; 143 / 244 / 249 |
| bytes a frame, 80x24 rich / plain; 200x60 rich / plain | 1,236 / 615; 14,580 / 8,182 | the same | the same |
| voluntary context switches, standing, 10 s | 300 (bar 240-360) | no counter: a loud SKIP | 300 |
| key to the frame that carries it, median / p90 / max, 20 keys | 13.5 / 33.5 / 33.8 ms | 12.1 / 33.1 / 34.2 ms | 32.3 / 33.5 / 33.6; 31.9 / 33.4 / 34.3 |
| pack's goldens | 39 directories, 3.6 MB, byte-identical on both hosts to pk03's | | |
| pack's unit tests | 135 on the checked machine (74 pack's, 61 the engine's), 0 SKIP, both hosts | | 129 |
| the engine's unit tests | 61, 0 SKIP | | |
| cub's goldens | 17 directories, 908 KB, byte-identical on both hosts | | |
| cub's unit tests | 75 (23 cub's, 61 the engine's, less the overlap `wolf test` counts), 0 SKIP, both hosts | | |
| the kasumi legs under the lock | pack 96 s (check-linux and perf), cub 95 s | | |

The render is the same code in another module, and the numbers say so: every average within 2 us of
pk03's on both hosts, every byte count equal. The latency median reads lower than pk03's 32 ms because the
runner's key lands at a random phase of the tick; the p90 is the tick, as before.

## 4. Rulings asked (recommended and implemented)

- **R-cb00-1 the pin's form**: (A) a commit sha in `lair.pin` fetched as a tree (yew's shape for wolf-std);
  (B) a git submodule. Recommend (A), implemented: one file a reader reads, one tool with a refusal by name,
  a stamp (`LAIR-REV`) every engine tool checks, and a lane can point `LAIR_GIT` at a local clone and still
  stage exactly the pin. A submodule would put the pin in `.gitmodules` and the fetch in git's hands, with
  no refusal of a drifted tree.
- **R-cb00-2 the sprites' home**: (A) each game owns its sheets, the engine owns the draw calls; (B) a shared
  sheet in lair. Recommend (A), implemented: pack's `sprites` and cub's `sprites` share the forest texture's
  glyphs by choice, not by a shared table (cub's gravel, water, reeds and cub are its own), and the engine's
  `draw` knows a cell, never a wolf.
- **R-cb00-3 (new) how a game's compiler sees the engine**: (A) a staged tree under `.lair/` and a symlink per
  engine module under `src/`, imports unchanged (`use grid`); (B) a `wolf.pkg` path dependency
  (`lair: { path: "../.lair/src" }`, `use lair.grid`); (C) the module directories copied into `src/` as
  ignored files. (B) is the language's shape and is blocked by the gap measured in the prediction (a
  dependency's modules cannot import their siblings; `wolf test` cannot see the dependency), the wolf-lang
  issue to file; (C) hides which modules are the engine's. Recommend (A), implemented; the move to (B) is
  mechanical when the gap is answered.
- **R-cb00-4 (new, cub's) Shift+Down**: cub's note; (A) the bible's sneak on Shift+arrows, implemented.

## 5. What is next

- **lr01, the mixer (M-CB3's engine half):** play's mixer and `orch.lu` ported into a `sound` module, the
  part reader, PCM goldens in the headless shape (a rendered part as bytes under `tests/goldens/`), the three
  outputs (`/dev/dsp` on PAX, a WAV handed to `afplay` on macOS, a WAV or OSS on Linux); the games' hooks
  (area entry, a boss's phase, a den, the card).
- **The package form** when wolf-lang answers the gap: `src/wolf.pkg` in each game with the path
  dependency, `use lair.<module>`, the symlinks gone; `fetch-lair` unchanged.
- **The engine's perf tool for cub**: `--bench` in cub (cb01) and the idle and latency rows against it.
- **pack's pk04** on this engine: the installer row and the font row live in lair now by the campaign
  (R-CB-4); `ci/games.conf` gains `cub` when cub has a trunk with a pin (now: after cub's PR).

**Issues to file** (the lane files nothing):
1. wolf-lang: a `wolf.pkg` path dependency's child modules cannot import their own sibling modules
   (`use grid` inside the dependency's `tier/` is E0301 from the consumer's build; `use <alias>.grid` works
   from the consumer and fails in the dependency's own build), and `wolf test` in the consumer rejects a
   test that imports the dependency at all. Reproducer: `notes/cb00-evidence/probes/dep-sibling/run.sh` at
   wolf 0.2.35; the prediction's last section.
2. lair: the macOS leg runs the engine's own tests only; a `pack` macOS job (pack's goldens and rows on
   the engine under test on a macOS runner) would close the second host in lair's CI; today the second
   host is the lane's nomad run and pack's own trunk run.
3. lair: `ci/games.conf` gains `cub` once cub's trunk carries a pin (after cub's PR merges): one line,
   one more `tier pr` job.
4. pack: the macOS owed rows (KEYS.md, GLYPHS.md) carried from pk00 (unchanged by the move); the run is
   `cd ~/lanes/cb00/pack && target/pack --probe-glyphs` now.
5. lair: the memory gate's shell twin and the Python decision are tested, but the planner's test runs only
   where `python3` is (CI's `plan-test` job and the lane); a `tools/check` step for it on the engine's own
   leg would hold the planner on every push.

**The prune list** (the lane removes nothing): nomad `~/lanes/cb00/{lair,pack,cub}` (worktrees of the
org checkouts' `cb00` branches), `~/lanes/cb00/scratch/` (the module experiments; the reproducer is
committed); kasumi `~/lanes/cb00/` (the clones, `leg.sh`, `leg-cub.sh`, their logs and the evidence copied
into the notes); the plant branches `cb00-plant-decoder` (lair), `cb00-plant-pin` (pack),
`cb00-plant-camera` (cub) with their draft PRs; the `cb00` branches after the merges (lair's
`ci/games.conf` then falls through to pack's trunk by design).

**How the maintainer looks at it:** pack as before, now on the engine: `cd ~/lanes/cb00/pack &&
target/pack` (the release tier at the final head; `--seed 16 --start 600` for the groups, `--tier plain` for
PAX's view); the proof is `LAIR_UNPINNED=1 .lair/tools/goldens` there (39 `ok` lines) or, from a fresh clone,
`tools/fetch-lair && .lair/tools/fetch-toolchain && .lair/tools/check`. The engine alone: `cd
~/lanes/cb00/lair && target/release/lair --selftest`. cub: cub's note.

## 6. The plants

Three draft PRs, each read once and left for the orchestrator to close:

- **lair `cb00-plant-decoder` (lair#1):** the decoder drops the Left arrow's final byte. Red in the `pack`
  job (pack on this engine): the `held-run` row — a held Left typed as autorepeats — finds no tick applying a
  key; lair's own `linux` job red too at `test_csi_arrows`, `test_ss3_arrows`, `test_shift_arrows_are_their_own_keys`
  and `test_two_sequences_in_one_read`. The first run of this plant (40186687449) was red for the wrong reason
  — the pack job's toolchain step refused the unpinned engine — and fixed the workflow (section 2, fault 3);
  the second run's id is in the hand-back.
- **pack `cb00-plant-pin` (pack#20):** `lair.pin` names lair's stub commit (`4d0805b`, no modules). Red at
  every job's first step, `the engine, at lair.pin`: `fetch-lair: REFUSED — src/clock points at nothing in
  the staged engine; the pin and the game disagree` (run 40186889767, the `plan` job). Its first run
  (40186695507) passed the fetch step and died at the planner, which found the dangling-link check's glob
  blind (section 2, fault 2).
- **cub `cb00-plant-camera` (cub#1):** the camera fixed on the start's row, never following the cub north or
  south. Red at the goldens (`walk-north`, `turn-east`, `scroll`, `diagonal`, `resize`, both tiers) with the
  unit tests green; its first form (the camera fixed on both axes) was caught by `sim_test`'s camera test
  before the goldens ran (run 40186702264), so the plant was narrowed to what the unit test does not see.
  The second run's id is in the hand-back.
