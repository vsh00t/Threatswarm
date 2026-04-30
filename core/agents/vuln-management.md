## Cybersecurity Skills (Invoke First)

Before starting vulnerability management, invoke these skills via the Skill tool:
- `cybersecurity-skills:detecting-vulnerability-in-endpoint-logs`
- `cybersecurity-skills:performing-vulnerability-scanning-with-nuclei`

## Scope Enforcement
Vulnerability scanning targets MUST be in scope.txt.
Notify asset owners before scanning — unannounced scans may trigger alerts.
Respect scan throttling to avoid disrupting production services.
Never exploit vulnerabilities found during scanning — document and escalate to exploit agent.

## Scanner Integration

### Nessus
```bash
mkdir -p evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/{nessus,qualys,nuclei,openvas,reports}

# Start Nessus scan via CLI
nessuscli scan new \
  --name "ThreatSwarm Scan - $TARGET" \
  --targets "$TARGET" \
  --policy "Full Scan" \
  --enabled 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/nessus/scan_create.txt

# List scans and get UUID
nessuscli scan list 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/nessus/scan_list.txt

# Download results (Nessus DB format)
nessuscli scan export $SCAN_UUID \
  --format db \
  -o evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/nessus/results.db 2>&1

# Download report (HTML/PDF)
nessuscli report download $SCAN_UUID \
  --format html \
  -o evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/nessus/report.html 2>&1

# Extract critical/high findings from Nessus DB
sqlite3 evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/nessus/results.db \
  "SELECT plugin_name, severity, pluginID, host, port, synopsis, description, solution
   FROM results
   WHERE severity IN (4,3)
   ORDER BY severity DESC, host" 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/nessus/critical_high.txt
```

### Qualys
```bash
# Qualys API authentication
QUALYS_USER="admin@example.com"
QUALYS_PASS="$QUALYS_PASSWORD"
QUALYS_API="https://qualysapi.qg2.apps.qualys.com/api/2.0/fo"

# Login and get session cookie
curl -s -c /tmp/qualys_cookie \
  -d "action=login&username=$QUALYS_USER&password=$QUALYS_PASS" \
  "$QUALYS_API/session/" 2>&1 | head -5

# Launch vulnerability scan
curl -s -b /tmp/qualys_cookie \
  -d "action=launch&scan_title=ThreatSwarm+$TARGET&target=$TARGET&option_id=1" \
  "$QUALYS_API/scan/" 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/qualys/scan_launch.xml

# Check scan status
curl -s -b /tmp/qualys_cookie \
  -d "action=list&state=Running,Finished" \
  "$QUALYS_API/scan/" 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/qualys/scan_status.xml

# Download results
curl -s -b /tmp/qualys_cookie \
  -d "action=list&truncation_limit=5000&severity_levels=3,4,5" \
  "$QUALYS_API/scan/result/" 2>&1 | \
  xmllint --format - 2>/dev/null | \
  tee evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/qualys/results.xml

# Cleanup session
curl -s -b /tmp/qualys_cookie \
  -d "action=logout" "$QUALYS_API/session/" > /dev/null
rm -f /tmp/qualys_cookie
```

### Nuclei (Template-Based Scanning)
```bash
# Nuclei with community templates + custom templates
nuclei -u $TARGET \
  -t ~/nuclei-templates/ \
  -t custom-templates/ \
  -severity critical,high,medium \
  -o evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/nuclei/results.txt \
  -jsonl -o evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/nuclei/results.jsonl \
  -rl 50 -c 10 \
  2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/nuclei/scan.log

# Update nuclei templates
nuclei -ut 2>&1 | tail -5

# Scan specific vulnerability templates only
nuclei -u $TARGET \
  -tags cve,exposure,misconfig \
  -severity critical,high \
  -o evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/nuclei/cve_results.txt 2>&1

# Network-level nuclei templates
nuclei -u $TARGET \
  -t ~/nuclei-templates/http/ \
  -t ~/nuclei-templates/network/ \
  -t ~/nuclei-templates/ssl/ \
  -o evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/nuclei/network_results.txt 2>&1
```

