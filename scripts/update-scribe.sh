#!/usr/bin/env bash
# Pull the newest Scribe into Scriptorium.
#
# Scribe lives at lib/scribe as a git submodule. A submodule records one exact
# commit, so cloning Scriptorium always gets a Scribe that is known to work with
# it — but it also means Scribe moving forward does NOT move Scriptorium. This
# script is what moves the pin: it fetches Scribe's tracking branch (`main`, as
# recorded in .gitmodules), checks out its tip, and stages the new pin.
#
# Usage:
#   scripts/update-scribe.sh            # bump to the latest Scribe, stage it
#   scripts/update-scribe.sh --check    # report whether a newer Scribe exists,
#                                       # change nothing (exit 1 if behind)
#
# After a bump, run the tests before committing:
#   wfl --test TestPrograms/util.test.wfl   (and the rest — see README)
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

check_only=no
if [ "${1:-}" = "--check" ]; then
    check_only=yes
elif [ "$#" -gt 0 ]; then
    echo "usage: scripts/update-scribe.sh [--check]" >&2
    exit 2
fi

if [ ! -e lib/scribe/src/scribe.wfl ]; then
    echo "lib/scribe is not checked out. Run:" >&2
    echo "    git submodule update --init --recursive" >&2
    exit 1
fi

before="$(git -C lib/scribe rev-parse HEAD)"

branch="$(git config -f .gitmodules submodule.lib/scribe.branch || echo main)"
git -C lib/scribe fetch --quiet origin "$branch"
after="$(git -C lib/scribe rev-parse FETCH_HEAD)"

if [ "$before" = "$after" ]; then
    echo "Scribe is already at the tip of $branch ($(git -C lib/scribe log -1 --format=%h))."
    exit 0
fi

# The pin can legitimately sit *ahead* of the tracking branch — e.g. it points at
# a Scribe branch whose PR has not merged yet. Bumping would be a downgrade, so
# say so and leave it alone.
if git -C lib/scribe merge-base --is-ancestor "$after" "$before"; then
    echo "The pinned Scribe is ahead of $branch — nothing to bump."
    echo "Pinned commits not yet on $branch:"
    git -C lib/scribe log --oneline --no-decorate "$after..$before" | sed 's/^/    /'
    exit 0
fi

echo "Scribe $branch has moved:"
git -C lib/scribe log --oneline --no-decorate "$before..$after" | sed 's/^/    /'

if [ "$check_only" = yes ]; then
    echo
    echo "Run scripts/update-scribe.sh (without --check) to bump the pin."
    exit 1
fi

git -C lib/scribe checkout --quiet --detach "$after"
git add lib/scribe

echo
echo "Bumped lib/scribe: $(git -C lib/scribe rev-parse --short "$before") -> $(git -C lib/scribe rev-parse --short "$after") (staged)."
echo "Run the test suites, then commit."
