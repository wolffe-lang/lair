# Keyboard input

## Two paths, one held query

Existing games keep `term.open()` / `term.enter(mut terminal)`, `input.feed` /
`feed_all`, and `input.held(h: Hold, tick: int) -> bool`. These interfaces retain
legacy key numbers and ignore the formerly ignored CSI-u and tilde forms.
They do not negotiate a keyboard protocol. Re-pinning an existing game does
not silently change its input mode or its inferred movement model.

New consumers opt in with `term.open_input(cols: int, rows: int) -> Session !
OpenErrors`. This opens and enters the terminal, then queries the kitty keyboard
protocol for at most **150 ms**. A valid `CSI ? flags u` reply enables flags
**11** (1 disambiguation, 2 event types, 8 all keys). Without a reply, no flags
are pushed and the game uses inferred holds. TERM's spelling is not evidence
of protocol support. A busy input stream is bounded too (4096 startup bytes).

The session owns `terminal: Term`, `keyboard: bool`, and `startup: List[byte]`.
Feed `startup` once before reading further input; it contains every byte read
during negotiation except the support reply. `term.resize_input(mut session)`
uses the same floor as the opener. `term.close_input(mut session)` is idempotent
and pops the keyboard stack **before** leaving the alternate screen. The runtime
restore is armed with the same bytes before the push, so an error, explicit
process exit or runtime trap restores the previous mode too. As with the old
terminal API, SIGKILL and unhandled native faults cannot be repaired in-process.

For a legacy-only game needing a smaller terminal, use `term.open_min(cols,
rows)`, `term.resize_min(mut terminal, cols, rows)` and `term.message_min(error,
program, cols, rows)`. Old `open`, `resize` and `message` keep 80×24. Minima must
be positive. `Term`'s layout is unchanged, including for existing literal users.

## The event loop

```wolf
var session = term.open_input(80, 24) else |e| {
    eprint(term.message_min("{e}", "game", 80, 24))
    return 2
}
defer term.close_input(mut session)
var decoder = input.new()
var state = input.state_new(session.keyboard)
input.register(mut state, input.char_key(32)) // Space
var events = List[input.Event]()
input.events_all(mut decoder, session.startup, now_ms, mut events)
// For each later read: reset events, events_all(...), then update each event.
for event in events {
    input.update(mut state, event, tick)
}
let down = input.held(input.key_hold(state, input.KEY_DOWN), tick)
let sprint = input.held(input.key_hold(state, input.KEY_CTRL), tick)
let precise = input.exact(state)
```

`now_ms` is monotonic milliseconds; `tick` is the game's nonnegative simulation
tick. As with the legacy decoder, call `input.flush_events(mut decoder, now_ms,
mut events)` to resolve a lone Escape after 50 ms, and use `esc_pending` /
`esc_deadline_ms` to bound the wait. Consume events in arrival order before
sampling the held set. Clear the output list between reads, and use the game's
per-iteration scratch region for transient byte/event buffers.

The API signatures are:

- `state_new(negotiated: bool) -> KeyState`
- `register(mut state: KeyState, key: int)` (idempotent)
- `feed_events(mut decoder: Decoder, byte: byte, now_ms: int, mut out: List[Event])`
- `events_all(mut decoder: Decoder, bytes: List[byte], now_ms: int, mut out: List[Event])`
- `flush_events(mut decoder: Decoder, now_ms: int, mut out: List[Event])`
- `update(mut state: KeyState, event: Event, tick: int)`
- `key_hold(state: KeyState, key: int) -> Hold`
- `held(hold: Hold, tick: int) -> bool`
- `exact(state: KeyState) -> bool`
- `clear(mut state: KeyState)` (for a game transition or externally detected focus loss)

`Event` contains `key: int`, `mods: int`, `kind: int`. `mods` is the modifier
bitfield, **not** the wire value with one added: `MOD_SHIFT=1`, `MOD_ALT=2`,
`MOD_CTRL=4`. `PRESS=1`, `REPEAT=2`, `RELEASE=3`. The event key is physical and
unshifted: Shift+Up is `KEY_UP` with `MOD_SHIFT`, not `KEY_SHIFT_UP`; Shift+A is
`char_key(97)` with `MOD_SHIFT`. Do not trigger attacks or quit actions on
`RELEASE`. Ctrl-C can be the legacy `KEY_INTERRUPT`, the terminal interrupt
signal (listen as before), or an event for `char_key(99)` with `MOD_CTRL`.

