# lib-root.sh — sourced by every tool; not executable on its own.
#
# Where things are. The engine's tools run from two places: lair's own
# checkout (`tools/check`), and a game's staged copy of the engine
# (`<game>/.lair/tools/check`, put there by the game's tools/fetch-lair at
# the commit `lair.pin` names). So:
#   LAIR_ROOT  the directory holding these tools and wolf-toolchain.toml
#   GAME_ROOT  the game's root when LAIR_ROOT is a game's `.lair`, else
#              LAIR_ROOT (lair is then the "game": its own entry and tests)
#   GAME       the program's name: the one `src/*.lu` that is no test
#              (`pack`, `cub`, `lair`); the binary is target/<tier>/<GAME>
#              and the entry src/<GAME>.lu
# The toolchain is staged into $GAME_ROOT/.wolf-bin (one per checkout, so a
# re-staged engine never costs a re-fetched compiler).
#
# THE PIN. In a game, `$LAIR_ROOT/LAIR-REV` (written by fetch-lair) must be
# the commit `$GAME_ROOT/lair.pin` names, or every tool refuses: a game is
# built on the engine it pinned and nothing else. LAIR_UNPINNED=1 lifts the
# refusal LOUDLY (printed on every tool) for the one place that means to
# run a game on another engine: lair's own CI, which runs pack on the
# engine under test, and a lane developing both at once.
: "${LAIR_ROOT:?lib-root.sh needs LAIR_ROOT}"
if [ -f "$LAIR_ROOT/../lair.pin" ]; then
    GAME_ROOT=$(cd "$LAIR_ROOT/.." && pwd)
else
    GAME_ROOT=$LAIR_ROOT
fi
GAME=
for f in "$GAME_ROOT"/src/*.lu; do
    case "$f" in
    *_test.lu) ;;
    *)
        [ -z "$GAME" ] || { echo "lib-root: two entries under src/: $GAME and $(basename "$f" .lu)" >&2; exit 2; }
        GAME=$(basename "$f" .lu)
        ;;
    esac
done
[ -n "$GAME" ] || { echo "lib-root: no entry under $GAME_ROOT/src/" >&2; exit 2; }
if [ "$GAME_ROOT" != "$LAIR_ROOT" ]; then
    pin=$(sed -n 's/^\([0-9a-f]\{40\}\).*/\1/p' "$GAME_ROOT/lair.pin" | head -1)
    have=$(cat "$LAIR_ROOT/LAIR-REV" 2>/dev/null || echo "(no LAIR-REV: not staged by tools/fetch-lair)")
    if [ "$have" != "$pin" ]; then
        if [ "${LAIR_UNPINNED:-0}" = 1 ]; then
            echo "${0##*/}: the engine is NOT the pinned one (LAIR_UNPINNED=1): have $have, lair.pin $pin" >&2
        else
            echo "${0##*/}: REFUSED — .lair is $have, lair.pin wants $pin; run tools/fetch-lair" >&2
            exit 1
        fi
    fi
fi
export LAIR_ROOT GAME_ROOT GAME
