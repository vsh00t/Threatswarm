---
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
