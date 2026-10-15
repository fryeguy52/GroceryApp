#!/usr/bin/env bash
set -Eeuo pipefail

REPO_DIR="/home/clegane/GroceryApp"
SERVICE="groceryapp"
EXPECTED_BRANCH="develop"

cd "$REPO_DIR"

branch="$(git branch --show-current)"
if [[ "$branch" != "$EXPECTED_BRANCH" ]]; then
  echo "ERROR: This updater expects branch '$EXPECTED_BRANCH'; current branch is '$branch'." >&2
  echo "Switch to the intended branch manually, then run this script again." >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: Working tree has local changes. Nothing was updated." >&2
  git status --short
  echo "This app may edit recipe files. Preserve or commit those changes before retrying." >&2
  exit 1
fi

echo "Fetching latest changes..."
git fetch origin "$EXPECTED_BRANCH"

echo "Updating $EXPECTED_BRANCH (fast-forward only)..."
git pull --ff-only origin "$EXPECTED_BRANCH"

echo "Restarting $SERVICE..."
sudo systemctl restart "$SERVICE"

if systemctl is-active --quiet "$SERVICE"; then
  echo "$SERVICE restarted successfully."
  systemctl --no-pager --full status "$SERVICE"
else
  echo "ERROR: $SERVICE is not active. Recent logs:" >&2
  sudo journalctl -u "$SERVICE" -n 50 --no-pager >&2
  exit 1
fi
