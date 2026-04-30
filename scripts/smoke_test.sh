#!/usr/bin/env bash
# ThreatSwarm Smoke Test — validates repository integrity
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

check() {
    local desc="$1"
    shift
    if "$@" 2>/dev/null; then
        echo "  [PASS] $desc"
        PASS=$((PASS + 1))
    else
        echo "  [FAIL] $desc"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== ThreatSwarm Smoke Test ==="
echo "Repo: $REPO_DIR"
echo ""

# --- Agent files ---
echo "--- Agents (32 expected) ---"
AGENT_COUNT=$(find "$REPO_DIR/core/agents" -maxdepth 1 -name '*.md' ! -name '_registry.md' | wc -l | tr -d ' ')
check "32 agent .md files in core/agents/ (found $AGENT_COUNT)" [ "$AGENT_COUNT" -eq 32 ]

EXPECTED_AGENTS=(
    active-directory api-attacker blue-team c2-operator cloud-attacker cloud-postex
    compliance-scanner container-attacker crypto-attacker dfir evasion exploit
    iot-attacker log-analyst malware-analyst mobile-attacker network-ops osint
    password-attacks post-ex purple-team recon red-infra report-writer
    reverse-engineer segmentation-tester social-engineer threat-hunter
    vuln-management vuln-researcher web-attacker wireless-attacker
)
for agent in "${EXPECTED_AGENTS[@]}"; do
    check "Agent: $agent.md exists" [ -f "$REPO_DIR/core/agents/$agent.md" ]
done

# --- Adapters ---
echo ""
echo "--- Adapters (4 platforms) ---"
for adapter in claude-code github-copilot opencode openclaw; do
    ADAPTER_DIR="$REPO_DIR/adapters/$adapter"
    if [ -d "$ADAPTER_DIR" ]; then
        FILE_COUNT=$(find "$ADAPTER_DIR" -type f | wc -l | tr -d ' ')
        check "Adapter $adapter: non-empty ($FILE_COUNT files)" [ "$FILE_COUNT" -gt 0 ]
    else
        check "Adapter $adapter: directory exists" false
    fi
done

# --- Core scripts compile ---
echo ""
echo "--- Core Scripts ---"
for script in report_generate.py scope_validate.py; do
    check "core/scripts/$script compiles" python3 -c "import py_compile; py_compile.compile('$REPO_DIR/core/scripts/$script', doraise=True)"
done

# --- Hooks compile ---
echo ""
echo "--- Hooks ---"
for hook in evidence_capture.py findings_sync.py scope_check.py; do
    check "core/hooks/$hook compiles" python3 -c "import py_compile; py_compile.compile('$REPO_DIR/core/hooks/$hook', doraise=True)"
done

# --- Build system ---
echo ""
echo "--- Build System ---"
check "scripts/build.py compiles" python3 -c "import py_compile; py_compile.compile('$REPO_DIR/scripts/build.py', doraise=True)"
check "build.py --list runs" python3 "$REPO_DIR/scripts/build.py" --list >/dev/null 2>&1

# --- MCP Servers ---
echo ""
echo "--- MCP Servers (3) ---"
for mcp in scope-mcp evidence-mcp report-mcp; do
    MCP_FILE="$REPO_DIR/integrations/mcp/$mcp/server.py"
    if [ -f "$MCP_FILE" ]; then
        check "MCP $mcp/server.py compiles" python3 -c "import py_compile; py_compile.compile('$MCP_FILE', doraise=True)"
    else
        check "MCP $mcp/server.py exists" false
    fi
done

# --- Skill libraries ---
echo ""
echo "--- Skill Libraries (5) ---"
SKILL_COUNT=$(find "$REPO_DIR/core/skills" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
check "5 skill directories in core/skills/ (found $SKILL_COUNT)" [ "$SKILL_COUNT" -ge 5 ]

EXPECTED_SKILLS=(ad-attacks exploit-db mitre-attack report-templates wordlists)
for skill in "${EXPECTED_SKILLS[@]}"; do
    check "Skill library: $skill/ exists" [ -d "$REPO_DIR/core/skills/$skill" ]
done

# --- Report templates ---
echo ""
echo "--- Report Templates ---"
TEMPLATE_COUNT=$(find "$REPO_DIR/core/templates" -type f | wc -l | tr -d ' ')
check "At least 4 template files in core/templates/ (found $TEMPLATE_COUNT)" [ "$TEMPLATE_COUNT" -ge 4 ]

EXPECTED_TEMPLATES=(executive_summary.md technical_finding.md remediation_roadmap.md)
for tmpl in "${EXPECTED_TEMPLATES[@]}"; do
    check "Template: $tmpl exists" [ -f "$REPO_DIR/core/templates/$tmpl" ]
done
check "Template: client/ directory exists" [ -d "$REPO_DIR/core/templates/client" ]

# --- Registry ---
echo ""
echo "--- Registry ---"
check "_registry.json exists and is valid JSON" python3 -c "import json; json.load(open('$REPO_DIR/core/agents/_registry.json'))"

# --- Key docs ---
echo ""
echo "--- Documentation ---"
check "README.md exists and is non-empty" [ -s "$REPO_DIR/README.md" ]
check "LICENSE exists" [ -f "$REPO_DIR/LICENSE" ]
check "scope.txt exists" [ -f "$REPO_DIR/scope.txt" ]

# --- Summary ---
echo ""
echo "================================"
echo "  Results: $PASS passed, $FAIL failed"
echo "================================"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
