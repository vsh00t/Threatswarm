# Cybersecurity Workspace — Master Context (Generated 2026-04-30T13:36:59Z)

## Scope Enforcement (MANDATORY — ZERO EXCEPTIONS)
**ALL targets MUST be listed in `scope.txt` before any network tool runs.**
The `scope_check.py` hook enforces this automatically on every Bash command.
Add targets: IP, CIDR, or domain — one per line, comments start with `#`.

## Agent Delegation Table
| Category | Agent | Description |
|----------|-------|-------------|
| offensive / windows | `active-directory` | Active Directory exploitation specialist — BloodHound attack path analysis, Kerb... |
| offensive / web | `api-attacker` | API security testing — REST/GraphQL/SOAP testing, IDOR, BOLA/BFLA, broken authen... |
| defensive / detection | `blue-team` | Defensive security — detection rule creation (Sigma), CIS hardening, log configu... |
| offensive / red-team | `c2-operator` | Command and Control infrastructure — Sliver framework, Havoc C2, Cobalt Strike p... |
| offensive / cloud | `cloud-attacker` | Cloud penetration testing — AWS, Azure, GCP enumeration, Pacu automation, S3 buc... |
| offensive / cloud | `cloud-postex` | Cloud post-exploitation — IAM persistence, data exfiltration from cloud storage,... |
| defensive / compliance | `compliance-scanner` | Compliance assessment — CIS benchmarks, PCI-DSS, NIST CSF, SOC 2, ISO 27001 gap ... |
| offensive / containers | `container-attacker` | Container and Kubernetes security — Docker escape techniques, K8s RBAC abuse, cl... |
| offensive / web | `crypto-attacker` | Cryptographic security assessment — SSL/TLS analysis, JWT algorithm confusion, p... |
| defensive / forensics | `dfir` | Digital Forensics and Incident Response — memory forensics with Volatility3, dis... |
| offensive / red-team | `evasion` | Evasion techniques — AMSI bypass, ETW patching, process injection, living-off-th... |
| offensive / exploitation | `exploit` | Vulnerability exploitation — Metasploit framework, manual exploit development, R... |
| offensive / IoT | `iot-attacker` | IoT and OT security assessment — firmware analysis with Binwalk/Ghidra, emulatio... |
| defensive / detection | `log-analyst` | Security log analysis — Splunk queries, Linux audit logs, web server intrusion a... |
| defensive / malware | `malware-analyst` | Malware analysis — Linux ELF and Windows PE analysis, YARA rule creation, sandbo... |
| offensive / mobile | `mobile-attacker` | Mobile application security — Android APK analysis (apktool/jadx), iOS IPA analy... |
| offensive / network | `network-ops` | Network-level attacks — ARP spoofing, man-in-the-middle interception, SMB relay,... |
| recon / OSINT | `osint` | Open source intelligence gathering — passive reconnaissance, SpiderFoot automati... |
| offensive / credentials | `password-attacks` | Password and credential attacks — hash cracking with hashcat, credential stuffin... |
| offensive / post-exploitation | `post-ex` | Post-exploitation — Linux/Windows privilege escalation, credential harvesting wi... |
| collaborative / offensive | `purple-team` | Purple team operations — MITRE ATT&CK mapping, detection gap identification, off... |
| recon / offensive | `recon` | External and internal reconnaissance — advanced Nmap scanning, subdomain enumera... |
| offensive / red-team | `red-infra` | Red team infrastructure — C2 deployment, redirector chains, domain registration ... |
| reporting / documentation | `report-writer` | Security report generation — executive summaries, technical findings, threat int... |
| offensive / reverse-engineering | `reverse-engineer` | Binary reverse engineering — Ghidra analysis, .NET decompilation with dnSpy, bin... |
| offensive / network | `segmentation-tester` | Network segmentation testing — cross-segment access validation, firewall rule te... |
| offensive / social-engineering | `social-engineer` | Social engineering — phishing campaign simulation with GoPhish, spear phishing, ... |
| defensive / detection | `threat-hunter` | Threat hunting — hypothesis-driven hunts, Cobalt Strike beacon detection, C2 bea... |
| defensive / compliance | `vuln-management` | Vulnerability management — Nuclei template scanning, authenticated scanning, Nes... |
| offensive / research | `vuln-researcher` | Vulnerability research — CVE analysis, KEV catalog prioritization, PoC developme... |
| offensive / web | `web-attacker` | Web application penetration testing — SQLMap exploitation, XSS testing, SSRF, de... |
| offensive / wireless | `wireless-attacker` | Wireless network security — WPA/WPA3 handshake capture and cracking, PMKID attac... |

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
