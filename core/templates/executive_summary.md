# Executive Summary — Penetration Test Report

**Client:** [CLIENT_NAME]  
**Engagement ID:** [ENGAGEMENT_ID]  
**Report Date:** [DATE]  
**Classification:** [CONFIDENTIAL / RESTRICTED]  
**Prepared by:** [TESTER_NAME / TEAM]

---

## 1. Engagement Overview

| Field | Detail |
|-------|--------|
| Engagement Type | [Black Box / Gray Box / White Box] |
| Start Date | [START_DATE] |
| End Date | [END_DATE] |
| Test Lead | [LEAD_NAME] |
| Scope Summary | [IP ranges / applications / facilities tested] |
| Methodology | [PTES / OSSTMM / OWASP / NIST SP 800-115 / Custom] |

### Engagement Objectives

- [Objective 1: e.g., Identify exploitable vulnerabilities in the external attack surface]
- [Objective 2: e.g., Test internal network segmentation and AD security posture]
- [Objective 3: e.g., Validate security controls against a realistic threat scenario]

### Out of Scope

- [Exclusion 1: e.g., Denial of Service testing]
- [Exclusion 2: e.g., Social engineering against employees]

---

## 2. Scope Summary

### Networks

| Range | Type | Hosts Tested | Findings |
|-------|------|-------------|----------|
| [CIDR/IP] | [External / Internal / DMZ] | [N] | [N critical, N high, N medium, N low] |
| [CIDR/IP] | [External / Internal / DMZ] | [N] | [N critical, N high, N medium, N low] |

### Applications

| Application | URL / Endpoint | Type | Findings |
|-------------|----------------|------|----------|
| [App Name] | [URL] | [Web App / API / Mobile] | [N critical, N high, N medium, N low] |

---

## 3. Risk Rating

### Overall Risk Score: [CRITICAL / HIGH / MEDIUM / LOW]

> [1-2 sentence executive-level assessment of the organization's security posture based on testing results. Example: "The engagement identified multiple critical vulnerabilities that could allow an unauthenticated attacker to gain domain administrator privileges and access sensitive customer data. Immediate remediation is required."]

### Findings by Severity

| Severity | Count | Percentage |
|----------|-------|------------|
| CRITICAL | [N] | [%] |
| HIGH | [N] | [%] |
| MEDIUM | [N] | [%] |
| LOW | [N] | [%] |
| INFO | [N] | [%] |
| **Total** | **[N]** | **100%** |

### Risk Distribution

```
CRITICAL ████████████████ N findings
HIGH     ██████████       N findings
MEDIUM   ██████           N findings
LOW      ███              N findings
INFO     █                N findings
```

---

## 4. Key Findings Summary

| ID | Finding | Severity | CVSS | ATT&CK | Status |
|----|---------|----------|------|--------|--------|
| TS-0001 | [Finding title] | CRITICAL | 9.8 | T1210 | Open |
| TS-0002 | [Finding title] | HIGH | 8.1 | T1190 | Open |
| TS-0003 | [Finding title] | HIGH | 7.5 | T1078 | Remediated |
| TS-0004 | [Finding title] | MEDIUM | 6.5 | T1059 | Open |
| TS-0005 | [Finding title] | LOW | 3.1 | T1046 | Accepted Risk |

### Top 3 Critical Risks

1. **[Finding Title]** — [1-2 sentence description of the business impact. Example: "An unpatched Domain Controller allows remote code execution as SYSTEM, giving an attacker full domain compromise without any authentication."]
2. **[Finding Title]** — [Impact description]
3. **[Finding Title]** — [Impact description]

---

## 5. Strategic Recommendations

### Immediate Actions (0–48 hours)

- [ ] [Recommendation with clear owner and deadline]
- [ ] [Recommendation]

### Short-Term (1–4 weeks)

- [ ] [Recommendation]
- [ ] [Recommendation]

### Medium-Term (1–3 months)

- [ ] [Recommendation]
- [ ] [Recommendation]

### Long-Term / Strategic

- [ ] [Recommendation]
- [ ] [Recommendation]

---

## 6. Positive Observations

- [Security control that worked well]
- [Security control that worked well]

---

## 7. Conclusion

[2-3 sentence wrap-up summarizing the overall security posture, the most critical risk to address, and the recommended next steps. Should be actionable for C-suite and board-level readers.]

---

*This report is confidential and intended solely for [CLIENT_NAME]. Distribution without written consent from [TESTER_ORG] is prohibited.*