### OpenVAS
```bash
# Create target
gvmd --create-target \
  name="ThreatSwarm-$TARGET" \
  hosts="$TARGET" \
  2>&1 | tee -a evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/openvas/target.txt

TARGET_UUID=$(tail -1 evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/openvas/target.txt | grep -oP '[0-9a-f-]{36}')

# Create task
gvmd --create-task \
  name="ThreatSwarm Scan $TARGET $(date +%Y%m%d)" \
  target="$TARGET_UUID" \
  2>&1 | tee -a evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/openvas/task.txt

TASK_UUID=$(tail -1 evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/openvas/task.txt | grep -oP '[0-9a-f-]{36}')

# Start scan
gvmd --start-task "$TASK_UUID" 2>&1

# Check progress
gvmd --get-tasks --detail 2>&1 | grep -A3 "$TASK_UUID"

# Export results (XML)
gvmd --get-report "$TASK_UUID" f 89c5d9a4-8fb3-49a8-bcc2-5134b2f77104 \
  > evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/openvas/report.xml 2>&1

# Parse results
omp -u admin -w admin --get-report "$TASK_UUID" 2>&1 | \
  xmllint --xpath "//result[severity/text() > '5.0']" - 2>/dev/null
```

### Trivy (Container & IaC Scanning)
```bash
# Container image scanning
trivy image --severity CRITICAL,HIGH \
  --format json \
  --output evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/trivy/image_scan.json \
  $CONTAINER_IMAGE 2>&1

# Filesystem scanning
trivy fs --severity CRITICAL,HIGH \
  --format table \
  /path/to/app/source 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/trivy/fs_scan.txt

# Kubernetes cluster scanning
trivy k8s --severity CRITICAL,HIGH \
  --report summary \
  cluster 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/trivy/k8s_scan.txt

# Infrastructure as Code scanning
trivy config --severity CRITICAL,HIGH \
  tf:/path/to/terraform/ \
  2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/trivy/iac_scan.txt
```

## CVSS Prioritization

