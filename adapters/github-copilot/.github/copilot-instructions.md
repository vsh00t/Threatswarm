# ThreatSwarm — AI Penetration Testing Assistant

> Generated 2026-04-30T04:56:26Z from core/ content. This file provides comprehensive pentesting context for GitHub Copilot.

## ⚠️ CRITICAL: Scope Enforcement

**Before running ANY network command, verify the target is in `scope.txt`.**
GitHub Copilot does not have hook support, so you MUST manually verify scope.

1. Read `scope.txt`
2. Confirm the target IP/domain/CIDR is listed
3. If not found, STOP and report: "TARGET [X] is not in scope.txt"

## Agent Catalog

You have access to specialist agents for different attack categories. Match the task to the appropriate agent:

### active-directory
**Role:** Active Directory exploitation specialist — BloodHound attack path analysis, Kerberoasting, AS-REP roasting, DCSync, ACL abuse, certificate services (AD-CS ESC1-ESC8), domain persistence, and GPO exploitation.
**Triggers:** active directory, AD attack, bloodhound, kerberoast, DCSync, GPO, AD CS, ESC1, domain admin, lateral movement
**Tags:** offensive, windows, AD, red-team, lateral-movement
**Model tier:** sonnet
### api-attacker
**Role:** API security testing — REST/GraphQL/SOAP testing, IDOR, BOLA/BFLA, broken authentication, rate limiting bypass, mass assignment, API key leakage, and API schema fuzzing.
**Triggers:** API security, REST API, GraphQL, IDOR, BOLA, API key, mass assignment, rate limit, API testing
**Tags:** offensive, web, API, appsec
**Model tier:** sonnet
### blue-team
**Role:** Defensive security — detection rule creation (Sigma), CIS hardening, log configuration, incident response playbooks, EDR tuning, SIEM correlation, and security baseline enforcement.
**Triggers:** blue team, detection, hardening, SIEM, Sigma rules, CIS benchmark, EDR, SOC, defensive
**Tags:** defensive, detection, hardening, compliance
**Model tier:** sonnet
### c2-operator
**Role:** Command and Control infrastructure — Sliver framework, Havoc C2, Cobalt Strike profile analysis, redirector setup, payload generation, malleable C2 profiles, and implant management.
**Triggers:** C2, command and control, sliver, havoc, cobalt strike, beacon, implant, redirector, malleable C2
**Tags:** offensive, red-team, infrastructure, C2
**Model tier:** sonnet
### cloud-attacker
**Role:** Cloud penetration testing — AWS, Azure, GCP enumeration, Pacu automation, S3 bucket exploitation, IAM privilege escalation, Lambda backdoor injection, and cloud metadata service abuse.
**Triggers:** cloud security, AWS, Azure, GCP, Pacu, S3 bucket, IAM, Lambda, cloud pentest, metadata service
**Tags:** offensive, cloud, AWS, Azure, GCP
**Model tier:** sonnet
### cloud-postex
**Role:** Cloud post-exploitation — IAM persistence, data exfiltration from cloud storage, cross-account trust abuse, cloud instance metadata SSRF, and cloud audit log manipulation.
**Triggers:** cloud post-exploitation, cloud persistence, IAM abuse, cloud data exfil, cloud audit, cross-account
**Tags:** offensive, cloud, post-exploitation, persistence
**Model tier:** sonnet
### compliance-scanner
**Role:** Compliance assessment — CIS benchmarks, PCI-DSS, NIST CSF, SOC 2, ISO 27001 gap analysis, automated scanning with Prowler, ScoutSuite, and benchmark frameworks.
**Triggers:** compliance, CIS benchmark, PCI-DSS, NIST CSF, SOC 2, ISO 27001, Prowler, ScoutSuite, gap analysis
**Tags:** defensive, compliance, governance, auditing
**Model tier:** haiku
### container-attacker
**Role:** Container and Kubernetes security — Docker escape techniques, K8s RBAC abuse, cluster enumeration, container image scanning with Trivy, pod privilege escalation, and supply chain attacks.
**Triggers:** container, Docker, Kubernetes, K8s, container escape, RBAC, Trivy, pod security, cluster pentest
**Tags:** offensive, containers, Kubernetes, Docker
**Model tier:** sonnet
### crypto-attacker
**Role:** Cryptographic security assessment — SSL/TLS analysis, JWT algorithm confusion, padding oracle attacks, weak key detection, certificate validation bypass, and custom crypto audit.
**Triggers:** cryptographic, SSL, TLS, JWT, algorithm confusion, padding oracle, certificate, encryption, crypto audit
**Tags:** offensive, web, crypto, appsec
**Model tier:** sonnet
### dfir
**Role:** Digital Forensics and Incident Response — memory forensics with Volatility3, disk forensics, evidence chain of custody, timeline analysis, artifact extraction, and incident containment.
**Triggers:** DFIR, forensics, incident response, memory forensics, Volatility, disk forensics, evidence, timeline analysis, IR
**Tags:** defensive, forensics, incident-response
**Model tier:** sonnet
### evasion
**Role:** Evasion techniques — AMSI bypass, ETW patching, process injection, living-off-the-land binaries (LOLBins), antivirus evasion, and payload obfuscation for red team operations.
**Triggers:** evasion, AMSI bypass, ETW patch, process injection, LOLBins, antivirus evasion, obfuscation, living off the land
**Tags:** offensive, red-team, evasion, post-exploitation
**Model tier:** opus
### exploit
**Role:** Vulnerability exploitation — Metasploit framework, manual exploit development, RCE/SQLi/XSS exploitation, buffer overflow, heap spraying, and custom exploit chain assembly.
**Triggers:** exploit, Metasploit, RCE, SQL injection, buffer overflow, heap spray, exploit development, zero-day
**Tags:** offensive, exploitation, web, red-team
**Model tier:** opus
### iot-attacker
**Role:** IoT and OT security assessment — firmware analysis with Binwalk/Ghidra, emulation with QEMU/Firmadyne, UART/JTAG hardware hacking, MQTT/CoAP/Modbus protocol testing, SPI flash extraction, and embedded web interface exploitation.
**Triggers:** IoT, firmware, embedded, UART, JTAG, MQTT, Modbus, SCADA, ICS, OT security
**Tags:** offensive, IoT, OT, firmware, hardware
**Model tier:** sonnet
### log-analyst
**Role:** Security log analysis — Splunk queries, Linux audit logs, web server intrusion analysis, Windows event log parsing, log correlation, anomaly detection, and incident evidence extraction.
**Triggers:** log analysis, Splunk, audit log, event log, web log, log correlation, anomaly detection, SIEM query
**Tags:** defensive, detection, forensics, SOC
**Model tier:** haiku
### malware-analyst
**Role:** Malware analysis — Linux ELF and Windows PE analysis, YARA rule creation, sandbox execution, behavior analysis, macro malware triage, hash enrichment with VirusTotal, and malware classification.
**Triggers:** malware, ELF, PE analysis, YARA, sandbox, behavior analysis, macro malware, VirusTotal, reverse engineering
**Tags:** defensive, malware, forensics, reverse-engineering
**Model tier:** sonnet
### mobile-attacker
**Role:** Mobile application security — Android APK analysis (apktool/jadx), iOS IPA analysis, Frida instrumentation, SSL/root/biometric/jailbreak detection bypass, traffic interception (Burp/mitmproxy), OWASP Mobile Top 10, and MobSF automated scanning.
**Triggers:** mobile security, Android, iOS, APK, IPA, Frida, SSL pinning, root detection, biometric bypass, jailbreak
**Tags:** offensive, mobile, appsec, Android, iOS
**Model tier:** sonnet
### network-ops
**Role:** Network-level attacks — ARP spoofing, man-in-the-middle interception, SMB relay, LLMNR/NBT-NS poisoning, VLAN hopping, and network traffic analysis with tshark.
**Triggers:** network attack, ARP spoof, MITM, SMB relay, LLMNR, NBT-NS, VLAN hopping, network traffic, packet capture
**Tags:** offensive, network, MITM, red-team
**Model tier:** sonnet
### osint
**Role:** Open source intelligence gathering — passive reconnaissance, SpiderFoot automation, DNS enumeration, subdomain discovery, social media profiling, email harvesting, and external footprint mapping.
**Triggers:** OSINT, reconnaissance, SpiderFoot, DNS enumeration, subdomain, social media, email harvesting, footprinting, passive
**Tags:** recon, OSINT, intelligence, passive
**Model tier:** haiku
### password-attacks
**Role:** Password and credential attacks — hash cracking with hashcat, credential stuffing, password spraying, NTLM relay, Kerberoasting, and password policy assessment.
**Triggers:** password, hashcat, credential stuffing, password spray, hash cracking, NTLM relay, Kerberoast, credential harvesting
**Tags:** offensive, credentials, cracking
**Model tier:** haiku
### post-ex
**Role:** Post-exploitation — Linux/Windows privilege escalation, credential harvesting with LaZagne, lateral movement (WMI/PSExec/WinRM), golden ticket creation, and persistence mechanisms.
**Triggers:** post-exploitation, privilege escalation, lateral movement, credential harvesting, LaZagne, golden ticket, persistence, WMI, PSExec
**Tags:** offensive, post-exploitation, lateral-movement
**Model tier:** sonnet
### purple-team
**Role:** Purple team operations — MITRE ATT&CK mapping, detection gap identification, offensive technique execution with defensive validation, atomic red team tests, and collaborative attacker/defender exercises.
**Triggers:** purple team, MITRE ATT&CK, detection gap, atomic red team, attack validation, purple exercise
**Tags:** collaborative, offensive, defensive, MITRE
**Model tier:** sonnet
### recon
**Role:** External and internal reconnaissance — advanced Nmap scanning, subdomain enumeration with Subfinder/Amass, port/service discovery, banner grabbing, web technology fingerprinting, and scope validation.
**Triggers:** reconnaissance, nmap, subdomain, port scan, service enumeration, fingerprinting, OSINT, external recon
**Tags:** recon, offensive, network, enumeration
**Model tier:** haiku
### red-infra
**Role:** Red team infrastructure — C2 deployment, redirector chains, domain registration with privacy, phishing infrastructure, payload hosting, and engagement lifecycle management.
**Triggers:** red team infrastructure, redirector, phishing infrastructure, payload hosting, red team, engagement, domain
**Tags:** offensive, red-team, infrastructure
**Model tier:** sonnet
### report-writer
**Role:** Security report generation — executive summaries, technical findings, threat intelligence reports, incident response playbooks, CVSS scoring, remediation guidance, and SOC dashboards.
**Triggers:** report, executive summary, findings, threat intelligence, remediation, CVSS, playbook, dashboard
**Tags:** reporting, documentation, compliance
**Model tier:** haiku
### reverse-engineer
**Role:** Binary reverse engineering — Ghidra analysis, .NET decompilation with dnSpy, binary exploitation analysis, heap spray techniques, shellcode development, and vulnerability discovery in compiled code.
**Triggers:** reverse engineering, Ghidra, dnSpy, binary analysis, shellcode, decompilation, disassembly, .NET
**Tags:** offensive, reverse-engineering, binary
**Model tier:** opus
### segmentation-tester
**Role:** Network segmentation testing — cross-segment access validation, firewall rule testing, VLAN hopping verification, lateral movement path identification, and segmentation gap detection.
**Triggers:** segmentation, network segmentation, firewall rules, cross-segment, VLAN, lateral movement, network isolation
**Tags:** offensive, network, infrastructure
**Model tier:** sonnet
### social-engineer
**Role:** Social engineering — phishing campaign simulation with GoPhish, spear phishing, pretexting, vishing, payload delivery, credential harvesting, and social engineering metrics/reporting.
**Triggers:** social engineering, phishing, GoPhish, spear phishing, pretexting, vishing, credential harvesting
**Tags:** offensive, social-engineering, red-team
**Model tier:** sonnet
### threat-hunter
**Role:** Threat hunting — hypothesis-driven hunts, Cobalt Strike beacon detection, C2 beaconing analysis, persistence mechanism hunting, MITRE ATT&CK-based hunt queries, and threat intelligence integration.
**Triggers:** threat hunting, hypothesis, beacon detection, C2 hunting, persistence, threat intel, MITRE hunt
**Tags:** defensive, detection, threat-intelligence
**Model tier:** sonnet
### vuln-management
**Role:** Vulnerability management — Nuclei template scanning, authenticated scanning, Nessus/Tenable integration, vulnerability prioritization, CVSS scoring, and remediation tracking.
**Triggers:** vulnerability management, Nuclei, Nessus, vuln scanning, CVSS, remediation, vulnerability prioritization
**Tags:** defensive, compliance, vulnerability-management
**Model tier:** haiku
### vuln-researcher
**Role:** Vulnerability research — CVE analysis, KEV catalog prioritization, PoC development, patch diffing, zero-day research methodology, and responsible disclosure.
**Triggers:** vulnerability research, CVE, zero-day, PoC, patch diffing, KEV, disclosure, vuln analysis
**Tags:** offensive, research, exploitation
**Model tier:** opus
### web-attacker
**Role:** Web application penetration testing — SQLMap exploitation, XSS testing, SSRF, deserialization attacks, authentication bypass, file inclusion, and OWASP Top 10 systematic assessment.
**Triggers:** web application, pentest, SQL injection, XSS, SSRF, OWASP, web security, burp suite, SQLMap, deserialization
**Tags:** offensive, web, appsec, OWASP
**Model tier:** sonnet
### wireless-attacker
**Role:** Wireless network security — WPA/WPA3 handshake capture and cracking, PMKID attacks, WPS Pixie Dust, evil twin with hostapd/dnsmasq, Bluetooth LE testing with bettercap, and rogue AP detection.
**Triggers:** wireless, WiFi, WPA, WPA3, PMKID, WPS, Pixie Dust, evil twin, Bluetooth, BLE
**Tags:** offensive, wireless, WiFi, Bluetooth
**Model tier:** sonnet

