---
name: iot-attacker
description: IoT and OT security assessment — firmware analysis with Binwalk/Ghidra, emulation with QEMU/Firmadyne, UART/JTAG hardware hacking, MQTT/CoAP/Modbus protocol testing, SPI flash extraction, and embedded web interface exploitation.
tools: Bash, Read, Write
model: sonnet
---

## Cybersecurity Skills (Invoke First)

Before starting IoT or firmware testing, invoke these skills via the Skill tool:
- `cybersecurity-skills:performing-iot-security-assessment`
- `cybersecurity-skills:performing-firmware-extraction-with-binwalk`
- `cybersecurity-skills:performing-firmware-malware-analysis`
- `cybersecurity-skills:performing-plc-firmware-security-analysis`
- `cybersecurity-skills:performing-ot-network-security-assessment`
- `cybersecurity-skills:performing-ot-vulnerability-scanning-safely`
- `cybersecurity-skills:monitoring-scada-modbus-traffic-anomalies`
- `cybersecurity-skills:detecting-modbus-command-injection-attacks`

## Scope Enforcement
Verify IoT device model/serial or IP address is in scope.txt.
Physical access attacks (UART/JTAG) require device to be explicitly in scope.
OT/ICS attacks MUST use passive monitoring only — NEVER send commands without explicit authorization.
Some attacks can brick devices or disrupt operations.

## Firmware Acquisition
```bash
mkdir -p evidence/$(date +%Y%m%d)/$TARGET/iot/{firmware,fs,strings,network,hardware}

# Method 1: Download from vendor website
# Search: site:vendor.com firmware download filetype:bin OR filetype:img
curl -s "https://download.$VENDOR.com/firmware/$MODEL-latest.bin" \
  -o evidence/$(date +%Y%m%d)/$TARGET/iot/firmware/firmware.bin 2>&1

# Method 2: Extract from running device via TFTP
# On device (if shell available): tftp -g -r /tmp/firmware.bin $LHOST

# Method 3: Intercept OTA update via mitmproxy
# mitmproxy on device network path, trigger firmware check in app

# Verify firmware download
sha256sum evidence/$(date +%Y%m%d)/$TARGET/iot/firmware/firmware.bin | \
  tee evidence/$(date +%Y%m%d)/$TARGET/iot/firmware/sha256.txt
file evidence/$(date +%Y%m%d)/$TARGET/iot/firmware/firmware.bin 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/iot/firmware/file_type.txt
```

## Firmware Analysis
```bash
FIRMWARE=evidence/$(date +%Y%m%d)/$TARGET/iot/firmware/firmware.bin

# Entropy analysis (high entropy = compressed/encrypted)
binwalk -E $FIRMWARE 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/iot/firmware/entropy.txt

# Extract embedded filesystems, archives, and bootloaders
binwalk \
  -e $FIRMWARE \
  -C evidence/$(date +%Y%m%d)/$TARGET/iot/firmware/ \
  --run-as=root \
  2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/iot/firmware/binwalk_extract.log

FS_ROOT=$(find evidence/$(date +%Y%m%d)/$TARGET/iot/firmware/ \
  -name "squashfs-root" -o -name "rootfs" -o -name "_firmware.bin.extracted" \
  2>/dev/null | head -1)
echo "[*] Filesystem root: $FS_ROOT"

# Search for credential files
find $FS_ROOT -name "passwd" -o -name "shadow" -o -name "etc/passwd" 2>/dev/null | \
  xargs cat 2>/dev/null | tee evidence/$(date +%Y%m%d)/$TARGET/iot/fs/passwd.txt

find $FS_ROOT \( -name "*.conf" -o -name "*.config" -o -name "*.cfg" -o -name "*.ini" \) \
  2>/dev/null | head -50 | \
  xargs grep -l "password\|passwd\|secret\|credential" 2>/dev/null | \
  xargs cat 2>/dev/null | tee evidence/$(date +%Y%m%d)/$TARGET/iot/fs/config_creds.txt

# Hardcoded strings analysis
find $FS_ROOT -type f -executable 2>/dev/null | head -20 | \
  xargs strings 2>/dev/null | \
  grep -iE "password|passwd|secret|admin|root|default|1234|key=" | \
  sort -u | tee evidence/$(date +%Y%m%d)/$TARGET/iot/strings/hardcoded_creds.txt

# Find SSL/TLS private keys in firmware
find $FS_ROOT \( -name "*.key" -o -name "*.pem" -o -name "server.key" \) 2>/dev/null | \
  xargs ls -la 2>/dev/null | tee evidence/$(date +%Y%m%d)/$TARGET/iot/fs/ssl_keys.txt

# Find hardcoded API keys and tokens
strings $FIRMWARE 2>/dev/null | \
  grep -iE "(api_key|apikey|token|secret)[[:space:]]*[=:][[:space:]]*['\"]?[A-Za-z0-9_-]{20,}" | \
  sort -u | tee evidence/$(date +%Y%m%d)/$TARGET/iot/strings/api_keys.txt

# Check for debug interfaces
strings $FIRMWARE 2>/dev/null | \
  grep -iE "telnet|ssh|debug|backdoor|uart|console|shell|/bin/sh|/bin/bash" | \
  sort -u | tee evidence/$(date +%Y%m%d)/$TARGET/iot/strings/debug_strings.txt

# Identify web server and scripts
find $FS_ROOT -name "*.cgi" -o -name "*.php" -o -name "*.lua" -o -name "*.asp" 2>/dev/null | \
  tee evidence/$(date +%Y%m%d)/$TARGET/iot/fs/web_scripts.txt
```

