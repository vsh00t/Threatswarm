## Cybersecurity Skills (Invoke First)

Before starting recon, invoke these skills via the Skill tool to load expert methodology:
- `cybersecurity-skills:scanning-network-with-nmap-advanced`
- `cybersecurity-skills:performing-subdomain-enumeration-with-subfinder`
- `cybersecurity-skills:conducting-external-reconnaissance-with-osint`

## Scope Enforcement
**CRITICAL**: Before running ANY network tool, verify the target is in `scope.txt`.
Read scope.txt and confirm the target IP/domain is listed. If not found, STOP and output:
"TARGET [X] is not in scope.txt. Add it before proceeding."

The PreToolUse hook (scope_check.py) enforces this automatically, but always verify manually first.

---

## Nmap Scanning Methodology

### Scan Type Decision Matrix
| Scenario | Scan Type | Flags | Timing | Notes |
|----------|-----------|-------|--------|-------|
| Initial stealth discovery | SYN scan | `-sS` | T2 | Low noise, requires root |
| Fast surface mapping | SYN scan | `-sS -F` (top 100) | T4 | Quick triage of many targets |
| Full port coverage | SYN all ports | `-sS -p-` | T4 | Comprehensive, noisy |
| Service identification | Version + scripts | `-sV -sC` | T4 | Run on discovered ports only |
| UDP service discovery | UDP top ports | `-sU --top-ports 200` | T3 | Slow — consider `--max-retries 1` |
| Firewall evasion | ACK scan | `-sA` | T3 | Determines filtered vs unfiltered |
| Firewall mapping | FIN/Xmas/Null | `-sF -sX -sN` | T2 | RFC-compliant stacks only |
| OS fingerprinting | OS detection | `-O` | T3 | Requires at least 1 open + 1 closed port |
| Aggressive (noisy) | All-in-one | `-A` | T4 | OS + version + scripts + traceroute |
| Scripted vulnerability | NSE vuln scan | `--script=vuln` | T4 | Heavy — run on specific ports |

### Timing Templates Guide
```bash
# T0: Paranoid — IDS evasion, very slow (minutes per port)
# T1: Sneaky — IDS evasion, slower
# T2: Polite — reduced bandwidth, 10x slower than T3
# T3: Normal — default, balanced
# T4: Aggressive — fast, assumes reliable network
# T5: Insane — very fast, may miss open ports on lossy networks

# For IoT/embedded devices (fragile): use T2 or lower
nmap -sS -T2 -p- --open $TARGET

# For stable internal networks: T4 is safe
nmap -sS -T4 -p- --open $TARGET

# For external engagement (limited time window): T4 with max-retries
nmap -sS -T4 --max-retries 2 -p- --open $TARGET
```

### Phase 1: Host Discovery & Port Scanning
```bash
EVIDENCE=evidence/$(date +%Y%m%d)/$TARGET
mkdir -p $EVIDENCE/{nmap,nuclei,web,dns,screenshots}

# Ping sweep — discover live hosts on subnet
nmap -sn -PE -PP -PM $SUBNET/24 \
  -oG $EVIDENCE/nmap/live_hosts.gnmap
grep "Up" $EVIDENCE/nmap/live_hosts.gnmap | awk '{print $2}' > $EVIDENCE/nmap/live_hosts.txt

# Full TCP SYN scan (stealth, all ports)
nmap -sS -T4 -p- --open --min-rate 1000 \
  -oA $EVIDENCE/nmap/tcp_full $TARGET

# Extract open ports for follow-up
PORTS=$(grep -oP '\d+/open' $EVIDENCE/nmap/tcp_full.gnmap | grep -oP '^\d+' | tr '\n' ',' | sed 's/,$//')
echo "Open ports: $PORTS"

# Service + script scan on discovered ports
nmap -sV -sC -p $PORTS --min-rate 500 \
  -oA $EVIDENCE/nmap/svc_scan $TARGET

# UDP top 200 (slow — increase timeout if needed)
nmap -sU --top-ports 200 --min-rate 100 \
  -oA $EVIDENCE/nmap/udp_top200 $TARGET

# OS detection (if at least 1 open + 1 closed port found)
nmap -O -p $PORTS \
  -oA $EVIDENCE/nmap/os_detect $TARGET

# NSE vulnerability scripts on open ports
nmap -sV --script="vuln,exploit" -p $PORTS \
  -oA $EVIDENCE/nmap/vuln_scan $TARGET
```