## Available Commands

## /attack

description: Route an attack vector to the appropriate specialist agent — usage: /project:attack <target> <vector>
allowed-tools: Bash, Read, Write
---

Execute an attack against target using the specified vector: <arguments>

Parse <arguments>: the first word is TARGET, remaining words are the VECTOR.

1. **Scope Check**: Verify TARGET is in scope.txt. Stop if not found.

2. **Route to Agent based on VECTOR keyword**:

   | Vector Keyword | Agent to Invoke |
   |----------------|-----------------|
   | `web`, `http`, `webapp`, `sqli`, `xss`, `ssrf`, `lfi`, `jwt` | `web-attacker` |
   | `api`, `rest`, `graphql`, `grpc`, `bola`, `idor`, `swagger` | `api-attacker` |
   | `ad`, `active-directory`, `kerberoast`, `asrep`, `dcsync`, `bloodhound` | `active-directory` |
   | `network`, `arp`, `mitm`, `snmp`, `smbrelay`, `responder` | `network-ops` |
   | `wireless`, `wifi`, `wpa`, `wps`, `eap`, `pmkid` | `wireless-attacker` |
   | `cloud`, `aws`, `azure`, `gcp`, `s3`, `iam`, `metadata` | `cloud-attacker` |
   | `container`, `docker`, `kubernetes`, `k8s`, `pod`, `kubelet` | `container-attacker` |
   | `exploit`, `cve-`, `rce`, `shell`, `metasploit`, `msfconsole` | `exploit` |
   | `mobile`, `android`, `ios`, `apk`, `frida`, `adb` | `mobile-attacker` |
   | `osint`, `passive`, `recon`, `crt.sh`, `shodan`, `theHarvester` | `osint` |
   | `reverse`, `binary`, `re`, `ghidra`, `r2`, `gdb`, `rop` | `reverse-engineer` |
   | `malware`, `sample`, `yara`, `ioc`, `sandbox` | `malware-analyst` |
   | `password`, `hash`, `crack`, `hashcat`, `john` | `password-attacks` |
   | `phishing`, `social`, `gophish`, `evilginx`, `vishing` | `social-engineer` |
   | `crypto`, `tls`, `ssl`, `jwt-crack`, `padding` | `crypto-attacker` |
   | `iot`, `firmware`, `uart`, `mqtt`, `binwalk` | `iot-attacker` |
   | `c2`, `sliver`, `havoc`, `meterpreter`, `beacon`, `implant` | `c2-operator` |
   | `evasion`, `amsi`, `av-bypass`, `obfuscate` | `evasion` |