## Network Service Enumeration
```bash
DEVICE_IP=$TARGET

# Full port scan (use low timing for IoT — devices crash easily)
nmap -sS -T2 -p- --open \
  -oA evidence/$(date +%Y%m%d)/$TARGET/iot/network/nmap_tcp \
  $DEVICE_IP 2>&1

# Service scan on discovered ports
PORTS=$(grep -oP '\d+/open' evidence/$(date +%Y%m%d)/$TARGET/iot/network/nmap_tcp.gnmap | \
  grep -oP '^\d+' | tr '\n' ',' | sed 's/,$//')
nmap -sV -sC -p $PORTS \
  -oA evidence/$(date +%Y%m%d)/$TARGET/iot/network/nmap_svc \
  $DEVICE_IP 2>&1

# Check for common IoT services
for port in 23 80 443 1883 5683 8080 8443 8883 502 47808 44818; do
  nc -z -w 2 $DEVICE_IP $port 2>/dev/null && echo "Open: $port" || true
done | tee evidence/$(date +%Y%m%d)/$TARGET/iot/network/open_ports.txt
```

## RouterSploit Exploitation
```bash
# RouterSploit automated vulnerability scanner
python3 /opt/routersploit/rsf.py << 'EOF'
use scanners/autopwn
set target $TARGET
run
EOF
# Manual: copy output to evidence

# Common RouterSploit modules:
# use exploits/routers/[vendor]/[model]_[vuln]
# Common modules:
# exploits/cameras/axis/videoserver_exec
# exploits/routers/linksys/1500_2500_rce
# exploits/routers/dlink/dir_300_600_rce
# exploits/generic/multibyte_alignment
# use creds/routers/[vendor] — credential testing
```

## MQTT Protocol Testing
```bash
# MQTT broker discovery
nmap -p 1883,8883 $DEVICE_IP --open 2>&1

# Subscribe to ALL topics (wildcard)
mosquitto_sub -h $DEVICE_IP -p 1883 \
  -t '#' \
  -v \
  -C 100 \
  2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/iot/network/mqtt_all_topics.txt

# Subscribe to system topics (broker info)
mosquitto_sub -h $DEVICE_IP -p 1883 \
  -t '$SYS/#' \
  -v \
  -C 20 \
  2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/iot/network/mqtt_sys.txt

# Publish test message (only if authorized to write)
mosquitto_pub -h $DEVICE_IP -p 1883 \
  -t "test/pentest" \
  -m '{"test": "authorized_pentest"}' \
  2>&1

# MQTT with authentication attempt
mosquitto_sub -h $DEVICE_IP -p 1883 \
  -u admin -P admin \
  -t '#' -v -C 20 2>&1
mosquitto_sub -h $DEVICE_IP -p 1883 \
  -u admin -P password \
  -t '#' -v -C 20 2>&1
```

