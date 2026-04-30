#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ThreatSwarm v2.0 — Kali Linux Prerequisite Installer                  ║
# ║  Installs all tools referenced by the 32 ThreatSwarm agents            ║
# ║  Usage: sudo bash install_kali.sh [--full] [--core] [--check]           ║
# ╚══════════════════════════════════════════════════════════════════════════╝
#
# Modes:
#   --core   Install core tools only (recon, exploit, post-ex, AD) [DEFAULT]
#   --full   Install everything including cloud, mobile, IoT, wireless
#   --check  Only verify what's installed, don't install anything
#
# Requires: Kali Linux (or Debian-based with Kali repos)
# Run as root or with sudo.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

MODE="${1:---core}"
INSTALL=1
[[ "$MODE" == "--check" ]] && INSTALL=0

CATEGORIES=("core")
[[ "$MODE" == "--full" ]] && CATEGORIES=("core" "mobile" "iot" "wireless" "cloud" "compliance" "social" "infra" "reporting" "misc")

PASS=0
FAIL=0
SKIP=0

log_ok()   { echo -e "  ${GREEN}✅${NC} $1"; ((PASS++)) || true; }
log_fail() { echo -e "  ${RED}❌${NC} $1"; ((FAIL++)) || true; }
log_skip() { echo -e "  ${YELLOW}⏭${NC}  $1"; ((SKIP++)) || true; }
log_info() { echo -e "  ${BLUE}ℹ${NC}  $1"; }
log_cat()  { echo -e "\n${CYAN}${BOLD}━━━ $1 ━━━${NC}"; }

check_cmd() {
    local cmd="$1" pkg="$2"
    if command -v "$cmd" &>/dev/null; then
        log_ok "$cmd"
        return 0
    else
        if [[ $INSTALL -eq 1 ]]; then
            echo -e "  ${YELLOW}⬇${NC}  Installing $pkg..."
            if apt-get install -y "$pkg" &>/dev/null; then
                command -v "$cmd" &>/dev/null && log_ok "$cmd (installed)" && return 0
            fi
        fi
        log_fail "$cmd ($pkg)"
        return 1
    fi
}

check_pip() {
    local pkg="$1"
    if python3 -c "import $(echo $pkg | tr '-' '_')" &>/dev/null 2>&1; then
        log_ok "pip:$pkg"
        return 0
    else
        if [[ $INSTALL -eq 1 ]]; then
            echo -e "  ${YELLOW}⬇${NC}  pip install $pkg..."
            if pip3 install "$pkg" &>/dev/null 2>&1; then
                log_ok "pip:$pkg (installed)" && return 0
            fi
        fi
        log_fail "pip:$pkg"
        return 1
    fi
}

check_go() {
    local pkg_path="$1" pkg_name="$2"
    if command -v "$pkg_name" &>/dev/null; then
        log_ok "go:$pkg_name"
        return 0
    else
        if [[ $INSTALL -eq 1 ]]; then
            echo -e "  ${YELLOW}⬇${NC}  go install $pkg_path..."
            if go install "$pkg_path@latest" &>/dev/null 2>&1; then
                log_ok "go:$pkg_name (installed)" && return 0
            fi
        fi
        log_fail "go:$pkg_name"
        return 1
    fi
}

check_gem() {
    local gem_name="$1"
    if gem list -i "$gem_name" &>/dev/null; then
        log_ok "gem:$gem_name"
        return 0
    else
        if [[ $INSTALL -eq 1 ]]; then
            echo -e "  ${YELLOW}⬇${NC}  gem install $gem_name..."
            if gem install "$gem_name" &>/dev/null 2>&1; then
                log_ok "gem:$gem_name (installed)" && return 0
            fi
        fi
        log_fail "gem:$gem_name"
        return 1
    fi
}

check_cargo() {
    local crate_name="$1" bin_name="$2"
    bin_name="${bin_name:-$crate_name}"
    if command -v "$bin_name" &>/dev/null; then
        log_ok "cargo:$bin_name"
        return 0
    else
        if [[ $INSTALL -eq 1 ]]; then
            echo -e "  ${YELLOW}⬇${NC}  cargo install $crate_name..."
            if cargo install "$crate_name" &>/dev/null 2>&1; then
                log_ok "cargo:$bin_name (installed)" && return 0
            fi
        fi
        log_fail "cargo:$bin_name"
        return 1
    fi
}

check_manual() {
    local cmd="$1" url="$2" install_cmd="$3"
    if command -v "$cmd" &>/dev/null; then
        log_ok "$cmd"
        return 0
    else
        if [[ $INSTALL -eq 1 ]]; then
            echo -e "  ${YELLOW}⬇${NC}  $cmd (manual: $url)"
            if eval "$install_cmd" &>/dev/null 2>&1; then
                log_ok "$cmd (installed)" && return 0
            fi
            log_skip "$cmd — install manually: $url"
            return 0
        fi
        log_fail "$cmd (manual install: $url)"
        return 1
    fi
}

