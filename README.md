# lair

The wolf games collection, and the engine they share. Every game the org writes in wolf runs on this one
engine: the cell grid and its diff renderer, the two glyph tiers, the terminal (raw mode, the alternate
screen, restored on every exit path), the key decoder and the held-key model, the fixed 30 Hz clock, replay
files, the forest's seeded noise, the headless goldens, the pty runner, the perf gate, the memory gate and
the CI tier planner. The games are their own repositories and pin this one by commit: `pack` (lead a pack
of wolves up a forest path) and `cub` (a cub finds its way home through Thornmere, a souls-like). The
installer row for PAX and the collection's documents will live here too.

## Where it runs

| machine | what runs | state |
|---|---|---|
| macOS, Terminal.app or iTerm2 (arm64) | the engine's tests and selftest; the games' rich tier | the maintainer's play; CI's macOS leg on every push to trunk |
| Linux, any UTF-8 terminal emulator (x86-64) | the same, in a container | CI's Linux leg on every pull request, and pack's whole Linux leg on the engine under test |
| a Linux virtual terminal (`TERM=linux`) | the games' plain tier (code points 0-255, sixteen colours) | detected from `TERM` |
| PAX's console | the plain tier today; the rich tier once PAX's font draws the games' `docs/GLYPHS.md` | the font row and the installer row are the games' PAX lanes' |

## What is engine and what is game

`docs/ENGINE.md` draws the line, module by module: the engine puts cells on a grid, turns a grid into
bytes, reads bytes into keys, waits for the next tick and writes a frame to disk; a game decides what a
cell means. A game's sprite table, its simulation, its key vocabulary and every tuning number are the
game's. Nothing is in both repositories; the extraction from pack was proven by pack's 39 golden
directories staying byte-identical and its eight pty rows green on both hosts.

The modules under `src/`: `grid` (the cell, the grid, the diff renderer, the dumps, the terminal model),
`tier` (rich and plain, detection, the dialect, the nearest 256-colour index and the blend), `draw` (text,
fill, frame, a sprite blitted from rows), `term`, `input` (the decoder and `Hold`), `clock`, `replay` (the
`.pk` file with a game's vocabulary), `world` (the noise, the hash, the density, the forest's cover),
`headless` (frames as text and styles, a capture through the model, the diff property) and `probe` (the
glyph-width probe). `src/lair.lu` is the engine's own small binary: `lair --selftest` on the shipped tier
and `lair --apply`.

## How a game holds it

```
lair.pin                 the engine's commit, forty hex digits on the first line
tools/fetch-lair         stage that tree into .lair/ (refused on a mismatch)
src/grid -> ../.lair/src/grid    a symlink per engine module; `use grid` in the game as in the engine
.lair/tools/...          the engine's tools, run from the game's root
```

The symlinks are the shape because a `wolf.pkg` path dependency's child modules cannot import their own
siblings at wolf 0.2.35 (`docs/ENGINE.md` has the reproducer's place); the package form waits on the fix.

## Build and test

The toolchain is pinned by digest in `wolf-toolchain.toml` (wolf 0.2.35, lupin 0.1.56, the std tree the
compiler bundles) for the engine and for every game that pins it.

```
tools/fetch-toolchain    stage the pinned toolchain into .wolf-bin/
tools/check              fmt, the 61 unit tests on the checked machine, both builds, lair --selftest
tools/build --release    target/release/lair
```

In a game the same tools run from `.lair/tools/` and add the game's goldens (`goldens`), its pty rows
(`pty`, the engine's five rows plus the game's own from `tests/pty_rows.py`) and the perf gate (`perf`).
The pty runner's rows: `quit`, `ctrl-c` (the byte 0x03 through the line discipline), `trap` (a planted
trap), `agree-rich` and `agree-plain` (a replayed case's captured bytes, through the terminal model, equal
its headless final frame). The memory gate (`tools/memgate.py`, `tools/lib-mem.sh`) is the maintainer's
Mac's rule and nobody else's.

CI (`.github/workflows/ci.yml`, `ci/tiers.py`): a pull request runs the planner's test, the Linux leg and
pack on this engine (pack cloned at the first ref of `ci/games.conf` that exists, this checkout staged as
its `.lair`, its whole Linux leg run); trunk, the nightly and the `full-matrix` label add the macOS leg.
The games' workflows run the same planner from their staged engine.

## Documents

`docs/ENGINE.md` what is engine and what is game, and how a game holds the engine; `docs/REPLAY.md` the
`.pk` replay file. The games' own documents (the design constants, the sprites, the glyph lists, the
palettes, the keys) are in the games.

## Licence

GNU GPL v3 with the wolf Training Data Permission (see LICENSE and LICENSE-TRAINING-DATA).
