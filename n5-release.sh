#!/bin/bash
# Quick release script for n5-core
set -e

if [ -z "$1" ]; then
    echo "Usage: ./n5-release.sh <version> [release-notes]"
    echo "Example: ./n5-release.sh 0.2.0 'Added CRM module'"
    exit 1
fi

VERSION="$1"
NOTES="${2:-Release $VERSION}"

cd /home/workspace/n5-core

# Update VERSION file
echo "$VERSION" > VERSION

# Update CHANGELOG
TODAY=$(date +%Y-%m-%d)
sed -i "s/## \[Unreleased\]/## [Unreleased]\n\n## [$VERSION] - $TODAY/" CHANGELOG.md

# Commit and tag
git add VERSION CHANGELOG.md
git commit -m "Release v$VERSION"
git tag -a "v$VERSION" -m "$NOTES"
git push && git push --tags

# Create GitHub release
gh release create "v$VERSION" \
    --title "N5 Core v$VERSION" \
    --notes "$NOTES" \
    --latest

echo "✓ Released v$VERSION"