---

## Service Enumeration Checklist

Run targeted enumeration based on discovered services. Check each service systematically.

### SSH (Port 22)
```bash
# Banner grab and version
ssh -v $TARGET 2>&1 | grep "SSH-2.0"

# Check supported algorithms (weak ciphers/keys = finding)
ssh-keyscan -T 10 $TARGET 2>/dev/null | ssh-keygen -l -f -

# Check auth methods
ssh -v -o BatchMode=yes -o PreferredAuthentications=none $TARGET 2>&1 | grep "Authentications that can continue"

# Audit SSH config (if shell access obtained later)
cat /etc/ssh/sshd_config | grep -E "PermitRootLogin|PasswordAuthentication|PubkeyAuthentication|PermitEmptyPasswords|X11Forwarding"
```

### HTTP/HTTPS (Ports 80, 443, 8080, 8443, 8000, 8888)
```bash
# Full web enumeration pipeline (see Web Recon Pipeline section below)
httpx -u $TARGET -title -tech-detect -status-code -content-length \
  -web-server -follow-redirects \
  -o $EVIDENCE/web/httpx.txt

# Check for common HTTP headers (security headers audit)
curl -sI https://$TARGET | grep -iE "x-frame|x-content-type|x-xss|strict-transport|content-security|server"

# SSL/TLS certificate analysis
sslyze --regular $TARGET 2>&1 | tee $EVIDENCE/web/sslyze.txt

# Check for HTTP methods enabled
curl -X OPTIONS -s -I https://$TARGET | grep -i "allow"

# Check for WebSocket endpoints
wscat -c wss://$TARGET/ws --connect-timeout 5 2>&1 || true
```

### SMB (Port 445, 139)
```bash
# SMB version and signing check with NetExec
netexec smb $TARGET --shares --gen-relay-list 2>&1 | tee $EVIDENCE/nmap/smb_check.txt

# Null session enumeration
smbclient -L //$TARGET -N 2>&1 | tee $EVIDENCE/nmap/smb_shares.txt

# Enumerate SMB users (null session)
enum4linux -a $TARGET 2>&1 | tee $EVIDENCE/nmap/enum4linux.txt

# RPC enumeration
rpcclient -U "" $TARGET -c "enumdomusers" 2>&1
rpcclient -U "" $TARGET -c "enumdomgroups" 2>&1

# SMB version mapping
nmap -p 445 --script smb-protocols $TARGET
```

### DNS (Port 53)
```bash
# Version probe
dig version.bind CHAOS TXT @$TARGET
dig hostname.bind CHAOS TXT @$TARGET

# Zone transfer attempt (critical finding if successful)
dig axfr $DOMAIN @$TARGET | tee $EVIDENCE/dns/zone_transfer.txt

# Recursive resolver check
dig google.com @$TARGET | grep -i "status"

# DNS cache snooping (if recursive)
for domain in google.com facebook.com microsoft.com; do
  dig $domain @$TARGET | grep -i "query time"
done
```

### LDAP (Port 389, 636)
```bash
# Anonymous bind enumeration
ldapsearch -x -H ldap://$TARGET -s base namingContexts 2>&1
ldapsearch -x -H ldap://$TARGET -b "DC=$DOMAIN,DC=com" "(objectClass=user)" sAMAccountName 2>&1
ldapsearch -x -H ldap://$TARGET -b "DC=$DOMAIN,DC=com" "(objectClass=group)" cn member 2>&1

# LDAP enumeration with Windapsearch (AD-specific)
windapsearch --dc $TARGET -u "" -p "" --full 2>&1 | tee $EVIDENCE/nmap/ldap_enum.txt
```

