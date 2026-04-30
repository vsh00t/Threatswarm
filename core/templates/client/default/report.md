# Penetration Test Report

**Client:** [CLIENT_NAME]  
**Engagement ID:** [ENGAGEMENT_ID]  
**Report Date:** [DATE]  
**Classification:** [CONFIDENTIAL]  
**Prepared by:** [TESTER_NAME / TEAM]  
**Version:** [1.0 / 1.1 / Final]

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [DATE] | [Author] | Initial release |
| 1.1 | [DATE] | [Author] | Re-test results added |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Methodology](#2-methodology)
3. [Scope](#3-scope)
4. [Findings](#4-findings)
5. [Detailed Technical Findings](#5-detailed-technical-findings)
6. [Remediation Roadmap](#6-remediation-roadmap)
7. [Appendices](#7-appendices)

---

<!-- ============================================================ -->
<!-- SECTION 1: EXECUTIVE SUMMARY                                  -->
<!-- ============================================================ -->

## 1. Executive Summary

> [Insert executive summary content from executive_summary.md template here.
> This section is designed to be extracted standalone for non-technical stakeholders.]

- Engagement Overview
- Scope Summary  
- Overall Risk Rating
- Key Findings Summary (table)
- Strategic Recommendations
- Positive Observations
- Conclusion

---

<!-- ============================================================ -->
<!-- SECTION 2: METHODOLOGY                                        -->
<!-- ============================================================ -->

## 2. Methodology

### 2.1 Standards and Frameworks

- [PTES — Penetration Testing Execution Standard](https://www.pentest-standard.org/)
- [OWASP Testing Guide v4](https://owasp.org/www-project-web-security-testing-guide/)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [CVSS v3.1](https://www.first.org/cvss/v3.1/specification-document)

### 2.2 Testing Phases

| Phase | Activities | Tools |
|-------|-----------|-------|
| Reconnaissance | Passive/active enumeration, OSINT | [nmap, subfinder, amass, theHarvester] |
| Vulnerability Assessment | Automated scanning, manual verification | [Nessus, Burp Suite, nuclei] |
| Exploitation | Proof of concept development, privilege escalation | [Metasploit, custom scripts, manual] |
| Post-Exploitation | Lateral movement, data access, persistence | [BloodHound, Impacket, CrackMapExec] |
| Reporting | Documentation, evidence packaging, remediation | ThreatSwarm |

### 2.3 Rules of Engagement

| Rule | Detail |
|------|--------|
| Testing Window | [START] — [END], [HOURS] |
| Notification | [No notification / 24h advance / SOC notified] |
| DoS Testing | [Not authorized / Authorized with limits] |
| Social Engineering | [In scope / Out of scope] |
| Data Handling | [No exfiltration / Sampling only / Full access] |
| Debrief | [Date/Time of outbrief session] |

---

<!-- ============================================================ -->
<!-- SECTION 3: SCOPE                                              -->
<!-- ============================================================ -->

## 3. Scope

### 3.1 In Scope

| Target | Type | Details |
|--------|------|---------|
| [CIDR / IP] | Network | [Description] |
| [FQDN / URL] | Application | [Description] |
| [Facility / Location] | Physical | [Description] |

### 3.2 Out of Scope

- [Target/Activity]

### 3.3 Assumptions and Limitations

- [Assumption or constraint that may have affected test results]

---

<!-- ============================================================ -->
<!-- SECTION 4: FINDINGS SUMMARY                                   -->
<!-- ============================================================ -->

## 4. Findings

### 4.1 Findings Overview

| Severity | Count |
|----------|-------|
| CRITICAL | [N] |
| HIGH | [N] |
| MEDIUM | [N] |
| LOW | [N] |
| INFO | [N] |
| **Total** | **[N]** |

### 4.2 Findings Summary Table

| ID | Title | Severity | CVSS | ATT&CK | Asset | Status |
|----|-------|----------|------|--------|-------|--------|
| TS-0001 | [Title] | CRITICAL | 9.8 | T1210 | [Asset] | Open |
| TS-0002 | [Title] | HIGH | 8.1 | T1190 | [Asset] | Open |
| [Add all findings] | | | | | | |

---

<!-- ============================================================ -->
<!-- SECTION 5: DETAILED TECHNICAL FINDINGS                        -->
<!-- ============================================================ -->

## 5. Detailed Technical Findings

> [Insert one technical_finding.md template section per finding.
> Order by severity descending: CRITICAL → HIGH → MEDIUM → LOW → INFO.]

### 5.1 TS-0001 — [Finding Title]

[Full technical finding using the technical_finding.md template structure:
Description, Impact, Proof of Concept, Affected Assets, Remediation, References]

---

### 5.2 TS-0002 — [Finding Title]

[...]

---

<!-- ============================================================ -->
<!-- SECTION 6: REMEDIATION ROADMAP                                -->
<!-- ============================================================ -->

## 6. Remediation Roadmap

> [Insert remediation roadmap from remediation_roadmap.md template here.
> Priority matrix, dependencies, resource estimates, timeline, re-test plan.]

---

<!-- ============================================================ -->
<!-- SECTION 7: APPENDICES                                         -->
<!-- ============================================================ -->

## 7. Appendices

### Appendix A: Evidence Package

Evidence files are provided separately:
- `evidence/screenshots/` — Screenshots with SHA-256 hashes
- `evidence/pcap/` — Network captures
- `evidence/output/` — Tool output and command logs
- `evidence_manifest.json` — Chain of custody manifest

### Appendix B: Tool Versions

| Tool | Version | Purpose |
|------|---------|---------|
| nmap | [v] | Network scanning |
| [Tool] | [v] | [Purpose] |

### Appendix C: Raw Scan Data

Raw output files available upon request in the evidence package.

### Appendix D: Glossary

| Term | Definition |
|------|-----------|
| CVSS | Common Vulnerability Scoring System |
| ATT&CK | Adversarial Tactics, Techniques, and Common Knowledge (MITRE) |
| [Term] | [Definition] |

---

*End of Report*

*This report is confidential and intended solely for [CLIENT_NAME]. Unauthorized distribution is prohibited.*
*© [YEAR] [TESTER_ORG] — All rights reserved.*