Arrows, `KEY_LEFT_SHIFT`, `KEY_RIGHT_SHIFT`, `KEY_LEFT_CTRL`, `KEY_RIGHT_CTRL`,
`KEY_LEFT_ALT`, `KEY_RIGHT_ALT`, and aggregate `KEY_SHIFT`, `KEY_CTRL`, `KEY_ALT`
are registered by `state_new`. Register other keys before use. The aggregate
modifiers reflect each exact event's post-event modifier mask, including a
modifier already held when the game entered; the two physical sides remain
independent. Keys without registration never appear held.

When exact, press or repeat establishes a hold and only release or `clear`
ends it; time and another key cannot cancel it. Down held, Left tapped and
released leaves Down held. Left and Up coexist. Ctrl persists through arrow
presses and releases. A game decides whether opposing keys cancel and whether
a diagonal or the most recent direction wins; those are not decoder rules.

When not exact, every registered key uses the original `Hold` inference:
`HOLD_TAP_TICKS=12`, `HOLD_RATE_MAX=5`, `HOLD_MARGIN=1`. A tap holds 400 ms at
30 Hz; repeats estimate their interval, then expire one interval plus the
margin after the last press. Modifier bits on legacy Ctrl+arrow sequences
refresh the aggregate Ctrl hold by the same rule. A terminal without key-up
cannot promise held-key resumption, simultaneous arrows, or Ctrl alone.

## Supported forms

The event decoder accepts printable ASCII (including letters, digits, Space),
Enter, Escape, Tab and Backspace as CSI-u; standalone left/right Shift, Control
and Alt; arrows, Home, End and F1/F2/F4 in final-letter forms; Insert, Delete,
Page Up/Down, Home/End and F1–F12 in tilde forms. Every form accepts press,
repeat and release with Shift/Alt/Ctrl combinations. Unknown codes are consumed,
not mistaken for text; numeric overflow, invalid event kinds and malformed
parameters are ignored. Optional alternate key/text fields are consumed but
not requested or used; this is game control input, not a Unicode text editor.
Legacy printable bytes, SS3/CSI arrows and the lone-Escape timer also become
events on this path.

The shared binary/checked matrix contains 1,980 sequence rows, each whole and
split at every byte boundary (95 printable codes + 10 special/modifier codes +
9 final-letter forms + 18 tilde forms, times five modifier masks and three
kinds). Additional tests cover default fields, malformed input, unchanged
legacy projection, inference, scripted held sets and startup reply buffering.

## Try your terminal

Run `.lair/tools/keyprobe --kitty` from a staged game, or `tools/keyprobe --kitty`
from the engine checkout. It uses no installed package beyond Python 3.

1. Check `exact=true; flags=11`. If it says `exact=false`, the query was not
   answered within 150 ms; do not claim an exact-key witness.
2. Hold Down, tap and release Left without releasing Down. The held list must
   retain Down when Left disappears. Release Down; the list becomes empty.
3. Hold Left and Up together. Both must appear until their individual releases.
4. Hold left Ctrl; press/release several arrows. Ctrl must remain. Hold right
   Ctrl too, release left Ctrl, then right Ctrl; the two sides disappear separately.
5. Tap Shift and Alt alone, then Enter, Escape, Tab, Backspace, Space, digits,
   letters and Shift+Space. Check the press/repeat/release rows and modifier bits.
6. Press `q`. At the shell, type normally and run the probe without `--kitty`:
   it must not have left all-key reporting enabled. Record terminal name/version,
   platform, the exact/fallback line and the rows. Automated ptys emulate the
   reply and event stream; they do not replace this live terminal witness.

Specification only: [kitty keyboard protocol](https://sw.kovidgoyal.net/kitty/keyboard-protocol/),
sections **Detection of support for this protocol**, **Progressive enhancement**,
**Disambiguate escape codes**, **Report event types**, **Report all keys as escape
codes**, **Key codes**, **Modifiers**, **Event types**, and **Functional key definitions**.