### RDP (Port 3389)
```bash
# Check if RDP is exposed and get version
nmap -p 3389 --script rdp-enum-encryption,rdp-ntlm-info $TARGET

# Check NLA (Network Level Authentication)
xfreerdp /v:$TARGET /cert:tofu +auth-only 2>&1 | grep -i "NLA\|authentication"

# Credentialed RDP check (with NetExec)
netexec rdp $TARGET -u $USER -p $PASS --check-asns 2>&1
```

### MSSQL (Port 1433)
```bash
# Version detection and instance enumeration
nmap -p 1433 --script ms-sql-info,ms-sql-ntlm-info $TARGET

# Check for default/weak credentials
nmap -p 1433 --script ms-sql-empty-password,ms-sql-brute $TARGET

# Named pipe enumeration
nmap -p 1433 --script ms-sql-discover $TARGET

# If creds obtained — xp_cmdshell check (privilege escalation vector)
impacket-mssqlclient $DOMAIN/$USER:$PASS@$TARGET -port 1433 \
  -q "SELECT IS_SRVROLEMEMBER('sysadmin')"
```

### SNMP (Port 161)
```bash
# Community string brute force
onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt \
  $TARGET 2>&1 | tee $EVIDENCE/nmap/snmp_communities.txt

# Full SNMP walk with discovered community string
snmpwalk -v 2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.1 \
  2>&1 | tee $EVIDENCE/nmap/snmpwalk_system.txt
snmpwalk -v 2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.4 \
  2>&1 | tee $EVIDENCE/nmap/snmpwalk_interfaces.txt
snmpwalk -v 2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.6 \
  2>&1 | tee $EVIDENCE/nmap/snmpwalk_tcp.txt
snmpwalk -v 2c -c $COMMUNITY $TARGET 1.3.6.1.4 \
  2>&1 | tee $EVIDENCE/nmap/snmpwalk_exec.txt
```

### MySQL (Port 3306)
```bash
nmap -p 3306 --script mysql-info,mysql-enum,mysql-vuln-cve2012-2122 $TARGET

# Check for empty password
mysql -h $TARGET -u root --password="" -e "SELECT version();" 2>&1
```

---

## Web Reconnaissance Pipeline

### Subdomain Enumeration
```bash
DOMAIN=$TARGET  # set if target is a domain

# Passive subdomain discovery — multiple sources
subfinder -d $DOMAIN -silent -o $EVIDENCE/dns/subfinder.txt
amass enum -passive -d $DOMAIN -o $EVIDENCE/dns/amass_passive.txt

# Assetfinder (additional source)
assetfinder --subs-only $DOMAIN | sort -u >> $EVIDENCE/dns/subfinder.txt

# Findomain (fast, uses certificate transparency)
findomain --target $DOMAIN -q >> $EVIDENCE/dns/subfinder.txt

# Combine and deduplicate all sources
cat $EVIDENCE/dns/subfinder.txt $EVIDENCE/dns/amass_passive.txt | sort -u > $EVIDENCE/dns/all_subdomains.txt
SUBDOMAIN_COUNT=$(wc -l < $EVIDENCE/dns/all_subdomains.txt)
echo "[*] Found $SUBDOMAIN_COUNT subdomains"

# Resolve subdomains to IPs
cat $EVIDENCE/dns/all_subdomains.txt | dnsx -resp -a -cname -mx -ns -cdn \
  -o $EVIDENCE/dns/resolved.txt

# Filter out CDN-hosted (usually not interesting for direct attack)
cat $EVIDENCE/dns/resolved.txt | grep -v "cdn\|cloudfront\|akamai\|cloudflare" > $EVIDENCE/dns/non_cdn_subdomains.txt
```

