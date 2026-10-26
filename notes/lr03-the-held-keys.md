# lr03 — the held keys

_Materialised from lair#21's PR body at the merge (74bf5781); the lane's wrapper could not write Markdown notes._

## Prediction

Exact press/repeat/release will preserve Down through a Left tap, simultaneous Left+Up, and Ctrl through arrow presses; unsupported terminals will retain inferred holds. Every supported sequence will decode at every byte split. All four games will build unchanged and keep their goldens byte-identical. Prediction committed before implementation in `4876b33`.

Footprint: cross-cutting

Addresses #12 and #13. This body is the complete **lr03-the-held-keys** note: the wrapper forbids Markdown report/note files. Materialise it as `notes/lr03-the-held-keys.md` at merge.

## Forbidden

No kitty, terminal, TUI-library or other engine implementation source read. Only kitty's published keyboard-protocol specification and the project's own code. No game source or pushed pin edits, dependencies, host packages, configuration/planning edits, merges, labels, releases or attribution trailers. Signal witnesses are typed pty bytes, including 0x03, never process-name/group signals.

## Inputs verified

- Base `57870143ebbb4806b8bee40379e8c6e781f50842`; isolated lr03 Mac worktree and hasu clone.
- Contract, cub playtest and cb04b consumer, lair #12/#13, ENGINE, cb00/lr01 notes, campaign/index, RULES and wolf guide read.
- Unchanged wolf 0.2.35 / lupin 0.1.56 / wolf-std `2386522eb059cca5a84108562c2c0a0e72345d34`; release API digests read twice, archives verified on both hosts and binary/std identity checked by every build.
- Specification: https://sw.kovidgoyal.net/kitty/keyboard-protocol/ — **Detection of support for this protocol**, **Progressive enhancement**, **Disambiguate escape codes**, **Report event types**, **Report all keys as escape codes**, **Key codes**, **Modifiers**, **Event types**, **Functional key definitions**.
- README refreshed: four consumers, exact input, commands/counts, and removal of the stale claim that games have no sound wiring.

### Recommendations implemented

**R-lr03-1:** additive held-set API. Keep `held(h: Hold, tick: int) -> bool`; obtain a registered key's value-only view from `key_hold`. The coordinator accepted this recommendation during the lane.

**R-lr03-2:** retain `Term`'s layout and the exact legacy open/enter path (trail constructs a literal). Add an opt-in Session opener and closer. The coordinator accepted this too. The old `feed`/`feed_all` adapter continues ignoring its formerly ignored CSI-u/tilde forms: pack, cub and fugue embed assertions for that behavior. New consumers use `feed_events`/`events_all`. A pin bump alone does not change existing games' controls.

## Evidence index

- `4876b33`: prediction before edits.
- `3625179`: bounded negotiation, stack restoration and real-pty exit witnesses.
- `84d3983`: CSI-u and functional-key event decoder.
- `29275af`: registered exact holds and unchanged inference.
- `8d18fa0`: configurable terminal floor.
- `4868ae8`: shared binary/checked matrix, scripted pty streams, keyprobe and CI gates.
- `e25e49e`: ENGINE and KEYS adoption documentation.
- `94c7e67`, `45e86cc`: README refresh.
- `2e32a14`: host, consumer and deliberate-red evidence.

### Negotiation and restoration

`term.open_input(min_cols: int, min_rows: int) -> Session ! OpenErrors` opens, enters raw/alternate-screen mode, then sends `CSI ? u`. The query deadline is **150 ms**, also bounded to 4096 buffered startup bytes. No reply means no push/pop and `session.keyboard=false`. Unrelated startup bytes are retained. A valid decimal reply pushes exactly **11 = 1|2|8**. Main/alternate screens have separate stacks, so push follows alternate-screen entry and pop precedes exit. The pop+leave runtime registration is installed before pushing. `close_input(mut s: Session)` is idempotent; normal quit, typed Ctrl-C, explicit error and runtime crash paths restore termios, cursor, alternate screen and keyboard stack. SIGKILL/unhandled native faults remain outside in-process restoration, as before.

