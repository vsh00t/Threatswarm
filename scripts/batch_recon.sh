#!/usr/bin/env bash
# batch_recon.sh — Run recon agent against all targets in scope.txt
# Usage: ./scripts/batch_recon.sh [scope_file]
#
# Each target gets its own evidence directory with full recon output.
# Runs sequentially to avoid detection-triggering parallel scans.

set -euo pipefail

SCOPE_FILE="${1:-${SCOPE_FILE:-./scope.txt}}"
EVIDENCE_DIR="${EVIDENCE_DIR:-./evidence}"
DATE=$(date +%Y%m%d)
LOG_FILE="$EVIDENCE_DIR/batch_recon_$(date +%H%M%S).log"

# Validate scope file exists
if [ ! -f "$SCOPE_FILE" ]; then
    echo "[!] Scope file not found: $SCOPE_FILE"
    echo "    Create scope.txt with one target per line (IP, CIDR, or domain)"
    exit 1
fi

# Count non-comment, non-empty targets
TOTAL=$(grep -v '^[[:space:]]*#' "$SCOPE_FILE" | grep -v '^[[:space:]]*$' | wc -l)

if [ "$TOTAL" -eq 0 ]; then
    echo "[!] No targets found in $SCOPE_FILE"
    exit 1
fi

mkdir -p "$EVIDENCE_DIR"

echo "═══════════════════════════════════════════════════════"
echo "  BATCH RECON"
echo "  Scope file:  $SCOPE_FILE"
echo "  Targets:     $TOTAL"
echo "  Date:        $DATE"
echo "  Log:         $LOG_FILE"
echo "  Started:     $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "═══════════════════════════════════════════════════════"

N=0
FAILED=0

while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue

    TARGET="${line// /}"  # Strip spaces
    N=$((N + 1))

    echo ""
    echo "[$N/$TOTAL] Target: $TARGET — $(date -u +%Y-%m-%dT%H:%M:%SZ)"

    # Create evidence directory for this target
    TARGET_SAFE="${TARGET//\//_}"   # Replace / with _ for directory safety
    TARGET_SAFE="${TARGET_SAFE//:/_}"
    TARGET_DIR="$EVIDENCE_DIR/$DATE/$TARGET_SAFE"
    mkdir -p "$TARGET_DIR/nmap" "$TARGET_DIR/web" "$TARGET_DIR/screenshots"

    # Log start
    echo "[$N/$TOTAL] [$TARGET] START $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG_FILE"

    # Run nmap TCP full port scan
    echo "  [*] nmap TCP full scan..."
    if command -v nmap &>/dev/null; then
        nmap -sS -T4 -p- --open \
            -oA "$TARGET_DIR/nmap/tcp_full" \
            "$TARGET" 2>&1 | tail -5 || true
    else
        echo "  [!] nmap not found — skipping TCP scan"
    fi

    # Run nuclei CVE/exposure scan if web port detected
    echo "  [*] nuclei scan (if httpx finds web services)..."
    if command -v httpx &>/dev/null; then
        echo "$TARGET" | httpx -silent -title -tech-detect -status-code \
            -o "$TARGET_DIR/web/httpx.txt" 2>/dev/null || true
    fi

    if [ -s "$TARGET_DIR/web/httpx.txt" ] && command -v nuclei &>/dev/null; then
        nuclei -l "$TARGET_DIR/web/httpx.txt" \
            -t cves/ -t exposures/ -t vulnerabilities/ \
            -severity critical,high,medium \
            -o "$TARGET_DIR/web/nuclei.txt" \
            -silent 2>/dev/null || true
    fi

    # Run subdomain enum if target looks like a domain
    if echo "$TARGET" | grep -qE '^[a-zA-Z]'; then
        echo "  [*] subdomain enumeration..."
        if command -v subfinder &>/dev/null; then
            subfinder -d "$TARGET" -silent \
                -o "$TARGET_DIR/subdomains.txt" 2>/dev/null || true
        fi
    fi

    # Write recon summary stub
    cat > "$TARGET_DIR/recon_summary.md" << SUMMARY
# Recon Summary — $TARGET

**Date:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Operator:** $(whoami 2>/dev/null || echo "unknown")

## Scan Files

| File | Description |
|------|-------------|
| nmap/tcp_full.nmap | TCP full port scan |
| web/httpx.txt | HTTP service fingerprint |
| web/nuclei.txt | CVE/exposure scan results |
| subdomains.txt | Subdomain enumeration |

## Open Ports

\`\`\`
$(grep "open" "$TARGET_DIR/nmap/tcp_full.nmap" 2>/dev/null | head -20 || echo "Run nmap manually — binary not found")
\`\`\`

## Web Services

\`\`\`
$(cat "$TARGET_DIR/web/httpx.txt" 2>/dev/null || echo "No web services detected")
\`\`\`

## Next Steps

Review findings above and run:
  /project:attack $TARGET web
  /project:attack $TARGET exploit [CVE-NUMBER]
SUMMARY

    echo "  [+] Done: $TARGET_DIR/recon_summary.md"
    echo "[$N/$TOTAL] [$TARGET] DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG_FILE"

done < "$SCOPE_FILE"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  BATCH RECON COMPLETE"
echo "  Scanned:   $N targets"
echo "  Failed:    $FAILED targets"
echo "  Evidence:  $EVIDENCE_DIR/$DATE/"
echo "  Log:       $LOG_FILE"
echo "  Finished:  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "═══════════════════════════════════════════════════════"
