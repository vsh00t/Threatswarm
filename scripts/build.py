#!/usr/bin/env python3
"""
ThreatSwarm Build Script — Generates platform adapters from core/ content.

Usage:
    python3 scripts/build.py --all              # Generate all adapters
    python3 scripts/build.py --adapter claude-code  # Single adapter
    python3 scripts/build.py --adapter github-copilot
    python3 scripts/build.py --adapter opencode
    python3 scripts/build.py --adapter openclaw
    python3 scripts/build.py --list             # List available adapters

Reads from core/agents/, core/rules/, core/commands/, core/hooks/ and generates
platform-specific output in adapters/<name>/.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = BASE_DIR / "core"
ADAPTERS_DIR = BASE_DIR / "adapters"


def load_registry():
    """Load the agent registry from core/agents/_registry.json."""
    reg_path = CORE_DIR / "agents" / "_registry.json"
    if not reg_path.exists():
        print(f"[ERROR] Agent registry not found: {reg_path}", file=sys.stderr)
        sys.exit(1)
    with open(reg_path) as f:
        return json.load(f)


def load_agent_md(name):
    """Load the markdown content of an agent file."""
    path = CORE_DIR / "agents" / f"{name}.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def load_all_rules():
    """Load all rule markdown files."""
    rules = {}
    rules_dir = CORE_DIR / "rules"
    if not rules_dir.exists():
        return rules
    for f in sorted(rules_dir.glob("*.md")):
        rules[f.stem] = f.read_text(encoding="utf-8")
    return rules


def load_all_commands():
    """Load all command markdown files."""
    commands = {}
    cmds_dir = CORE_DIR / "commands"
    if not cmds_dir.exists():
        return commands
    for f in sorted(cmds_dir.glob("*.md")):
        commands[f.stem] = f.read_text(encoding="utf-8")
    return commands


def claude_frontmatter(name, description, tools, model):
    """Generate Claude Code agent frontmatter."""
    return f"""---
