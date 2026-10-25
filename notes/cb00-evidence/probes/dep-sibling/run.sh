#!/bin/sh
# The reproducer: the dependency builds alone; the consumer fails with
# E0301 inside the dependency's tier.lu (`use grid` cannot be resolved
# when eng is compiled as app's path dependency). WOLF names the compiler.
set -u
here=$(cd "$(dirname "$0")" && pwd)
echo "== eng alone (expected: 'eng 32')"
(cd "$here/eng" && "${WOLF:-wolf}" run eng.lu)
echo "== app depending on eng (expected 'app 32'; measured at 0.2.35: E0301 in pkg://eng/tier/tier.lu)"
(cd "$here/app" && "${WOLF:-wolf}" run app.lu)