`open_min`, `resize_min`, `message_min` support legacy-only custom floors; `resize_input` preserves the session floor. Existing entrypoints default to 80×24. Tests accept 40×12, reject 39×12 and 40×11 before mutation, reject 40×12 under the legacy default, and clamp/resume resizing correctly.

### Exact API for cb04b

```wolf
state_new(negotiated: bool) -> KeyState
register(mut s: KeyState, key: int)
feed_events(mut d: Decoder, b: byte, now_ms: int, mut out: List[Event])
events_all(mut d: Decoder, bytes: List[byte], now_ms: int, mut out: List[Event])
flush_events(mut d: Decoder, now_ms: int, mut out: List[Event])
update(mut s: KeyState, e: Event, tick: int)
key_hold(s: KeyState, key: int) -> Hold
held(h: Hold, tick: int) -> bool
exact(s: KeyState) -> bool
clear(mut s: KeyState)
```

Create state with `input.state_new(session.keyboard)`, feed `session.startup` once, then subsequent input chunks; apply each event before querying holds. `Event { key: int, mods: int, kind: int }` uses an unshifted physical key, modifier bits (Shift=1, Alt=2, Ctrl=4), and PRESS=1 / REPEAT=2 / RELEASE=3. Trigger actions only on press/repeat as appropriate, never release. Arrows and modifiers are pre-registered; register other game keys with `input.register(mut state, input.char_key(code))`.

Names: `KEY_LEFT_CTRL`, `KEY_RIGHT_CTRL`, aggregate `KEY_CTRL`; likewise `KEY_LEFT_SHIFT`, `KEY_RIGHT_SHIFT`, `KEY_SHIFT`, and `KEY_LEFT_ALT`, `KEY_RIGHT_ALT`, `KEY_ALT`. Query `input.held(input.key_hold(state, input.KEY_CTRL), tick)` for sprint. Left/right modifiers stay independent. Aggregate modifiers use the event's post-event mask, including modifiers already held at entry. Shift+arrow events use the bare arrow key plus MOD_SHIFT, not the legacy KEY_SHIFT_* projection.

Exact holds last until release/clear; inferred holds retain HOLD_TAP_TICKS=12, HOLD_RATE_MAX=5, HOLD_MARGIN=1. Legacy Ctrl+arrow refreshes an inferred aggregate Ctrl hold. Fallback cannot promise simultaneous physical arrows, held-key resumption or Ctrl alone.

### Tests and measurements

- [x] hasu block B, rootless container: fmt, **79 checked tests, 0 SKIP**, native/release builds, PCM/sound regression gates, both binary selftests, all input pty rows.
- [x] nomad final code: **79 checked tests, 0 SKIP**, native/release builds, both binary selftests, **26 pty/keyprobe rows** (12 per tier plus legacy/kitty keyprobe), green. Every heavy command behind the script's 8 GiB vm_stat gate; observed 32–33 GiB. One successful final pty run, no local game builds.
- [x] **1,980 decoder sequences**, **20,250 whole/split executions per tier**: 95 printable codes, 10 special/modifier codes, 9 final-letter forms, 18 tilde forms × five modifier masks × three event kinds. Same matrix on checked/native/release. Defaults, optional fields, malformed/overflow input and unchanged legacy forms additionally tested.
- [x] Actual pty streams: Down survives Left press/release; Left+Up coexist; Ctrl survives arrow events, with independent left/right Control; unrelated repeats do not expire exact holds. All green on both hosts and binary tiers.
- [x] **All four games' full Linux legs**, unchanged sources and expected goldens, staged engine override only: pack `278480955f7c088b40b9f2cdd57565ece8f4a865` — **77** golden comparisons; cub `8fed72893efd10a30db76c99c8d233f31a1ffe3d` — **163**; trail `59050227e82d7d97401f4747207c0acef9e99afd` — **83**; fugue `39464a18974a655c599430f94a9a4ca99ae8f00a` — **85**. Counts include each game's art study. Every comparison is recursive byte equality, no regeneration; each game's tests, both builds, selftest and all pty rows also passed. hasu Linux x86-64 only for these consumer proofs.
- [x] CI planner, memory-gate selftests and git diff --check.
- [ ] Physical kitty witness: operator steps below; automated ptys are not a claim about a live terminal.
- [ ] PR/full CI and plant CI verdicts: coordinator watches and labels; lane does not wait or label.