name: {name}
description: {description}
tools: {tools}
model: {model}
---"""


# ─── Claude Code Adapter ─────────────────────────────────────────────────

def build_claude_code(registry):
    """Generate Claude Code adapter with frontmatter-wrapped agents."""
    out_dir = ADAPTERS_DIR / "claude-code" / ".claude"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Agents
    agents_dir = out_dir / "agents"
    agents_dir.mkdir(exist_ok=True)
    for agent in registry["agents"]:
        name = agent["name"]
        content = load_agent_md(name)
        if not content:
            continue

        # Map tags to Claude tools
        tools = "Bash, Read, Write"
        if "reporting" in agent["tags"] or "documentation" in agent["tags"]:
            tools = "Read, Write, Glob"
        elif "logging" in agent["tags"] or "siem" in agent["tags"]:
            tools = "Bash, Read, Write, Grep, Glob"
        else:
            has_glob = "recon" in agent["tags"] or "osint" in agent["tags"] or "enumeration" in agent["tags"]
            has_grep = "research" in agent["tags"] or "vulnerability" in agent["tags"] or "logging" in agent["tags"]
            tools = "Bash, Read, Write"
            if has_glob:
                tools += ", Glob"
            if has_grep:
                tools += ", Grep"

        frontmatter = claude_frontmatter(name, agent["description"], tools, agent["recommended_model"])
        full_content = f"{frontmatter}\n\n{content}"

        (agents_dir / f"{name}.md").write_text(full_content, encoding="utf-8")

    # Hooks
    hooks_dir = out_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    src_hooks = CORE_DIR / "hooks"
    for hf in src_hooks.glob("*.py"):
        (hooks_dir / hf.name).write_text(hf.read_text(encoding="utf-8"), encoding="utf-8")

    # Copy cmd_log.sh if it exists in original
    orig_hooks = BASE_DIR / ".claude" / "hooks"
    if orig_hooks.exists():
        for hf in orig_hooks.glob("*.sh"):
            (hooks_dir / hf.name).write_text(hf.read_text(encoding="utf-8"), encoding="utf-8")

    # Commands
    cmds_dir = out_dir / "commands"
    cmds_dir.mkdir(exist_ok=True)
    commands = load_all_commands()
    for cmd_name, cmd_content in commands.items():
        # Add frontmatter with $ARGUMENTS back
        frontmatter = f"---\ndescription: {cmd_name} command\nallowed-tools: Bash, Read, Write\n---"
        # Replace <arguments> back to $ARGUMENTS for Claude Code
        claude_content = cmd_content.replace("<arguments>", "$ARGUMENTS")
        (cmds_dir / f"{cmd_name}.md").write_text(f"{frontmatter}\n\n{claude_content}", encoding="utf-8")

    # Rules
    rules_dir = out_dir / "rules"
    rules_dir.mkdir(exist_ok=True)
    rules = load_all_rules()
    rule_path_map = {"evidence": "evidence/**", "exploits": "**/*.py\n  - \"**/*.rb\"\n  - \"**/*.c\"", "loot": "loot/**", "reports": "reports/**"}
    for rule_name, rule_content in rules.items():
        paths = rule_path_map.get(rule_name, "**/*")
        frontmatter = f"---\npaths:\n  - \"{paths}\"\n---"
        (rules_dir / f"{rule_name}.md").write_text(f"{frontmatter}\n\n{rule_content}", encoding="utf-8")

    # CLAUDE.md (generated version)
    claude_md = generate_claude_md(registry)
    (ADAPTERS_DIR / "claude-code" / "CLAUDE.md").write_text(claude_md, encoding="utf-8")

    print(f"  ✓ Claude Code adapter: {len(registry['agents'])} agents, {len(commands)} commands, {len(rules)} rules")


def generate_claude_md(registry):
    """Generate CLAUDE.md for Claude Code adapter."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    agent_table_rows = []
    for a in registry["agents"]:
        agent_table_rows.append(f"| {' / '.join(a['tags'][:2])} | `{a['name']}` | {a['description'][:80]}{'...' if len(a['description'])>80 else ''} |")

    return f"""# Cybersecurity Workspace — Master Context (Generated {timestamp})

## Scope Enforcement (MANDATORY — ZERO EXCEPTIONS)
**ALL targets MUST be listed in `scope.txt` before any network tool runs.**
The `scope_check.py` hook enforces this automatically on every Bash command.
Add targets: IP, CIDR, or domain — one per line, comments start with `#`.

## Agent Delegation Table
| Category | Agent | Description |
|----------|-------|-------------|
{chr(10).join(agent_table_rows)}

**NEVER run active recon or exploitation in the main conversation thread.**
**ALWAYS delegate to the appropriate agent.**

## OPSEC Defaults
- External traffic: route through `proxychains` where possible
- Nmap timing: `-T3` maximum unless explicitly authorized for `-T4`
- No real PII exfiltration — reference paths only in evidence/
- Minimize footprint: staged payloads for initial access only

## Evidence Output Pattern
```
evidence/$(date +%Y%m%d)/$TARGET/{{nmap,nuclei,web,creds,screenshots}}/
```

## Environment Variables
| Variable | Purpose | Default |
|----------|---------|---------|
| `LHOST` | Attacker IP for callbacks | `10.10.14.1` |
| `LPORT` | Listener port | `4444` |
| `SCOPE_FILE` | Path to scope file | `./scope.txt` |
| `EVIDENCE_DIR` | Evidence base directory | `./evidence` |

## Anti-Patterns (Claude MUST NEVER Do These)
1. Run any network tool without target being in scope.txt
2. Store plaintext passwords — hashes + location references only
3. Exfiltrate real PII from target systems
4. Run -T5 nmap or DoS-class attacks without explicit written authorization
5. Execute exploits in the main conversation thread (always delegate)
6. Write credentials in cleartext — use [REDACTED]
7. Push engagement data to public repos
8. Run rm -rf on evidence directories

---
*Auto-generated by ThreatSwarm build.py from core/ content*
"""


# ─── GitHub Copilot Adapter ──────────────────────────────────────────────

