#!/usr/bin/env bash
# Vercel "Ignored Build Step" for monorepo apps. Run from the app's folder (its Root Directory):
#   bash ../../scripts/vercel-ignore.sh
# Exit 0 skips the build, exit 1 builds. Builds whenever the last deployed commit is unknown or
# missing from the clone, and otherwise only if this folder or packages/family changed since then.
prev="$VERCEL_GIT_PREVIOUS_SHA"
[ -z "$prev" ] && exit 1
git cat-file -e "$prev^{commit}" 2>/dev/null || exit 1
git diff --quiet "$prev" HEAD -- . ../../packages/family && exit 0
exit 1
