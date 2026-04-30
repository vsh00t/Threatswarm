#!/usr/bin/env python3
"""
ThreatSwarm Evidence Capture Utility

Provides chain-of-custody evidence management for pentest engagements:
- Screenshot capture with SHA-256 hashing
- PCAP file tracking and size rotation alerts
- Evidence manifest management
- Chain-of-custody verification

Usage:
    python3 evidence_capture.py screenshot <target> [--evidence-dir ./evidence] [--tool <tool>]
    python3 evidence_capture.py pcap <evidence_dir> [--max-size-mb 500]
    python3 evidence_capture.py verify <evidence_dir>
    python3 evidence_capture.py hash <filepath> [--evidence-type <type>] [--target <target>]
"""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

__version__ = "1.0.0"

MANIFEST_FILE = "evidence_manifest.json"


def sha256_file(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()


def load_manifest(evidence_dir: Path) -> dict:
    """Load evidence manifest from directory. Returns empty dict if not found."""
    manifest_path = evidence_dir / MANIFEST_FILE
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[ERROR] Failed to load manifest: {e}", file=sys.stderr)
            sys.exit(1)
    return {"version": "1.0", "created": None, "entries": []}


def save_manifest(evidence_dir: Path, manifest: dict) -> None:
    """Save evidence manifest to directory."""
    evidence_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = evidence_dir / MANIFEST_FILE
    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
    except OSError as e:
        print(f"[ERROR] Failed to save manifest: {e}", file=sys.stderr)
        sys.exit(1)


def capture_screenshot(target: str, evidence_dir: Path, tool: str = "manual") -> dict:
    """
    Capture a screenshot of the current screen and hash it.

    On macOS: uses /usr/sbin/screencapture
    On Linux: uses scrot (falls back to import from ImageMagick)

    Returns dict with filepath, sha256, and metadata.
    """
    evidence_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir = evidence_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_target = target.replace("/", "_").replace(":", "_").replace(" ", "_")[:60]
    filename = f"{timestamp}_{safe_target}.png"
    filepath = screenshots_dir / filename

    system = platform.system()
    if system == "Darwin":
        cmd = ["/usr/sbin/screencapture", "-x", str(filepath)]
    elif system == "Linux":
        # Try scrot first, fall back to ImageMagick import
        cmd = ["scrot", "-z", str(filepath)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                cmd = ["import", "-window", "root", str(filepath)]
        except FileNotFoundError:
            cmd = ["import", "-window", "root", str(filepath)]
    else:
        print(f"[ERROR] Unsupported platform: {system}. Only macOS and Linux are supported.", file=sys.stderr)
        sys.exit(1)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            print(f"[ERROR] Screenshot capture failed: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print(f"[ERROR] Screenshot tool not found: {cmd[0]}. Install screencapture (macOS), scrot or imagemagick (Linux).", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("[ERROR] Screenshot capture timed out.", file=sys.stderr)
        sys.exit(1)

    if not filepath.exists():
        print(f"[ERROR] Screenshot file was not created: {filepath}", file=sys.stderr)
        sys.exit(1)

    file_hash = sha256_file(filepath)

    entry = append_to_manifest(
        filepath=filepath,
        sha256=file_hash,
        evidence_type="screenshot",
        target=target,
        tool=tool,
        evidence_dir=evidence_dir,
    )

    print(f"[OK] Screenshot captured: {filepath}")
    print(f"     SHA-256: {file_hash}")
    print(f"     Size: {filepath.stat().st_size:,} bytes")

    return entry


def manage_pcap(evidence_dir: Path, max_size_mb: float = 500.0) -> list:
    """
    Check PCAP file sizes in evidence_dir/pcap/.

    Returns list of dicts with filename, size_mb, and status.
    Alerts if any file exceeds max_size_mb.
    """
    pcap_dir = evidence_dir / "pcap"
    if not pcap_dir.exists():
        print(f"[INFO] No pcap directory at {pcap_dir}")
        return []

    results = []
    total_size = 0
    alerts = []

    for pcap_file in sorted(pcap_dir.glob("*.pcap*")):
        size_bytes = pcap_file.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        total_size += size_mb

        status = "OK"
        if size_mb > max_size_mb:
            status = "OVER_LIMIT"
            alerts.append(pcap_file.name)

        results.append({
            "filename": pcap_file.name,
            "size_bytes": size_bytes,
            "size_mb": round(size_mb, 2),
            "status": status,
        })

    if not results:
        print("[INFO] No PCAP files found.")
        return []

    print(f"[PCAP] Found {len(results)} file(s), total {total_size:.2f} MB")

    for r in results:
        status_icon = "⚠️" if r["status"] == "OVER_LIMIT" else "✅"
        print(f"  {status_icon} {r['filename']}: {r['size_mb']:.2f} MB")

    if alerts:
        print(f"\n[WARNING] {len(alerts)} file(s) exceed {max_size_mb} MB limit:")
        for a in alerts:
            print(f"  - {a}")
        print(f"  Recommend: rotate, compress, or split these files.")

    return results


def verify_evidence_chain(evidence_dir: Path) -> dict:
    """
    Verify SHA-256 hashes of all evidence files against evidence_manifest.json.

    Returns dict with total, verified, failed, missing entries.
    """
    manifest = load_manifest(evidence_dir)

    if not manifest.get("entries"):
        print("[INFO] No entries in evidence manifest.")
        return {"total": 0, "verified": 0, "failed": 0, "missing": 0}

    verified = 0
    failed = 0
    missing = 0
    failures = []

    for entry in manifest["entries"]:
        filepath = Path(entry.get("path", ""))
        expected_hash = entry.get("sha256", "")

        # Resolve path — manifest stores paths relative to evidence_dir
        if not filepath.is_absolute():
            filepath = evidence_dir / filepath

        if not filepath.exists():
            missing += 1
            failures.append({"file": str(filepath), "error": "FILE_MISSING"})
            continue

        if not expected_hash:
            verified += 1  # No hash to verify against
            continue

        actual_hash = sha256_file(filepath)
        if actual_hash == expected_hash:
            verified += 1
        else:
            failed += 1
            failures.append({
                "file": str(filepath),
                "error": "HASH_MISMATCH",
                "expected": expected_hash,
                "actual": actual_hash,
            })

    total = len(manifest["entries"])
    print(f"[CHAIN OF CUSTODY] Verification complete:")
    print(f"  Total entries:  {total}")
    print(f"  ✅ Verified:    {verified}")
    print(f"  ❌ Failed:      {failed}")
    print(f"  ⚠️  Missing:    {missing}")

    if failures:
        print(f"\n[ERRORS]:")
        for f in failures:
            if f["error"] == "FILE_MISSING":
                print(f"  MISSING: {f['file']}")
            elif f["error"] == "HASH_MISMATCH":
                print(f"  MISMATCH: {f['file']}")
                print(f"    Expected: {f['expected']}")
                print(f"    Actual:   {f['actual']}")

    result = {"total": total, "verified": verified, "failed": failed, "missing": missing}

    if failed > 0 or missing > 0:
        print(f"\n[CRITICAL] Chain of custody broken — {failed} hash mismatch(es), {missing} missing file(s).")
        result["integrity"] = "BROKEN"
    else:
        print(f"\n[OK] Chain of custody intact.")
        result["integrity"] = "INTACT"

    return result


def append_to_manifest(
    filepath: Path,
    sha256: str,
    evidence_type: str,
    target: str,
    tool: str = "manual",
    evidence_dir: Path = None,
    description: str = None,
    operator: str = None,
) -> dict:
    """
    Append an entry to evidence_manifest.json.

    Returns the created entry dict.
    """
    if evidence_dir is None:
        evidence_dir = Path(filepath).parent.parent

    manifest = load_manifest(evidence_dir)

    if manifest.get("created") is None:
        manifest["created"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Store path relative to evidence_dir
    try:
        rel_path = filepath.relative_to(evidence_dir)
    except ValueError:
        rel_path = filepath

    entry = {
        "id": f"EVD-{len(manifest['entries']) + 1:04d}",
        "path": str(rel_path),
        "sha256": sha256,
        "type": evidence_type,
        "target": target,
        "tool": tool,
        "collected_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "operator": operator or os.environ.get("THREATSWARM_OPERATOR", "unknown"),
    }

    if description:
        entry["description"] = description

    manifest["entries"].append(entry)
    manifest["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    save_manifest(evidence_dir, manifest)

    return entry


def cmd_screenshot(args: argparse.Namespace) -> None:
    """Handle the 'screenshot' subcommand."""
    evidence_dir = Path(args.evidence_dir)
    tool = args.tool or "manual"
    capture_screenshot(args.target, evidence_dir, tool)


def cmd_pcap(args: argparse.Namespace) -> None:
    """Handle the 'pcap' subcommand."""
    evidence_dir = Path(args.evidence_dir)
    manage_pcap(evidence_dir, args.max_size_mb)


def cmd_verify(args: argparse.Namespace) -> None:
    """Handle the 'verify' subcommand."""
    evidence_dir = Path(args.evidence_dir)
    result = verify_evidence_chain(evidence_dir)
    sys.exit(0 if result.get("integrity") == "INTACT" else 1)


def cmd_hash(args: argparse.Namespace) -> None:
    """Handle the 'hash' subcommand — hash a file and optionally add to manifest."""
    filepath = Path(args.filepath)

    if not filepath.exists():
        print(f"[ERROR] File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    file_hash = sha256_file(filepath)
    print(f"[HASH] {filepath}")
    print(f"  SHA-256: {file_hash}")
    print(f"  Size:    {filepath.stat().st_size:,} bytes")

    if args.add_to_manifest:
        evidence_dir = Path(args.evidence_dir)
        entry = append_to_manifest(
            filepath=filepath,
            sha256=file_hash,
            evidence_type=args.evidence_type or "other",
            target=args.target or "unknown",
            evidence_dir=evidence_dir,
        )
        print(f"  Added to manifest: {entry['id']}")


def main():
    parser = argparse.ArgumentParser(
        prog="evidence_capture",
        description="ThreatSwarm Evidence Capture — chain-of-custody evidence management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"evidence_capture {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # screenshot
    p_screenshot = subparsers.add_parser("screenshot", help="Capture screenshot with SHA-256 hash")
    p_screenshot.add_argument("target", help="Target being tested (IP, FQDN, or description)")
    p_screenshot.add_argument("--evidence-dir", default="./evidence", help="Evidence root directory (default: ./evidence)")
    p_screenshot.add_argument("--tool", default="manual", help="Tool being used (default: manual)")
    p_screenshot.set_defaults(func=cmd_screenshot)

    # pcap
    p_pcap = subparsers.add_parser("pcap", help="Check PCAP file sizes and rotation alerts")
    p_pcap.add_argument("evidence_dir", help="Evidence root directory")
    p_pcap.add_argument("--max-size-mb", type=float, default=500.0, help="Max PCAP size in MB before alert (default: 500)")
    p_pcap.set_defaults(func=cmd_pcap)

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify evidence chain of custody against manifest")
    p_verify.add_argument("evidence_dir", help="Evidence root directory")
    p_verify.set_defaults(func=cmd_verify)

    # hash
    p_hash = subparsers.add_parser("hash", help="Hash a file and optionally add to manifest")
    p_hash.add_argument("filepath", help="File to hash")
    p_hash.add_argument("--evidence-type", default="other", help="Evidence type (screenshot, pcap, command_output, etc.)")
    p_hash.add_argument("--target", default="unknown", help="Target the evidence relates to")
    p_hash.add_argument("--evidence-dir", default="./evidence", help="Evidence root directory (default: ./evidence)")
    p_hash.add_argument("--add-to-manifest", action="store_true", help="Add entry to evidence manifest")
    p_hash.set_defaults(func=cmd_hash)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
