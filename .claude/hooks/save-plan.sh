#!/usr/bin/env bash
# save-plan.sh — Auto-save the most recent Claude Code plan to plans/
# Called by the PostToolUse hook on ExitPlanMode.
# Must be run from the project root (where .claude/ and plans/ live).

set -euo pipefail

PLANS_DIR="$HOME/.claude/plans"
OUTPUT_DIR="plans"
TODAY=$(date +%Y-%m-%d)

# Find the most recently modified plan file
PLAN_FILE=$(ls -t "$PLANS_DIR"/*.md 2>/dev/null | head -1)
if [[ -z "$PLAN_FILE" ]]; then
  echo "[save-plan] No plan files found in $PLANS_DIR — skipping."
  exit 0
fi

# Extract title from first # heading
TITLE=$(grep -m1 '^# ' "$PLAN_FILE" | sed 's/^# //')
if [[ -z "$TITLE" ]]; then
  TITLE="Untitled Plan"
fi

# Generate slug: lowercase, spaces to hyphens, strip non-alphanumeric (except hyphens)
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[[:space:]]/-/g' | sed 's/[^a-z0-9-]//g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')

OUTPUT_FILE="$OUTPUT_DIR/${TODAY}_${SLUG}.txt"

# Don't overwrite an existing file
if [[ -f "$OUTPUT_FILE" ]]; then
  echo "[save-plan] File already exists: $OUTPUT_FILE — skipping."
  exit 0
fi

mkdir -p "$OUTPUT_DIR"

# Copy plan verbatim (no frontmatter)
cp "$PLAN_FILE" "$OUTPUT_FILE"

echo "[save-plan] Plan saved to $OUTPUT_FILE"
