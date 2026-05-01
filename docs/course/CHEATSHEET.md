# ThreatSwarm v2.0 — Cheatsheet | Ironcybersec

---

## Setup

```
git clone https://github.com/vsh00t/ThreatSwarm.git && cd ThreatSwarm
sudo bash scripts/install_kali.sh
python3 scripts/build.py --all
export ANTHROPIC_API_KEY=sk-***
opencode -c .
```

---

## Slash Commands

| Cmd | Desc | Example |
|-----|------|---------|
| `/engage` | Start engagement | `/engage 192.168.1.0/24` |
| `/attack` | Route attack vector | `/attack web sqli 192.168.1.100` |
| `/hunt` | Threat hunt | `/hunt "beacon detection in DNS logs"` |
| `/ir` | Incident response | `/ir suspicious_process_on_DC` |
| `/pwned` | Post-ex after shell | `/pwned 192.168.1.100` |
| `/report` | Generate report | `/report --format html` |

---

## 32 Agents by Category

| Category | Agents |
|----------|--------|
| Recon | recon, osint |
| Web | web-attacker, api-attacker, vuln-researcher |
| Network | network-ops, wireless-attacker |
| Exploitation | exploit, password-attacks, reverse-engineer |
| Post-Ex | post-ex, cloud-postex |
| AD/Windows | active-directory |
| Mobile | mobile-attacker |
| Cloud | cloud-attacker, red-infra |
| Containers | container-attacker |
| Evasion | evasion |
| C2 | c2-operator |
| Crypto | crypto-attacker |
| DFIR | dfir, log-analyst |
| Malware | malware-analyst |
| IoT | iot-attacker |
| Threat Intel | threat-hunter |
| Defense | blue-team, purple-team, compliance-scanner |
| Social | social-engineer |
| Reporting | report-writer |
| Testing | segmentation-tester, vuln-management |

---

## MCP Servers

| Server | Tools |
|--------|-------|
| **scope-mcp** | `scope_check`, `scope_list`, `scope_add` |
| **evidence-mcp** | `screenshot`, `verify`, `list`, `export` |
| **report-mcp** | `generate`, `template_list` |

---

## Scope Enforcement

```
echo "192.168.1.0/24" > scope.txt
echo "10.0.0.0/24" >> scope.txt
echo "testlab.local" >> scope.txt
python3 core/scripts/scope_validate.py
```

## Report Generation

```
python3 core/scripts/report_generate.py generate \
  --type executive --evidence-dir evidence/ \
  --output reports/ --format html
```

**Types:** `executive` · `technical` · `remediation` · `client`
**Formats:** `markdown` (default) · `html` · `pdf`

---

---

# ThreatSwarm v2.0 — Workflows & Tips | Ironcybersec

---

## Full Engagement Workflow

```
1. Configure scope.txt
2. /engage <target>
3. [AI runs recon: nmap, subfinder, httpx]
4. Delegate: "analiza puertos abiertos y busca vulns con nuclei"
5. Delegate: "explota la SQLi encontrada en el puerto 8080"
6. /pwned <target>
7. /report --format html
```

---

## Key Tips

- Verify `scope.txt` before every engagement
- Use `--format html` for professional reports
- Evidence auto-captures to `evidence/YYYYMMDD/`
- Model: **sonnet** for most tasks, **opus** for complex exploitation
- Run `smoke_test.sh` after any update

---

## Common Commands

```
nmap -sV -sC -oA recon/scan $TARGET
nuclei -u http://$TARGET -t cves/ -o evidence/nuclei.txt
sqlmap -u "http://$TARGET/page?id=1" --batch --dbs
netexec smb $TARGET -u admin -p '' --shares
bloodhound-python -d domain.local -u user -p pass -ns DC_IP
hashcat -m 1000 hashes.txt /usr/share/wordlists/rockyou.txt
frida -U -f com.app.package -l hook.js
python3 core/hooks/scope_check.py < input.json
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MCP server not responding | Check python3 path, run manually |
| Out of scope blocked | Add target to `scope.txt` |
| Report shows INFO not CRITICAL | Update `findings.json` severity field |
| Build fails | Delete `__pycache__`, run `build.py --all` |
| Model timeout | Switch to haiku for simple tasks |

---

## Ecosystem 2026

- **Burp MCP** — BApp Store (PortSwigger, Feb 2026)
- **Frida MCP** — kahlo-mcp, frida-c2-mcp
- **pentest-ai-agents** — github.com/0xSteph/pentest-ai-agents
- **Claude Code Security** — anthropic.com/news/claude-code-security

---

## Key Files

```
core/agents/            # 32 agent definitions
core/hooks/             # scope_check, evidence_capture
core/scripts/           # report_generate, scope_validate
core/skills/            # 5 reference libraries
core/templates/         # 4 report templates
integrations/mcp/       # 3 MCP servers
scripts/build.py        # Adapter generator
scripts/smoke_test.sh   # Validation suite
scripts/install_kali.sh # Kali installer
adapters/opencode/      # OpenCode adapter
```

---

*ironcybersec.com · github.com/vsh00t/ThreatSwarm*
