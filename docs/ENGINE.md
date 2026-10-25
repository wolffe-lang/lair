# What is engine, what is game

`lair` holds what every wolf game in the terminal needs and nothing a particular game decides. The line
(pack's campaign and the cub track's ruling #130, R-CB-4; cb00's R-cb00-2 A: each game owns its sheets, the
engine owns the draw calls):

| engine (`lair/src`) | game (`pack/src`, `cub/src`) |
|---|---|
| `grid`: the cell (code point, two colour indices, attribute bits), the grid, the diff renderer in three colour dialects, the headless dump formats, the terminal model (`model.lu`) | the simulation (`sim`): every creature's position, heading, speed, stamina; every rule and every number (`docs/DESIGN.md`) |
| `tier`: the two tiers (rich, plain), detection from `TERM` and the locale, the dialect, the nearest 256-colour index and the RGB blend between two indices | the sprite table (pack's `sprites`): which semantic sprite is which code point and colour role on each tier, the palette's keyframes by phase, the card cells, the list `docs/GLYPHS.md` is held to |
| `draw`: text in a style, a filled rectangle, a framed box, a sprite blitted from rows of text, the text fitting the cards need | the frame (pack's `art`): what is drawn where, in what order, from the simulation; the sheets the art study commits; the cards and their words |
| `term`: raw mode and the alternate screen through `std.term`, the restore registered before the first byte and re-armed on leave, the signal set, the size and its change, the refusals by name (`not_tty`, `dumb`, `small`, `io`) | the live loop and the title loop: what the keys do, what ends a run, what the closing line says |
| `input`: the decoder (arrows in both forms, the Shift+arrows, Esc by a timeout, Ctrl-C as a byte, Enter, Backspace, every printable byte as a character key; the kitty and tilde forms ignored) and the held-key model from ticks | the key vocabulary (pack's `keys`): which character or Shift+arrow is the leap, the parry, the quit; which keys the title reads and which the run records |
| `clock`: the fixed 30 Hz tick, the one wait on standard input, the signals and the next deadline | nothing: a game never reads a clock |
| `replay`: the `.pk` file, read and written with the game's words (`Vocab`); keys, resizes and numeric events by tick; `start`; the score comment | the words, and what the numeric events mean (pack's `health`) |
| `world`: the seeded value noise, the hash of a cell, the forest's density and its three bands, the forest's cover by distance from open ground, a cell's texture variant and marks | what lies over the forest: pack's path (its centre and half width from the noise's channels 1 and 2), its spawn and deer rates (`trail`); cub's areas and their graph |
| `headless`: a frame written as cell text and styles, a captured stream applied through the model, the diff property | the headless runner's loop over the game's own simulation |
| `probe`: the glyph-width probe (`CSI 6 n`) | the list of code points to measure (the sprite table's) |
| `tools/`: the pinned toolchain and its fetcher, `build`, `test`, `check-fmt`, `check`, `check-linux`, `in-container`, `goldens`, the pty runner's engine rows (quit, ctrl-c, trap, agree-rich, agree-plain), `perf` and `perf-idle`, the memory gate; `ci/`: the tier planner and its test, the container, the nightly issue | `lair.pin` and `tools/fetch-lair`; `tests/cases` and `tests/goldens`; `tests/lair.conf` (the bench's and the rows' arguments) and `tests/pty_rows.py` (the game's own rows); the workflow file, from the engine's shape |
| `docs/REPLAY.md`, this file | `docs/DESIGN.md`, `docs/ART.md`, `docs/GLYPHS.md`, `docs/PALETTE.md`, `docs/KEYS.md` |

Nothing is in both repositories. A function that decides a cell's glyph or colour for a creature is the
game's; a function that puts a cell on a grid, turns a grid into bytes, reads bytes into keys, waits for the
next tick or writes a frame to disk is the engine's. The test of the line was the extraction itself: pack
re-pinned to the engine draws every one of its 39 goldens byte for byte and passes its eight pty rows on both
hosts, with no golden regenerated (cb00's note, section 2).

## How a game holds the engine

A game names the engine's commit in `lair.pin` and stages that tree into `.lair/` with its
`tools/fetch-lair` (refused on a mismatch, as the toolchain's digest is). The game's `src/` holds a symlink
per engine module (`src/grid -> ../.lair/src/grid`, and so on), so the compiler sees one package and every
module imports a sibling by its plain name (`use grid`), in the game and in the engine alike. The engine's
tools run from the staged tree (`.lair/tools/check`) and find the game's root above it; they refuse a
`.lair` that is not the pinned commit unless `LAIR_UNPINNED=1` says, loudly, that another engine is meant
(lair's own CI, which runs pack on the engine under test; a lane developing both).

The symlinks are the shape because of a compiler gap measured on 2026-10-25 at wolf 0.2.35: a `wolf.pkg`
path dependency's child modules cannot import their own siblings (`use grid` inside the dependency's
`tier` module is E0301 from the consumer's build), and `wolf test` in the consumer rejects a test that
imports the dependency at all. The reproducer is `notes/cb00-evidence/probes/dep-sibling/`. When the gap
is answered, the package form is a mechanical move: `deps: { lair: { path: "../.lair/src" } }` and
`use lair.grid` at every import.

## What the engine promises

- **Determinism.** Nothing here reads a clock or the environment except `clock` (the wait) and the
  callers of `tier.detect` and `term.open`; a frame is a function of the simulation's state and the tier.
- **The terminal restored on every exit path.** `term.enter` registers the runtime's restore with the
  leave bytes before the mode changes, so a return, a row, `os_exit` and a trap all restore; `term.leave`
  re-arms it empty. The pty runner's `quit`, `ctrl-c` and `trap` rows measure it for every game.
- **The plain tier inside Latin-1 and the sixteen colours.** `grid.plain_ok` says whether a frame keeps
  it; a game's sprite table test holds every sprite to it.
- **The bytes a frame are the fewest the pen allows**, in the dialect the tier names; the terminal model
  reads them back to the grid (the diff property, in every shipped binary's `--selftest`).