def build_github_copilot(registry):
    """Generate GitHub Copilot copilot-instructions.md."""
    out_dir = ADAPTERS_DIR / "github-copilot" / ".github"
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rules = load_all_rules()
    commands = load_all_commands()

    agent_summaries = []
    for a in registry["agents"]:
        triggers = ", ".join(a["triggers"][:10]) if a["triggers"] else "N/A"
        agent_summaries.append(f"""### {a['name']}
**Role:** {a['description']}
**Triggers:** {triggers}
**Tags:** {', '.join(a['tags'])}
**Model tier:** {a['recommended_model']}""")

    rule_sections = []
    for name, content in rules.items():
        rule_sections.append(f"## {name.replace('-', ' ').title()}\n\n{content}")

    command_sections = []
    for name, content in commands.items():
        command_sections.append(f"## /{name}\n\n{content}")

    instructions = f"""# ThreatSwarm — AI Penetration Testing Assistant

> Generated {timestamp} from core/ content. This file provides comprehensive pentesting context for GitHub Copilot.

## ⚠️ CRITICAL: Scope Enforcement

**Before running ANY network command, verify the target is in `scope.txt`.**
GitHub Copilot does not have hook support, so you MUST manually verify scope.

1. Read `scope.txt`
2. Confirm the target IP/domain/CIDR is listed
3. If not found, STOP and report: "TARGET [X] is not in scope.txt"

## Agent Catalog

You have access to specialist agents for different attack categories. Match the task to the appropriate agent:

{chr(10).join(agent_summaries)}

## Available Commands

{chr(10).join(command_sections)}

## Rules

{chr(10).join(rule_sections)}

## OPSEC Defaults
- Route external traffic through `proxychains` where possible
- Nmap timing: `-T3` maximum unless explicitly authorized
- No PII exfiltration — reference paths only
- Minimize footprint: staged payloads only

## Evidence Structure
```
evidence/YYYYMMDD/TARGET/{{nmap,nuclei,web,creds,screenshots}}/
```

## Anti-Patterns — NEVER Do These
1. Run network tools without verifying scope.txt first
2. Store plaintext passwords
3. Exfiltrate real PII
4. Run -T5 nmap or DoS attacks without explicit authorization
5. Write credentials in cleartext
6. Push engagement data to public repos

## Environment Variables
- `LHOST`: Attacker IP (default: 10.10.14.1)
- `LPORT`: Listener port (default: 4444)
- `SCOPE_FILE`: Path to scope file (default: ./scope.txt)
- `EVIDENCE_DIR`: Evidence directory (default: ./evidence)

---
*Auto-generated by ThreatSwarm build.py*
"""

    (out_dir / "copilot-instructions.md").write_text(instructions, encoding="utf-8")
    print(f"  ✓ GitHub Copilot adapter: copilot-instructions.md")


# ─── OpenCode Adapter ────────────────────────────────────────────────────

def build_opencode(registry):
    """Generate OpenCode adapter with instructions.md."""
    out_dir = ADAPTERS_DIR / "opencode"
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rules = load_all_rules()
    commands = load_all_commands()

    agent_entries = []
    for a in registry["agents"]:
        triggers = ", ".join(a["triggers"][:8]) if a["triggers"] else ""
        agent_entries.append(f"- **{a['name']}**: {a['description']} | Triggers: {triggers}")

    instructions = f"""# ThreatSwarm — OpenCode Penetration Testing Framework

> Generated {timestamp}

## Scope Enforcement
**MANDATORY**: Verify all targets in `scope.txt` before any network command. OpenCode has no hook system — manual verification is required.

## Agents
{chr(10).join(agent_entries)}

## Commands
{chr(10).join(f'- `/{name}`: {content.split(chr(10))[0].strip()}' for name, content in commands.items())}

## Rules
{chr(10).join(f'### {name.replace("-"," ").title()}\\n{content[:300]}...' if len(content)>300 else f'### {name.replace("-"," ").title()}\\n{content}' for name, content in rules.items())}

## OPSEC
- proxychains for external traffic
- nmap -T3 max
- No PII exfiltration
- Hashes only, no plaintext passwords
- Evidence: evidence/YYYYMMDD/TARGET/

## Anti-Patterns
1. No unscoped network commands
2. No plaintext credentials
3. No DoS without authorization
4. No public repo pushes of engagement data

---
*Auto-generated by ThreatSwarm build.py*
"""

    (out_dir / "instructions.md").write_text(instructions, encoding="utf-8")

    # Also generate opencode.json config
    opencode_config = {
        "name": "threatswarm",
        "version": "1.0.0",
        "agents_dir": "core/agents",
        "rules_dir": "core/rules",
        "commands_dir": "core/commands"
    }
    (out_dir / "opencode.json").write_text(json.dumps(opencode_config, indent=2), encoding="utf-8")

    print(f"  ✓ OpenCode adapter: instructions.md, opencode.json")