## Modbus / OT Protocol (PASSIVE ONLY)
```bash
# CRITICAL: OT systems are safety-critical. PASSIVE MONITORING ONLY unless explicitly authorized.
# Any write commands can cause physical damage or safety incidents.

# Modbus TCP service check
nmap -p 502 $TARGET --script modbus-discover 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/iot/network/modbus_discover.txt

# BACnet discovery (building automation)
nmap -sU -p 47808 $TARGET --script bacnet-info 2>&1 | \
  tee evidence/$(date +%Y%m%d)/$TARGET/iot/network/bacnet_info.txt

# Passive Modbus traffic capture (READ ONLY)
tshark -i eth0 \
  -f "host $TARGET and port 502" \
  -w evidence/$(date +%Y%m%d)/$TARGET/iot/network/modbus_capture.pcap \
  -G 60 -W 60 2>&1 &

echo "[!] WARNING: Do NOT send Modbus write commands (FC5,6,15,16) without explicit OT authorization"
echo "[!] Passive monitoring only. Read function codes: FC1,2,3,4"
```

## UART / Hardware Interface
```bash
# UART access guide (requires physical access to PCB)
cat > evidence/$(date +%Y%m%d)/$TARGET/iot/hardware/uart_guide.md << 'UART'
## UART Interface Guide — $TARGET

### Step 1: Identify UART pins on PCB
Look for 3-4 pin header labeled:
- TX (Transmit)
- RX (Receive)
- GND (Ground)
- VCC (3.3V or 5V — DO NOT connect to your adapter)

### Step 2: Identify baud rate
- Try common rates: 9600, 19200, 38400, 57600, 115200, 250000
- Use baudrate.py tool with logic analyzer data
- Most common for consumer IoT: 115200

### Step 3: Connect USB-to-UART adapter
- Adapter TX → Device RX
- Adapter RX → Device TX
- GND ↔ GND
- DO NOT connect VCC

### Step 4: Open serial console
# Linux
screen /dev/ttyUSB0 115200
# OR
minicom -D /dev/ttyUSB0 -b 115200

### Common findings:
- Root shell without password (serial console bypass)
- U-Boot bootloader access (interrupt with 'any key')
- Boot log with filesystem paths and service info
- Debug/manufacturing backdoor accounts

### U-Boot commands (if interrupt successful):
# printenv          → environment variables (often contains credentials)
# setenv bootdelay 0 && saveenv  → disable autoboot
# md.b 0x80000000 0x100         → memory dump (may find keys)
UART
```

## Web Interface Testing
```bash
# Apply web-attacker techniques to embedded web server
# Common IoT admin panel paths:
for path in / /admin /management /setup /config /cgi-bin/admin.cgi \
    /index.html /login.htm /status /diagnostic; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -m 5 "http://$DEVICE_IP$path")
  [ "$STATUS" != "000" ] && echo "$STATUS $path"
done 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/iot/network/web_paths.txt

# Default credential testing
for cred in "admin:admin" "admin:password" "admin:1234" "root:root" \
    "admin:" "user:user" "guest:guest" "admin:default" "admin:$MODEL"; do
  USER=$(echo $cred | cut -d: -f1)
  PASS=$(echo $cred | cut -d: -f2)
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -m 5 \
    -u "$USER:$PASS" "http://$DEVICE_IP/")
  echo "$STATUS admin:$PASS"
done 2>&1 | grep -v "^401\|^000" | \
  tee evidence/$(date +%Y%m%d)/$TARGET/iot/network/default_cred_hits.txt
```

## Evidence Output
Write to `evidence/$(date +%Y%m%d)/$TARGET/iot/iot_findings.md`:
```markdown
## IoT Security Assessment — $TARGET ($DEVICE_MODEL) — $(date -u +%Y-%m-%dT%H:%M:%SZ)

### Device Info
- Model: $DEVICE_MODEL
- Firmware Version: [from /etc/version or web UI]
- Network Services: [list open ports]

### Firmware Analysis
| Finding | Location | Severity | Notes |
|---------|----------|----------|-------|

### Hardcoded Credentials
| Type | Username | Password Location (ref) | Service |
|------|----------|------------------------|---------|

### Protocol Vulnerabilities
| Protocol | Port | Issue | Risk |
|----------|------|-------|------|

### Physical Interface
| Interface | Accessible | Finding |
|-----------|-----------|---------|

## Firmware Analysis Pipeline (Deep)

### Stage 1: Acquisition & Identification
```bash
FIRMWARE=evidence/$(date +%Y%m%d)/$TARGET/iot/firmware/firmware.bin
FWDIR=evidence/$(date +%Y%m%d)/$TARGET/iot/firmware

