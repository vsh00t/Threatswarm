# Cybersecurity Workspace — Master Context (Generated 2026-04-30T04:35:13Z)

## Scope Enforcement (MANDATORY — ZERO EXCEPTIONS)
**ALL targets MUST be listed in `scope.txt` before any network tool runs.**
The `scope_check.py` hook enforces this automatically on every Bash command.
Add targets: IP, CIDR, or domain — one per line, comments start with `#`.

## Agent Delegation Table
| Category | Agent | Description |
|----------|-------|-------------|
| offensive / ad | `active-directory` | Active Directory and Windows domain attack specialist. Use for Kerberoasting, AS... |
| offensive / api | `api-attacker` | API security testing specialist for REST, GraphQL, gRPC, and WebSocket APIs. Han... |
| defensive / hardening | `blue-team` | Defensive security and hardening specialist. Creates detection rules, hardens Li... |
| offensive / c2 | `c2-operator` | Command and control infrastructure specialist for authorized red team operations... |
| offensive / cloud | `cloud-attacker` | Cloud penetration testing specialist for AWS, Azure, and GCP. Handles IAM enumer... |
| compliance / defensive | `compliance-scanner` | Compliance and security standards assessment specialist. Handles CIS benchmarks,... |
| offensive / containers | `container-attacker` | Container and Kubernetes security specialist. Handles Docker escape techniques, ... |
| offensive / crypto | `crypto-attacker` | Cryptography and TLS security specialist. Handles TLS configuration auditing, JW... |
| defensive / forensics | `dfir` | Digital forensics and incident response specialist. Handles triage, memory acqui... |
| offensive / evasion | `evasion` | Antivirus and EDR evasion specialist for authorized red team engagements. Handle... |
| offensive / exploitation | `exploit` | Exploitation specialist for gaining initial access. Use when exploiting CVEs, ru... |
| offensive / iot | `iot-attacker` | IoT and embedded systems security specialist. Handles firmware extraction and an... |
| defensive / logging | `log-analyst` | Security log analysis specialist. Parses and correlates auth.log, nginx/apache a... |
| malware / analysis | `malware-analyst` | Malware analysis specialist for static and dynamic analysis. Handles PE/ELF/APK ... |
| offensive / mobile | `mobile-attacker` | Mobile application security specialist for Android and iOS. Handles APK decompil... |
| offensive / network | `network-ops` | Network penetration testing specialist for ARP attacks, MitM, packet capture, SN... |
| recon / osint | `osint` | Open source intelligence specialist for passive reconnaissance. Handles domain i... |
| offensive / credential-access | `password-attacks` | Password cracking and credential attack specialist. Use when working with passwo... |
| offensive / post-exploitation | `post-ex` | Post-exploitation specialist for privilege escalation, lateral movement, persist... |
| recon / offensive | `recon` | Reconnaissance and enumeration specialist. Use when scanning, enumerating ports,... |
| reporting / documentation | `report-writer` | Penetration test report writing specialist. Consolidates evidence from all evide... |
| offensive / malware | `reverse-engineer` | Binary reverse engineering and exploit development specialist. Handles static an... |
| offensive / social-engineering | `social-engineer` | Social engineering and phishing simulation specialist. Handles GoPhish campaign ... |
| defensive / threat-hunting | `threat-hunter` | Proactive threat hunting specialist using ATT&CK-based hypotheses. Hunts for lat... |
| research / vulnerability | `vuln-researcher` | Vulnerability research and CVE analysis specialist. Handles NVD API queries, sea... |
| offensive / web | `web-attacker` | Web application penetration testing — SQL injection, XSS, SSRF, LFI, IDOR, JWT a... |
| offensive / wireless | `wireless-attacker` | Wireless network penetration testing specialist. Handles WPA2/WPA3 capture and c... |

**NEVER run active recon or exploitation in the main conversation thread.**
**ALWAYS delegate to the appropriate agent.**

## OPSEC Defaults
- External traffic: route through `proxychains` where possible
- Nmap timing: `-T3` maximum unless explicitly authorized for `-T4`
- No real PII exfiltration — reference paths only in evidence/
- Minimize footprint: staged payloads for initial access only

## Evidence Output Pattern
```
evidence/$(date +%Y%m%d)/$TARGET/{nmap,nuclei,web,creds,screenshots}/
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
