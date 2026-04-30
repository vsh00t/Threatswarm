#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "⟁ ThreatSwarm — OpenCode Setup"
echo "─────────────────────────────────"
echo ""

# Check OpenCode is installed
if ! command -v opencode &>/dev/null; then
    echo "❌ OpenCode not found. Install with:"
    echo "   brew install opencode-ai/tap/opencode"
    echo "   or: go install github.com/opencode-ai/opencode@latest"
    exit 1
fi
echo "✅ OpenCode found: $(opencode --version 2>/dev/null || echo 'installed')"

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 required"
    exit 1
fi
echo "✅ Python 3: $(python3 --version)"

# Verify scope.txt exists
if [ ! -f "$PROJECT_DIR/scope.txt" ]; then
    echo "⚠️  No scope.txt found. Create one with your authorized targets."
    echo "   Example: echo '192.168.1.0/24' > $PROJECT_DIR/scope.txt"
fi

# Verify MCP servers compile
echo ""
echo "── Verifying MCP servers ──"
for mcp in scope-mcp evidence-mcp report-mcp; do
    script="$PROJECT_DIR/integrations/mcp/$mcp/server.py"
    if python3 -c "import py_compile; py_compile.compile('$script', doraise=True)" 2>/dev/null; then
        echo "  ✅ $mcp"
    else
        echo "  ❌ $mcp — compilation failed"
    fi
done

# Copy config template
echo ""
if [ ! -f "$PROJECT_DIR/.opencode.json" ]; then
    cp "$SCRIPT_DIR/.opencode.json.template" "$PROJECT_DIR/.opencode.json"
    echo "✅ Created .opencode.json"
else
    echo "ℹ️  .opencode.json already exists (not overwritten)"
fi

# Copy instructions
if [ ! -f "$PROJECT_DIR/instructions.md" ]; then
    cp "$SCRIPT_DIR/instructions.md" "$PROJECT_DIR/instructions.md"
    echo "✅ Created instructions.md"
else
    echo "ℹ️  instructions.md already exists (not overwritten)"
fi

echo ""
echo "═══════════════════════════════"
echo "  Setup complete!"
echo "  Run: opencode"
echo "═══════════════════════════════"