Evidence: `notes/lr03-evidence/{check-linux,mac-final,hosts-and-consumers,pack-linux,cub-linux,trail-linux,fugue-linux}.txt`, release JSON pairs, and `plant-*-local.txt`. Production source is unchanged since `4868ae8`; later commits are docs/evidence. The first Mac build failed before pty execution because my source rsync copied an ignored Linux `.lu-cache`; I deleted only that lane-generated cache and rebuilt clean. No code workaround or suppressed failure. Source syncs must exclude `.lu-cache`.

Hasu recipe: `PATH=~/lanes/hasu-env/bin:~/lanes/hasu-env/profile/bin:$PATH`, then `flock /home/mfwolffe/lanes/hasu-B.lock env LAIR_CPUS=6-11 tools/in-container tools/check-linux`. The existing runner already supplies rootless podman, taskset **inside** the container and `--memory 12g`; measured affinity 6–11 and memory.max 12884901888. `check-linux` gained input-check and native selftest, not a host-specific bypass. The lock was held only for gates/builds.

### Deliberate plants

Each immediate once-only lane run lookup returned `[]`; GitHub had not indexed the run yet. The coordinator subsequently read the verdicts: #17/run **40373508334**, #18/run **40373519241**, #19/run **40373528489** were red by the intended rows and closed unmerged. #20/run **40373538984** is red and held open pending the minimum-size explanation below. These CI verdicts are coordinator-reported, not a lane poll.

- #17 restore, `5a04503d76da09f511f824b242f57fc0bc1ad04e`: remove the runtime pop, keep normal pop. **Local red specifically on the crash row**, normal and Ctrl-C rows green.
- #18 decoder, `8439ca6fc6b1957a915920c206607e2b5ca1a3e4`: replace decoded event kind with PRESS. **Local red: four decoder matrix groups and four event/held tests**, 71 pass / 8 fail.
- #19 held, `ef86fff6aff02c5dca2b742f34527d4bff1e5132`: every release clears all holds. **Local red: Down resumes and diagonal/Ctrl tests**, 77 pass / 2 fail.
- #20 minimum, `3fb59933f7f165e3e2c71971d45f7c957c37cedf`: force default floor in the session opener. **Local red on the 40×12 small-terminal pty row**, normal rows green. The predicted failure is the acceptance row's `assert QUERY in s.out`: the call stack is `row(binary, "small", rows=12, cols=40)`, and the injected 80×24 floor rejects before entry/query. It is not failed negotiation on a valid-size terminal. A direct additional container witness confirmed: **open_input(40,12) on a 40×12 pty exits 2, emits no query or alternate-screen entry, and leaves termios unchanged**. Earlier 80×24 negotiation rows are green; the unplanted 40×12 acceptance row is green on both hosts. The generic assertion text is an acceptance sentinel, so this is the intended minimum-size plant, not an unrelated red. Direct witness log: `/Users/mfwolffe/lanes/lr03/minimum-direct.txt`; source `/Users/mfwolffe/lanes/lr03/minimum-direct.py`.

### Live kitty witness

From a staged game run `.lair/tools/keyprobe --kitty` (or from lair, `tools/keyprobe --kitty`). Record terminal/version and platform.

1. Require `exact=true; flags=11`; fallback output is not an exact-key witness.
2. Hold Down, tap/release Left without releasing Down: Down remains in held. Then release Down.
3. Hold Left+Up together; release each separately: both coexist, then disappear separately.
4. Hold left Ctrl across arrow presses/releases. Add right Ctrl, release left Ctrl, then right Ctrl: independent sides and no prematurely ended Ctrl hold.
5. Tap Shift/Alt alone; Enter/Esc/Tab/Backspace/Space, letters/digits and Shift+Space. Inspect press/repeat/release and modifiers.
6. Press q; type at the shell and run plain keyprobe to verify all-key reporting was restored. Full steps and API caveats are in `docs/KEYS.md`.

### macOS full-tier follow-up