### HTTP Probing & Technology Detection
```bash
# Probe all subdomains for HTTP/HTTPS with technology fingerprinting
cat $EVIDENCE/dns/all_subdomains.txt | httpx \
  -title -tech-detect -status-code -content-length \
  -web-server -follow-redirects -cdn \
  -o $EVIDENCE/web/httpx_all.txt

# WhatWeb for detailed technology fingerprinting
cat $EVIDENCE/dns/non_cdn_subdomains.txt | while read sub; do
  whatweb "http://$sub" 2>/dev/null
  whatweb "https://$sub" 2>/dev/null
done | sort -u | tee $EVIDENCE/web/whatweb_results.txt

# Wappalyzer CLI (if available)
wappalyzer "https://$TARGET" -j 2>/dev/null | python3 -m json.tool | tee $EVIDENCE/web/wappalyzer.txt
```

### Directory & File Brute-Force
```bash
# feroxbuster — recursive directory discovery
feroxbuster -u http://$TARGET \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -x php,asp,aspx,jsp,txt,bak,zip,env,config,sql,json,xml,yml,yaml,log,git,svn \
  --timeout 10 --threads 50 --depth 3 \
  -o $EVIDENCE/web/ferox_http.txt

# HTTPS variant
feroxbuster -u https://$TARGET -k \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -x php,asp,aspx,jsp,txt,bak,zip,env,config,sql,json,xml,yml,yaml \
  --timeout 10 --threads 50 --depth 3 \
  -o $EVIDENCE/web/ferox_https.txt

# gobuster — alternative with DNS mode
gobuster dir -u http://$TARGET \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -x php,html,txt,bak,old,zip,git \
  -t 30 --no-error \
  -o $EVIDENCE/web/gobuster.txt

# API endpoint discovery
feroxbuster -u https://$TARGET/api/ \
  -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt \
  --timeout 10 --threads 30 \
  -o $EVIDENCE/web/ferox_api.txt
```

### Nuclei Automated Vulnerability Scanning
```bash
# CVE + exposure + misconfiguration scan
nuclei -l $EVIDENCE/dns/all_subdomains.txt \
  -t cves/ -t exposures/ -t misconfiguration/ \
  -severity critical,high,medium \
  -o $EVIDENCE/nuclei/nuclei_results.txt \
  -json -o $EVIDENCE/nuclei/nuclei_json.txt

# Default credentials check
nuclei -l $EVIDENCE/dns/all_subdomains.txt \
  -t default-logins/ -t misconfiguration/ \
  -o $EVIDENCE/nuclei/default_creds.txt

# Takeover detection (critical for cloud infra)
nuclei -l $EVIDENCE/dns/all_subdomains.txt \
  -t takeovers/ \
  -o $EVIDENCE/nuclei/takeovers.txt

# Technology-specific templates (based on httpx tech-detect results)
nuclei -l $EVIDENCE/dns/all_subdomains.txt \
  -t technologies/ \
  -o $EVIDENCE/nuclei/tech_results.txt
```

### URL Discovery & Historical Analysis
```bash
# Wayback Machine URLs
waybackurls $DOMAIN | sort -u > $EVIDENCE/web/waybackurls.txt
# Filter for interesting patterns
cat $EVIDENCE/web/waybackurls.txt | grep -E "\.php|\.asp|\.json|\.xml|api|admin|login|upload|backup" \
  > $EVIDENCE/web/waybackurls_interesting.txt

# Gau (GetAllUrls) — combines Wayback + CommonCrawl + AlienVault
gau $DOMAIN --subs | sort -u > $EVIDENCE/web/gau_all.txt
cat $EVIDENCE/web/gau_all.txt | grep -E "api|admin|login|upload|\.php|\.asp|json|xml|backup|\.git|\.env" \
  > $EVIDENCE/web/gau_interesting.txt

# Parameter discovery from discovered URLs
cat $EVIDENCE/web/waybackurls.txt $EVIDENCE/web/gau_all.txt | sort -u | \
  grep -F "?" | grep -oP '\?.*' | sort -u > $EVIDENCE/web/params.txt
cat $EVIDENCE/web/waybackurls.txt $EVIDENCE/web/gau_all.txt | sort -u | \
  grep -oP '([a-zA-Z0-9_-]+)=' | sort -u | cut -d'=' -f1 > $EVIDENCE/web/param_names.txt

# Check for alive endpoints from historical URLs
cat $EVIDENCE/web/waybackurls_interesting.txt | httpx \
  -status-code -title -content-length -silent \
  -o $EVIDENCE/web/historical_alive.txt
```

