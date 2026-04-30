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
