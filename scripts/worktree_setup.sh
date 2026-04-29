#!/usr/bin/env bash
# worktree_setup.sh — Create isolated git worktrees for parallel pentesting engagements
# Usage: ./scripts/worktree_setup.sh <engagement-name> [engagement-name-2 ...]
#
# Each worktree gets its own branch, copied scope.txt, and fresh evidence/reports/loot dirs.
# Allows running multiple engagements simultaneously without cross-contamination.

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Usage: $0 <engagement-name> [engagement-name-2 ...]"
    echo ""
    echo "Examples:"
    echo "  $0 acme-external"
    echo "  $0 acme-external acme-internal"
    echo "  $0 client-webapps-q1-2025"
    exit 1
fi

# Check if we're in a git repo; initialize one if not
if ! git rev-parse --git-dir &>/dev/null; then
    echo "[*] Not in a git repository. Initializing git..."
    git init
    git add -A
    git commit -m "Initial workspace commit — $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --allow-empty 2>/dev/null || true
    echo "[+] Git repository initialized"
fi

PROJECT_ROOT=$(git rev-parse --show-toplevel)
PROJECT_NAME=$(basename "$PROJECT_ROOT")

echo "═══════════════════════════════════════════════════════"
echo "  WORKTREE SETUP"
echo "  Project root: $PROJECT_ROOT"
echo "  Creating:     $# engagement(s)"
echo "═══════════════════════════════════════════════════════"

for ENGAGEMENT in "$@"; do
    # Sanitize engagement name (lowercase, hyphens only)
    ENGAGEMENT_CLEAN=$(echo "$ENGAGEMENT" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
    BRANCH_NAME="engagement/$ENGAGEMENT_CLEAN"
    WORKTREE_PATH="$PROJECT_ROOT/../$PROJECT_NAME-$ENGAGEMENT_CLEAN"

    echo ""
    echo "[*] Setting up worktree: $ENGAGEMENT_CLEAN"
    echo "    Branch:   $BRANCH_NAME"
    echo "    Path:     $WORKTREE_PATH"

    # Check if worktree already exists
    if git worktree list | grep -q "$WORKTREE_PATH"; then
        echo "    [!] Worktree already exists at $WORKTREE_PATH — skipping"
        continue
    fi

    # Create branch if it doesn't exist, then add worktree
    if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
        echo "    [*] Branch $BRANCH_NAME exists — adding worktree"
        git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"
    else
        echo "    [*] Creating new branch: $BRANCH_NAME"
        git worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH"
    fi

    # Create required directories in worktree
    mkdir -p "$WORKTREE_PATH/evidence"
    mkdir -p "$WORKTREE_PATH/reports"
    mkdir -p "$WORKTREE_PATH/loot"
    mkdir -p "$WORKTREE_PATH/scripts"
    touch "$WORKTREE_PATH/evidence/.gitkeep"
    touch "$WORKTREE_PATH/reports/.gitkeep"
    touch "$WORKTREE_PATH/loot/.gitkeep"

    # Copy scope.txt if it exists in the main workspace
    if [ -f "$PROJECT_ROOT/scope.txt" ]; then
        cp "$PROJECT_ROOT/scope.txt" "$WORKTREE_PATH/scope.txt"
        echo "    [+] Copied scope.txt — EDIT before starting engagement"
    else
        # Create blank scope.txt template
        cat > "$WORKTREE_PATH/scope.txt" << 'SCOPE_TEMPLATE'
# Engagement Scope — Edit before running any tools
# One entry per line: IP address, CIDR range, or domain name
# Lines starting with # are ignored

# Example entries:
# 10.10.10.0/24
# 192.168.1.100
# target.example.com

SCOPE_TEMPLATE
        echo "    [+] Created blank scope.txt — ADD TARGETS before running"
    fi

    # Create engagement-specific CLAUDE.md override
    cat > "$WORKTREE_PATH/CLAUDE.md" << ENGAGEMENT_CLAUDE
# Claude Code — Engagement: $ENGAGEMENT_CLEAN

This is an isolated worktree for engagement: **$ENGAGEMENT_CLEAN**

Refer to the main workspace CLAUDE.md for full operator instructions.

## Engagement Context

- **Engagement:** $ENGAGEMENT_CLEAN
- **Started:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
- **Branch:** $BRANCH_NAME
- **Evidence dir:** evidence/ (relative to this worktree)
- **Scope file:** scope.txt (EDIT WITH ACTUAL TARGETS)

## Quick Start

1. Edit \`scope.txt\` with authorized targets
2. Run: \`/project:engage <target>\`
3. Run: \`/project:attack <target> <vector>\`
4. Run: \`/project:report $ENGAGEMENT_CLEAN\`

## Anti-Patterns

- Never run tools before verifying scope.txt is populated
- Never commit loot/ or evidence/ to this branch
ENGAGEMENT_CLAUDE

    echo "    [+] Worktree ready at: $WORKTREE_PATH"
    echo ""
    echo "    To start this engagement:"
    echo "      cd \"$WORKTREE_PATH\" && claude"
    echo ""

done

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  SETUP COMPLETE"
echo ""
echo "  Active worktrees:"
git worktree list
echo ""
echo "  To remove a worktree when engagement is done:"
echo "    git worktree remove <path>"
echo "    git branch -d engagement/<name>"
echo "═══════════════════════════════════════════════════════"