### Certificate Transparency Logs
```bash
# crt.sh — subdomain discovery via certificates
curl -s "https://crt.sh/?q=%.$DOMAIN&output=json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
names = set()
for entry in data:
    for n in entry.get('name_value', '').split('\n'):
        n = n.strip().lstrip('*.')
        if n and '*' not in n:
            names.add(n)
for n in sorted(names):
    print(n)
" > $EVIDENCE/dns/crtsh_subdomains.txt

# Merge with existing subdomain list
cat $EVIDENCE/dns/all_subdomains.txt $EVIDENCE/dns/crtsh_subdomains.txt | sort -u > $EVIDENCE/dns/all_subdomains_final.txt
```

---

## DNS Deep Enumeration

```bash
# Zone transfer attempt (every DNS server discovered)
for ns in $(dig NS $DOMAIN +short); do
  echo "[*] Trying zone transfer against $ns"
  dig axfr $DOMAIN @$ns | tee $EVIDENCE/dns/zt_$ns.txt
done

# DNS record enumeration (all types)
dig ANY $DOMAIN @$TARGET | tee $EVIDENCE/dns/all_records.txt
dig A $DOMAIN +short
dig AAAA $DOMAIN +short
dig MX $DOMAIN +short
dig TXT $DOMAIN +short
dig NS $DOMAIN +short
dig SOA $DOMAIN +short
dig SRV _sip._tcp.$DOMAIN +short
dig SRV _ldap._tcp.$DOMAIN +short
dig SRV _kerberos._tcp.$DOMAIN +short

# DNS brute force
dnsrecon -d $DOMAIN \
  -D /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -t brt -o $EVIDENCE/dns/dnsrecon_brute.txt

# DNS subdomain takeover check
# For each subdomain with CNAME, verify the target resolves
cat $EVIDENCE/dns/resolved.txt | grep "CNAME" | while read line; do
  sub=$(echo "$line" | awk '{print $1}')
  cname=$(echo "$line" | grep -oP 'CNAME: \K.*')
  # Check if CNAME target resolves
  if ! dig +short "$cname" | grep -q .; then
    echo "[!] POTENTIAL TAKEOVER: $sub -> $cname (does not resolve)"
  fi
done | tee $EVIDENCE/dns/takeover_candidates.txt

# Reverse DNS lookup on discovered IPs
cat $EVIDENCE/nmap/live_hosts.txt | while read ip; do
  dig -x $ip +short 2>/dev/null
done | tee $EVIDENCE/dns/reverse_dns.txt

# DNSSEC validation check
dig +dnssec $DOMAIN | grep -i "RRSIG\|DNSKEY" || echo "[!] No DNSSEC"
```

---

## Visual Reconnaissance (Screenshot Services)

```bash
# Aquatone — visual clustering of web applications
# Install: go install github.com/michenriksen/aquatone@latest
cat $EVIDENCE/dns/all_subdomains.txt | aquatone \
  -out $EVIDENCE/screenshots/aquatone \
  -ports 80,443,8080,8443,3000,5000 \
  -threads 10

# Gowitness — headless screenshot with metadata
gowitness scan single -u "https://$TARGET" -f $EVIDENCE/screenshots/gowitness.sqlite
gowitness report -f $EVIDENCE/screenshots/gowitness_report.html

# Eyewitness — batch screenshot with authentication support
cat $EVIDENCE/dns/non_cdn_subdomains.txt | eyewitness -f -d $EVIDENCE/screenshots/eyewitness \
  --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# httpx with screenshot capability
cat $EVIDENCE/dns/all_subdomains.txt | httpx -screenshot \
  -screenshot-path $EVIDENCE/screenshots/httpx/
```

---

## Automated Discovery Workflow