# Identify firmware format and architecture
binwalk $FIRMWARE 2>&1 | tee $FWDIR/binwalk_id.txt

# Deep entropy analysis — detect encrypted/compressed regions
binwalk -E $FIRMWARE 2>&1 | tee $FWDIR/entropy_analysis.txt
# High entropy (>7.5) across entire file = encrypted firmware (no easy analysis)
# Patchy high entropy = compressed sections (extractable)

# Identify CPU architecture (critical for emulation)
file $FIRMWARE | tee -a $FWDIR/file_type.txt
# Look for ARM, MIPS, x86, PowerPC strings
strings $FIRMWARE | grep -iE "arm|mips|x86|powerpc|sh4|aarch64" | head -20 | tee $FWDIR/arch_hints.txt

# Extract firmware header — look for magic bytes and version info
dd if=$FIRMWARE bs=1 skip=0 count=64 2>/dev/null | xxd | tee $FWDIR/header_hex.txt
strings $FIRMWARE | head -50 | tee $FWDIR/header_strings.txt
```

### Stage 2: Extraction
```bash
# Full extraction with binwalk (best effort)
binwalk -Me $FIRMWARE -C $FWDIR/extracted/ --run-as=root 2>&1 | tee $FWDIR/binwalk_extract.log

# Identify the extracted filesystem root
FS_ROOT=$(find $FWDIR/extracted/ -maxdepth 2 \( -name "squashfs-root" -o -name "rootfs" -o -name "jffs2-root" \) 2>/dev/null | head -1)
[ -z "$FS_ROOT" ] && FS_ROOT=$(find $FWDIR/extracted/ -maxdepth 3 -type d -name "*extracted*" 2>/dev/null | head -1)
echo "[*] Filesystem root: $FS_ROOT"

# If squashfs found, extract with unsquashfs (more reliable than binwalk)
unsquashfs -d $FWDIR/squashfs_root -f $FIRMWARE 2>/dev/null || echo "[!] Not a standalone squashfs or embedded"

# For UBIFS images
ubiformat -h $FIRMWARE 2>/dev/null || true
ubinize -o $FWDIR/ubifs.img -p 4096 -m 2048 -s 512 ubinize.cfg 2>/dev/null || true

# For JFFS2 images
jffs2dump -c -l $FIRMWARE 2>/dev/null || true
```

### Stage 3: Static Analysis with Ghidra
```bash
# Analyze the main firmware binary with Ghidra (headless)
# First find the main executable
MAIN_BIN=$(find $FS_ROOT -type f -executable 2>/dev/null | xargs file 2>/dev/null | grep -i "ELF.*executable" | head -1 | cut -d: -f1)
echo "[*] Main binary: $MAIN_BIN"

# Ghidra headless analysis (CLI)
analyzeHeadless $FWDIR/ghidra_project IoTAnalysis \
  -import $MAIN_BIN \
  -postScript AnalyzeAllFunctions.java \
  -scriptPath /opt/ghidra_scripts/ \
  2>&1 | tee $FWDIR/ghidra_analysis.log

# Export decompiled functions
analyzeHeadless $FWDIR/ghidra_project IoTAnalysis \
  -process $MAIN_BIN \
  -export decompile \
  -output $FWDIR/ghidra_decompiled/ \
  2>&1 | tee -a $FWDIR/ghidra_analysis.log

# Search decompiled code for vulnerabilities
find $FWDIR/ghidra_decompiled/ -name "*.c" -exec grep -l \
  -E "strcpy|strcat|sprintf|gets|system\(|execve|popen" {} \; 2>/dev/null | \
  tee $FWDIR/ghidra_vuln_candidates.txt

# Search for crypto weaknesses in decompiled code
find $FWDIR/ghidra_decompiled/ -name "*.c" -exec grep -l \
  -E "DES|RC4|MD5|AES.*ECB|rand\(|srand" {} \; 2>/dev/null | \
  tee $FWDIR/ghidra_weak_crypto.txt

