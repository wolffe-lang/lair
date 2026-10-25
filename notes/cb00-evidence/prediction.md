# cb00 — the prediction, written before the first change (2026-10-25T10:07Z)

Read against pack at `91d93ac` (pk03's head, pack#16, labelled; the contract says to rebase onto it, so the
extraction is cut from it): 9,446 lines of wolf under `src/` (6,826 of source, 2,620 of tests), 39 golden
directories (3.6 MB), eight pty rows, 129 unit tests.

1. **How many of pack's source lines move.** About 2,750 of the 6,826 source lines (40 percent) move into
   `lair` whole or nearly: `grid` (858, both files), `tier`'s machinery (about 200 of 700: the tier ids,
   detection, the dialect, `nearest_index` and the blend), `term` (218), `input` (325, plus the held-key
   model's 50 from `sim`), `clock` (89), `replay` (268), `world`'s noise (about 120 of 230), `art`'s text
   and frame primitives (about 60 of 700), and `pack.lu`'s headless and apply helpers (about 150 of 1,400).
   Of the tests about 800 of 2,620 lines move (grid, clock, input, replay, the noise half of world, the
   machinery half of tier). What stays in pack is the game: `sim` (1,908), `best`, the sprite table and the
   palette's keyframes, `art`'s render, sheet and cards, `pack.lu`'s loops.
2. **Whether any golden changes.** None: the bar is none, and nothing that decides a cell moves except by
   copy — the sprite table, the keyframes, the blend arithmetic, the noise and the simulation keep their
   text; only the module a function lives in changes. The place a byte could move is the blend (`rich_at`
   generalised to `tier.blend(from, to, t, span)`): the same integer arithmetic in the same order, or the
   dusk goldens show it first.
3. **The pin tooling's size.** `lair.pin` is one line (a 40-hex commit) plus comment lines; `tools/fetch-lair`
   about 90 lines of POSIX sh (the toolchain fetcher's shape: fetch at the sha, refuse a mismatch, a stamp so
   a staged pin is left alone, a local source for a lane); the root-finding helper the engine's tools share
   about 30 lines; the game's two config files (the shell `tests/lair.conf`, the Python `tests/pty_rows.py`
   that carries pack's three game rows) about 20 and 330 lines, the rows moved rather than written.
4. **The render cost after the split at 200x60.** Unchanged within noise: a call across modules costs what
   a call within one does, and the hot loop (`terrain_row`, `glyph_at`, `diff`) is the same code. pk03
   measured 146 / 143 us (rich / plain) on nomad and 215 / 215 us on kasumi; I predict within 10 percent on
   both, the same bytes a frame (14,580 / 8,182).
5. **How many pack imports the move touches.** Every `use` line in `pack.lu`, `art.lu`, `sim.lu` and the
   seven test files that import a module: about 35 `use` lines, and under them about 420 qualified
   references renamed by module (`tier.` to `sprites.` for the table, `world.path` and the spawn and deer
   rates to `trail.`, `input.KEY_*` to `keys.`, the held-key model to `input.`). `grid.`, `clock.`,
   `term.`, `replay.` references keep their spelling because those modules keep their names (the pin's
   shape is the symlinked module directory, so `use grid` stays `use grid`: see the gap below).

**A wolf gap found while choosing the pin's shape (measured 2026-10-25T10:05Z, wolf 0.2.35):** a
`wolf.pkg` path dependency's child modules cannot import their own siblings. With `eng/{wolf.pkg,
eng.lu, grid/grid.lu, tier/tier.lu}` where `tier.lu` says `use grid`, and `app/wolf.pkg` naming
`eng: { path: "../eng" }`, `wolf run app.lu` (`use eng.tier`) answers `E0301: there is no module named
grid to import` at `pkg://eng/tier/tier.lu`; `use eng.grid` inside the dependency fails the same way (no
module `eng`), and `use app_alias.grid` resolves from the consumer but not in the dependency's own build.
`wolf test` in the consumer rejects a test that imports the dependency at all. The reproducer is in
`probes/dep-sibling/` (two directories, `run.sh`). So R-cb00-3 recommends the staged tree plus symlinked
module directories; the package form waits on the fix.
