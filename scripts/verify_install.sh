#!/usr/bin/env bash
# Install pddlstream into a throwaway virtualenv and check that it can actually plan.
#
#   ./scripts/verify_install.sh                     # install from the default git ref
#   ./scripts/verify_install.sh packaging           # a branch, tag or SHA
#   ./scripts/verify_install.sh .                   # a local checkout (fast, no clone)
#
# Override the repository with PDDLSTREAM_REPO.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-packaging}"
REPO="${PDDLSTREAM_REPO:-https://github.com/Minseo10/pddlstream.git}"

if [ -d "$TARGET" ]; then
    SOURCE="$(cd "$TARGET" && pwd)"
    LABEL="local checkout $SOURCE"
else
    SOURCE="git+${REPO}@${TARGET}"
    LABEL="$REPO @ $TARGET"
fi

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

echo "installing : $LABEL"
echo "python     : $(python3 -V)"
echo

python3 -m venv "$WORKDIR/venv"
"$WORKDIR/venv/bin/pip" install --quiet --upgrade pip
# Building FastDownward takes a few minutes; --no-cache-dir keeps a stale wheel from
# hiding a broken build.
"$WORKDIR/venv/bin/pip" install --quiet --no-cache-dir "$SOURCE"

SITE="$("$WORKDIR/venv/bin/python" -c 'import site; print(site.getsitepackages()[0])')"
echo "installed  : $(du -sh "$SITE/pddlstream" | cut -f1)"

# Run from the throwaway directory: no pddlstream source tree, so nothing can mask the
# installed package.
cd "$WORKDIR"
"$WORKDIR/venv/bin/python" "$SCRIPT_DIR/smoke_test.py"
