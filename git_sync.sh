#!/bin/bash

# $1 is the path passed from Python
TARGET_DIR="$1"
BRANCH="main"

if [ -z "$TARGET_DIR" ]; then
    echo "Error: No target directory provided."
    exit 1
fi

# Change to the data directory
cd "$TARGET_DIR" || exit

echo "Syncing inside: $(pwd)"

# 1. Add changes
git add .

# 2. Commit
if git diff --cached --quiet; then
    echo "No changes to commit."
else
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    git commit -m "Auto-Update: $TIMESTAMP"
fi

# 3. Push
echo "Pushing..."
git push origin "$BRANCH"
echo "Pushed to git"