# ─── OpenClaw Adapter ────────────────────────────────────────────────────

def build_openclaw(registry):
    """Generate OpenClaw adapter with SKILL.md files."""
    out_dir = ADAPTERS_DIR / "openclaw"
    skills_dir = out_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    rules = load_all_rules()
    commands = load_all_commands()

    # Consolidated skill: threatswarm-core
    agent_list = "\n".join(f"- **{a['name']}** ({', '.join(a['tags'][:2])}): {a['description'][:100]}" for a in registry["agents"])

    rule_blocks = []
    for name, content in rules.items():
        rule_blocks.append(f"### {name.replace('-', ' ').title()}\n{content}")

    skill_md = f"""# ThreatSwarm Pentesting Framework

Comprehensive multi-agent penetration testing framework with {len(registry['agents'])} specialist agents.

## Description
Platform-agnostic pentesting framework for AI coding agents. Use when working on penetration testing, vulnerability assessment, red team operations, or security auditing tasks.

## Agents
{agent_list}

## Scope Enforcement
**CRITICAL**: Before ANY network command, verify target is in scope.txt.
Use the scope_check.py hook: `python3 core/hooks/scope_check.py --check "<command>"`
Exit code 0 = pass, 2 = scope violation.

## Commands
{chr(10).join(f'- `/{name}`: {content.split(chr(10))[0].strip()}' for name, content in commands.items())}

## Rules
{chr(10).join(rule_blocks)}

## OPSEC Defaults
- proxychains for external traffic
- nmap -T3 max timing
- No PII exfiltration — evidence paths only
- Hashes + references only, no plaintext credentials
- Evidence structure: evidence/YYYYMMDD/TARGET/

## Environment
- `LHOST`: Attacker callback IP (default 10.10.14.1)
- `LPORT`: Listener port (default 4444)
- `SCOPE_FILE`: scope file path (default ./scope.txt)
- `EVIDENCE_DIR`: evidence directory (default ./evidence)
"""

    (skills_dir / "threatswarm-core.md").write_text(skill_md, encoding="utf-8")

    # Individual agent skills for targeted loading
    for agent in registry["agents"]:
        content = load_agent_md(agent["name"])
        if not content:
            continue

        agent_skill = f"""# {agent['display_name']}

{agent['description']}

## Tags
{', '.join(agent['tags'])}

## Triggers
{', '.join(agent['triggers']) if agent['triggers'] else 'N/A'}

## Recommended Model
{agent['recommended_model']}

---
{content}
"""
        (skills_dir / f"threatswarm-{agent['name']}.md").write_text(agent_skill, encoding="utf-8")

    print(f"  ✓ OpenClaw adapter: 1 consolidated skill + {len(registry['agents'])} agent skills")


# ─── Main ────────────────────────────────────────────────────────────────

ADAPTERS = {
    "claude-code": build_claude_code,
    "github-copilot": build_github_copilot,
    "opencode": build_opencode,
    "openclaw": build_openclaw,
}


def main():
    parser = argparse.ArgumentParser(
        description="ThreatSwarm Build Script — generate platform adapters from core/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Generate all adapters")
    group.add_argument("--adapter", choices=ADAPTERS.keys(), help="Generate a specific adapter")
    group.add_argument("--list", action="store_true", help="List available adapters")
    args = parser.parse_args()

    if args.list:
        print("Available adapters:")
        for name in ADAPTERS:
            print(f"  • {name}")
        return

    registry = load_registry()
    print(f"ThreatSwarm Build — {registry['total']} agents loaded from core/agents/")

    if args.all:
        for name, builder in ADAPTERS.items():
            print(f"\nBuilding {name}...")
            builder(registry)
    else:
        ADAPTERS[args.adapter](registry)

    print(f"\n✓ Build complete.")


if __name__ == "__main__":
    main()
