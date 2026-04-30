# ThreatSwarm — OpenCode Penetration Testing Framework

> Generated 2026-04-30T14:53:40Z

## Scope Enforcement
**MANDATORY**: Verify all targets in `scope.txt` before any network command. OpenCode has no hook system — manual verification is required.

## Agents
- **active-directory**: Active Directory exploitation specialist — BloodHound attack path analysis, Kerberoasting, AS-REP roasting, DCSync, ACL abuse, certificate services (AD-CS ESC1-ESC8), domain persistence, and GPO exploitation. | Triggers: active directory, AD attack, bloodhound, kerberoast, DCSync, GPO, AD CS, ESC1
- **api-attacker**: API security testing — REST/GraphQL/SOAP testing, IDOR, BOLA/BFLA, broken authentication, rate limiting bypass, mass assignment, API key leakage, and API schema fuzzing. | Triggers: API security, REST API, GraphQL, IDOR, BOLA, API key, mass assignment, rate limit
- **blue-team**: Defensive security — detection rule creation (Sigma), CIS hardening, log configuration, incident response playbooks, EDR tuning, SIEM correlation, and security baseline enforcement. | Triggers: blue team, detection, hardening, SIEM, Sigma rules, CIS benchmark, EDR, SOC
- **c2-operator**: Command and Control infrastructure — Sliver framework, Havoc C2, Cobalt Strike profile analysis, redirector setup, payload generation, malleable C2 profiles, and implant management. | Triggers: C2, command and control, sliver, havoc, cobalt strike, beacon, implant, redirector
- **cloud-attacker**: Cloud penetration testing — AWS, Azure, GCP enumeration, Pacu automation, S3 bucket exploitation, IAM privilege escalation, Lambda backdoor injection, and cloud metadata service abuse. | Triggers: cloud security, AWS, Azure, GCP, Pacu, S3 bucket, IAM, Lambda
- **cloud-postex**: Cloud post-exploitation — IAM persistence, data exfiltration from cloud storage, cross-account trust abuse, cloud instance metadata SSRF, and cloud audit log manipulation. | Triggers: cloud post-exploitation, cloud persistence, IAM abuse, cloud data exfil, cloud audit, cross-account
- **compliance-scanner**: Compliance assessment — CIS benchmarks, PCI-DSS, NIST CSF, SOC 2, ISO 27001 gap analysis, automated scanning with Prowler, ScoutSuite, and benchmark frameworks. | Triggers: compliance, CIS benchmark, PCI-DSS, NIST CSF, SOC 2, ISO 27001, Prowler, ScoutSuite
- **container-attacker**: Container and Kubernetes security — Docker escape techniques, K8s RBAC abuse, cluster enumeration, container image scanning with Trivy, pod privilege escalation, and supply chain attacks. | Triggers: container, Docker, Kubernetes, K8s, container escape, RBAC, Trivy, pod security
- **crypto-attacker**: Cryptographic security assessment — SSL/TLS analysis, JWT algorithm confusion, padding oracle attacks, weak key detection, certificate validation bypass, and custom crypto audit. | Triggers: cryptographic, SSL, TLS, JWT, algorithm confusion, padding oracle, certificate, encryption
- **dfir**: Digital Forensics and Incident Response — memory forensics with Volatility3, disk forensics, evidence chain of custody, timeline analysis, artifact extraction, and incident containment. | Triggers: DFIR, forensics, incident response, memory forensics, Volatility, disk forensics, evidence, timeline analysis
- **evasion**: Evasion techniques — AMSI bypass, ETW patching, process injection, living-off-the-land binaries (LOLBins), antivirus evasion, and payload obfuscation for red team operations. | Triggers: evasion, AMSI bypass, ETW patch, process injection, LOLBins, antivirus evasion, obfuscation, living off the land
- **exploit**: Vulnerability exploitation — Metasploit framework, manual exploit development, RCE/SQLi/XSS exploitation, buffer overflow, heap spraying, and custom exploit chain assembly. | Triggers: exploit, Metasploit, RCE, SQL injection, buffer overflow, heap spray, exploit development, zero-day
- **iot-attacker**: IoT and OT security assessment — firmware analysis with Binwalk/Ghidra, emulation with QEMU/Firmadyne, UART/JTAG hardware hacking, MQTT/CoAP/Modbus protocol testing, SPI flash extraction, and embedded web interface exploitation. | Triggers: IoT, firmware, embedded, UART, JTAG, MQTT, Modbus, SCADA
- **log-analyst**: Security log analysis — Splunk queries, Linux audit logs, web server intrusion analysis, Windows event log parsing, log correlation, anomaly detection, and incident evidence extraction. | Triggers: log analysis, Splunk, audit log, event log, web log, log correlation, anomaly detection, SIEM query
- **malware-analyst**: Malware analysis — Linux ELF and Windows PE analysis, YARA rule creation, sandbox execution, behavior analysis, macro malware triage, hash enrichment with VirusTotal, and malware classification. | Triggers: malware, ELF, PE analysis, YARA, sandbox, behavior analysis, macro malware, VirusTotal
- **mobile-attacker**: Mobile application security — Android APK analysis (apktool/jadx), iOS IPA analysis, Frida instrumentation, SSL/root/biometric/jailbreak detection bypass, traffic interception (Burp/mitmproxy), OWASP Mobile Top 10, and MobSF automated scanning. | Triggers: mobile security, Android, iOS, APK, IPA, Frida, SSL pinning, root detection
- **network-ops**: Network-level attacks — ARP spoofing, man-in-the-middle interception, SMB relay, LLMNR/NBT-NS poisoning, VLAN hopping, and network traffic analysis with tshark. | Triggers: network attack, ARP spoof, MITM, SMB relay, LLMNR, NBT-NS, VLAN hopping, network traffic
- **osint**: Open source intelligence gathering — passive reconnaissance, SpiderFoot automation, DNS enumeration, subdomain discovery, social media profiling, email harvesting, and external footprint mapping. | Triggers: OSINT, reconnaissance, SpiderFoot, DNS enumeration, subdomain, social media, email harvesting, footprinting
- **password-attacks**: Password and credential attacks — hash cracking with hashcat, credential stuffing, password spraying, NTLM relay, Kerberoasting, and password policy assessment. | Triggers: password, hashcat, credential stuffing, password spray, hash cracking, NTLM relay, Kerberoast, credential harvesting
- **post-ex**: Post-exploitation — Linux/Windows privilege escalation, credential harvesting with LaZagne, lateral movement (WMI/PSExec/WinRM), golden ticket creation, and persistence mechanisms. | Triggers: post-exploitation, privilege escalation, lateral movement, credential harvesting, LaZagne, golden ticket, persistence, WMI
- **purple-team**: Purple team operations — MITRE ATT&CK mapping, detection gap identification, offensive technique execution with defensive validation, atomic red team tests, and collaborative attacker/defender exercises. | Triggers: purple team, MITRE ATT&CK, detection gap, atomic red team, attack validation, purple exercise
- **recon**: External and internal reconnaissance — advanced Nmap scanning, subdomain enumeration with Subfinder/Amass, port/service discovery, banner grabbing, web technology fingerprinting, and scope validation. | Triggers: reconnaissance, nmap, subdomain, port scan, service enumeration, fingerprinting, OSINT, external recon
- **red-infra**: Red team infrastructure — C2 deployment, redirector chains, domain registration with privacy, phishing infrastructure, payload hosting, and engagement lifecycle management. | Triggers: red team infrastructure, redirector, phishing infrastructure, payload hosting, red team, engagement, domain
- **report-writer**: Security report generation — executive summaries, technical findings, threat intelligence reports, incident response playbooks, CVSS scoring, remediation guidance, and SOC dashboards. | Triggers: report, executive summary, findings, threat intelligence, remediation, CVSS, playbook, dashboard
- **reverse-engineer**: Binary reverse engineering — Ghidra analysis, .NET decompilation with dnSpy, binary exploitation analysis, heap spray techniques, shellcode development, and vulnerability discovery in compiled code. | Triggers: reverse engineering, Ghidra, dnSpy, binary analysis, shellcode, decompilation, disassembly, .NET
- **segmentation-tester**: Network segmentation testing — cross-segment access validation, firewall rule testing, VLAN hopping verification, lateral movement path identification, and segmentation gap detection. | Triggers: segmentation, network segmentation, firewall rules, cross-segment, VLAN, lateral movement, network isolation
- **social-engineer**: Social engineering — phishing campaign simulation with GoPhish, spear phishing, pretexting, vishing, payload delivery, credential harvesting, and social engineering metrics/reporting. | Triggers: social engineering, phishing, GoPhish, spear phishing, pretexting, vishing, credential harvesting
- **threat-hunter**: Threat hunting — hypothesis-driven hunts, Cobalt Strike beacon detection, C2 beaconing analysis, persistence mechanism hunting, MITRE ATT&CK-based hunt queries, and threat intelligence integration. | Triggers: threat hunting, hypothesis, beacon detection, C2 hunting, persistence, threat intel, MITRE hunt
- **vuln-management**: Vulnerability management — Nuclei template scanning, authenticated scanning, Nessus/Tenable integration, vulnerability prioritization, CVSS scoring, and remediation tracking. | Triggers: vulnerability management, Nuclei, Nessus, vuln scanning, CVSS, remediation, vulnerability prioritization
- **vuln-researcher**: Vulnerability research — CVE analysis, KEV catalog prioritization, PoC development, patch diffing, zero-day research methodology, and responsible disclosure. | Triggers: vulnerability research, CVE, zero-day, PoC, patch diffing, KEV, disclosure, vuln analysis
- **web-attacker**: Web application penetration testing — SQLMap exploitation, XSS testing, SSRF, deserialization attacks, authentication bypass, file inclusion, and OWASP Top 10 systematic assessment. | Triggers: web application, pentest, SQL injection, XSS, SSRF, OWASP, web security, burp suite
- **wireless-attacker**: Wireless network security — WPA/WPA3 handshake capture and cracking, PMKID attacks, WPS Pixie Dust, evil twin with hostapd/dnsmasq, Bluetooth LE testing with bettercap, and rogue AP detection. | Triggers: wireless, WiFi, WPA, WPA3, PMKID, WPS, Pixie Dust, evil twin