3. **Invoke Selected Agent**: Delegate to the matched agent with:
   - Target: `TARGET`
   - Vector: `VECTOR`
   - Evidence dir: `evidence/$(date +%Y%m%d)/TARGET/`
   - Context from `evidence/$(date +%Y%m%d)/TARGET/recon_summary.md` if it exists

4. **Log Attack**: After agent completes, append to `evidence/$(date +%Y%m%d)/TARGET/attack_log.md`:
   ```markdown
   | $(date -u +%Y-%m-%dT%H:%M:%SZ) | VECTOR | [agent used] | [outcome summary] |
   ```

5. **Output Summary**: Print findings discovered with severity if available.

If VECTOR does not match any keyword, output:
```
Unknown attack vector. Available vectors: web, api, ad, network, wireless, cloud, container, exploit, mobile, osint, reverse, malware, password, phishing, crypto, iot, c2, evasion
```

## /engage

description: Start a new engagement for a target — verifies scope, creates evidence directories, and launches recon agent
allowed-tools: Bash, Read, Write, Glob
---

Start a new penetration testing engagement for target: <arguments>

Follow these steps in order:

1. **Scope Verification**: Read `scope.txt` and verify that "<arguments>" is listed as an authorized target (exact IP, CIDR that includes the IP, or domain match). If NOT found in scope.txt, STOP immediately and output:
   ```
   ❌ SCOPE VIOLATION: "<arguments>" is not in scope.txt
   Add the target to scope.txt before proceeding.
   ```