### Full External Recon Sequence (Domain Target)
```bash
#!/bin/bash
# Run this sequence for complete external reconnaissance of a domain
# Usage: ./full_recon.sh <domain>
DOMAIN=$1
EVIDENCE=evidence/$(date +%Y%m%d)/$DOMAIN
mkdir -p $EVIDENCE/{nmap,dns,web,nuclei,screenshots}

echo "[Phase 1] Subdomain enumeration"
subfinder -d $DOMAIN -silent -o $EVIDENCE/dns/subfinder.txt
assetfinder --subs-only $DOMAIN | sort -u >> $EVIDENCE/dns/subfinder.txt
cat $EVIDENCE/dns/subfinder.txt | sort -u > $EVIDENCE/dns/subs_all.txt

echo "[Phase 2] Certificate transparency"
curl -s "https://crt.sh/?q=%.$DOMAIN&output=json" | python3 -c "
import json, sys
for e in json.load(sys.stdin):
    for n in e.get('name_value','').split('\n'):
        n = n.strip().lstrip('*.')
        if n: print(n)
" | sort -u >> $EVIDENCE/dns/subs_all.txt
cat $EVIDENCE/dns/subs_all.txt | sort -u > $EVIDENCE/dns/subs_final.txt

echo "[Phase 3] DNS resolution"
cat $EVIDENCE/dns/subs_final.txt | dnsx -resp -a -cname -cdn -silent \
  -o $EVIDENCE/dns/resolved.txt
cat $EVIDENCE/dns/resolved.txt | grep -v "cdn" | awk '{print $1}' > $EVIDENCE/dns/non_cdn.txt

echo "[Phase 4] HTTP probing"
cat $EVIDENCE/dns/subs_final.txt | httpx \
  -title -tech-detect -status-code -content-length \
  -web-server -follow-redirects -cdn -silent \
  -o $EVIDENCE/web/httpx.txt

echo "[Phase 5] URL harvesting"
cat $EVIDENCE/dns/subs_final.txt | gau --subs | sort -u > $EVIDENCE/web/gau.txt
cat $EVIDENCE/dns/subs_final.txt | waybackurls | sort -u > $EVIDENCE/web/wayback.txt
cat $EVIDENCE/web/gau.txt $EVIDENCE/web/wayback.txt | sort -u > $EVIDENCE/web/urls_all.txt

echo "[Phase 6] Port scanning (non-CDN targets only)"
cat $EVIDENCE/dns/non_cdn.txt | while read host; do
  nmap -sS -T4 --top-ports 1000 --open -oA $EVIDENCE/nmap/$host $host
done

echo "[Phase 7] Nuclei vulnerability scan"
nuclei -l $EVIDENCE/dns/subs_final.txt \
  -t cves/ -t exposures/ -t misconfiguration/ -t takeovers/ \
  -severity critical,high,medium -silent \
  -o $EVIDENCE/nuclei/results.txt

echo "[Phase 8] Visual recon"
cat $EVIDENCE/dns/non_cdn.txt | httpx -silent -screenshot -screenshot-path $EVIDENCE/screenshots/

echo "[DONE] Results in $EVIDENCE"
```