### CVSS v3.1 Scoring with Environmental Metrics
```python
#!/usr/bin/env python3
"""CVSS v3.1 scoring with environmental metrics for risk-based prioritization."""

import json
from datetime import datetime, timezone
from pathlib import Path

def score_vulnerability(base_vector: str, environmental: dict = None) -> dict:
    """
    Calculate CVSS v3.1 score with optional environmental adjustments.
    base_vector: e.g. "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N"
    environmental: {"confidentiality_requirement": "HIGH", "integrity_requirement": "HIGH"}
    """
    # Parse base vector metrics
    metrics = {}
    for part in base_vector.split("/"):
        if ":" in part:
            key, val = part.split(":", 1)
            metrics[key] = val
    
    # Base score lookup (simplified — use cvss library in production)
    # Key metrics: AV, AC, PR, UI, S, C, I, A
    av_scores = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.20}
    ac_scores = {"L": 0.77, "H": 0.44}
    pr_scores_impact = {"N": 0.85, "L": 0.62, "H": 0.27}
    
    # Calculate impact sub-scores
    impact_score = 0
    if metrics.get("C") == "H": impact_score += 0.56
    elif metrics.get("C") == "L": impact_score += 0.22
    if metrics.get("I") == "H": impact_score += 0.56
    elif metrics.get("I") == "L": impact_score += 0.22
    if metrics.get("A") == "H": impact_score += 0.56
    elif metrics.get("A") == "L": impact_score += 0.22
    
    iss = min(impact_score, 0.75) * 6.42
    
    # Environmental adjustments
    if environmental:
        # CR = Modified Confidentiality Impact * Confidentiality Requirement
        cr = {"HIGH": 1.5, "MEDIUM": 1.0, "LOW": 0.5}
        env_mult = cr.get(environmental.get("confidentiality_requirement", "MEDIUM"), 1.0)
        iss *= env_mult
    
    return {
        "vector": base_vector,
        "impact_score": round(impact_score, 2),
        "base_score": round(min(iss * av_scores.get(metrics.get("AV", "N"), 0.85) * 
                         ac_scores.get(metrics.get("AC", "L"), 0.77), 10.0), 1)
    }


def epss_lookup(cve: str) -> dict:
    """
    Look up Exploit Prediction Scoring System (EPSS) probability.
    Higher EPSS = more likely to be exploited in the wild.
    API: https://api.first.org/data/v1/epss?cve=$CVE
    """
    import urllib.request
    try:
        url = f"https://api.first.org/data/v1/epss?cve={cve}"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            epss_data = data.get("data", [])
            if epss_data:
                return {
                    "cve": cve,
                    "epss_score": float(epss_data[0].get("epss", 0)),
                    "epss_percentile": float(epss_data[0].get("percentile", 0))
                }
    except Exception as e:
        return {"cve": cve, "error": str(e)}
    return {"cve": cve, "epss_score": 0.0, "epss_percentile": 0.0}


def cisa_kev_check(cve: str) -> bool:
    """
    Check if CVE is in CISA Known Exploited Vulnerabilities catalog.
    API: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
    """
    import urllib.request
    try:
        url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            for vuln in data.get("vulnerabilities", []):
                if vuln.get("cveID", "").lower() == cve.lower():
                    return True
    except Exception:
        pass
    return False


def prioritize_findings(findings: list) -> list:
    """
    Prioritize findings based on CVSS + EPSS + CISA KEV + exploitability.
    Returns sorted list with composite risk score.
    """
    prioritized = []
    for f in findings:
        cve = f.get("cve", "")
        cvss = f.get("cvss_score", 0.0)
        
        # Base priority from CVSS
        priority = cvss * 10
        
        # EPSS boost (0-1.0 → 0-30 points)
        epss = epss_lookup(cve)
        priority += epss.get("epss_score", 0) * 30
        f["epss"] = epss.get("epss_score", 0)
        
        # CISA KEV boost (+50 points if actively exploited)
        if cisa_kev_check(cve):
            priority += 50
            f["cisa_kev"] = True
        else:
            f["cisa_kev"] = False
        
        # Internet-facing boost (+20 points)
        if f.get("internet_facing", False):
            priority += 20
        
        f["risk_score"] = round(priority, 1)
        prioritized.append(f)
    
    return sorted(prioritized, key=lambda x: x["risk_score"], reverse=True)
```

### Risk-Based Prioritization Matrix
```markdown
## Risk-Based Vulnerability Prioritization

### Scoring Factors
| Factor | Weight | Description |
|--------|--------|-------------|
| CVSS Base Score | 0-100 | Standard severity scoring |
| EPSS Score | 0-30 | Probability of exploitation in wild |
| CISA KEV | +50 | Known exploited vulnerability |
| Internet-Facing | +20 | Directly accessible from internet |
| Asset Criticality | +10-30 | Business impact of asset |
| Exploit Available | +15 | Public exploit code exists |

### SLA by Severity
| Severity | CVSS Range | Remediation SLA | Review Cadence |
|----------|-----------|----------------|----------------|
| Critical | 9.0-10.0 | 24 hours | Daily until patched |
| High | 7.0-8.9 | 7 days | Every 3 days |
| Medium | 4.0-6.9 | 30 days | Weekly |
| Low | 0.1-3.9 | 90 days | Monthly |
| Informational | 0.0 | Best effort | Quarterly |

### Composite Risk Score Thresholds
| Score | Action | Notification |
|-------|--------|-------------|
| 150+ | Emergency patch / isolate immediately | Page on-call |
| 100-149 | Patch within 48 hours | Notify within 4 hours |
| 60-99 | Patch within SLA | Notify within 24 hours |
| 30-59 | Schedule for next patch cycle | Weekly digest |
| <30 | Track and monitor | Monthly review |
```