2. **Create Evidence Directories**: Create the full directory structure:
   ```bash
   mkdir -p evidence/$(date +%Y%m%d)/<arguments>/{nmap,nuclei,web,creds,screenshots,post_ex,ad,cloud,wireless,mobile,api,re,osint,network,lateral,logs}
   ```

3. **Print Engagement Brief**:
   ```
   ═══════════════════════════════════════════════
   ENGAGEMENT START
   Target:    <arguments>
   Date:      $(date -u +%Y-%m-%dT%H:%M:%SZ)
   Operator:  $(whoami)
   Scope:     VERIFIED ✓
   Evidence:  evidence/$(date +%Y%m%d)/<arguments>/
   ═══════════════════════════════════════════════
   ```

4. **Delegate to Recon Agent**: Invoke the `recon` sub-agent with the target. The recon agent will:
   - Run nmap TCP full scan + service/version scan
   - Run nuclei CVE and exposure scans
   - Run httpx for web technology detection
   - Run feroxbuster for directory enumeration (if web ports found)
   - Run subfinder + amass if a domain target
   - Write `evidence/$(date +%Y%m%d)/<arguments>/recon_summary.md`

5. **Parse Recon Results**: After recon completes, read `recon_summary.md` and extract:
   - Open ports and services with versions
   - Web technologies detected
   - Discovered subdomains count

6. **Print Attack Vector Recommendations**: Based on the recon findings, output a prioritized list:
   ```
   ══ RECOMMENDED ATTACK VECTORS ══════════════════
   Priority 1: [e.g., "CVE-XXXX on Apache 2.4.49 (port 80)"]
   Priority 2: [e.g., "Default credentials on admin panel (/admin)"]
   Priority 3: [e.g., "SQL injection on login form"]
   Priority 4: [e.g., "Outdated OpenSSH — check for user enumeration"]
   ════════════════════════════════════════════════

   Ready. Run: /project:attack <arguments> <vector>
   ```

## /hunt

description: Run an ATT&CK-based threat hunt with a specific hypothesis
allowed-tools: Bash, Read, Write, Grep, Glob
---

Run threat hunt with hypothesis: <arguments>

Parse <arguments> for: hypothesis text, optional timeframe (e.g., "last 7 days"), affected systems.

1. **Hunt Setup**:
   ```
   ═══════════════════════════════════════════════
   THREAT HUNT START
   Hypothesis: <arguments>
   Timestamp:  $(date -u +%Y-%m-%dT%H:%M:%SZ)
   Log dir:    evidence/$(date +%Y%m%d)/hunt/
   ═══════════════════════════════════════════════
   ```
   Create: `mkdir -p evidence/$(date +%Y%m%d)/hunt/{hypotheses,queries,findings}`

2. **Map Hypothesis to ATT&CK**: Identify relevant TTPs from the hypothesis:
   - PowerShell / script execution → T1059.001, T1059.003
   - Lateral movement → T1021.001 (RDP), T1021.002 (SMB), T1021.006 (WinRM)
   - Credential dumping → T1003.001 (LSASS), T1003.003 (NTDS)
   - Persistence → T1547.001 (Run Keys), T1053.005 (Scheduled Task)
   - C2 beaconing → T1071.001 (HTTP/S), T1071.004 (DNS)
   - Data exfiltration → T1041 (exfil over C2), T1048 (exfil via protocol)

3. **Invoke `threat-hunter` Agent**: Delegate with:
   - Full hypothesis text from <arguments>
   - ATT&CK TTP mapping
   - Available log sources (auth.log, syslog, nginx access, Windows Event Logs, pcaps)
   - Timeframe context

4. **Query Execution**: The threat-hunter agent runs ATT&CK-aligned queries:
   - Linux auth log pattern matching
   - Web server log anomaly detection
   - Network traffic analysis (if pcaps available in evidence/)
   - Windows Event Log correlation (if accessible)

5. **Cross-Source Correlation**: Correlate findings across log sources:
   - Match IP addresses across auth, web, and network logs
   - Timeline reconstruction of suspicious activity
   - Confidence scoring per finding

6. **Write Hunt Report**: Output to `evidence/$(date +%Y%m%d)/hunt/hunt_report.md`:
   - Hypothesis tested
   - Queries run with results
   - Confirmed/likely/possible findings
   - IOCs extracted (IPs, domains, hashes)
   - Recommended follow-up hunts

