# Protocol sources

## Keyboard controls in the terminal model

The source for `src/grid/model.lu` is the published [kitty keyboard protocol](https://sw.kovidgoyal.net/kitty/keyboard-protocol/), specifically **Detection of support for this protocol** and **Progressive enhancement** (consulted 2026-10-26). No terminal emulator or library implementation was consulted.

`CSI` is `ESC [`; spaces below are explanatory, not wire bytes.

| Control | Wire form | Defaults |
| --- | --- | --- |
| Query | `CSI ? u` | No parameters. The terminal's `CSI ? flags u` reply is input, not an output control. |
| Push | `CSI > flags u` | Omitted flags mean zero. |
| Pop | `CSI < number u` | Omitted number means one. |
| Set | `CSI = flags ; mode u` | Omitted flags mean zero; omitted mode means one. Modes 1, 2 and 3 replace, enable and disable flags. |

The model recognises these as non-rendering controls, not as a keyboard-state emulator. It retains the prefix across feeds and distinguishes it from private cursor/alternate-screen modes. Other prefixes, unsupported finals, repeated or misplaced prefixes, and malformed keyboard parameter layouts still increment `unknown`. Supported flag values need not be enumerated to recognise an output command; the model does not execute those flags.

## Capture fixture

`tests/fixtures/cub-cb04b/agree-rich.bin` is the unchanged 80×24 rich-tier capture made by cub's `cb04b` lane on macOS, copied from `/Users/mfwolffe/lanes/cb04b/cub/target/pty/agree-rich.bin`. The issue that records its origin is [lair#22](https://github.com/wolffe-lang/lair/issues/22); the originating consumer work was `cb04b` at `1edbce4f` using lair `74bf5781689a56a65945335d2ba829ed05fa92af`.

- Size: 56,288 bytes.
- SHA-256: `174552af26240164d433d41f8033b71a600b5525408ad4a002b31edf1c90e8a7` (source and copy compared).
- `tools/input-check` replays it through both binary tiers and requires exactly `alt_enters 1 alt_leaves 1 cursor_visible true unknown 0`.
- The same assertion covers the engine's own live input-loop captures, including negotiation, fallback, normal/error/crash exits and the typed Ctrl-C path.