## Remediation Tracking
```bash
# Vulnerability findings database (JSON-based)
VULN_DB="evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/vuln_db.json"

# Initialize vulnerability database
cat > $VULN_DB << 'EOF'
{
  "engagement": "$TARGET",
  "created": "$TIMESTAMP",
  "findings": []
}
EOF

# Add finding to database
add_finding() {
  local cve="$1" severity="$2" host="$3" port="$4" title="$5" cvss="$6"
  python3 -c "
import json, sys
from datetime import datetime, timezone

db_path = '$VULN_DB'
cve, severity, host, port, title, cvss = sys.argv[1:7]

with open(db_path) as f:
    db = json.load(f)

finding = {
    'id': f'{host}-{port}-{cve}',
    'cve': cve,
    'severity': severity,
    'host': host,
    'port': int(port),
    'title': title,
    'cvss_score': float(cvss),
    'status': 'NEW',
    'discovered': datetime.now(timezone.utc).isoformat(),
    'owner': '',
    'sla_deadline': '',
    'remediation_notes': '',
    'retest_date': '',
    'evidence_ref': ''
}

# Calculate SLA deadline
sla_days = {'CRITICAL': 1, 'HIGH': 7, 'MEDIUM': 30, 'LOW': 90}
if severity in sla_days:
    from datetime import timedelta
    deadline = datetime.now(timezone.utc) + timedelta(days=sla_days[severity])
    finding['sla_deadline'] = deadline.isoformat()

db['findings'].append(finding)

with open(db_path, 'w') as f:
    json.dump(db, f, indent=2)

print(f'[+] Added: {severity} {cve} on {host}:{port} - SLA: {finding[\"sla_deadline\"]}')" \
  "$cve" "$severity" "$host" "$port" "$title" "$cvss" 2>&1
}

# Update finding status
update_status() {
  local finding_id="$1" new_status="$2" owner="$3"
  python3 -c "
import json, sys
from datetime import datetime, timezone

db_path = '$VULN_DB'
finding_id, new_status, owner = sys.argv[1:4]

with open(db_path) as f:
    db = json.load(f)

for finding in db['findings']:
    if finding['id'] == finding_id:
        finding['status'] = new_status
        finding['owner'] = owner
        finding['last_updated'] = datetime.now(timezone.utc).isoformat()
        if new_status == 'REMEDIATED':
            finding['retest_date'] = datetime.now(timezone.utc).isoformat()
        break

with open(db_path, 'w') as f:
    json.dump(db, f, indent=2)

print(f'[+] Updated {finding_id} → {new_status} (owner: {owner})')" \
  "$finding_id" "$new_status" "$owner" 2>&1
}

# Generate SLA breach report
generate_sla_report() {
  python3 -c "
import json
from datetime import datetime, timezone

db_path = '$VULN_DB'
with open(db_path) as f:
    db = json.load(f)

now = datetime.now(timezone.utc)
breached = []
at_risk = []

for f in db['findings']:
    if f['status'] not in ('REMEDIATED', 'VERIFIED', 'CLOSED'):
        if f.get('sla_deadline'):
            deadline = datetime.fromisoformat(f['sla_deadline'])
            if now > deadline:
                breached.append(f)
            elif (deadline - now).days <= 2:
                at_risk.append(f)

print(f'=== SLA Report ===')
print(f'Open findings: {len([f for f in db[\"findings\"] if f[\"status\"] not in (\"REMEDIATED\",\"VERIFIED\",\"CLOSED\")])}')
print(f'BREACHED: {len(breached)}')
for f in breached:
    print(f'  [BREACHED] {f[\"severity\"]} {f[\"cve\"]} on {f[\"host\"]}:{f[\"port\"]} - was due {f[\"sla_deadline\"]}')
print(f'AT RISK (2 days): {len(at_risk)}')
for f in at_risk:
    print(f'  [AT RISK] {f[\"severity\"]} {f[\"cve\"]} on {f[\"host\"]}:{f[\"port\"]} - due {f[\"sla_deadline\"]}')
"
}
```

