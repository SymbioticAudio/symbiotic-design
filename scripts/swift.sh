#!/usr/bin/env bash
# Runs SwiftPM on this package with the flags the toolchain needs.
# Usage: scripts/swift.sh <build|test> [swift args...]
# MIT licence: see LICENSE.
set -euo pipefail
if [[ $# -lt 1 ]]; then
    echo "usage: scripts/swift.sh <build|test> [args...]" >&2
    exit 2
fi
root="$(cd "$(dirname "$0")/.." && pwd)"
cmd="$1"
shift
clt="/Library/Developer/CommandLineTools"
if [[ "${DEVELOPER_DIR:-}" != "$clt" ]]; then
    # Full Xcode (CI runners): default build system, Swift Testing in place.
    exec swift "$cmd" --package-path "$root" "$@"
fi
# Command Line Tools only: the native build system, plus the paths of
# Swift Testing, which the CLT ship outside the default search paths.
fw="$clt/Library/Developer/Frameworks"
exec swift "$cmd" --package-path "$root" --build-system native \
    -Xswiftc "-F$fw" \
    -Xlinker "-F$fw" \
    -Xlinker -rpath -Xlinker "$fw" \
    -Xlinker -rpath -Xlinker "$clt/Library/Developer/usr/lib" \
    "$@"
