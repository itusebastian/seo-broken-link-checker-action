#!/bin/bash

echo "==================="

git config --global user.name "${GITHUB_ACTOR}"
git config --global user.email "${INPUT_EMAIL}"
git config --global --add safe.directory /github/workspace

python3 /usr/bin/broken_link_checker.py --sitemap "$SITEMAP_URL" --output broken_links_report.csv --html || true

git add -A && git commit -m "Update Broken Links"
git push --set-upstream origin main

echo "==================="