## Vulnerability Lifecycle Management
```bash
# Retest workflow — verify remediation
retest_finding() {
  local finding_id="$1"
  echo "[*] Retesting $finding_id..."
  
  # Read finding details
  local details=$(python3 -c "
import json, sys
with open('$VULN_DB') as f:
    db = json.load(f)
for f in db['findings']:
    if f['id'] == sys.argv[1]:
        print(f['cve'], f['host'], f['port'], f['severity'])
        break" "$finding_id")
  
  local cve=$(echo $details | awk '{print $1}')
  local host=$(echo $details | awk '{print $2}')
  local port=$(echo $details | awk '{print $3}')
  local severity=$(echo $details | awk '{print $4}')
  
  # Re-scan specific host:port with nuclei
  nuclei -u "$host:$port" \
    -tags "$cve" \
    -severity "$severity" \
    -o evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/retest_${finding_id}.txt 2>&1
  
  if grep -q "FOUND" evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/retest_${finding_id}.txt 2>/dev/null; then
    echo "[!] STILL VULNERABLE: $finding_id"
    update_status "$finding_id" "RETEST_FAILED" ""
  else
    echo "[+] REMEDIATED: $finding_id"
    update_status "$finding_id" "VERIFIED" ""
  fi
}

# Export vulnerability report
export_report() {
  python3 -c "
import json
from datetime import datetime, timezone

with open('$VULN_DB') as f:
    db = json.load(f)

by_severity = {}
for f in db['findings']:
    s = f['severity']
    if s not in by_severity:
        by_severity[s] = []
    by_severity[s].append(f)

print(f'# Vulnerability Management Report — {db[\"engagement\"]} — {datetime.now(timezone.utc).strftime(\"%Y-%m-%d\")}')
print()
print(f'## Summary')
print(f'- Total Findings: {len(db[\"findings\"])}')
for s in ['CRITICAL','HIGH','MEDIUM','LOW','INFO']:
    c = len(by_severity.get(s, []))
    if c > 0:
        print(f'- {s}: {c}')
open_count = len([f for f in db['findings'] if f['status'] not in ('VERIFIED','CLOSED')])
print(f'- Open: {open_count}')
closed_count = len([f for f in db['findings'] if f['status'] in ('VERIFIED','CLOSED')])
print(f'- Verified/Closed: {closed_count}')
print()
print('## SLA Compliance')
breached = len([f for f in db['findings'] if f.get('sla_deadline') and f['status'] not in ('VERIFIED','CLOSED')])
print(f'- SLA Breached: {breached}')
print(f'- SLA Met: {len(db[\"findings\"]) - breached}')
"
}
```

## Evidence Output
Write to `evidence/$(date +%Y%m%d)/$TARGET/vuln-mgmt/vuln_mgmt_findings.md`:
```markdown
## Vulnerability Management Report — $TARGET — $(date -u +%Y-%m-%dT%H:%M:%SZ)

### Scan Summary
| Scanner | Start | End | Findings | Critical | High | Medium |
|---------|-------|-----|----------|----------|------|--------|

### Prioritized Findings (Top 20)
| # | CVE | Host:Port | CVSS | EPSS | KEV | Risk Score | Status |
|---|-----|-----------|------|------|-----|-----------|--------|

### SLA Compliance
| Severity | Total | Within SLA | Breached | Remediated |
|----------|-------|-----------|----------|------------|

### Remediation Progress
| CVE | Owner | Status | SLA Deadline | Last Updated |
|-----|-------|--------|-------------|-------------|

### Recommendations
[Priority-ordered remediation guidance based on risk scoring]
```
