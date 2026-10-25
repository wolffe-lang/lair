# lr01 — the mixer (lair#8, merged at 09f5aa54)

The lane's report, materialised from the PR body at the merge by the orchestrator (the Codex wrapper writes no Markdown). Evidence under `notes/lr01-evidence/`.

## Prediction

Prepared parts render to byte-identical PCM on both hosts and native/release. Cue and tick do bounded work without I/O; frame cost remains under 1 ms and key latency under the existing 40/70 ms bars. Prediction committed before implementation in `1f812e3`.

Footprint: cross-cutting

## Forbidden

No other sound implementation read; only the org's own `pax/user/play/`, its format and orchestra note. No dependency, assembly adapter, game cue wiring, merge, label, tag, release or issue action. No signal scripts. No attribution trailers. The private planning repo and configuration were not edited.

## Inputs verified

- Base `aa6c4dc0`, isolated `lr01` worktree.
- Source PAX trunk `09471da41cee86eb2c1d9aa5a8f647532b48551c`; `parts.lu`, `orch.lu`, `mix.lu` and parsing/pitch helpers from `play.lu`. Latest ported-pair change `a9f42752a8ad4b9ec6711b8019292f6de7fd620a`; authorship in `docs/SOUND.md`.
- Unchanged pinned wolf 0.2.35 / lupin 0.1.56 / wolf-std `2386522eb059cca5a84108562c2c0a0e72345d34`; both hosts fetched archives by the existing digest verifier and checked binary identities on every build.
- README read and refreshed, including 68 tests, the sound commands and the live-output boundary.

## Evidence index

- `16486ab`: port reader and integer orchestra.
- `77cd899`: cue mixing, WAV output ownership and CLI.
- `4e19022`: original studies, PCM goldens and CI sound rows.
- `8f3595c`: acknowledge a key only after its cue/tick/frame.
- `98684a4`: format, authorship and output boundary documentation.
- `efa19be`: shorten overlapping fades for short cues, with regression test.
- `09f5aa5`: final host logs, after the last code change.

Tests:
- [x] nomad `tools/check`: fmt, 68 checked tests (0 SKIP), native/release builds, sound gate, selftest.
- [x] kasumi `tools/check-linux` in the container, taskset 4–7 under the shared flock: same tests and byte-identical PCM.
- [x] Three PCM goldens: den, chase, cue replay; replay rendered twice per tier on each host.
- [x] All 17 reader timbres and aliases; named malformed-part refusal; ties/hairpins; WAV bytes; OSS stub request/answer contract; cue fades, replacement, layers and capacity; short-cue audibility.
- [x] macOS afplay child started and reaped, second start refused, repeated finish harmless; missing paplay and unsupported OSS each log once.
- [x] Real pty quit and typed Ctrl-C restore with mixing on/off; latency on/off; Linux idle wakes on/off.
- [x] CI planner and memory-gate selftests; `git diff --check`.
- [x] Both local plants red by their intended rows, logs committed.
- [ ] CI plant red verdicts: first reads were in_progress / queued; orchestrator watches, no lane polling.
- [ ] PR tier/full CI and canonical lane audit: orchestrator owns the remaining watch, label and audit.

### Note

This is the full `lr01-the-mixer` lane note, carried here under the contract's fallback: this SDK forbids writing report/note Markdown files. Materialise it as `notes/lr01-the-mixer.md` on trunk at merge.

**What was built.** The complete PAX part reader and seventeen-timbre integer orchestra, with device writes replaced by PCM appends. `render(score, seconds)` returns exactly bounded 48 kHz stereo S16_LE PCM, with silence after tails. `prepare` reads optional `cue replace|layer fade N` metadata and renders before the frame loop. A bank holds at most sixteen cues; the frame mixer holds at most four active slots, fades by sample count and reserves quarter-scale headroom per slot. Unknown names and full capacity are non-mutating refusals. A long requested fade is shortened to half a short cue so it does not silence that cue.

Original den and chase studies live in `tests/parts/`; their four-second PCM and the fixed cue replay live in `tests/goldens/sound/`. `lair --play PART` auditions six seconds using an exclusively created temporary WAV, reaps its own child and removes the file. `--render`, `--wav`, `--sound-replay` and the benchmark/terminal witnesses expose the deterministic paths.

**Scope boundary.** Lair does not synthesise live: it mixes prepared PCM. The WAV-per-cue adapter owns and reaps a prepared WAV's afplay/paplay child asynchronously during playback, but finish waits during teardown. It does not stream tick PCM into an already-running player. Audible live replacement/layering needs a streaming output or precomputed transition WAVs; neither game is wired here. This lane proves mixed PCM/replay and isolated output lifecycle, not that missing audible bridge. OSS is a tested negotiation stub and a named unsupported refusal, never an unconfigured `/dev/dsp` write.

**Recommendations implemented, not rulings decided.**
- R-lr01-1 A: play's own 48000 Hz, stereo S16_LE, no resampling.
- R-lr01-2 A: WAV per cue via afplay on macOS; no installation, explicit child ownership and reaping.
- R-lr01-3: portable OSS request/answer contract, named `oss_ioctl_unsupported`; real device adapter goes to the PAX integration or wolf-std when it exposes ioctl. No assembly in lair.
- R-lr01-4: render ahead during cue preparation, bounded fade/layer mixing during the tick. The audible live-transition bridge is a follow-on.

**Final measurements.** Frame = the same 80x24 grid render/diff, without sound and with four cached layers; preparation excluded, cue/tick included. These are the sound witness's numbers, not claims about pack's simulation.