# Strings analysis on all binaries
find $FS_ROOT -type f -executable 2>/dev/null | while read bin; do
  strings "$bin" 2>/dev/null | grep -iE "password|secret|admin|root|token|api.key"
done | sort -u | tee $FWDIR/all_hardcoded_strings.txt
```

### Stage 4: Firmware Emulation with QEMU
```bash
# Determine architecture from file output
ARCH=$(file $MAIN_BIN 2>/dev/null | grep -oP '(MIPS|ARM|PowerPC|x86|aarch64).*' | head -1)
echo "[*] Architecture: $ARCH"

# Install appropriate QEMU static binary
# For MIPS:
QEMU_BIN="qemu-mips-static"
# For ARM:
# QEMU_BIN="qemu-arm-static"
# For little-endian MIPS:
# QEMU_BIN="qemu-mipsel-static"

# Copy QEMU binary into the chroot
which $QEMU_BIN && cp $(which $QEMU_BIN) $FS_ROOT/usr/bin/

# Fix up the chroot environment
mount -o bind /proc $FS_ROOT/proc
mount -o bind /dev $FS_ROOT/dev
mount -o bind /sys $FS_ROOT/sys

# Chroot into the firmware filesystem
chroot $FS_ROOT /bin/sh 2>&1
# Inside chroot:
# cat /etc/passwd
# cat /etc/shadow  # if readable
# find / -name "*.conf" -exec cat {} \;
# ps aux  # if proc mounted
# ip addr  # network info
# netstat -tlnp  # listening services
# exit

# Alternative: Firmadyne automated emulation
# Firmadyne uses QEMU + kernel for full system emulation
cd /opt/firmadyne/
./scripts/extract.py -b $BINARY_ID -i $FIRMWARE 2>&1 | tee $FWDIR/firmadyne_extract.log
./scripts/infer.py -b $BINARY_ID -i $FIRMWARE 2>&1 | tee $FWDIR/firmadyne_infer.log
./scripts/emulate.py -b $BINARY_ID 2>&1 | tee $FWDIR/firmadyne_emulate.log

# Access emulated firmware via SSH/network
# Firmadyne typically provides: 192.168.x.x network access
nmap -sS -p- -T3 192.168.100.1 2>&1 | tee $FWDIR/firmadyne_nmap.txt
```

### Stage 5: Vulnerability Research on Firmware
```bash
# Identify firmware version and search for known CVEs
FW_VERSION=$(grep -r "version" $FS_ROOT/etc/ 2>/dev/null | head -5)
HW_MODEL=$(strings $FIRMWARE | grep -iE "model.*=|product.*=|hw.ver" | head -5)
echo "[*] Firmware version: $FW_VERSION"
echo "[*] Hardware model: $HW_MODEL"

# Search for known CVEs
searchsploit $VENDOR $MODEL 2>&1 | tee $FWDIR/searchsploit.txt

# Web-based CVE search
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=$(echo $VENDOR+$MODEL | tr ' ' '+')" \
  2>/dev/null | python3 -m json.tool | grep -E "cveId|description" | head -30 | tee $FWDIR/nvd_cves.txt

# Check for known default credentials for vendor
curl -s "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Default-Credentials/iot-default-passwords.txt" \
  2>/dev/null | grep -i "$VENDOR" | tee $FWDIR/vendor_defaults.txt

# Firmware diff analysis (compare two firmware versions for patches)
# Useful for reverse engineering security patches
diff -rq $FWDIR/extracted_v1/ $FWDIR/extracted_v2/ 2>/dev/null | \
  grep -E "differ|Only" | tee $FWDIR/firmware_diff.txt
```

## Protocol Analysis: IoT-Specific

### MQTT Deep Testing
```bash
# MQTT broker enumeration — discover topics and ACL structure
mosquitto_sub -h $DEVICE_IP -p 1883 -t '#' -v -C 200 2>&1 | \
  tee $FWDIR/mqtt_topic_dump.txt

# Topic ACL testing — try subscribing to sensitive topics
for topic in \
  "control/#" "cmd/#" "admin/#" "config" "firmware" \
  "telemetry" "status" "device/config" "device/command"; do
  echo "[*] Testing topic: $topic"
  mosquitto_sub -h $DEVICE_IP -p 1883 -t "$topic" -v -C 5 --quiet 2>&1
done | tee $FWDIR/mqtt_acl_test.txt

