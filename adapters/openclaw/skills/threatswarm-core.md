# ThreatSwarm Pentesting Framework

Comprehensive multi-agent penetration testing framework with 32 specialist agents.

## Description
Platform-agnostic pentesting framework for AI coding agents. Use when working on penetration testing, vulnerability assessment, red team operations, or security auditing tasks.

## Agents
- **active-directory** (offensive, windows): Active Directory exploitation specialist — BloodHound attack path analysis, Kerberoasting, AS-REP ro
- **api-attacker** (offensive, web): API security testing — REST/GraphQL/SOAP testing, IDOR, BOLA/BFLA, broken authentication, rate limit
- **blue-team** (defensive, detection): Defensive security — detection rule creation (Sigma), CIS hardening, log configuration, incident res
- **c2-operator** (offensive, red-team): Command and Control infrastructure — Sliver framework, Havoc C2, Cobalt Strike profile analysis, red
- **cloud-attacker** (offensive, cloud): Cloud penetration testing — AWS, Azure, GCP enumeration, Pacu automation, S3 bucket exploitation, IA
- **cloud-postex** (offensive, cloud): Cloud post-exploitation — IAM persistence, data exfiltration from cloud storage, cross-account trust
- **compliance-scanner** (defensive, compliance): Compliance assessment — CIS benchmarks, PCI-DSS, NIST CSF, SOC 2, ISO 27001 gap analysis, automated 
- **container-attacker** (offensive, containers): Container and Kubernetes security — Docker escape techniques, K8s RBAC abuse, cluster enumeration, c
- **crypto-attacker** (offensive, web): Cryptographic security assessment — SSL/TLS analysis, JWT algorithm confusion, padding oracle attack
- **dfir** (defensive, forensics): Digital Forensics and Incident Response — memory forensics with Volatility3, disk forensics, evidenc
- **evasion** (offensive, red-team): Evasion techniques — AMSI bypass, ETW patching, process injection, living-off-the-land binaries (LOL
- **exploit** (offensive, exploitation): Vulnerability exploitation — Metasploit framework, manual exploit development, RCE/SQLi/XSS exploita
- **iot-attacker** (offensive, IoT): IoT and OT security assessment — firmware analysis with Binwalk/Ghidra, emulation with QEMU/Firmadyn
- **log-analyst** (defensive, detection): Security log analysis — Splunk queries, Linux audit logs, web server intrusion analysis, Windows eve
- **malware-analyst** (defensive, malware): Malware analysis — Linux ELF and Windows PE analysis, YARA rule creation, sandbox execution, behavio
- **mobile-attacker** (offensive, mobile): Mobile application security — Android APK analysis (apktool/jadx), iOS IPA analysis, Frida instrumen
- **network-ops** (offensive, network): Network-level attacks — ARP spoofing, man-in-the-middle interception, SMB relay, LLMNR/NBT-NS poison
- **osint** (recon, OSINT): Open source intelligence gathering — passive reconnaissance, SpiderFoot automation, DNS enumeration,
- **password-attacks** (offensive, credentials): Password and credential attacks — hash cracking with hashcat, credential stuffing, password spraying
- **post-ex** (offensive, post-exploitation): Post-exploitation — Linux/Windows privilege escalation, credential harvesting with LaZagne, lateral 
- **purple-team** (collaborative, offensive): Purple team operations — MITRE ATT&CK mapping, detection gap identification, offensive technique exe
- **recon** (recon, offensive): External and internal reconnaissance — advanced Nmap scanning, subdomain enumeration with Subfinder/
- **red-infra** (offensive, red-team): Red team infrastructure — C2 deployment, redirector chains, domain registration with privacy, phishi
- **report-writer** (reporting, documentation): Security report generation — executive summaries, technical findings, threat intelligence reports, i
- **reverse-engineer** (offensive, reverse-engineering): Binary reverse engineering — Ghidra analysis, .NET decompilation with dnSpy, binary exploitation ana
- **segmentation-tester** (offensive, network): Network segmentation testing — cross-segment access validation, firewall rule testing, VLAN hopping 
- **social-engineer** (offensive, social-engineering): Social engineering — phishing campaign simulation with GoPhish, spear phishing, pretexting, vishing,
- **threat-hunter** (defensive, detection): Threat hunting — hypothesis-driven hunts, Cobalt Strike beacon detection, C2 beaconing analysis, per
- **vuln-management** (defensive, compliance): Vulnerability management — Nuclei template scanning, authenticated scanning, Nessus/Tenable integrat
- **vuln-researcher** (offensive, research): Vulnerability research — CVE analysis, KEV catalog prioritization, PoC development, patch diffing, z
- **web-attacker** (offensive, web): Web application penetration testing — SQLMap exploitation, XSS testing, SSRF, deserialization attack
- **wireless-attacker** (offensive, wireless): Wireless network security — WPA/WPA3 handshake capture and cracking, PMKID attacks, WPS Pixie Dust, 

## Scope Enforcement
**CRITICAL**: Before ANY network command, verify target is in scope.txt.
Use the scope_check.py hook: `python3 core/hooks/scope_check.py --check "<command>"`
Exit code 0 = pass, 2 = scope violation.

## Commands
- `/attack`: description: Route an attack vector to the appropriate specialist agent — usage: /project:attack <target> <vector>
- `/engage`: description: Start a new engagement for a target — verifies scope, creates evidence directories, and launches recon agent
- `/hunt`: description: Run an ATT&CK-based threat hunt with a specific hypothesis
- `/ir`: description: Incident response workflow — triage, evidence collection, timeline, and IOC extraction
- `/pwned`: description: Post-exploitation workflow after getting shell access — privesc, credential harvest, lateral movement
- `/report`: description: Generate a professional penetration test report from all evidence files

## Rules
### Evidence
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

### Exploits
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

### Loot
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

### Reports
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
