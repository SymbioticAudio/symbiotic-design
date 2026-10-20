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
# The active developer directory: DEVELOPER_DIR if set and non-empty, else xcode-select's choice.
dev="${DEVELOPER_DIR:-}"
if [[ -z "$dev" ]]; then
    dev="$(xcode-select -p 2>/dev/null || true)"
fi
# Ignore trailing slashes, so .../CommandLineTools/ counts as the CLT.
while [[ "$dev" == */ ]]; do
    dev="${dev%/}"
done
if [[ "$dev" != "$clt" ]]; then
    # Full Xcode (CI runners): default build system, Swift Testing in place.
    echo "swift.sh: Xcode (${dev:-unknown developer dir}): plain swift $cmd" >&2
    exec swift "$cmd" --package-path "$root" "$@"
fi
echo "swift.sh: Command Line Tools: swift $cmd with the native build system" >&2
# Command Line Tools only: the native build system, plus the paths of
# Swift Testing, which the CLT ship outside the default search paths.
fw="$clt/Library/Developer/Frameworks"
exec swift "$cmd" --package-path "$root" --build-system native \
    -Xswiftc "-F$fw" \
    -Xlinker "-F$fw" \
    -Xlinker -rpath -Xlinker "$fw" \
    -Xlinker -rpath -Xlinker "$clt/Library/Developer/usr/lib" \
    "$@"
