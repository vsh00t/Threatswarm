#!/usr/bin/env python3
"""
ThreatSwarm Build Script — Generates platform adapters from core/ content.

Usage:
    python3 scripts/build.py --all              # Generate all adapters + sync root
    python3 scripts/build.py --adapter claude-code  # Single adapter
    python3 scripts/build.py --adapter github-copilot
    python3 scripts/build.py --adapter opencode
    python3 scripts/build.py --adapter openclaw
    python3 scripts/build.py --sync-root        # Sync core/ to root .claude/ and threatswarm-plugin/
    python3 scripts/build.py --list             # List available adapters

Reads from core/agents/, core/rules/, core/commands/, core/hooks/ and generates
platform-specific output in adapters/<name>/.

--all always includes --sync-root to keep root directories in sync.
"""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = BASE_DIR / "core"
ADAPTERS_DIR = BASE_DIR / "adapters"
ROOT_CLAUDE_DIR = BASE_DIR / ".claude"
PLUGIN_DIR = BASE_DIR / "threatswarm-plugin"


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


def get_agent_tools(agent):
    """Map agent tags to Claude Code tools string."""
    tags = agent["tags"]
    if "reporting" in tags or "documentation" in tags:
        return "Read, Write, Glob"
    if "logging" in tags or "siem" in tags:
        return "Bash, Read, Write, Grep, Glob"
    has_glob = "recon" in tags or "osint" in tags or "enumeration" in tags
    has_grep = "research" in tags or "vulnerability" in tags or "logging" in tags
    tools = "Bash, Read, Write"
    if has_glob:
        tools += ", Glob"
    if has_grep:
        tools += ", Grep"
    return tools


def claude_frontmatter(name, description, tools, model):
    """Generate Claude Code agent frontmatter."""
    return f"""---
name: {name}
description: {description}
tools: {tools}
model: {model}
---"""


def claude_command_frontmatter(cmd_name):
    """Generate Claude Code command frontmatter."""
    return f"""---
description: {cmd_name} command
allowed-tools: Bash, Read, Write
---"""


def claude_rule_frontmatter(rule_name):
    """Generate Claude Code rule frontmatter with path scoping."""
    rule_path_map = {
        "evidence": "evidence/**",
        "exploits": "**/*.py\n  - \"**/*.rb\"\n  - \"**/*.c\"",
        "loot": "loot/**",
        "reports": "reports/**",
    }
    paths = rule_path_map.get(rule_name, "**/*")
    return f"""---
paths:
  - "{paths}"
---"""


def copy_tree(src: Path, dst: Path, pattern="*"):
    """Recursively copy files from src to dst (flat or recursive by extension)."""
    if not src.exists():
        return 0
    count = 0
    for f in src.rglob(pattern):
        if f.is_file():
            rel = f.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
            count += 1
    return count


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

        tools = get_agent_tools(agent)

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
        frontmatter = claude_command_frontmatter(cmd_name)
        claude_content = cmd_content.replace("<arguments>", "$ARGUMENTS")
        (cmds_dir / f"{cmd_name}.md").write_text(f"{frontmatter}\n\n{claude_content}", encoding="utf-8")

    # Rules
    rules_dir = out_dir / "rules"
    rules_dir.mkdir(exist_ok=True)
    rules = load_all_rules()
    for rule_name, rule_content in rules.items():
        frontmatter = claude_rule_frontmatter(rule_name)
        (rules_dir / f"{rule_name}.md").write_text(f"{frontmatter}\n\n{rule_content}", encoding="utf-8")

    # CLAUDE.md (generated version)
    claude_md = generate_claude_md(registry)
    (ADAPTERS_DIR / "claude-code" / "CLAUDE.md").write_text(claude_md, encoding="utf-8")

    # Copy settings.json
    src_settings = BASE_DIR / ".claude" / "settings.json"
    if src_settings.exists():
        dst = ADAPTERS_DIR / "claude-code" / ".claude" / "settings.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src_settings.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"    ✓ settings.json copied to claude-code adapter")

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
    """Generate OpenCode adapter — copies static files and writes opencode.json."""
    src_dir = Path(__file__).resolve().parent.parent / "adapters" / "opencode"
    out_dir = ADAPTERS_DIR / "opencode"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy static files: instructions.md, .opencode.json, .opencode.json.template, README.md, setup.sh
    static_files = ["instructions.md", ".opencode.json", ".opencode.json.template", "README.md", "setup.sh"]
    copied = []
    for fname in static_files:
        src = src_dir / fname
        dst = out_dir / fname
        if src.exists() and src.resolve() != dst.resolve():
            shutil.copy2(src, dst)
            copied.append(fname)

    # Write opencode.json adapter descriptor
    opencode_config = {
        "name": "threatswarm",
        "version": "2.0.0",
        "description": "ThreatSwarm v2.0 — Multi-Agent Pentesting Framework for OpenCode",
        "instructions_file": "adapters/opencode/instructions.md",
        "config_template": "adapters/opencode/.opencode.json.template"
    }
    (out_dir / "opencode.json").write_text(json.dumps(opencode_config, indent=2), encoding="utf-8")
    copied.append("opencode.json")

    print(f"  ✓ OpenCode adapter: {', '.join(copied)}")


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


# ─── Sync Root Directories ──────────────────────────────────────────────

