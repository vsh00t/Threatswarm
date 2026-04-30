# ThreatSwarm v2.0 — Multi-Agent Pentesting Framework

> 32 specialized agents for offensive security, defense, and reconnaissance — running on Claude Code, GitHub Copilot, OpenCode, or OpenClaw.

Fork of [mukul975/ThreatSwarm](https://github.com/mukul975/ThreatSwarm) with multi-platform support, 5 new agents, report pipeline, MCP integrations, and n8n workflow automation.

---

## What It Does

ThreatSwarm gives AI coding agents pentesting knowledge. Each agent is a system prompt that knows specific tools, techniques, and tradecraft. The framework handles scope enforcement, evidence capture, report generation, and cross-platform deployment.

**Core principle:** The agent suggests commands and explains trade-offs. You decide what to run. Nothing executes without you.

## Agents

| # | Agent | Category | Focus |
|---|-------|----------|-------|
| 1 | Active Directory | Offensive | BloodHound, Kerberoasting, DCSync, AD-CS ESC1-8, GPO abuse |
| 2 | API Attacker | Offensive | REST/GraphQL, IDOR, BOLA/BFLA, mass assignment |
| 3 | Blue Team | Defensive | Sigma rules, CIS hardening, SIEM, EDR tuning |
| 4 | C2 Operator | Offensive | Sliver, Havoc, Cobalt Strike profiles, redirectors |
| 5 | Cloud Attacker | Offensive | AWS/Azure/GCP, Pacu, S3, IAM escalation |
| 6 | Cloud Post-Exploitation | Offensive | IAM persistence, cloud exfiltration, cross-account abuse |
| 7 | Compliance Scanner | Defensive | CIS, PCI-DSS, NIST CSF, SOC 2, Prowler, ScoutSuite |
| 8 | Container Attacker | Offensive | Docker escape, K8s RBAC, Trivy, pod escalation |
| 9 | Crypto Attacker | Offensive | TLS analysis, JWT confusion, padding oracle, custom crypto |
| 10 | DFIR Analyst | Defensive | Volatility3, disk forensics, timeline analysis |
| 11 | Evasion Specialist | Offensive | AMSI bypass, process injection, LOLBins, obfuscation |
| 12 | Exploitation Specialist | Offensive | Metasploit, RCE, SQLi, buffer overflows, exploit chains |
| 13 | IoT/OT Attacker | Offensive | Firmware analysis, UART/JTAG, SCADA, MQTT, QEMU |
| 14 | Log Analyst | Defensive | Splunk, audit logs, anomaly detection, SIEM queries |
| 15 | Malware Analyst | Defensive | ELF/PE analysis, YARA, sandbox, VirusTotal |
| 16 | Mobile Attacker | Offensive | Android/iOS, Frida, SSL pinning bypass, MobSF |
| 17 | Network Operator | Offensive | ARP spoofing, SMB relay, VLAN hopping, LLMNR poisoning |
| 18 | OSINT Collector | Recon | SpiderFoot, DNS enumeration, subdomain discovery, footprinting |
| 19 | Password Attacker | Offensive | Hashcat, credential stuffing, password spraying, NTLM relay |
| 20 | Post-Exploitation | Offensive | Privilege escalation, lateral movement, golden tickets, persistence |
| 21 | Purple Team | Collaborative | MITRE ATT&CK mapping, detection gaps, atomic red team |
| 22 | Recon Specialist | Recon | Nmap, Subfinder, Amass, service enumeration, scope validation |
| 23 | Red Team Infrastructure | Offensive | C2 deployment, redirector chains, phishing infrastructure |
| 24 | Report Writer | Reporting | Executive summaries, CVSS scoring, remediation guidance |
| 25 | Reverse Engineer | Offensive | Ghidra, dnSpy, shellcode, decompilation |
| 26 | Segmentation Tester | Offensive | Cross-segment access, firewall rules, VLAN hopping |
| 27 | Social Engineer | Offensive | GoPhish, spear phishing, pretexting, vishing |
| 28 | Threat Hunter | Defensive | Hypothesis-driven hunts, beacon detection, threat intel |
| 29 | Vulnerability Manager | Defensive | Nuclei, Nessus, CVSS prioritization, remediation tracking |
| 30 | Vulnerability Researcher | Offensive | CVE analysis, PoC development, patch diffing, zero-day research |
| 31 | Web Attacker | Offensive | SQLMap, XSS, SSRF, OWASP Top 10, Burp Suite |
| 32 | Wireless Attacker | Offensive | WPA/WPA3, PMKID, evil twin, BLE, Bluetooth |

**Breakdown:** 21 offensive · 7 defensive · 2 recon · 1 collaborative · 1 reporting

## Multi-Platform Support

ThreatSwarm works with any AI coding agent through platform adapters:

| Platform | Adapter | Format |
|----------|---------|--------|
| **Claude Code** | `adapters/claude-code/` | CLAUDE.md (project instructions) |
| **GitHub Copilot** | `adapters/github-copilot/` | Workspace rules (agent instructions) |
| **OpenCode** | `adapters/opencode/` | instructions.md + opencode.json |
| **OpenClaw** | `adapters/openclaw/` | Skill library (SKILL.md per agent) |

### Build System

```bash
python3 scripts/build.py --all                # Generate all adapters
python3 scripts/build.py --adapter claude-code # Single adapter
python3 scripts/build.py --list               # List available adapters
```

The build script reads `core/agents/` and generates platform-specific output. Edit agent definitions in `core/agents/`, rebuild, deploy.

## MCP Servers

Three MCP servers provide tool access for compatible agents:

| Server | Tools | Purpose |
|--------|-------|---------|
| **scope-mcp** | `validate_target`, `check_scope`, `add_scope`, `list_scope`, `import_scope` | Scope validation before any test |
| **evidence-mcp** | `capture_evidence`, `get_evidence`, `list_evidence`, `export_evidence` | Evidence capture and chain of custody |
| **report-mcp** | `create_report`, `add_finding`, `generate_report`, `get_template` | Report generation from findings |

### Running MCP Servers

```bash
# Via stdio (uvx)
uvx --from integrations/mcp/scope-mcp scope-mcp
uvx --from integrations/mcp/evidence-mcp evidence-mcp
uvx --from integrations/mcp/report-mcp report-mcp

# Or directly with Python
python3 integrations/mcp/scope-mcp/server.py
python3 integrations/mcp/evidence-mcp/server.py
python3 integrations/mcp/report-mcp/server.py
```

## Report Pipeline

Automated report generation from engagement findings:

```bash
# Generate a full engagement report
python3 core/scripts/report_generate.py \
  --engagement client-name \
  --template technical \
  --output reports/client-name-technical.md
```

**Templates:**
- `executive_summary` — C-suite overview, risk posture, key metrics
- `technical_finding` — Detailed vulnerability writeups with CVSS
- `remediation_roadmap` — Prioritized fix plan with effort estimates
- `client` — Full client-deliverable combining all sections

## Integrations

### n8n Workflows

Pre-built workflow templates in `integrations/n8n/`:

| Workflow | Trigger | Action |
|----------|---------|--------|
| `engagement-start.json` | Manual | Initialize scope, create project structure |
| `finding-sync.json` | Webhook | Sync findings to external trackers |
| `report-notification.json` | Schedule | Alert when reports need review |

### OpenProject

```bash
python3 integrations/openproject/sync.py --engagement client-name
```

Imports engagement template with phases, milestones, and finding tracking.

## Core Architecture

```
ThreatSwarm/
├── core/                        # Agent definitions and shared logic
│   ├── agents/                  # 32 agent markdown files + registry
│   ├── scripts/                 # Python utilities (report, scope, evidence)
│   ├── hooks/                   # Evidence capture, scope checks, sync
│   ├── templates/               # Report templates (exec, technical, remediation)
│   └── skills/                  # Reference libraries (MITRE ATT&CK, exploit-db, wordlists)
├── adapters/                    # Platform-specific output (generated by build.py)
│   ├── claude-code/
│   ├── github-copilot/
│   ├── opencode/
│   └── openclaw/
├── integrations/                # External tool integrations
│   ├── mcp/                     # MCP servers (scope, evidence, report)
│   ├── n8n/                     # Workflow templates
│   └── openproject/             # Project management sync
├── scripts/
│   ├── build.py                 # Adapter build system
│   └── smoke_test.sh            # Repository validation
├── reports/                     # Generated reports
└── scope.txt                    # Active engagement scope
```

## Scope Enforcement

All agents enforce scope boundaries before executing:

```
scope.txt format:
10.0.0.0/8
*.client-domain.com
192.168.1.0/24
```

The `core/hooks/scope_check.py` hook validates every target against `scope.txt`. Out-of-scope targets are blocked with a warning — no accidental testing of unauthorized systems.

## Installation

### Claude Code
```bash
git clone https://github.com/vsh00t/ThreatSwarm.git
cd ThreatSwarm
cp adapters/claude-code/CLAUDE.md .claude/CLAUDE.md  # or place in project root
# Start Claude Code in the repo — agents auto-activate based on context
```

### GitHub Copilot
```bash
git clone https://github.com/vsh00t/ThreatSwarm.git
cd ThreatSwarm
cp -r adapters/github-copilot/workspace-rules .github/
# Agents activate via workspace rules in VS Code / Copilot
```

### OpenCode
```bash
git clone https://github.com/vsh00t/ThreatSwarm.git
cd ThreatSwarm
cp adapters/opencode/instructions.md ./
# Launch OpenCode — instructions load automatically
```

### OpenClaw
```bash
git clone https://github.com/vsh00t/ThreatSwarm.git
cd ThreatSwarm
cp -r adapters/openclaw/skills/ ~/.openclaw/workspace/skills/threatswarm/
# Agents available as skills — spawn via sessions_spawn or task routing
```

### Build All Adapters
```bash
python3 scripts/build.py --all
```

## Requirements

- **Python 3.9+** for build system and MCP servers
- **AI coding agent** (Claude Code, GitHub Copilot, OpenCode, or OpenClaw)
- **uvx** (optional, for MCP server execution via `uv`)
- Pentesting tools referenced by agents (Metasploit, Nmap, Burp Suite, etc.) are **external** — install separately

## Verification

```bash
bash scripts/smoke_test.sh
```

Validates agent files, adapter content, script compilation, MCP servers, skill libraries, and templates. Fails fast on any issue.

## Demo

```
You: "I need to test this web app for SQL injection."
→ Web Attacker activates. Suggests SQLMap commands, Burp Suite workflow,
  parameter identification, time-based vs error-based techniques.
  Asks which WAF is in front (affects technique selection).

You: "Found domain admin via Kerberoasting."
→ Post-Exploitation activates. Suggests credential harvesting,
  lateral movement paths, persistence options. Links to
  Active Directory agent for DCSync if needed.

You: "Generate the final report."
→ Report Writer activates. Uses evidence from Evidence MCP,
  fills technical_finding and executive_summary templates,
  outputs to reports/.
```

## Fork Attribution

This is a fork of [mukul975/ThreatSwarm](https://github.com/mukul975/ThreatSwarm). Original concept: AI-powered multi-agent pentesting with Claude Code. This fork extends it with:

- Multi-platform support (4 adapters, not Claude Code only)
- 5 new agents (cloud-postex, purple-team, segmentation-tester, red-infra, vuln-management)
- Report generation pipeline with 4 templates
- Evidence capture system with chain of custody
- 3 MCP servers for scope, evidence, and report tooling
- n8n workflow automation
- OpenProject integration
- Build system for adapter generation
- Agent registry with metadata, triggers, and model recommendations

## License

MIT — see [LICENSE](LICENSE).