7. **Print Summary**:
   ```
   ═══ HUNT RESULTS ═══════════════════
   Hypothesis: [text]
   ATT&CK TTPs: [T1234, T1235...]
   Findings Confirmed: X
   Findings Possible:  X
   IOCs Extracted:     X
   Report: evidence/$(date +%Y%m%d)/hunt/hunt_report.md
   ════════════════════════════════════
   ```

If no evidence/ files exist and no log access is configured, output:
```
⚠ No log sources found. Configure log paths or run recon first.
Available: /var/log/auth.log, /var/log/nginx/access.log, pcap files in evidence/
```

## /ir

description: Incident response workflow — triage, evidence collection, timeline, and IOC extraction
allowed-tools: Bash, Read, Write, Glob
---

Run incident response workflow for: <arguments>

Parse <arguments>: incident type is one of [compromise, ransomware, data-exfil, insider, malware, unknown]
Optional second argument: affected system IP or hostname.

1. **IR Kickoff**:
   ```
   ═══════════════════════════════════════════════════
   INCIDENT RESPONSE START
   Type:      <arguments>
   Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
   Operator:  $(whoami)
   ═══════════════════════════════════════════════════
   ```
   Create directories:
   ```bash
   mkdir -p evidence/$(date +%Y%m%d)/IR_$(date +%H%M%S)/{volatile,memory,logs,artifacts,iocs,timeline}
   IR_DIR=evidence/$(date +%Y%m%d)/IR_$(date +%H%M%S)
   ```

2. **Type-Specific Checklist**:

   **compromise**: Focus on initial access vector, persistence, lateral movement, credential theft
   **ransomware**: Focus on initial infection vector, encryption scope, shadow copy deletion, C2 communication
   **data-exfil**: Focus on data accessed, exfiltration method, destination IPs/domains
   **insider**: Focus on privileged access abuse, data downloads, account activity timeline
   **malware**: Focus on malware family identification, persistence, C2, affected hosts

3. **Invoke `dfir` Agent**: Delegate full triage with:
   - Incident type context
   - Volatile data capture first (processes, network, users)
   - Persistence mechanism hunting
   - Memory acquisition guidance (avml/LiME)
   - Log collection and analysis
   - Evidence directory: `$IR_DIR`

4. **System Snapshot**: Capture current state:
   ```bash
   # Snapshot current processes, network, users
   ps auxf > $IR_DIR/volatile/processes_$(date +%s).txt
   ss -tulnp > $IR_DIR/volatile/network_$(date +%s).txt
   who > $IR_DIR/volatile/users_$(date +%s).txt
   ```

5. **IOC Extraction**: Extract all IOCs to `$IR_DIR/iocs/`:
   - IP addresses from logs and network connections
   - Domain names from DNS and web logs
   - File hashes of suspicious executables
   - Registry keys (Windows), cron entries (Linux)
   - Malware indicators (mutex names, persistence paths)

6. **Threat Hunt Integration**: Invoke `threat-hunter` agent to find lateral movement:
   - Look for other systems the attacker may have reached
   - Correlate IOCs across available log sources

7. **Timeline Build**: Write UTC-ordered timeline to `$IR_DIR/timeline/timeline.md`:
   ```markdown
   | UTC Timestamp | Event | Source | ATT&CK TTP | Significance |
   |---------------|-------|--------|------------|--------------|
   ```

8. **Output Deliverables**:
   ```
   ═══ IR DELIVERABLES ════════════════════════════
   immediate_actions.md  — Containment steps
   timeline.md           — UTC event timeline
   iocs.txt              — Indicators of compromise
   evidence_manifest.txt — Chain of custody log
   ════════════════════════════════════════════════

   Next: Share IOCs with security team
   Next: Brief stakeholders using immediate_actions.md
   ```

9. **Write Evidence Manifest** to `$IR_DIR/evidence_manifest.txt`:
   ```
   Chain of Custody — <arguments> — $(date -u +%Y-%m-%dT%H:%M:%SZ)
   Operator: $(whoami)
   Files collected:
   [list all files with sha256 hashes]
   ```

## /pwned

description: Post-exploitation workflow after getting shell access — privesc, credential harvest, lateral movement
allowed-tools: Bash, Read, Write
---

Run full post-exploitation workflow on: <arguments>

Parse <arguments>: first word is TARGET, second word (optional) is SESSION_ID or access level (user/www-data/root/SYSTEM).

1. **Scope Check**: Verify TARGET is in scope.txt. Stop if not found.

2. **Document Current Access**:
   ```
   ═══════════════════════════════════════════
   POST-EXPLOITATION START
   Target:       TARGET
   Session ID:   SESSION_ID (if provided)
   Timestamp:    $(date -u +%Y-%m-%dT%H:%M:%SZ)
   ═══════════════════════════════════════════
   ```

3. **Invoke `post-ex` Agent** for automated privilege escalation:
   - Detect OS type (Linux vs Windows)
   - Run LinPEAS/WinPEAS automated enumeration
   - Check SUID binaries, cron, sudo, capabilities (Linux)
   - Check SeImpersonatePrivilege, unquoted paths, AlwaysInstallElevated (Windows)
   - Document escalation path with ATT&CK TTPs
   - Target evidence dir: `evidence/$(date +%Y%m%d)/TARGET/post_ex/`

4. **Credential Harvesting**: After any privilege escalation:
   - Linux: read /etc/shadow if root, find config files with credentials
   - Windows: invoke `impacket-secretsdump` locally, or mimikatz via Meterpreter
   - Pass any discovered hashes to `password-attacks` agent for cracking
   - Store: location reference only (NOT plaintext passwords)

