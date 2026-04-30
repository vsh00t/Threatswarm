# ThreatSwarm — OpenCode Penetration Testing Framework

> Generated 2026-04-30T04:35:13Z

## Scope Enforcement
**MANDATORY**: Verify all targets in `scope.txt` before any network command. OpenCode has no hook system — manual verification is required.

## Agents
- **active-directory**: Active Directory and Windows domain attack specialist. Use for Kerberoasting, AS-REP roasting, DCSync, BloodHound enumeration, ADCS ESC attacks, Golden/Silver Ticket, and domain privilege escalation. Triggers on: kerberoast, AS-REP, bloodhound, DCSync, golden ticket, ADCS, ESC, domain controller, LDAP, GPO, AD, domain admin. | Triggers: kerberoast, AS-REP, bloodhound, DCSync, golden ticket, ADCS, ESC, domain controller
- **api-attacker**: API security testing specialist for REST, GraphQL, gRPC, and WebSocket APIs. Handles BOLA/IDOR, mass assignment, authentication bypass, rate limit evasion, JWT attacks, GraphQL introspection abuse, API enumeration, and OWASP API Top 10. Triggers on: API, REST, GraphQL, gRPC, WebSocket, BOLA, IDOR, mass assignment, API key, JWT, OpenAPI, swagger, rate limit, API auth, endpoint discovery. | Triggers: API, REST, GraphQL, gRPC, WebSocket, BOLA, IDOR, mass assignment
- **blue-team**: Defensive security and hardening specialist. Creates detection rules, hardens Linux/Windows systems, writes Sigma rules, configures auditd, fail2ban, Sysmon, and provides CIS benchmark remediation guidance. Triggers on: harden, detection, Sigma rule, Sysmon, auditd, fail2ban, CIS benchmark, SIEM detection, blue team, defensive, firewall rules, access control, Windows hardening, Linux hardening. | Triggers: harden, detection, Sigma rule, Sysmon, auditd, fail2ban, CIS benchmark, SIEM detection
- **c2-operator**: Command and control infrastructure specialist for authorized red team operations. Handles Sliver C2 framework, Havoc C2, Metasploit multi-handler, msfvenom payload generation, implant configuration, HTTPS C2 traffic blending, and operator session management. Triggers on: C2, command and control, Sliver, Havoc, msfvenom, implant, beacon, Meterpreter, payload generation, listener, handler, staged payload. | Triggers: C2, command and control, Sliver, Havoc, msfvenom, implant, beacon, Meterpreter
- **cloud-attacker**: Cloud penetration testing specialist for AWS, Azure, and GCP. Handles IAM enumeration, privilege escalation, S3 bucket abuse, metadata SSRF, Pacu framework, container escape to cloud, and cloud-native attack chains. Triggers on: AWS, Azure, GCP, cloud, IAM, S3, storage bucket, metadata endpoint, Pacu, cloud privesc, service account, managed identity. | Triggers: AWS, Azure, GCP, cloud, IAM, S3, storage bucket, metadata endpoint
- **compliance-scanner**: Compliance and security standards assessment specialist. Handles CIS benchmarks, PCI-DSS controls, NIST CSF, SOC2, GDPR technical controls, OpenSCAP assessments, Docker CIS bench, Kubernetes CIS bench, and security configuration auditing. Triggers on: compliance, CIS benchmark, PCI-DSS, NIST, SOC2, GDPR, lynis, OpenSCAP, docker bench, kube-bench, audit. | Triggers: compliance, CIS benchmark, PCI-DSS, NIST, SOC2, GDPR, lynis, OpenSCAP
- **container-attacker**: Container and Kubernetes security specialist. Handles Docker escape techniques, Kubernetes RBAC abuse, service account token theft, kubelet API exploitation, etcd access, namespace breakout, and cloud-to-container pivot chains. Triggers on: docker, container, Kubernetes, k8s, pod, kubelet, etcd, service account, RBAC, namespace escape, container escape, helm. | Triggers: docker, container, Kubernetes, k8s, pod, kubelet, etcd, service account
- **crypto-attacker**: Cryptography and TLS security specialist. Handles TLS configuration auditing, JWT algorithm confusion, padding oracle attacks, hash cracking mode selection, RSA weak key analysis, ECB mode detection, certificate inspection, and crypto protocol attacks. Triggers on: TLS, SSL, cipher, JWT, padding oracle, RSA, hash, crypto, certificate, BEAST, POODLE, Heartbleed, testssl, sslscan. | Triggers: TLS, SSL, cipher, JWT, padding oracle, RSA, hash, crypto
- **dfir**: Digital forensics and incident response specialist. Handles triage, memory acquisition with AVML/LiME, Volatility analysis, log timeline reconstruction, IOC extraction, persistence hunting, and incident reporting. Triggers on: DFIR, incident response, forensics, Volatility, memory dump, timeline, IOC, triage, compromise, malware on host, breach, intrusion. | Triggers: DFIR, incident response, forensics, Volatility, memory dump, timeline, IOC, triage
- **evasion**: Antivirus and EDR evasion specialist for authorized red team engagements. Handles AMSI bypass, payload obfuscation, living-off-the-land techniques, sandbox detection, process injection concepts, and detection gap identification. Triggers on: AMSI bypass, AV evasion, EDR bypass, obfuscation, LOTL, living off the land, payload encoding, sandbox detection, process injection, defender bypass. | Triggers: AMSI bypass, AV evasion, EDR bypass, obfuscation, LOTL, living off the land, payload encoding, sandbox detection
- **exploit**: Exploitation specialist for gaining initial access. Use when exploiting CVEs, running Metasploit modules, using searchsploit, obtaining shells, or executing proof-of-concept code. Triggers on: exploit, CVE-, initial access, get shell, msfconsole, owned, pwn, vulnerability exploit, remote code execution, RCE. | Triggers: exploit, CVE-, initial access, get shell, msfconsole, owned, pwn, vulnerability exploit
- **iot-attacker**: IoT and embedded systems security specialist. Handles firmware extraction and analysis, hardcoded credential discovery, UART/JTAG access, MQTT/CoAP protocol testing, RouterSploit exploitation, web interface attacks, and OT/ICS protocol analysis. Triggers on: IoT, firmware, binwalk, UART, JTAG, router, embedded, RouterSploit, MQTT, Modbus, BACnet, hardcoded credentials, ICS, SCADA. | Triggers: IoT, firmware, binwalk, UART, JTAG, router, embedded, RouterSploit
- **log-analyst**: Security log analysis specialist. Parses and correlates auth.log, nginx/apache access logs, Windows Event Logs, syslog, audit logs, and cloud logs for anomalies, intrusions, and security events. Generates timeline and Sigma rules from findings. Triggers on: log analysis, log parsing, auth.log, access log, SIEM, event log, anomaly detection, log correlation, wevtutil, log forensics. | Triggers: log analysis, log parsing, auth.log, access log, SIEM, event log, anomaly detection, log correlation
- **malware-analyst**: Malware analysis specialist for static and dynamic analysis. Handles PE/ELF/APK binary triage, behavioral analysis, IOC extraction, YARA rule writing, C2 protocol reverse engineering, deobfuscation, sandbox report interpretation, and ATT&CK mapping. Triggers on: malware, sample, IOC, YARA, sandbox, deobfuscate, unpack, C2, beacon, ransomware, trojan, RAT, dropper, PE analysis. | Triggers: malware, sample, IOC, YARA, sandbox, deobfuscate, unpack, C2
- **mobile-attacker**: Mobile application security specialist for Android and iOS. Handles APK decompilation, static/dynamic analysis, Frida instrumentation, SSL pinning bypass, ADB shell exploitation, MobSF scanning, traffic interception, and deep link abuse. Triggers on: Android, iOS, APK, IPA, Frida, ADB, MobSF, apktool, jadx, SSL pinning, smali, mobile pentest, deep link. | Triggers: Android, iOS, APK, IPA, Frida, ADB, MobSF, apktool
- **network-ops**: Network penetration testing specialist for ARP attacks, MitM, packet capture, SNMP enumeration, SMB relay, Responder credential capture, and network-level attacks. Triggers on: ARP, MitM, sniff, intercept, VLAN, network attack, packet capture, relay, Responder, NTLM relay, SMB relay, SNMP. | Triggers: ARP, MitM, sniff, intercept, VLAN, network attack, packet capture, relay
- **osint**: Open source intelligence specialist for passive reconnaissance. Handles domain intelligence, certificate transparency, Shodan enumeration, email harvesting, GitHub dorking, employee profiling, ASN/IP research, breach data, Google dorks, and Wayback Machine analysis. Triggers on: OSINT, passive recon, theHarvester, shodan, whois, crt.sh, google dork, wayback, LinkedIn, GitHub dork, ASN, breach data, email harvest. | Triggers: OSINT, passive recon, theHarvester, shodan, whois, crt.sh, google dork, wayback
- **password-attacks**: Password cracking and credential attack specialist. Use when working with password hashes, hash cracking, wordlist attacks, credential analysis, or password auditing. Triggers on: password, hash, crack, hashcat, john, wordlist, NetNTLMv2, Kerberoast, NTLM, bcrypt, credential, ASREP, JWT crack, mask attack, rule attack, CeWL, rockyou, hash mode. | Triggers: password, hash, crack, hashcat, john, wordlist, NetNTLMv2, Kerberoast
- **post-ex**: Post-exploitation specialist for privilege escalation, lateral movement, persistence, and credential harvesting. Use after obtaining initial shell access. Triggers on: privesc, lateral, pivot, persistence, escalate, post exploitation, linpeas, winpeas, mimikatz, secretsdump, pass the hash, token impersonation. | Triggers: privesc, lateral, pivot, persistence, escalate, post exploitation, linpeas, winpeas
- **recon**: Reconnaissance and enumeration specialist. Use when scanning, enumerating ports, fingerprinting services, discovering subdomains, running nuclei vulnerability scans, directory brute-forcing, or building an attack surface map. Triggers on: scan, enumerate, discover, ports, fingerprint, recon, nmap, httpx, feroxbuster, subfinder, amass, nuclei. | Triggers: scan, enumerate, discover, ports, fingerprint, recon, nmap, httpx
- **report-writer**: Penetration test report writing specialist. Consolidates evidence from all evidence/ directories into professional reports with CVSS scoring, executive summaries, technical findings, remediation roadmaps, and methodology sections. Triggers on: write report, pentest report, executive summary, findings report, CVSS, risk rating, remediation roadmap, evidence consolidation. | Triggers: write report, pentest report, executive summary, findings report, CVSS, risk rating, remediation roadmap, evidence consolidation
- **reverse-engineer**: Binary reverse engineering and exploit development specialist. Handles static analysis with Ghidra/Radare2, dynamic analysis with GDB/strace, shellcode crafting, ROP chain construction, format string exploits, heap exploitation, and CTF binary challenges. Triggers on: reverse engineer, binary analysis, Ghidra, r2, radare2, GDB, pwndbg, shellcode, ROP, format string, buffer overflow, heap, CTF, decompile, disassemble. | Triggers: reverse engineer, binary analysis, Ghidra, r2, radare2, GDB, pwndbg, shellcode
- **social-engineer**: Social engineering and phishing simulation specialist. Handles GoPhish campaign setup, spear-phishing email crafting, evilginx2 adversary-in-the-middle phishing, pretexting scripts, vishing scenarios, SMS phishing, and awareness training. Triggers on: phishing, spear phishing, gophish, vishing, smishing, pretexting, social engineering, email campaign, evilginx, fake login, credential harvest. | Triggers: phishing, spear phishing, gophish, vishing, smishing, pretexting, social engineering, email campaign
- **threat-hunter**: Proactive threat hunting specialist using ATT&CK-based hypotheses. Hunts for lateral movement, persistence, credential dumping, C2 beaconing, data exfiltration, and living-off-the-land techniques across logs, pcaps, and endpoint telemetry. Triggers on: threat hunt, hunt, hypothesis, ATT&CK, lateral movement detection, beaconing, persistence hunting, EDR hunt, SIEM hunt, log analysis, anomaly. | Triggers: threat hunt, hunt, hypothesis, ATT&CK, lateral movement detection, beaconing, persistence hunting, EDR hunt
- **vuln-researcher**: Vulnerability research and CVE analysis specialist. Handles NVD API queries, searchsploit cross-reference, PoC reliability assessment, CVSS scoring, version fingerprinting, exploit chain research, and responsible disclosure coordination. Triggers on: CVE, vulnerability research, searchsploit, NVD, exploit, CVSS score, PoC, version fingerprint, responsible disclosure, advisory. | Triggers: CVE, vulnerability research, searchsploit, NVD, exploit, CVSS score, PoC, version fingerprint
- **web-attacker**: Web application penetration testing — SQL injection, XSS, SSRF, LFI, IDOR, JWT attacks, GraphQL, API parameter discovery, and OWASP Top 10 exploitation | Triggers: 
- **wireless-attacker**: Wireless network penetration testing specialist. Handles WPA2/WPA3 capture and cracking, PMKID attacks, Evil Twin / rogue AP attacks, WPS PIN attacks, EAP/PEAP credential capture, Bluetooth assessment, and wireless deauthentication. Triggers on: wifi, wireless, WPA2, WPA3, aircrack, airmon, WPS, evil twin, rogue AP, 802.11, PMKID, EAP, PEAP, Bluetooth, BLE, hostapd-wpe. | Triggers: wifi, wireless, WPA2, WPA3, aircrack, airmon, WPS, evil twin

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
