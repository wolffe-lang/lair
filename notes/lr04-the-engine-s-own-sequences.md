# lr04 — the engine's own sequences

_Materialised from lair#23's body at the merge (`74b89744`); the Codex wrapper writes no .md notes._

## Prediction

Recognising the engine's four keyboard controls strictly will clear the capture tails without changing any rendered cell, style, cursor or pending wrap. Prediction committed before implementation in `ab0b36c`.


Addresses #22. This PR body is the five-section lr04 note; materialise it as `notes/lr04-the-engine-s-own-sequences.md` at merge (the lane wrapper forbids Markdown report/note files).

## Forbidden

No terminal emulator or library implementation source read. No game-source or committed consumer-pin changes, golden regeneration, dependencies, toolchain/CI edits, host packages, planning/configuration edits, labels, merges, issue closures or attribution trailers. The two deliberate breaks ran locally, not in CI.

## Inputs verified

- Base `5c81abb`; contract, RULES sections 1–10, lair#22 and lr03's trunk note read.
- Source: https://sw.kovidgoyal.net/kitty/keyboard-protocol/ — Detection of support for this protocol and Progressive enhancement. `docs/SOURCES.md` records the four output forms and fixture origin.
- Unchanged pinned wolf 0.2.35 / lupin 0.1.56 and bundled std identity checked by the existing toolchain loader on every test/build.
- Original cub capture copied unchanged: 56,288 bytes; source and fixture SHA-256 both `174552af26240164d433d41f8033b71a600b5525408ad4a002b31edf1c90e8a7`.
- Consumer: scratch cub checkout at the contract's `cb04b` head `1edbce4fa732a719b18a931204f4f0f10509394e`, pin and staged engine pointed at this final head; no cub commit. An earlier local cb04b clone at `a758a7d1` also passed, but the named contracted head was then fetched and tested explicitly.
- `ci/games.conf` currently names pack only. Its resolved `cb00` head was `59cef8077bc2fb16bfd9260ed1024437ae6c370a`.
- **R-lr04-1 implemented:** recognise output grammar, not every `u`: track the actual prefix; reject terminal replies (`?flags u`), bare/unknown/malformed controls and invalid set modes; keep existing private cursor/alternate-screen dispatch separate. Recognition does not emulate keyboard flags or mutate rendering state.
- README read and refreshed in its own commit: 86 checked tests and the model/capture guarantee.

## Evidence index

- `ab0b36c`: prediction.
- `201d42c`: strict model recogniser and seven named test groups, all byte splits.
- `e43f996`: original cub fixture and strict native/release replay of live engine captures.
- `dfac8b5`: protocol citation and fixture provenance.
- `65637e2`: README-only refresh.
- `74b8974`: immutable host, consumer and deliberate-red logs under `notes/lr04-evidence/`.

### Tests and measurements

- [x] Mac `tools/check`: fmt, **86 checked tests / zero SKIPs**, native and release builds, unchanged PCM goldens, sound gates, 28 input/keyprobe rows, both selftests. Behind the existing 8 GiB vm_stat gate; one full build. No code changed afterwards, only docs/evidence.
- [x] Kasumi `tools/check-linux` at final head **74b89744e8f8a4ed01539b2fe814daf819b9abfc**: same engine gates green, **86 tests / zero SKIPs**. Rootless `localhost/pack-ci:fbee7e864f7dbee6`, 12 GiB, taskset CPUs 0–3 under `/home/mfwolffe/lanes/kasumi-cores-0-3.lock`.
- [x] Four keyboard forms, omitted defaults, explicit pop count and set modes; whole feed and every byte boundary across two feeds. Unknown `CSI ? 1 h` and `CSI > 11 m` remain counted, as do unsupported prefixes/finals and malformed forms. Every case checks unchanged cells/style/cursor/wrap/modes and resumed parsing of ordinary/private controls.
- [x] Original cub fixture replayed by native and release binaries on both hosts: `alt_enters 1 alt_leaves 1 cursor_visible true unknown 0`.
- [x] The same exact tail asserted on **20 live input-loop replays per host** (10 each tier), including crash/error/typed Ctrl-C, negotiated/fallback/legacy, small and resized sessions. The existing keyprobe/minimum rows stay green.
- [x] Contracted cub builds both tiers; release `agree-rich` and `agree-plain` rows green at final engine head. Their captured text and styles agree with their respective headless runs, not merely the tails.
- [x] Pack full Linux leg at final engine head: **150 tests / zero SKIPs**, both builds, selftest, **39 golden directories unchanged** (38 rich/plain cases plus art), all eight pty rows green. No expected golden edited.
- [x] Both local deliberate plants red by the intended named row, below.
- [x] `git diff --check`; clean lr04 worktree; plant worktrees pruned after their runs.
- [ ] PR-tier CI: coordinator watches; lane reads the run once and never waits or labels.

Cub's two final-head tails, verbatim:

```text
cub agree-rich tail: alt_enters 1 alt_leaves 1 cursor_visible true unknown 0
cub agree-plain tail: alt_enters 1 alt_leaves 1 cursor_visible true unknown 0
```

Tracked evidence: `notes/lr04-evidence/{mac-check,check-linux,consumers-linux,cub-contracted,plant-forgive,plant-split}.log`. Exact-final-head rerun (engine, contracted cub, pack): `/Users/mfwolffe/lanes/lr04/final-check.log`; runner `/Users/mfwolffe/lanes/lr04/final-check.sh`. The earlier evidence commit naturally precedes that rerun; source code is identical.

### Deliberate plants

- Local branch `lr04-plant-forgive`, **80d43d7**: forgive `>` with final `m`. Nomad `tools/check` exits **1**: `test_model_unknown_push_sgr_every_split ... FAILED (trap(assert))`; **85 passed / 1 failed / zero rejected**. Log `notes/lr04-evidence/plant-forgive.log`.
- Local branch `lr04-plant-split`, **7dbd5a1**: lose `?` when the next feed resumes a CSI. Nomad `tools/check` exits **1**: `test_model_keyboard_query_every_split ... FAILED (trap(assert))`; **85 passed / 1 failed / zero rejected**. Log `notes/lr04-evidence/plant-split.log`.

An initial development test was rejected because `_test.lu` helpers are not shared across test files; a local byte helper fixed that before the first green. Neither deliberate plant failed compilation or formatting.

## Done-when

Final head **74b89744e8f8a4ed01539b2fe814daf819b9abfc** is pushed. Local gates and both negative witnesses are complete. No live lane job remains. The once-only immediate run lookup returned **40441366107**, `in_progress`. Canonical audit ran once and exited **1**, last line **`AUDIT FAIL (footprint: module)`**: only in-progress head CI/no green tier yet, and the retained lane worktree. All other checks passed, including every path fitting module, matching PR head, all five sections, no attribution and no orphaned lane processes. No wait or label followed. Close **lair#22** after acceptance; no new issue to file. The orchestrator owns PR-tier green, merge and note materialisation. Cub may adopt this head once merged.

Cleanup after acceptance: Mac `/Users/mfwolffe/lanes/lr04/lair` worktree and lane-owned scripts/logs/bundles under `/Users/mfwolffe/lanes/lr04/`; kasumi `/home/mfwolffe/lanes/lr04/` (engine and two scratch consumers). Local `lr04-plant-forgive` and `lr04-plant-split` branches retain their committed breaks; neither was pushed. No other lane path is owed cleanup.