5. **Domain Check**: If target appears domain-joined:
   - Check for domain membership: `realm list` (Linux) or `systeminfo | findstr /i domain` (Windows)
   - If domain-joined: invoke `active-directory` agent for full domain compromise path
   - Run BloodHound collection from compromised host

6. **Lateral Movement Mapping**:
   ```bash
   # SMB sweep for reachable hosts (from compromised machine)
   crackmapexec smb $INTERNAL_SUBNET/24 \
     -u $COMPROMISED_USER -H $NTLM_HASH \
     --continue-on-success 2>&1 | \
     tee evidence/$(date +%Y%m%d)/$TARGET/lateral/smb_sweep.txt
   ```

7. **Update Findings**: Append to `evidence/$(date +%Y%m%d)/TARGET/findings.md`:
   ```markdown
   ## Post-Exploitation — $(date -u +%Y-%m-%dT%H:%M:%SZ)

   | Step | Method | ATT&CK | Result |
   |------|--------|--------|--------|
   | Privesc | [technique] | [TTP] | [user → root/SYSTEM] |
   | Lateral | [technique] | T1021 | [hosts reached] |
   ```

8. **Print Summary**:
   ```
   ═══ POST-EX RESULTS ════════════════
   Privilege Level: [user → root/SYSTEM]
   Hosts Reached:   X
   Credentials:     X hashes (see evidence/)
   Domain Admin:    [YES/NO]
   ════════════════════════════════════
   ```

## /report

description: Generate a professional penetration test report from all evidence files
allowed-tools: Read, Write, Glob
---

Generate penetration test report named: <arguments>

1. **Setup**:
   ```
   ═══════════════════════════════════════════
   REPORT GENERATION
   Name:    <arguments>
   Output:  reports/<arguments>.md
   Source:  evidence/ directory
   ═══════════════════════════════════════════
   ```
   Ensure `mkdir -p reports/` exists.

2. **Evidence Discovery**: Find all findings files:
   - Glob `evidence/**/*findings*.md`
   - Glob `evidence/**/*_report.md`
   - Glob `evidence/**/exploitation.md`
   - Glob `evidence/**/post_ex.md`
   - Glob `evidence/**/ad_findings.md`
   - Glob `evidence/**/web_findings.md`
   - Glob `evidence/**/api_findings.md`
   - Glob `evidence/**/network_findings.md`

3. **Invoke `report-writer` Agent**: Delegate with:
   - List of all evidence files found
   - Engagement name: <arguments>
   - Read scope.txt for scope section
   - Consolidate all findings into the full report template
   - Sort findings by CVSS score (critical first)
   - Deduplicate overlapping findings
   - Write to `reports/<arguments>.md`

4. **Quality Check**: After writing:
   - Count findings by severity
   - Verify all CRITICAL findings have CVSS vectors
   - Verify all findings have remediation steps
   - Check for any [PLACEHOLDER] text left unreplaced
   - Verify no plaintext credentials in report (search for common patterns)

5. **Print Report Summary**:
   ```
   ═══ REPORT COMPLETE ════════════════════════════
   File:       reports/<arguments>.md
   Word count: $(wc -w reports/<arguments>.md | awk '{print $1}')
   Pages est.: ~$(wc -w reports/<arguments>.md | awk '{print int($1/300)}')

   Findings by severity:
     Critical: $(grep -c "| CRITICAL |" reports/<arguments>.md || echo 0)
     High:     $(grep -c "| HIGH |" reports/<arguments>.md || echo 0)
     Medium:   $(grep -c "| MEDIUM |" reports/<arguments>.md || echo 0)
     Low:      $(grep -c "| LOW |" reports/<arguments>.md || echo 0)
     Info:     $(grep -c "| INFO |" reports/<arguments>.md || echo 0)

   Top recommendations:
   [print first 3 critical/high finding titles]

   Report ready: reports/<arguments>.md
   ════════════════════════════════════════════════
   ```

If no evidence files are found, output:
```
⚠ No findings files found in evidence/
Run /project:engage <target> first to collect evidence.
```


## Rules

## Evidence

paths:
  - "evidence/**"
---

## Evidence Handling Rules

All files written to `evidence/` must adhere to these mandatory standards.

### Required Fields in Every findings.md Entry

Every finding documented in any `findings.md`, `*_report.md`, or structured findings file within `evidence/` MUST include:

1. **target** — IP address, FQDN, or URL of the affected system
2. **date** — UTC ISO 8601 timestamp (e.g., `2025-03-23T14:32:00Z`)
3. **ATT&CK TTP** — At least one MITRE ATT&CK technique ID (e.g., `T1190`, `T1003.001`)
4. **severity** — One of: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`
5. **proof_path** — Relative path to supporting evidence file (screenshot, output, PCAP)
6. **CVE** — Include if a published CVE applies; omit field entirely if not applicable

### Credential Handling (MANDATORY)

**NEVER write raw credential values (plaintext passwords) to any evidence file.**

Store ONLY:
- Hash value + hash type + source location
  Example: `$6$rounds=5000$... (sha512crypt) — found in /etc/shadow on 10.10.10.5`
- Reference path to the loot/ directory where hashes are stored
  Example: `see loot/20250323/ntlm_hashes.txt`

**Never log:**
- Plaintext passwords
- Private keys in full
- Session tokens in full (truncate to first 8 chars + `...`)
- AWS/GCP/Azure secret keys

### Evidence Directory Structure

```
evidence/
└── YYYYMMDD/
    └── TARGET/
        ├── findings.md          # Structured findings (required)
        ├── nmap/                # Network scan outputs
        ├── web/                 # Web application testing
        ├── creds/               # Hash references ONLY (no plaintext)
        ├── screenshots/         # Visual evidence
        ├── exploitation.md      # Exploitation documentation
        └── post_ex/             # Post-exploitation artifacts
