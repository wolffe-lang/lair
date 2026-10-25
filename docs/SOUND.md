# Sound

| machine | output | tested here |
|---|---|---|
| macOS arm64 | a prepared WAV started with `/usr/bin/afplay` | PCM, WAV header, one-second playback and child reaping; terminal restore and latency |
| Linux x86-64 | a prepared WAV started with `paplay`, or named silence when unavailable | PCM in the container, missing-player refusal, terminal restore, idle wakeups and latency |
| PAX | OSS negotiation contract | stub only; `oss_ioctl_unsupported` until a device adapter exists |

Sound is optional. The mixer uses no terminal, wall clock, random host seed or audio dependency.
A failed output logs once and does not stop a game. The pinned wolf-std has no general OSS ioctl
operation, so this engine does not open `/dev/dsp` or pretend to configure it.

## Prepare, cue, tick

`use sound` exposes two stages:

- **Loading:** `read(text)` returns a checked `Score` with a named `err`; `render(score, seconds)`
  returns exactly `seconds * 48000 * 4` PCM bytes, padding with silence after the release tails.
  `prepare(name, text, seconds)` renders a named `Part`, including its cue policy. Loading is
  deliberately outside the game loop. **This version does not synthesise live.**
- **Playing:** `mixer(bank)` loads a bank of up to sixteen prepared parts. `cue(mut mixer, name)`
  selects a part, and `tick(mut mixer)` returns exactly 1,600 stereo sample frames, one 30 Hz tick.
  Call once per simulation tick, including catch-up ticks; neither call reads a clock or does I/O.

A game chooses its own names: `den`, `area-entry`, `boss-phase`, `title`, `death`, `leap`. No name
has engine-specific meaning. Missing names and a full four-slot mixer return false without changing
current music. A replace cue fades the old slots out while its new slot fades in; a layer cue leaves
old slots playing. Each slot fades at the beginning and end of its PCM and runs at quarter scale,
so four simultaneous layers cannot overflow a signed 16-bit sample. Fades count sample frames, not
wall time. A disappearing slot is available again on the following sample frame.

Preparation is bounded to 262,144 text bytes and 0–30 seconds of output per cue. A full bank holds
at most 92,160,000 PCM bytes before allocator overhead. Small banks are preferable. The tick's returned
buffer belongs to its caller; use the game's per-frame region/lifetime rather than retaining every tick.

## Outputs and their boundary

`wav(pcm)` makes a canonical 44-byte RIFF/WAVE header and payload: stereo signed 16-bit little endian,
48,000 frames/second, 192,000 bytes/second, four bytes/frame. Incomplete frames are refused.

`silent()` creates an output owner. `start(mut output, "macos"|"linux"|"oss", prepared_wav_path)`
starts a player asynchronously or reports named silence. A second start while live is refused.
`finish(mut output)` waits for and reaps exactly that owner's child; a second finish is a no-op.
Call start during output setup and finish during teardown, **never from a frame tick**. Keep the WAV
until finish returns. A child can run for the prepared cue's duration; teardown is not a cancellation API.
Commands are argument vectors, never shell text.

The two stages are intentionally explicit: **the WAV adapter does not stream `tick`'s mixed PCM into
an already-running player.** Deterministic replacement/layering is available as PCM (and can be exported
as a replay WAV). A game's live audible transitions still need a streaming sink or prepared transition
WAVs. Starting an unrelated WAV does not demonstrate that bridge. No game is wired to sound by this change.

The OSS stub exposes `oss_requests()` in the order used by PAX's player:

| request | value |
|---|---|
| `SNDCTL_DSP_SETFMT` (`0xc0045005`) | `AFMT_S16_LE` (`0x10`) |
| `SNDCTL_DSP_CHANNELS` (`0xc0045006`) | 2 |
| `SNDCTL_DSP_SPEED` (`0xc0045002`) | 48000 |

`oss_answers` accepts only those exact answers. Unlike the original player, lair cannot silently adopt
another sample rate or channel count: its PCM is a replay contract. The real device adapter belongs in
a PAX integration or a future wolf-std ioctl API, not an assembly shim inside lair.

## The part format

The reader is the complete PAX part reader, not a new subset. One item per line, words separated by
spaces or tabs. `#` at the start of a word begins a comment; `F#4` is a note. The first malformed item
names its source line and word or part. No output starts until parsing and preparation succeed.

```
title Light under roots
cue replace fade 3
tempo 120
meter 4/4
part root harp mp pan -25
part breath flute p pan 30
bar 1
root D3,A3/2 F3,C4/2
breath A4/2_ F4/2
```

