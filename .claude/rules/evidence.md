---
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