def sync_root(registry):
    """Sync core/ content to root .claude/ and threatswarm-plugin/ directories.

    This keeps the root-level Claude Code installation paths in sync with core/.
    Handles: agents, hooks, commands, rules, skills, and settings.json permissions.
    """
    sync_targets = [
        (".claude", ROOT_CLAUDE_DIR),
        ("threatswarm-plugin", PLUGIN_DIR),
    ]

    total_agents = 0
    total_hooks = 0
    total_commands = 0
    total_rules = 0
    total_skills = 0

    for label, base in sync_targets:
        print(f"\n  Syncing → {label}/")

        # ── Agents ──────────────────────────────────────────────────────
        agents_dir = base / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for agent in registry["agents"]:
            name = agent["name"]
            content = load_agent_md(name)
            if not content:
                print(f"    [WARN] No core content for agent '{name}', skipping")
                continue
            tools = get_agent_tools(agent)
            frontmatter = claude_frontmatter(name, agent["description"], tools, agent["recommended_model"])
            full_content = f"{frontmatter}\n\n{content}"
            (agents_dir / f"{name}.md").write_text(full_content, encoding="utf-8")
            count += 1
        total_agents += count
        print(f"    ✓ {count} agents synced")

        # ── Hooks ───────────────────────────────────────────────────────
        hooks_dir = base / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        h_count = 0
        src_hooks = CORE_DIR / "hooks"
        if src_hooks.exists():
            for hf in src_hooks.glob("*.py"):
                (hooks_dir / hf.name).write_text(hf.read_text(encoding="utf-8"), encoding="utf-8")
                h_count += 1
        # Preserve cmd_log.sh (Claude-specific wiring)
        if label == ".claude" and (ROOT_CLAUDE_DIR / "hooks" / "cmd_log.sh").exists():
            # Already copied above if exists — it's the source of truth for .claude
            pass
        # Preserve hooks.json (Claude plugin wiring) in threatswarm-plugin
        if label == "threatswarm-plugin" and (PLUGIN_DIR / "hooks" / "hooks.json").exists():
            pass  # Don't overwrite hooks.json — it has ${CLAUDE_PLUGIN_ROOT} paths
        total_hooks += h_count
        print(f"    ✓ {h_count} hook scripts synced")

        # ── Commands ────────────────────────────────────────────────────
        cmds_dir = base / "commands"
        cmds_dir.mkdir(parents=True, exist_ok=True)
        commands = load_all_commands()
        c_count = 0
        for cmd_name, cmd_content in commands.items():
            frontmatter = claude_command_frontmatter(cmd_name)
            claude_content = cmd_content.replace("<arguments>", "$ARGUMENTS")
            (cmds_dir / f"{cmd_name}.md").write_text(f"{frontmatter}\n\n{claude_content}", encoding="utf-8")
            c_count += 1
        total_commands += c_count
        print(f"    ✓ {c_count} commands synced")

        # ── Rules ───────────────────────────────────────────────────────
        rules_dir = base / "rules"
        if rules_dir.exists() or label == ".claude":
            rules_dir.mkdir(parents=True, exist_ok=True)
            rules = load_all_rules()
            r_count = 0
            for rule_name, rule_content in rules.items():
                frontmatter = claude_rule_frontmatter(rule_name)
                (rules_dir / f"{rule_name}.md").write_text(f"{frontmatter}\n\n{rule_content}", encoding="utf-8")
                r_count += 1
            total_rules += r_count
            print(f"    ✓ {r_count} rules synced")

        # ── Skills ──────────────────────────────────────────────────────
        skills_src = CORE_DIR / "skills"
        skills_dst = base / "skills"
        if skills_src.exists():
            s_count = copy_tree(skills_src, skills_dst, "*")
            total_skills += s_count
            print(f"    ✓ {s_count} skill files synced")

    # ── Update settings.json with new agent tool permissions ──────────
    update_settings_permissions(registry)

    print(f"\n  Sync summary: {total_agents} agents, {total_hooks} hooks, "
          f"{total_commands} commands, {total_rules} rules, {total_skills} skill files")


def update_settings_permissions(registry):
    """Add Bash permissions for tools used by new/updated agents."""
    settings_path = ROOT_CLAUDE_DIR / "settings.json"
    if not settings_path.exists():
        print(f"  [WARN] settings.json not found at {settings_path}")
        return

    with open(settings_path) as f:
        settings = json.load(f)

    existing_perms = set(settings.get("permissions", {}).get("allow", []))

    # New tools that the 5 new agents might need — check against existing
    new_perms = [
        # cloud-postex: cloud CLI tools (likely already covered)
        "Bash(pacu *)",
        "Bash(cloudquery *)",
        # purple-team: atomic red team
        "Bash(atomic-red-team *)",
        "Bash(invoker *)",
        # red-infra: infrastructure tools
        "Bash(sliver *)",
        # segmentation-tester: network validation
        "Bash(nping *)",
        "Bash(nmap --script *)",
        # vuln-management: scanning tools
        "Bash(nessuscli *)",
        "Bash(tenable *)",
    ]

    added = []
    for perm in new_perms:
        if perm not in existing_perms:
            existing_perms.add(perm)
            added.append(perm)

    if added:
        settings["permissions"]["allow"] = sorted(existing_perms)
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)
            f.write("\n")
        print(f"  ✓ settings.json: added {len(added)} new Bash permissions")
        for p in added:
            print(f"      + {p}")
    else:
        print(f"  ✓ settings.json: permissions already up to date")


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
    group.add_argument("--all", action="store_true", help="Generate all adapters (includes --sync-root)")
    group.add_argument("--adapter", choices=ADAPTERS.keys(), help="Generate a specific adapter")
    group.add_argument("--sync-root", action="store_true", help="Sync core/ to root .claude/ and threatswarm-plugin/")
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
        # --all always syncs root
        print(f"\nSyncing root directories...")
        sync_root(registry)
    elif args.sync_root:
        sync_root(registry)
    else:
        ADAPTERS[args.adapter](registry)

    print(f"\n✓ Build complete.")


if __name__ == "__main__":
    main()
