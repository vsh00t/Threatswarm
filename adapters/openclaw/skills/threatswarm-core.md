# ThreatSwarm Pentesting Framework

Comprehensive multi-agent penetration testing framework with 27 specialist agents.

## Description
Platform-agnostic pentesting framework for AI coding agents. Use when working on penetration testing, vulnerability assessment, red team operations, or security auditing tasks.

## Agents
- **active-directory** (offensive, ad): Active Directory and Windows domain attack specialist. Use for Kerberoasting, AS-REP roasting, DCSyn
- **api-attacker** (offensive, api): API security testing specialist for REST, GraphQL, gRPC, and WebSocket APIs. Handles BOLA/IDOR, mass
- **blue-team** (defensive, hardening): Defensive security and hardening specialist. Creates detection rules, hardens Linux/Windows systems,
- **c2-operator** (offensive, c2): Command and control infrastructure specialist for authorized red team operations. Handles Sliver C2 
- **cloud-attacker** (offensive, cloud): Cloud penetration testing specialist for AWS, Azure, and GCP. Handles IAM enumeration, privilege esc
- **compliance-scanner** (compliance, defensive): Compliance and security standards assessment specialist. Handles CIS benchmarks, PCI-DSS controls, N
- **container-attacker** (offensive, containers): Container and Kubernetes security specialist. Handles Docker escape techniques, Kubernetes RBAC abus
- **crypto-attacker** (offensive, crypto): Cryptography and TLS security specialist. Handles TLS configuration auditing, JWT algorithm confusio
- **dfir** (defensive, forensics): Digital forensics and incident response specialist. Handles triage, memory acquisition with AVML/LiM
- **evasion** (offensive, evasion): Antivirus and EDR evasion specialist for authorized red team engagements. Handles AMSI bypass, paylo
- **exploit** (offensive, exploitation): Exploitation specialist for gaining initial access. Use when exploiting CVEs, running Metasploit mod
- **iot-attacker** (offensive, iot): IoT and embedded systems security specialist. Handles firmware extraction and analysis, hardcoded cr
- **log-analyst** (defensive, logging): Security log analysis specialist. Parses and correlates auth.log, nginx/apache access logs, Windows 
- **malware-analyst** (malware, analysis): Malware analysis specialist for static and dynamic analysis. Handles PE/ELF/APK binary triage, behav
- **mobile-attacker** (offensive, mobile): Mobile application security specialist for Android and iOS. Handles APK decompilation, static/dynami
- **network-ops** (offensive, network): Network penetration testing specialist for ARP attacks, MitM, packet capture, SNMP enumeration, SMB 
- **osint** (recon, osint): Open source intelligence specialist for passive reconnaissance. Handles domain intelligence, certifi
- **password-attacks** (offensive, credential-access): Password cracking and credential attack specialist. Use when working with password hashes, hash crac
- **post-ex** (offensive, post-exploitation): Post-exploitation specialist for privilege escalation, lateral movement, persistence, and credential
- **recon** (recon, offensive): Reconnaissance and enumeration specialist. Use when scanning, enumerating ports, fingerprinting serv
- **report-writer** (reporting, documentation): Penetration test report writing specialist. Consolidates evidence from all evidence/ directories int
- **reverse-engineer** (offensive, malware): Binary reverse engineering and exploit development specialist. Handles static analysis with Ghidra/R
- **social-engineer** (offensive, social-engineering): Social engineering and phishing simulation specialist. Handles GoPhish campaign setup, spear-phishin
- **threat-hunter** (defensive, threat-hunting): Proactive threat hunting specialist using ATT&CK-based hypotheses. Hunts for lateral movement, persi
- **vuln-researcher** (research, vulnerability): Vulnerability research and CVE analysis specialist. Handles NVD API queries, searchsploit cross-refe
- **web-attacker** (offensive, web): Web application penetration testing — SQL injection, XSS, SSRF, LFI, IDOR, JWT attacks, GraphQL, API
- **wireless-attacker** (offensive, wireless): Wireless network penetration testing specialist. Handles WPA2/WPA3 capture and cracking, PMKID attac

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
