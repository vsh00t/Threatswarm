# ThreatSwarm — OpenCode Adapter

ThreatSwarm v2.0 adapter for [OpenCode](https://github.com/opencode-ai/opencode) (or [Crush](https://github.com/charmbracelet/crush), the continuation).

## Quick Start

```bash
cd adapters/opencode
bash setup.sh
cd ../..
opencode
```

The setup script:
1. Checks OpenCode and Python 3 are installed
2. Verifies MCP server syntax
3. Copies `.opencode.json` and `instructions.md` to project root (if not present)

## Manual Setup

If you prefer to configure manually:

```bash
# Copy config to project root
cp adapters/opencode/.opencode.json .opencode.json
cp adapters/opencode/instructions.md instructions.md

# Verify JSON is valid
python3 -c "import json; json.load(open('.opencode.json'))"
```

## Configuration

### `.opencode.json`

The config file configures:

- **Providers**: Anthropic and OpenAI (add API keys via environment variables: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`)
- **Agents**: Coder and task agents using Claude Sonnet with 8000 max tokens
- **Shell**: `/bin/bash -l` for full environment
- **MCP Servers**: Three ThreatSwarm MCP servers for scope, evidence, and report management
- **autoCompact**: Enabled to keep context lean

### Agent Models

Default model is `claude-sonnet-4-20250514`. Edit `.opencode.json` to change:
- `agents.coder.model` — for coding tasks
- `agents.task.model` — for general tasks

### MCP Servers

| Server | Purpose | Path |
|--------|---------|------|
| threatswarm-scope | Target validation, scope checks | `integrations/mcp/scope-mcp/server.py` |
| threatswarm-evidence | Evidence logging, finding management | `integrations/mcp/evidence-mcp/server.py` |
| threatswarm-report | Report generation, CVSS scoring | `integrations/mcp/report-mcp/server.py` |

These are standard MCP servers using stdio transport. OpenCode launches them automatically.

## Instructions

The `instructions.md` file (loaded by OpenCode as `INSTRUCTIONS.md` in project root) contains:

- Core identity and scope enforcement rules
- 6 slash commands (`/engage`, `/attack`, `/hunt`, `/ir`, `/pwned`, `/report`)
- Agent roster (32 agents grouped by category — names only, not full descriptions)
- MCP tool descriptions
- Evidence handling, OPSEC, and anti-pattern rules

**Context efficiency**: Agent details are NOT in the instructions file. Instead, agent names are listed and OpenCode can read full details from `core/agents/<name>.md` using glob/grep tools when needed. This keeps the base prompt lean (~3KB vs ~8KB).

## Scope File

Create `scope.txt` in the project root with your authorized targets:

```
# Production Assessment — ACME Corp
192.168.1.0/24
10.0.0.0/16
*.example.com

# Exclusions
# 192.168.1.50  — critical system, no active testing
```

## Directory Structure

```
project/
├── .opencode.json          # OpenCode config (copied from adapter)
├── instructions.md         # ThreatSwarm instructions (copied from adapter)
├── scope.txt               # Your authorized targets
├── evidence/               # Auto-created engagement evidence
├── reports/                # Generated reports
├── core/
│   ├── agents/             # 32 agent definition files
│   ├── commands/           # Slash command definitions
│   ├── rules/              # Evidence, exploits, loot rules
│   └── hooks/              # Scope check hook (Claude Code only)
└── integrations/
    └── mcp/                # MCP servers (scope, evidence, report)
```

## Rebuilding

After changes to `core/`, regenerate all adapters:

```bash
python3 scripts/build.py --adapter opencode
```

This copies the static files (`instructions.md`, `.opencode.json.template`, `setup.sh`) and writes the `opencode.json` adapter descriptor.

## Notes

- OpenCode loads `INSTRUCTIONS.md` (or `instructions.md`) from the project root into every session context. Keep it concise.
- Unlike Claude Code, OpenCode has no hook system — scope checks are manual.
- The `.opencode.json` is the actual config; `.opencode.json.template` is a reference copy without provider keys.
- If using Crush (the OpenCode continuation), the config format is the same.