# ─── Pre-flight ───
if [[ $EUID -ne 0 ]] && [[ $INSTALL -eq 1 ]]; then
    echo -e "${RED}Run with sudo: sudo bash install_kali.sh $MODE${NC}"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║   ThreatSwarm v2.0 — Kali Linux Prerequisite Installer           ║"
echo "║   Mode: ${MODE}                                                 ║"
echo "╚══════════════════════════════════════════════════════════════════╝"

[[ $INSTALL -eq 0 ]] && log_info "Check mode — no changes will be made"
[[ $INSTALL -eq 1 ]] && log_info "Installing missing tools..."

# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CATEGORY: CORE — Always installed
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_cat "System Dependencies"
check_cmd python3      python3
check_cmd pip3         python3-pip
check_cmd git          git
check_cmd curl         curl
check_cmd wget         wget
check_cmd jq           jq
check_cmd netcat       netcat-openbsd
check_cmd ncat         nmap
check_cmd openssl      openssl
check_cmd ssdeep       ssdeep
check_cmd exiftool     libimage-exiftool-perl
check_cmd file         file
check_cmd unzip        unzip
check_cmd zip          zip

log_cat "Reconnaissance"
check_cmd nmap          nmap
check_cmd masscan       masscan
check_cmd subfinder     subfinder
check_cmd amass         amass
check_cmd httpx         httpx-toolkit
check_cmd nuclei        nuclei
check_cmd feroxbuster   feroxbuster
check_cmd gobuster      gobuster
check_cmd ffuf          ffuf
check_cmd nikto         nikto
check_cmd whatweb       whatweb
check_cmd wpscan        wpscan
check_cmd dnsrecon      dnsrecon
check_cmd fierce        fierce
check_cmd theharvester  theharvester
check_cmd shodan        --skip  # API key required
check_cmd aquatone      aquatone
check_cmd eyewitness    eyewitness

log_cat "Exploitation"
check_cmd sqlmap         sqlmap
check_cmd msfconsole     metasploit-framework
check_cmd msfvenom       metasploit-framework
check_cmd hydra          hydra
check_cmd hashcat        hashcat
check_cmd john           john
check_cmd arjun          --skip  # pip
check_cmd netexec        netexec

log_cat "Active Directory"
check_cmd netexec        netexec
check_cmd impacket-secretsdump  impacket-scripts
check_cmd bloodhound-python      bloodhound-python
check_cmd enum4linux     enum4linux
check_cmd enum4linux-ng  enum4linux-ng
check_cmd smbclient      smbclient
check_cmd rpcclient      smbclient
check_cmd ldapsearch     ldap-utils
check_cmd responder      responder
check_cmd ntlmrelayx     responder

log_cat "Post-Exploitation"
check_cmd linpeas        --skip  # git
check_cmd winpeas        --skip  # git
check_cmd linenum        --skip  # git
check_cmd lazagne        --skip  # git
check_cmd mimikatz       --skip  # Windows only
check_cmd chisel         --skip  # go
check_cmd ligolo         --skip  # go

log_cat "Web Proxies & Traffic"
check_cmd burpsuite      burpsuite
check_cmd mitmproxy      mitmproxy
check_cmd tshark         tshark
check_cmd tcpdump        tcpdump
check_cmd dsniff         dsniff

log_cat "Reverse Engineering"
check_cmd ghidra         ghidra
check_cmd r2             radare2
check_cmd gdb            gdb
check_cmd objdump        binutils
check_cmd strace         strace
check_cmd ltrace         ltrace
check_cmd yara           yara

log_cat "Forensics & Analysis"
check_cmd volatility3    --skip  # pip
check_cmd binwalk        binwalk
check_cmd foremost       foremost
check_cmd bulk_extractor bulk-extractor
check_cmd autopsy        autopsy
check_cmd sleuthkit      sleuthkit

# ─── Full mode categories ───

if [[ "$MODE" == "--full" ]]; then

log_cat "Mobile Security (Android/iOS)"
check_cmd apktool        apktool
check_cmd jadx           jadx
check_cmd objection      --skip  # pip
check_cmd frida          --skip  # pip
check_cmd mobsf          mobsf
check_cmd adb            adb
check_cmd aapt           aapt

log_cat "IoT & Embedded"
check_cmd qemu-system-x86_64 qemu-system-x86
check_cmd firmadyne      --skip  # manual
check_cmd stty           coreutils