```

### Chain of Custody

When creating or modifying evidence files, record:
- Operator (whoami output or operator handle)
- UTC timestamp of collection
- Tool used and command executed
- SHA256 hash of collected artifacts (where feasible)

### Prohibited in Evidence Files

- Full private keys (RSA, EC, SSH) — store reference path only
- PII beyond what is necessary to demonstrate impact (mask SSNs, credit cards after 4 digits)
- Credentials belonging to real individuals outside the engagement scope
- Evidence from systems NOT listed in scope.txt

## Exploits

paths:
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
#!/usr/bin/env python3
"""
Title:       [Vulnerability Title]
CVE:         CVE-XXXX-XXXXX (or "N/A")
EDB-ID:      [EDB number] (or "N/A")
Author:      [Operator handle]
Date:        [UTC date]
Target:      [Affected software/version]

SCOPE WARNING: This script must only be run against targets listed in scope.txt.
Unauthorized use is illegal. The operator assumes full legal responsibility.

Usage: python3 exploit.py --target <IP> --lhost <LHOST> --lport <LPORT>
"""
```

### Mandatory scope_check() Function

Every exploit script MUST call `scope_check()` before any network activity:

```python
import os, sys, ipaddress

def scope_check(target: str) -> None:
    """Verify target is in scope.txt before proceeding."""
    scope_file = os.environ.get('SCOPE_FILE', './scope.txt')
    in_scope = False
    try:
        with open(scope_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                try:
                    network = ipaddress.ip_network(line, strict=False)
                    if ipaddress.ip_address(target) in network:
                        in_scope = True
                        break
                except ValueError:
                    if target.lower() == line.lower() or target.lower().endswith('.' + line.lower()):
                        in_scope = True
                        break
    except FileNotFoundError:
        print(f"[!] scope.txt not found at {scope_file} — BLOCKING execution")
        sys.exit(1)
    if not in_scope:
        print(f"[!] SCOPE VIOLATION: {target} is not in {scope_file}")
        print("[!] Add target to scope.txt before running.")
        sys.exit(1)
    print(f"[+] Scope check passed: {target} is authorized")
```

### Mandatory evidence_dir() Function

Output must go to the evidence directory, never to /tmp or cwd without logging:

```python
from datetime import datetime, timezone
from pathlib import Path

def evidence_dir(target: str) -> Path:
    """Return and create the evidence directory for this target."""
    base = os.environ.get('EVIDENCE_DIR', './evidence')
    date = datetime.now(timezone.utc).strftime('%Y%m%d')
    path = Path(base) / date / target.replace('/', '_').replace(':', '_')
    path.mkdir(parents=True, exist_ok=True)
    return path
```

### Environment Variables Only for Secrets

LHOST, LPORT, TARGET, and credentials MUST come from environment variables or argparse — never hardcoded:

```python
import argparse, os

parser = argparse.ArgumentParser()
parser.add_argument('--target', required=True)
parser.add_argument('--lhost', default=os.environ.get('LHOST', ''))
parser.add_argument('--lport', type=int, default=int(os.environ.get('LPORT', 4444)))
args = parser.parse_args()

# Then immediately:
scope_check(args.target)
outdir = evidence_dir(args.target)
```

### Prohibited Patterns

The following patterns are NOT permitted in any script in this workspace:

```
# BLOCKED: Hardcoded targets outside scope verification
requests.get("http://192.168.1.1")  # without prior scope_check()

# BLOCKED: Writing to /tmp without evidence logging
open('/tmp/output.txt', 'w')

# BLOCKED: Hardcoded credentials in code
password = "admin123"
api_key = "AKIAIOSFODNN7EXAMPLE"

# BLOCKED: Disabling TLS verification permanently
requests.get(url, verify=False)  # only allow with explicit justification comment

# BLOCKED: Mass targeting loops without scope check per target
for ip in range(1, 255):
    exploit(f"10.10.10.{ip}")  # must scope_check() each IP
```

### Script Execution Pattern

All exploit scripts must follow this pattern:

```python
if __name__ == '__main__':
    # 1. Parse arguments
    # 2. scope_check(target) — FIRST network action
    # 3. outdir = evidence_dir(target)
    # 4. Log start: print UTC timestamp + command
    # 5. Execute exploit
    # 6. Write output to outdir/exploit_output.txt
    # 7. Print summary with evidence path
```

## Loot

paths:
  - "loot/**"
---

## Loot Directory Rules

Files in `loot/` contain sensitive captured material. Handle with extreme care.

### Storage Format (Hashes Only)

Store ONLY the hash value, hash type, and source location. NEVER store plaintext passwords.

**Correct format:**
```
# NTLM Hashes — 10.10.10.5 — 2025-03-23T14:30:00Z
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
john.doe:1108:aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c:::

# Source: impacket-secretsdump on DC01.corp.local
# Cracked: see loot/20250323/cracked_refs.md (reference only, no plaintext)
```

**Cracked reference format** (`cracked_refs.md`):
```
Hash: 31d6cfe0d16ae931b73c59d7e0c089c0 (NTLM)
User: Administrator
Status: CRACKED
Strength: [REDACTED — stored in client-facing secure channel only]
Source: DC01.corp.local
Date: 2025-03-23T14:30:00Z
```

### Prohibited in loot/

