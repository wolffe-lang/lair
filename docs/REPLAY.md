# The replay file (`.pk`)

A run of a lair game is a pure function of four things: the seed, the tier, the size of the field and the
inputs, each stamped with the tick it arrived on. A `.pk` file holds exactly those, so anyone can re-run it
and get the same frames, byte for byte, on any machine. The same text is the headless script a game's
goldens are made from, and the file a game's `--record` writes at the end of a run. The format is the
engine's (`src/replay`); the words in it are the game's.

## The format

Plain text, one fact a line. A blank line or one starting with `#` is ignored.

```
pk 1
seed 42
tier rich
size 80x24
start 600
# score 1240
t 30 up
t 30 left
t 95 size 100x30
t 110 health -25
t 120 quit
```

| line | meaning |
|---|---|
| `pk 1` | the format's version; a reader refuses any other number |
| `seed N` | the world's seed, any integer (negative too) |
| `tier rich` or `tier plain` | the glyph tier the run was drawn with (the simulation does not depend on it; the frames do) |
| `size WxH` | the field's columns and rows at the start |
| `start N` | optional: the run begins N units up the world, the same world (pack: rows up the path; the distance, the difficulty curve and the dusk read from there). Absent, 0 |
| `# score N` | optional: the score the run reached, written by a game's card when the run is saved. A comment to every reader; a game re-runs the simulation headless and compares (pack: `verified`, `UNVERIFIED` with both numbers, or the re-run's score alone for a file without the line), never silently accepted |
| `t TICK KEY` | a key at a tick, by the game's name for it (pack: `up`, `down`, `left`, `right`, `parry`, `leap`, `quit`, `interrupt`); a game records the quit or the interrupt that ended the run too, so a replay ends where the run did |
| `t TICK size WxH` | the terminal was resized at that tick |
| `t TICK WORD N` | a numeric event by the game's word for it (pack: `health`, the pack's health changed by N: the goldens' and the debug keys' channel; what the shadows do is never an event, since shadows are the seed's) |

Ticks count from 0 and never decrease; several events may share a tick and are applied in file order. The
four header lines must all be present (`start` may be absent); a missing one, an unknown word, a bad
number or a tick that goes backwards is a parse failure, and the game says so and exits 2.

## The vocabulary

The engine stores a key as the number the game gives it and writes the game's name for it, so the
simulation reads a file's keys as its own and two games never share a word by accident. A game hands the
parser its `replay.Vocab`: a list of key names indexed by key number (index 0 is the no-key, never written)
and a list of event words (the first is the one `replay.at` sums for the simulation's step; another kind is
read with `args_at`). pack's vocabulary is `up down left right parry leap quit interrupt` and `health`;
cub's is its own and is in cub's `docs/REPLAY.md`. A `.pk` file from one game is a parse failure in the
other at the first key, which is the right answer.

## What a game does with it

- `<game> --replay FILE` plays the run live on your terminal, ignoring the keyboard (q, Esc and Ctrl-C
  leave it) until the last recorded tick (`--ticks N` runs exactly N ticks instead). The terminal must be
  at least the recorded size.
- `<game> --headless --script FILE --frames N --every K --tier T --dump DIR` runs N ticks without a
  terminal and writes every Kth frame as `frame-NNNN.txt` (the glyphs, one line a row) and `frame-NNNN.sty`
  (the styles: runs of `fg,bg,attrs*count` a row), and the last frame as `final.txt` and `final.sty`
  (`src/headless`). Flags given on the command line override the file's header; `--seed` given overrides
  the file's seed. `tools/goldens` runs every `tests/cases/*.pk` this way on both tiers and diffs the
  frames against `tests/goldens/`.
- `<game> --record FILE` saves the run you just played, in this format, when the run ends.
- The pty runner's `agree-TIER` rows replay a case in a real pseudo-terminal and hold the captured bytes,
  through the terminal model (`<game> --apply`), to the headless final frame of the same case: the live
  path and the headless path draw the same cells.

A held key is in the file as what the terminal sent: its first press and every autorepeat, each at its
tick. The engine's held-key model (`src/input`, `Hold`) reads the hold from those ticks alone, so a replay
steers exactly as the hand did. A high score is such a file: re-run, it gives the same card; shared, it is
verifiable by anyone with the game.