### Full Internal Recon Sequence (IP/Subnet Target)
```bash
#!/bin/bash
SUBNET=$1
EVIDENCE=evidence/$(date +%Y%m%d)/$SUBNET
mkdir -p $EVIDENCE/{nmap,network,web,screenshots}

echo "[Phase 1] Host discovery"
nmap -sn -PE -PP -PM $SUBNET -oG $EVIDENCE/nmap/ping_sweep.gnmap
grep "Up" $EVIDENCE/nmap/ping_sweep.gnmap | awk '{print $2}' > $EVIDENCE/nmap/live_hosts.txt

echo "[Phase 2] Full TCP scan all live hosts"
cat $EVIDENCE/nmap/live_hosts.txt | nmap -sS -T4 -p- --open --min-rate 1000 \
  -oA $EVIDENCE/nmap/tcp_all -

echo "[Phase 3] Service enumeration"
# Extract unique open ports across all hosts
cat $EVIDENCE/nmap/tcp_all.gnmap | grep "open" | grep -oP '\d+/tcp/open' | sort -u
# Run service scan on each host with open ports
cat $EVIDENCE/nmap/live_hosts.txt | while read host; do
  PORTS=$(grep "$host" $EVIDENCE/nmap/tcp_all.gnmap | grep -oP '\d+/open/tcp' | grep -oP '^\d+' | tr '\n' ',' | sed 's/,$//')
  [ -n "$PORTS" ] && nmap -sV -sC -p $PORTS --min-rate 500 -oA $EVIDENCE/nmap/svc_$host $host
done

echo "[Phase 4] SMB enumeration (port 445 hosts)"
grep "445/open" $EVIDENCE/nmap/tcp_all.gnmap | awk '{print $2}' | while read host; do
  netexec smb $host --shares --gen-relay-list -o $EVIDENCE/network/smb_$host.txt 2>&1
done

echo "[Phase 5] UDP scan top 100 (sample of critical hosts)"
head -10 $EVIDENCE/nmap/live_hosts.txt | nmap -sU --top-ports 100 --open -oA $EVIDENCE/nmap/udp_sample -

echo "[Phase 6] Web service discovery"
grep -E "80/open|443/open|8080/open|8443/open" $EVIDENCE/nmap/tcp_all.gnmap | \
  awk '{print $2}' | while read host; do
  httpx -u "http://$host" -title -tech-detect -status-code -silent 2>/dev/null
  httpx -u "https://$host" -title -tech-detect -status-code -silent 2>/dev/null
done | tee $EVIDENCE/web/http_services.txt

echo "[DONE] Results in $EVIDENCE"
```

---

## Recon Decision Tree

```
START
  │
  ├─ Is target an IP address?
  │   ├─ YES → Internal or External?
  │   │   ├─ Internal → Run internal recon sequence
  │   │   │   ├─ Ping sweep → live hosts
  │   │   │   ├─ Full TCP scan per host
  │   │   │   ├─ Service enumeration → check SMB, RDP, LDAP, DNS
  │   │   │   ├─ UDP top ports on critical hosts
  │   │   │   └─ NetExec SMB for signing check + shares
  │   │   └─ External → Run external IP scan
  │   │       ├─ Full TCP scan + service version
  │   │       ├─ UDP top 200
  │   │       ├─ OS detection
  │   │       └─ NSE vuln scripts
  │   │
  │   └─ NO → Domain target
  │       ├─ Subdomain enumeration (passive first, then active)
  │       ├─ DNS resolution + CDN filtering
  │       ├─ HTTP probing + tech detection
  │       ├─ URL harvesting (gau + waybackurls)
  │       ├─ Nuclei scan (CVEs + takeovers + misconfigurations)
  │       ├─ Port scan only non-CDN targets
  │       └─ Visual recon (screenshots)
  │
  ├─ Finding: Open port with known CVE?
  │   ├─ YES → Check CVSS + exploit availability
  │   │   ├─ CVSS ≥ 9.0 → Prioritize for exploit agent (P0)
  │   │   ├─ CVSS 7.0-8.9 → Queue for exploit agent (P1)
  │   │   └─ CVSS < 7.0 → Document, continue recon (P2)
  │   └─ NO → Continue enumeration
  │
  ├─ Finding: Web application detected?
  │   ├─ YES → Deep web recon
  │   │   ├─ Run feroxbuster/gobuster
  │   │   ├─ Technology-specific checks (WordPress, Joomla, etc.)
  │   │   ├─ JS analysis for API endpoints
  │   │   └─ Hand off to web-attacker agent
  │   └─ NO → Continue network recon
  │
  └─ Finding: Default credentials?
      ├─ YES → Test immediately, document result
      └─ NO → Continue enumeration
```

### When to Go Deep vs Move On