`cue replace|layer fade N` is lair's optional metadata line (one per file, N = 1–30 ticks). It is removed
before the unchanged musical reader runs. Without it, a cue replaces with a three-tick fade.

The head declares `title`, required `tempo BPM [UNIT]` (20–400, quarter-note unit by default), optional
`meter n/d` (n 1–32, d 1, 2, 4, 8, 16 or 32), and up to 48 `part NAME TIMBRE [LEVEL] [pan P] [gain DB]`
lines. Names start with a letter, contain letters/digits/hyphens and are at most sixteen characters.
Level defaults to mf; pan is -100..100; gain is -24..12 whole dB. Names cannot be musical keywords.

Bars are numbered consecutively, from any nonnegative number. A bar may change meter or tempo, use
`rit|accel BPM [UNIT] over K`, and add `fermata LEN [at POS]`. Each present part line fills the bar
exactly; omitted parts rest. Multiple lines for a part in a bar concatenate.

Events are `PITCHES/LENGTH[MARKS]`. Pitches are `r`, one note, or up to six comma-separated notes.
Notes use A–G, optional `#`, `b`, `##` or `bb`, and octave 0–8; sounding range A0–C8, A4 = 440 Hz.
Lengths are 1, 2, 4, 8, 16, 32 or 64, optional one/two dots, `t` or `x3/x5/x6/x7/x9` tuplets,
and `+`-joined lengths. Musical time is exact in 1/80640 of a whole note.

| mark | meaning |
|---|---|
| `'` / `^` / `>` | staccato / marcato / accent |
| `-` / `_` | tenuto / slur to the next note |
| `*` | bowed tremolo, roll or repeated attack, by timbre |
| `~` | tie common pitches into the next event, across bars too |

Unmarked notes have a short gap, then their release. Rests take no marks. Dynamics are
`ppp pp p mp mf f ff fff`, five dB apart; `sfz`/`sf`/`fz` and `fp` affect the next attack.
`<`/`cresc` and `>`/`dim` begin hairpins, ending at the next dynamic, hairpin, or `!` (two steps).
Unclosed ties/hairpins are refused. Percussion and harp ring after their written note ends.

Seventeen timbres: strings, horn (brass), trumpet, trombone, clarinet (woodwind), oboe, flute,
organ, pedal, choir, voice, harp, timpani, bells, tamtam, cymbal, drum. All are arithmetic:
band-limited additive tables, fixed-point phase accumulators, envelopes, deterministic filtered
noise and struck partials, with constant-power pan and a look-ahead limiter. At most 128 synthesis
voices; releasing tails are stolen before ringing struck voices, never a held note.

The detailed musical specification is PAX's
[`px32-format.md`](https://github.com/wolffe-lang/pax/blob/09471da41cee86eb2c1d9aa5a8f647532b48551c/notes/px32-format.md).

## Commands and checks

```
tools/fetch-toolchain
tools/build --all
target/release/lair --play tests/parts/den.part
target/release/lair --render tests/parts/chase.part 4 chase.pcm
target/release/lair --wav tests/parts/den.part 4 den.wav
target/release/lair --sound-replay tests/parts/den.part tests/parts/chase.part replay.pcm
python3 -I tools/sound-check
```

`--play` auditions six seconds using an exclusively created temporary WAV in the current directory,
waits for its own child, then removes the WAV. It never changes terminal mode. The sound gate compares
committed PCM before the output/latency rows, on native and release; repeats the same cue replay twice;
checks WAV bytes, malformed parts, missing players, OSS stub answers, and owned child cleanup.
A real pty loop acknowledges each key only after its cue, tick and frame. Both silent and mixing modes
must meet median <40 ms / p90 <70 ms latency and Linux's 72–108 idle wakes in three seconds. macOS's
missing `/proc` counter is a loud, counted platform skip, not evidence for idle behaviour.

## Authorship

The musical reader and synthesis are a port of **wolffe-lang/PAX's own `play`**, originally written
for the orchestra work (px32), with its subsequent fixes through PAX trunk
`09471da41cee86eb2c1d9aa5a8f647532b48551c`. Sources read: `user/play/parts.lu`, `orch.lu`, `mix.lu`
and the parsing/pitch helpers in `play.lu`. The latest source change in the ported pair is
`a9f42752a8ad4b9ec6711b8019292f6de7fd620a`, authored by mfwolffe. `mix.lu` supplied the PCM/OSS
contract; legacy square/triangle slot playback is not exposed. The integer orchestra arithmetic
is preserved; device writes become PCM appends, and rendering has an explicit duration bound.

The den and chase studies in `tests/parts/` are original to lair. No other synth, player, tracker,
game or audio library source was consulted. No samples, sound fonts or new dependencies are used.