## Commands
- `/attack`: description: Route an attack vector to the appropriate specialist agent — usage: /project:attack <target> <vector>
- `/engage`: description: Start a new engagement for a target — verifies scope, creates evidence directories, and launches recon agent
- `/hunt`: description: Run an ATT&CK-based threat hunt with a specific hypothesis
- `/ir`: description: Incident response workflow — triage, evidence collection, timeline, and IOC extraction
- `/pwned`: description: Post-exploitation workflow after getting shell access — privesc, credential harvest, lateral movement
- `/report`: description: Generate a professional penetration test report from all evidence files

## Rules
### Evidence\npaths:
  - "evidence/**"
---

## Evidence Handling Rules

All files written to `evidence/` must adhere to these mandatory standards.

### Required Fields in Every findings.md Entry

Every finding documented in any `findings.md`, `*_report.md`, or structured findings file within `evidence/` MUST incl...
### Exploits\npaths:
  - "**/*.py"
  - "**/*.rb"
  - "**/*.c"
  - "**/*.go"
  - "**/*.sh"
---

## Exploit Code Rules

These rules apply to all Python, Ruby, C, Go, and shell scripts in this workspace.

### Mandatory Header

Every exploit or PoC script MUST begin with this header block:

```python
#!/usr/bin/env p...
### Loot\npaths:
  - "loot/**"
---

## Loot Directory Rules

Files in `loot/` contain sensitive captured material. Handle with extreme care.

### Storage Format (Hashes Only)

Store ONLY the hash value, hash type, and source location. NEVER store plaintext passwords.

**Correct format:**
```
# NTLM Hashes — 1...
### Reports\npaths:
  - "reports/**"
---

## Report Writing Rules

These rules apply to all files written inside the `reports/` directory.

### Tone and Language

- Use professional, objective third-person language throughout
- Avoid emotional language, hyperbole, or client-blaming language
- State facts: "The t...

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