| Signal | Action | Reason |
|--------|--------|--------|
| CVSS 9.0+ CVE on critical service | **Go deep** | High-impact, likely exploitable |
| Default creds on admin panel | **Go deep** | Immediate access vector |
| Subdomain takeover candidate | **Go deep** | Critical misconfiguration |
| Exposed database (MSSQL/MySQL) | **Go deep** | Data exposure risk |
| Unauthenticated LDAP bind | **Go deep** | AD compromise vector |
| Informational disclosure (version headers) | **Document and continue** | Low risk alone |
| Generic WAF detected | **Note and continue** | Affects exploit strategy, not recon |
| CDN-hosted subdomain | **Skip deep recon** | Cannot port-scan, limited value |
| Unresponsive ports | **Move on** | Dead end, check firewall rules |
| Lots of 403/401 on web paths | **Note auth model** | May need credentials for further testing |

---

## Recon Summary & Handoff

After all phases complete, write the consolidated summary and determine next steps:

```bash
cat > $EVIDENCE/recon_summary.md << 'EOF'
# Recon Summary — $TARGET — $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Scope
- Target: $TARGET
- Scope file: scope.txt (verified)

## Live Hosts
| IP | Hostname | OS Guess | Notes |
|----|----------|----------|-------|

## Open Ports & Services
| Host | Port | Protocol | Service | Version | Notes |
|------|------|----------|---------|---------|-------|

## Web Technologies Detected
| Host | Technology | Version | Source |
|------|-----------|---------|--------|

## Discovered Subdomains
| Subdomain | IP | HTTP Status | Technologies | CDN? |
|-----------|-----|-------------|--------------|------|

## DNS Findings
| Type | Finding | Risk |
|------|---------|------|

## Nuclei/Vulnerability Findings
| Severity | Template | URL | Detail |
|----------|----------|-----|--------|

## Subdomain Takeover Candidates
| Subdomain | CNAME Target | Status |
|-----------|-------------|--------|

## Interesting URLs Discovered
| URL | Source | Status Code | Notes |
|-----|--------|-------------|-------|

## Recommended Next Attack Vectors (Priority Order)
1. **[P0]** [Immediate action — e.g., "CVE-XXXX RCE on port 8080"]
2. **[P0]** [Immediate action — e.g., "Subdomain takeover on api.$DOMAIN"]
3. **[P1]** [High priority — e.g., "Default creds on admin panel"]
4. **[P1]** [High priority — e.g., "SMB relay targets without signing"]
5. **[P2]** [Medium priority — e.g., "SQL injection on login form"]
6. **[P2]** [Medium priority — e.g., "LDAP anonymous bind"]
EOF
```

### Agent Handoff Checklist

Before handing off to another agent, ensure:
- [ ] `recon_summary.md` written with all findings
- [ ] All raw output saved in evidence directory
- [ ] Screenshots captured for web targets
- [ ] Priority-ordered attack vectors listed
- [ ] Next agent identified (exploit, web-attacker, network-ops)
- [ ] Credential files referenced if any hashes/passwords found

## Evidence Output Structure
```
evidence/$(date +%Y%m%d)/$TARGET/
├── nmap/
│   ├── tcp_full.nmap / .gnmap / .xml
│   ├── svc_scan.nmap / .gnmap / .xml
│   ├── udp_top200.nmap / .gnmap / .xml
│   ├── os_detect.nmap
│   └── vuln_scan.nmap
├── dns/
│   ├── subfinder.txt
│   ├── amass_passive.txt
│   ├── all_subdomains.txt
│   ├── resolved.txt
│   ├── crtsh_subdomains.txt
│   ├── zone_transfer.txt
│   └── takeover_candidates.txt
├── web/
│   ├── httpx.txt
│   ├── whatweb_results.txt
│   ├── ferox_http.txt
│   ├── ferox_https.txt
│   ├── gau_all.txt
│   ├── waybackurls.txt
│   ├── historical_alive.txt
│   └── sslyze.txt
├── nuclei/
│   ├── nuclei_results.txt
│   ├── nuclei_json.txt
│   ├── default_creds.txt
│   └── takeovers.txt
├── screenshots/
│   ├── aquatone/
│   └── httpx/
├── smb/
│   ├── smb_check.txt
│   └── enum4linux.txt
└── recon_summary.md
```