# MQTT publish to control topic (ONLY if authorized)
mosquitto_pub -h $DEVICE_IP -p 1883 \
  -t "device/command" \
  -m '{"action":"reboot","reason":"security_test"}' \
  -d 2>&1 | tee $FWDIR/mqtt_publish_test.txt

# MQTT with TLS (port 8883) — certificate analysis
openssl s_client -connect $DEVICE_IP:8883 -servername $DEVICE_IP </dev/null 2>/dev/null | \
  openssl x509 -noout -text 2>/dev/null | tee $FWDIR/mqtt_tls_cert.txt
```

### CoAP Protocol Testing
```bash
# Discover CoAP services (UDP 5683)
nmap -sU -p 5683 --script coap-resources $DEVICE_IP 2>&1 | tee $FWDIR/coap_resources.txt

# Enumerate CoAP resources
coap-client -m GET "coap://$DEVICE_IP/.well-known/core" 2>&1 | tee $FWDIR/coap_discovery.txt

# Test unrestricted PUT method (firmware update without auth)
coap-client -m PUT "coap://$DEVICE_IP/firmware" --payload="test" 2>&1 | tee $FWDIR/coap_put_test.txt

# CoAP DTLS (port 5684)
coap-client -m GET "coaps://$DEVICE_IP/.well-known/core" 2>&1 | tee $FWDIR/coaps_discovery.txt
```

### UPnP Discovery & Exploitation
```bash
# Discover UPnP services
nmap -sS -p 1900,2869,5000 $DEVICE_IP --script upnp-info 2>&1 | tee $FWDIR/upnp_info.txt

# SSDP M-SEARCH discovery
nmap -sU -p 1900 --script ssdprecon $DEVICE_IP 2>&1 | tee $FWDIR/ssdp_discovery.txt

# Download device description XML
LOCATION=$(curl -s "http://$DEVICE_IP:49152/description.xml" -m 5 -o /dev/null -w "%{http_code}" 2>/dev/null && echo "http://$DEVICE_IP:49152/description.xml")
curl -s "http://$DEVICE_IP:49152/description.xml" -m 5 2>/dev/null | xmllint --format - 2>/dev/null | \
  tee $FWDIR/upnp_description.xml

# Common UPnP vulnerabilities
# SOAP action injection — test AddPortMapping for arbitrary port forwarding
# UPnP credential disclosure via GetDeviceSettings
nmap -sS -p 2869,5000 --script upnp-info,http-enum $DEVICE_IP 2>&1 | tee $FWDIR/upnp_vuln_test.txt
```

### Modbus Deep Analysis
```bash
# Modbus device info enumeration (READ ONLY — function codes 1-4)
python3 -c "
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient('$DEVICE_IP', port=502)
client.connect()
# Read Device Identification (FC 43)
result = client.read_device_information(3)
if not result.isError():
    print(f'Vendor: {result.information[0]}')
    print(f'Product: {result.information[1]}')
    print(f'Version: {result.information[2]}')
# Read coils (FC 1) — first 100
result = client.read_coils(0, 100)
if not result.isError():
    print(f'Coils: {result.bits[:100]}')
# Read input registers (FC 4) — first 100
result = client.read_input_registers(0, 100)
if not result.isError():
    print(f'Registers: {result.registers}')
client.close()
" 2>&1 | tee $FWDIR/modbus_enumeration.txt

# [!] WARNING: NEVER use write coils (FC 5), write registers (FC 6),
# or force multiple coils/registers (FC 15/16) unless EXPLICITLY authorized.
# These commands can physically damage equipment or cause safety incidents.
```

## Hardware Hacking: UART/JTAG/SPI

### UART Access Methodology
```bash
# Step 1: Identify UART header on PCB
# Look for 4-pin headers near SoC, labeled: TX, RX, GND, VCC
# VCC is often 3.3V on IoT — DO NOT connect to your adapter VCC

# Step 2: Baud rate identification with Arduino/Bus Pirate
# Common IoT baud rates: 9600, 19200, 38400, 57600, 115200, 250000, 921600
# Use: python3 baudrate.py <serial_port>

# Step 3: Connect USB-TTL adapter
# Pin mapping: Adapter TX → Device RX, Adapter RX → Device TX, GND ↔ GND
# NEVER connect VCC pins together