Run **40375328309**, macOS job **121756779674**, failed after 79 checked tests and sound-check passed. The first input row negotiated; the second reported `exact=false startup=5`, followed by the x and y events. This was **the stand-in terminal's delayed partial reply**, not decoder fragmentation or state surviving from the first session. Every row owns a fresh pty/process. Five startup bytes are precisely the first two writes (`x ESC [` and `?0`); the terminating `u y` arrived only after fallback. The original harness intentionally pumped between writes, with a 20 ms select quantum even for a requested 5 ms pump, exposing the unfinished reply to scheduling delays. The CI log did not timestamp individual writes, so its exact lateness cannot be reconstructed.

A controlled reproduction on nomad supplies that timing evidence: without an injected parent pause, the final write arrived **44.155 ms** after query observation and gave `exact=true startup=2`. Adding a **180 ms parent pause after fragment two** moved the final write to **249.104 ms** and reproduced the CI's `exact=false startup=5` plus later y event. The complete response therefore does arrive, but after the unchanged 150 ms negotiation deadline. See `notes/lr03-evidence/ci-handshake-repro.txt` and the runnable `handshake-repro.py` beside it. This is a controlled scheduling reproduction, not a claim to have measured the CI runner's scheduling delay directly.

- `77be9a2`: causal prediction recorded before the fix.
- `299fbb3`: Session's output pump now answers QUERY immediately with one complete tiny write, including during constructor settling; no inter-fragment sleeps. Assertions and the engine's **150 ms** deadline are unchanged. The same request-driven reply is used for keyprobe. A secondary local test-order race was removed: legacy keyprobe emits `keyprobe-ready` after entering raw mode, and the driver waits for it before typing q (instead of risking its loss during startup's input flush).
- `74bf578`: committed reproduction and post-fix host evidence.

New regression: constructor/caller setup lasts **250 ms**, longer than negotiation permits, while the pump must still reply promptly and the exact/startup assertions must pass. Both binary tiers pass this row on both hosts. Follow-up Mac input-check: **28 rows green**, behind the 8 GiB vm_stat gate. Follow-up hasu full check-linux: fmt, **79 tests / zero SKIPs**, both builds/selftests, sound gates and **28 input/keyprobe rows green**, under block B's lock. Logged reply latency is from query **observation** to write, not from the child's uninstrumented query emission. No wolf source, timeout, game, pin or expected golden changed in this fix. README read, current.

Current head: **74bf5781689a56a65945335d2ba829ed05fa92af**. The once-only immediate CI lookup filtered to that head returned **[]**, so no new run ID was indexed at that instant; no polling or label action followed. The coordinator owns the new run/watch. The earlier audit below is historical at the initial hand-back head, not a claim about this revision.

## Done-when

All five implementation items and local host/consumer/plant proofs are met. The additive compatibility decisions were accepted by the coordinator; no game adopts the new API in this PR. cb04b can now opt in after merge. No new issue needs filing; close #12/#13 after acceptance, and close plant drafts unmerged after recording their red CI verdicts. Materialise this note on trunk. Initial hand-back head (superseded by the follow-up above): `2e32a147347126da92bea0dcfe0ca2bdbc6597ba`. Once-read PR run: **40374425241**, in_progress. Canonical audit was run once at this head; last line **`AUDIT FAIL (footprint: cross-cutting)`**. Its failures are the in-progress run/no green tier, missing coordinator-owned full-matrix label, and the retained lane worktree; it found all five sections, correct footprint/head, no attribution and no orphaned lane processes. CI/full-matrix label, worktree pruning and merge belong to the coordinator; no code/test failure is claimed from this pending audit.

Prune after acceptance: Mac `/Users/mfwolffe/lanes/lr03/lair` and `/Users/mfwolffe/lanes/lr03/plant-{restore,decoder,held,minimum}` worktrees, lane archives/scripts/tmp/logs under `/Users/mfwolffe/lanes/lr03/`; hasu `/home/mfwolffe/lanes/lr03/` (engine, four consumer clones, plant trees, toolchains and targets); lr03 and four lr03-plant-* branches. No live job remains. Remove only these exact lane paths, never a repository-wide worktree loop.


