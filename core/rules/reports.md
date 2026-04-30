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