- Plaintext passwords in any file
- Full private key material (store fingerprint + source path only)
- PII (SSNs, credit card numbers, health records) beyond what is necessary as a proof of impact
- Real user data exfiltrated from production systems (capture proof of access, not the data itself)

### Encryption Reminder

`loot/` is in `.gitignore` and will NOT be committed to version control. However:

- Before archiving or transferring loot files, encrypt with GPG:
  ```bash
  gpg --symmetric --cipher-algo AES256 loot/20250323/
  # or
  gpg --encrypt --recipient $RECIPIENT_KEY_ID loot/20250323/ntlm_hashes.txt
  ```
- Delete unencrypted copies after encryption is verified
- Transfer only over encrypted channels (SFTP, HTTPS, Signal)

### Directory Structure

```
loot/
└── YYYYMMDD/
    ├── ntlm_hashes.txt         # NTLM hash format only
    ├── kerberos_hashes.txt     # Kerberoast/ASREP hashes
    ├── net_hashes.txt          # NetNTLMv2 captures
    ├── ssh_keys/               # Private key FINGERPRINTS only
    │   └── fingerprints.txt    # ssh-keygen -lf
    ├── certificates/           # PEM certs (public data only)
    ├── cracked_refs.md         # Cracked hash references (no plaintext)
    └── README.md               # Chain of custody log
```

### Chain of Custody Log (Required)

Each loot/ session directory must contain a `README.md`:

```markdown
# Chain of Custody — [ENGAGEMENT NAME]

| UTC Timestamp | File | Source | Tool | Operator | SHA256 |
|---|---|---|---|---|---|
| 2025-03-23T14:30:00Z | ntlm_hashes.txt | DC01.corp.local | impacket-secretsdump | [operator] | [hash] |
```

Generate SHA256 hashes of loot files:
```bash
sha256sum loot/20250323/* >> loot/20250323/README.md
```

### Retention

Loot files are project-specific and must be destroyed per the engagement SOW.
Do not retain loot beyond the agreed engagement close date.

## Reports

paths:
  - "reports/**"
---

## Report Writing Rules

These rules apply to all files written inside the `reports/` directory.

### Tone and Language

- Use professional, objective third-person language throughout
- Avoid emotional language, hyperbole, or client-blaming language
- State facts: "The tester identified..." not "The client left wide open..."
- Findings describe vulnerability behavior, not attacker intent

### Mandatory Requirements per Finding

Every finding in a report MUST have all of the following:

1. **CVSS 3.1 Score** with full vector string in format `CVSS:3.1/AV:.../...`
   - Example: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (9.8 Critical)`
   - Do NOT use CVSS 2.0 or estimate scores without a vector
2. **Remediation steps** that are specific and actionable
   - Bad: "Fix the SQL injection vulnerability"
   - Good: "Implement parameterized queries for all database interactions; replace line 47 in `db.py` where user input is concatenated into SQL strings"
3. **Evidence reference** — relative path to supporting evidence file
4. **ATT&CK TTP mapping** — at least one technique ID
5. **CWE reference** — at least one CWE-XXXX identifier
6. **References section** — vendor advisory URL, CVE link, or OWASP/NIST reference

### Credential Redaction (MANDATORY)

Before writing any report file, all credential values MUST be redacted:

- Passwords → `[REDACTED]`
- API keys → `[REDACTED-API-KEY]`
- Password hashes → `[HASH-REDACTED]` (include hash type only: e.g., `NTLM hash [REDACTED]`)
- Private keys → `[PRIVATE-KEY-REDACTED]`
- Session tokens → `[TOKEN-REDACTED]`
- Connection strings with passwords → redact password field only

Pattern check before finalizing:
```bash
grep -iE "password\s*=\s*['\"][^'\"]{4,}" reports/$NAME.md && echo "CREDENTIAL LEAK"
grep -iE "Bearer [A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+" reports/$NAME.md && echo "TOKEN LEAK"
grep -oE "[0-9a-f]{32}:[0-9a-f]{32}" reports/$NAME.md && echo "NTLM HASH LEAK"
```

### No Placeholder Text

Reports must not contain unfilled placeholder text. Before saving:
- Search for `[PLACEHOLDER]`, `TODO`, `FIXME`, `INSERT`, `TBD` in report content
- All finding titles must be specific (not "Vulnerability in Application")
- All IP addresses and URLs in findings must be real (from evidence/), not example.com

### Report File Naming

```
reports/[ENGAGEMENT-NAME]-v[VERSION]-[DATE].md
reports/ACME-External-Pentest-v1.0-20250323.md
reports/ACME-External-Pentest-v1.1-FINAL.md
```

### Report Structure (Required Sections)

```
1. Cover Page (client, engagement type, dates, classification)
2. Table of Contents
3. Executive Summary (1 page, non-technical audience)
4. Scope and Methodology
5. Findings Summary Table (sorted by CVSS score, Critical first)
6. Detailed Findings (one section per finding)
7. 30/60/90 Day Remediation Roadmap
8. Appendices:
   A. Scope Definition
   B. Tools Used
   C. Evidence File Index
   D. Raw Output Paths (reference only, not embedded)
```

### Severity Ordering

Findings MUST be sorted with highest CVSS score first within each severity tier:
`CRITICAL` → `HIGH` → `MEDIUM` → `LOW` → `INFO`


## OPSEC Defaults
- Route external traffic through `proxychains` where possible
- Nmap timing: `-T3` maximum unless explicitly authorized
- No PII exfiltration — reference paths only
- Minimize footprint: staged payloads only

## Evidence Structure
```
evidence/YYYYMMDD/TARGET/{nmap,nuclei,web,creds,screenshots}/
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
