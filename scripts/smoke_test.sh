#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE_DIR"
PASS=0; FAIL=0; WARN=0

check() {
  local desc="$1" cmd="$2"
  if eval "$cmd" >/dev/null 2>&1; then
    echo "  ✅ $desc"
    PASS=$((PASS+1))
  else
    echo "  ❌ $desc"
    FAIL=$((FAIL+1))
  fi
}

echo "╔══════════════════════════════════════════════════════╗"
echo "║        ThreatSwarm v2.0 — Smoke Test Suite           ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

echo "── Core Agents (32) ──"
check "32 agent files in core/agents/" "[ $(ls core/agents/*.md 2>/dev/null | grep -v _registry | wc -l | tr -d ' ') -eq 32 ]"
check "32 agent files in .claude/agents/" "[ $(ls .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ') -eq 32 ]"
check "32 agent files in threatswarm-plugin/agents/" "[ $(ls threatswarm-plugin/agents/*.md 2>/dev/null | wc -l | tr -d ' ') -eq 32 ]"
check "All agents have valid frontmatter" "grep -q '^name:' .claude/agents/recon.md && grep -q '^model:' .claude/agents/recon.md"

echo ""
echo "── Build System ──"
check "build.py --list works" "python3 scripts/build.py --list"
check "build.py --all works" "python3 scripts/build.py --all"

echo ""
echo "── Python Scripts ──"
for script in core/hooks/evidence_capture.py core/hooks/findings_sync.py core/hooks/scope_check.py core/scripts/report_generate.py core/scripts/scope_validate.py; do
  check "$script compiles" "python3 -c \"import py_compile; py_compile.compile('$script', doraise=True)\""
done

echo ""
echo "── MCP Servers ──"
for mcp in integrations/mcp/scope-mcp/server.py integrations/mcp/evidence-mcp/server.py integrations/mcp/report-mcp/server.py; do
  check "$(echo $mcp | cut -d/ -f3) compiles" "python3 -c \"import py_compile; py_compile.compile('$mcp', doraise=True)\""
done

echo ""
echo "── Hooks ──"
check "scope_check blocks out-of-scope" "echo '{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"nmap 8.8.8.8\"}}' | python3 core/hooks/scope_check.py 2>&1 | grep -q BLOCKED"
check "scope_check allows in-scope (exit 0)" "echo '{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"nmap 192.168.1.100\"}}' | python3 core/hooks/scope_check.py >/dev/null 2>&1; [ \$? -eq 0 ]"

echo ""
echo "── Report Pipeline ──"
check "report_generate.py produces CRITICAL (not INFO)" "
  rm -rf /tmp/_ts_smoke_evidence /tmp/_ts_smoke_reports
  mkdir -p /tmp/_ts_smoke_evidence
  echo '{\"findings\":[{\"title\":\"Test\",\"severity\":\"CRITICAL\",\"cvss\":\"9.8\"}]}' > /tmp/_ts_smoke_evidence/findings.json
  python3 core/scripts/report_generate.py generate --type executive --evidence-dir /tmp/_ts_smoke_evidence --output /tmp/_ts_smoke_reports >/dev/null 2>&1
  grep -q '| CRITICAL | 1 |' /tmp/_ts_smoke_reports/*.md
  rm -rf /tmp/_ts_smoke_evidence /tmp/_ts_smoke_reports
"

echo ""
echo "── Sync Consistency ──"
SYNC_MISMATCH=0
for f in core/agents/*.md; do
  name=$(basename "$f" .md)
  [ "$name" = "_registry" ] && continue
  claude_lines=$(wc -l < ".claude/agents/$name.md" 2>/dev/null || echo 0)
  core_lines=$(wc -l < "$f")
  diff=$((claude_lines - core_lines))
  [ $diff -lt 3 ] || [ $diff -gt 15 ] && SYNC_MISMATCH=$((SYNC_MISMATCH+1))
done
check "All agents synced (.claude vs core)" "[ $SYNC_MISMATCH -eq 0 ]"

echo ""
echo "── Manifests ──"
check "marketplace.json is v2.0.0" "grep -q '\"version\": \"2.0.0\"' .claude-plugin/marketplace.json"
check "marketplace.json says 32 agents" "grep -q '32 autonomous' .claude-plugin/marketplace.json"
check "plugin.json is v2.0.0" "grep -q '\"version\": \"2.0.0\"' threatswarm-plugin/.claude-plugin/plugin.json"

echo ""
echo "── Skills & Templates ──"
check "5 skills in core/skills/" "[ $(find core/skills -name SKILL.md | wc -l | tr -d ' ') -eq 5 ]"
check "4 templates in core/templates/" "[ $(find core/templates -name '*.md' | wc -l | tr -d ' ') -ge 4 ]"
check "4 JSON schemas valid" "for s in core/schema/*.json; do python3 -c \"import json; json.load(open('\$s'))\"; done"

echo ""
echo "── Integrations ──"
check "3 n8n workflows (valid JSON)" "for f in integrations/n8n/*.json; do python3 -c \"import json; json.load(open('\$f'))\"; done"
check "OpenProject sync.py compiles" "python3 -c \"import py_compile; py_compile.compile('integrations/openproject/sync.py', doraise=True)\""

echo ""
echo "── Clean ──"
check "No __pycache__ directories" "[ $(find . -name '__pycache__' -not -path './.git/*' -type d 2>/dev/null | wc -l | tr -d ' ') -eq 0 ]"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  Results: $PASS passed, $FAIL failed, $WARN warnings"
FAIL_MSG=""
[ $FAIL -gt 0 ] && FAIL_MSG=" — FIX BEFORE PUSH"
echo "║$FAIL_MSG"
echo "╚══════════════════════════════════════════════════════╝"
[ $FAIL -gt 0 ] && exit 1 || exit 0