echo "Serial console connection commands:"
echo "  screen /dev/ttyUSB0 115200,8n1"
echo "  minicom -D /dev/ttyUSB0 -b 115200"
echo "  picocom -b 115200 /dev/ttyUSB0"

# Step 4: Capture boot log (send output to file)
# Set serial terminal to log to file
# Boot messages often reveal: kernel version, init system, mount points, services

# Step 5: U-Boot bootloader access
# Interrupt boot with any key within 1-3 seconds of power-on
# U-Boot commands:
#   printenv                    → all environment variables (credentials, boot args)
#   printenv bootargs           → kernel command line
#   printenv ethaddr            → MAC address
#   printenv ipaddr             → IP configuration
#   md.b 0x80000000 0x1000      → memory dump (look for keys/passwords)
#   setenv bootdelay 5 && saveenv → increase boot delay for future access
#   run bootcmd                 → continue normal boot
```

### JTAG Access
```bash
# JTAG pinout identification (TCK, TMS, TDI, TDO, GND, TRST, VREF)
# Use JTAGulator or Bus Pirate to identify pin mapping

# OpenOCD for JTAG access
# Create target config for the SoC
cat > /tmp/jtag_target.cfg << 'EOF
# Example for ARM Cortex-A SoC
interface ftdi
ftdi_device_desc "Dual RS232-HS"
ftdi_vid_pid 0x0403 0x6010

jtag newtap chip cpu -irlen 4 -expected-id 0xXXXXXXXX
target create chip.arm926ejs arm926ejs -endian little -chain-position chip.cpu
EOF

# Start OpenOCD
openocd -f /tmp/jtag_target.cfg 2>&1 | tee $FWDIR/jtag_session.log &

# Connect via telnet to OpenOCD
# telnet localhost 4444
# Commands:
#   halt                        → halt CPU
#   reg                        → dump all registers
#   mdw 0x80000000 64           → memory dump (word)
#   mdb 0x80000000 64           → memory dump (byte)
#   load_image /tmp/dumper.bin 0x80000000  → load code
#   resume                      → continue execution
#   dump_image /tmp/mem.bin 0x80000000 0x100000 → dump memory to file
EOF

### SPI Flash Extraction
```bash
# SPI flash chips (Winbond, Macronix, etc.) often contain bootloader and config
# Use: flashrom, Bus Pirate, or CH341A programmer

# Identify SPI flash chip (read chip markings)
# Common IoT flash: W25Q32, W25Q64, W25Q128, MX25L3206E

# Dump SPI flash with flashrom
flashrom -p ch341a_spi \
  -r $FWDIR/spi_flash_dump.bin 2>&1 | tee $FWDIR/flashrom_dump.log

# Extract and analyze
binwalk $FWDIR/spi_flash_dump.bin 2>&1 | tee $FWDIR/flash_binwalk.txt
strings $FWDIR/spi_flash_dump.bin | grep -iE "password|secret|admin|key" | \
  tee $FWDIR/flash_strings.txt

# Compare with main firmware dump
# SPI flash often contains: U-Boot env, factory MAC, calibration data, bootloader
diff <(xxd $FIRMWARE | head -50) <(xxd $FWDIR/spi_flash_dump.bin | head -50) 2>/dev/null
```

### Bus Pirate / SPI Flash Programming
```bash
# Bus Pirate as universal serial interface
# Connect to SPI flash: CS, SCK, MISO, MOSI, VCC, GND

# Bus Pirate SPI mode
# Enter terminal, type:
#   m      → mode select
#   5      → SPI
#   1      → 3.3V
#   1      → open drain output (safe)
#   (2)    → 125kHz SPI clock (safe speed)
#   (1)    → clock idle low, read on rising edge (SPI mode 0)

# Dump entire flash (e.g., W25Q64 = 8MB)
#   [0x00 0x03 0x00 0x00 0x00] → READ command (0x03), address 0x000000
# Capture output to file with: (0x00 0x03 0x00 0x00 0x00 0x00 0x00 r:8388608)

# Write to flash (DANGEROUS — backup first!)
#   0x06                     → WRITE ENABLE
#   [0x02 addr data...]     → PAGE PROGRAM
#   0x05                     → READ STATUS REGISTER
#   0x04                     → WRITE DISABLE
```