log_cat "Wireless Security"
check_cmd airmon-ng      aircrack-ng
check_cmd airodump-ng    aircrack-ng
check_cmd aireplay-ng    aircrack-ng
check_cmd hcxdumptool    hcxdumptool
check_cmd hcxpcapngtool  hcxpcapngtool
check_cmd reaver         reaver
check_cmd pixiewps       pixiewps
check_cmd wifite         wifite
check_cmd hostapd        hostapd
check_cmd dnsmasq        dnsmasq
check_cmd bettercap      bettercap
check_cmd bluetoothctl   bluetooth

log_cat "Cloud Security (AWS/Azure/GCP)"
check_pip pacu
check_pip scoutsuite
check_cmd trivy          trivy
check_cmd kube-bench     kube-bench
check_cmd kubectl        kubectl

log_cat "Compliance & Hardening"
check_cmd lynis          lynis

log_cat "Social Engineering"
check_cmd gophish        --skip  # manual
check_cmd setoolkit      --skip  # social engineering toolkit

log_cat "C2 Frameworks"
check_cmd sliver-client  sliver
# Havoc and Cobalt Strike are commercial/download — mark as manual
check_manual havoc "https://github.com/HavocFramework/Havoc" ""
check_manual cobaltstrike "https://www.cobaltstrike.com/" ""

log_cat "Reporting & Evidence"
check_manual wkhtmltopdf "https://wkhtmltopdf.org/" "apt-get install -y wkhtmltopdf"
check_manual pandoc "https://pandoc.org/installing.html" "apt-get install -y pandoc"
check_manual scrot "https://en.wikipedia.org/wiki/Scrot_(software)" "apt-get install -y scrot"

fi  # end --full

# ─── Pip packages (always attempted in both modes) ───

log_cat "Python Packages"
check_pip impacket
check_pip requests
check_pip colorama
check_pip rich
check_pip pyyaml

if [[ "$MODE" == "--full" ]]; then
    check_pip volatility3
    check_pip ldapdomaindump
    check_pip certipy
    check_pip windapsearch
fi

# ─── Go tools (always attempted) ───

log_cat "Go Tools"
check_go github.com/ffuf/ffuf/v2 ffuf 2>/dev/null || true
check_go github.com/projectdiscovery/subfinder/v2 subfinder 2>/dev/null || true
check_go github.com/projectdiscovery/httpx/cmd/httpx httpx 2>/dev/null || true
check_go github.com/projectdiscovery/nuclei/v3 nuclei 2>/dev/null || true
check_go github.com/projectdiscovery/dnsx/cmd/dnsx dnsx 2>/dev/null || true

if [[ "$MODE" == "--full" ]]; then
    check_go github.com/bettercap/bettercap bettercap 2>/dev/null || true
fi

# ─── ThreatSwarm-specific setup ───

log_cat "ThreatSwarm Setup"
TS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
log_info "Project directory: $TS_DIR"

if [[ -f "$TS_DIR/scope.txt" ]]; then
    log_ok "scope.txt exists"
else
    if [[ $INSTALL -eq 1 ]]; then
        echo "192.168.1.0/24" > "$TS_DIR/scope.txt"
        log_ok "scope.txt created (default: 192.168.1.0/24)"
    else
        log_fail "scope.txt missing"
    fi
fi

if [[ -f "$TS_DIR/scripts/build.py" ]]; then
    log_ok "build.py exists"
    if [[ $INSTALL -eq 1 ]]; then
        log_info "Running build.py --all..."
        python3 "$TS_DIR/scripts/build.py" --all 2>&1 | tail -3
        log_ok "Adapters generated"
    fi
else
    log_fail "build.py missing"
fi

# ─── Summary ───

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Installation Complete                                          ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo -e "║  ${GREEN}✅ Installed/Found:${NC}  $PASS"
echo -e "║  ${RED}❌ Missing:${NC}          $FAIL"
echo -e "║  ${YELLOW}⏭  Skipped (manual):${NC} $SKIP"
echo "╚══════════════════════════════════════════════════════════════════╝"

if [[ $FAIL -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}⚠ Tools marked with ❌ require manual installation.${NC}"
    echo -e "${YELLOW}  Check the tool documentation for installation instructions.${NC}"
fi

if [[ $INSTALL -eq 1 ]]; then
    echo ""
    echo -e "${CYAN}${BOLD}Next steps:${NC}"
    echo "  1. Configure your API keys in ~/.opencode.json or environment"
    echo "  2. Edit scope.txt with your target ranges"
    echo "  3. Run: bash scripts/smoke_test.sh"
    echo "  4. Start: opencode -c $TS_DIR"
    echo ""
    echo -e "${BOLD}Happy hunting. 🜏${NC}"
fi

[[ $FAIL -gt 0 ]] && exit 1 || exit 0