| host/tier | silent avg/max us | mixing avg/max us |
|---|---:|---:|
| nomad native | 14 / 25 | 86 / 110 |
| nomad release | 8 / 17 | 29 / 38 |
| kasumi native | 29 / 126 | 170 / 235 |
| kasumi release | 19 / 50 | 77 / 168 |

| host | silent latency median/p90/max ms | mixing latency median/p90/max ms | idle wakes, silent/mixing |
|---|---:|---:|---|
| nomad | 33.12 / 34.12 / 34.18 | 33.15 / 34.13 / 34.19 | two loud platform SKIPs; no /proc counter |
| kasumi | 33.35 / 33.40 / 33.42 | 33.45 / 33.49 / 33.51 | 90 / 91 in 3 s; bar 72–108 |

Every frame average is below 1 ms; maxima below one 33.3 ms frame. Latency remains below median 40 ms / p90 70 ms. The Linux idle row adds no between-tick wake pattern. The unit tests have zero SKIPs; sound-check has exactly the two named macOS counter SKIPs and none on Linux. Real afplay succeeded on nomad; CI macOS audio-device availability remains for its run to answer.

**PCM sha256, identical on both hosts and tiers:**
- den: `4b9bd3308dcdccaa1967161d59e0e29f9e8e8ea0912213c5206f607333785c51`
- chase: `5f410524f659dcf3a6b0c33e3fd3fad39c38cc7e213cdb9c85a22c6c354dcf69`
- cue replay: `e5c4c2e4e5c398991396f8999a871ba18e55600ea9c6fd79ef521be14ff86893`

**Plants, left open.**
- #6 `lr01-plant-envelope`, head `10128b6eff15c6451c777ddc2d33a73317a3e51b`, run `40210198518`: flute attack 40→80 ms. Local `sound-golden den/native` red at byte 55. First CI read in_progress, no red CI claim yet.
- #7 `lr01-plant-latency`, head `1749c564d75b2dd3f6dd565edc55fe4c79d3add4`, run `40210201141`: key cue blocks 120 ms. Local PCM stays equal; off median/p90 33.08/33.98 ms, on 132.41/135.29 ms, `sound-latency on FAILED`. First CI read queued, no red CI claim yet.

The expected determinism and budget predictions held. Review found a short-cue fade-overlap bug not in the prediction; `efa19be` fixes it and both final host legs cover the fix. No golden was regenerated for that fix.

Evidence is in `notes/lr01-evidence/{prediction.txt,check-nomad.txt,check-linux.txt,plant-envelope-local.txt,plant-latency-local.txt}`. The kasumi build tree was pruned after its proof; its toolchain and final log remain under `~/lanes/lr01/`. No background job remains. Canonical audit is unrun by agreement: its hard-coded temporary files conflict with lane scratch restrictions; the orchestrator runs it at hand-back. No label was applied.

## Follow-ons

Issues to file (none filed here):
1. **wolf-std:** expose a safe int-in/out ioctl/device adapter sufficient for `SNDCTL_DSP_SETFMT (0xc0045005, AFMT_S16_LE=0x10)`, `SNDCTL_DSP_CHANNELS (0xc0045006, 2)`, `SNDCTL_DSP_SPEED (0xc0045002, 48000)`. PAX play negotiates these through assembly; lair must stay wolf-std-only. Returned values must be checked before any PCM writes.
2. **lair / lr02:** connect mixed tick PCM to a nonblocking audible sink, or precompute transition WAVs; prove audible replace/layer fades and bounded shutdown. The present WAV-per-cue owner is not that bridge.
3. **Games:** cub's den cue and pack's game cues remain their later lanes' integration work. No cue is added by this PR.

The orchestrator watches the PR and both plants, verifies the plants red by name, runs the audit, applies the full-matrix label at the final head and watches the full run. Close #6/#7 unmerged after recording their CI verdicts. No existing issue to close is claimed.


## Done-when

- **Met:** the sound module ports the authorized part reader, seventeen timbres, envelopes and integer orchestra; rendering is deterministic 48 kHz stereo S16_LE PCM.
- **Met within the agreed output scope:** WAV-per-cue playback owns and reaps its child; missing output is named silence; OSS negotiation is stub-tested. **Named follow-on:** a real OSS adapter requires wolf-std ioctl support or the PAX integration.
- **Met:** named cue replacement/layering and sample-count fades produce deterministic mixed PCM; bounded tick cost, idle wakes and key latency are measured with and without sound. **Named follow-on:** an audible live-transition bridge needs streaming output or prepared transition WAVs; no game is wired here.
- **Met:** original den/chase parts, committed PCM goldens and `lair --play`; goldens match on both hosts and native/release tiers, and cue replay matches twice per tier.
- **Met:** format/output/hook/authorship documentation, reader/render/WAV/OSS/cue tests and CI sound rows; the full lane note is retained under **Note** above for materialisation at merge.
- **Met locally:** both deliberate plants fail their intended rows. **Coordinator verification:** record the red-by-name CI verdicts for #6/run 40210198518 and #7/run 40210201141, then close those drafts unmerged.
- **Met, coordinator-reported:** PR #8 is green on both CI runs. Final head remains `09f5aa54ec7f1ba7f6687d98f445b5510339cd60`; no code push or label change accompanies this body correction.
- **Met:** hand-back includes PR/head, available run IDs, both plants, frame-cost numbers, recommendations implemented and issues to file. **Coordinator-owned:** canonical audit, final CI verification and merge.

