#!/usr/bin/env python3
"""
ThreatSwarm → OpenProject Sync

Syncs findings from ThreatSwarm evidence_manifest.json to OpenProject work packages
via the OpenProject REST API (v3).

Usage:
  python3 sync.py --base-url https://openproject.example.com \
                  --api-key YOUR_API_KEY \
                  --project-id 42 \
                  [--evidence-dir ./evidence] \
                  [--type-id 7] \
                  [--dry-run]

No external dependencies — Python stdlib only (json, urllib, argparse, os).
"""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin


DEFAULT_EVIDENCE_DIR = "./evidence"
DEFAULT_TYPE_ID = 7  # "Task" type in OpenProject — adjust to your instance


def _request(
    base_url: str,
    api_key: str,
    method: str,
    path: str,
    body: dict = None,
) -> dict:
    """Make an API request to OpenProject."""
    url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"OpenProject API error {exc.code}: {error_body}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"Connection error: {exc.reason}") from exc


def load_manifest(evidence_dir: str) -> dict:
    """Load evidence manifest from the ThreatSwarm evidence directory."""
    manifest_path = os.path.join(evidence_dir, "evidence_manifest.json")
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Evidence manifest not found: {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def finding_to_work_package(finding: dict, project_id: int, type_id: int) -> dict:
    """Convert a ThreatSwarm finding to an OpenProject work package payload."""
    severity = finding.get("severity", "INFO").upper()
    target = finding.get("target", finding.get("file", "Unknown target"))
    title = finding.get("title", finding.get("type", "Finding"))
    detail = finding.get("detail", finding.get("description", ""))
    timestamp = finding.get("timestamp", "")
    evidence_file = finding.get("file", "")
    evidence_hash = finding.get("hash_sha256", "")

    # Map severity to OpenProject priority (higher = more important)
    priority_map = {
        "CRITICAL": 8,
        "HIGH": 7,
        "MEDIUM": 5,
        "LOW": 3,
        "INFO": 1,
    }
    priority = priority_map.get(severity, 1)

    # Build description in OpenProject wiki/markdown format
    description_parts = [
        f"**Severity:** {severity}",
        f"**Target:** `{target}`",
    ]
    if detail:
        description_parts.append(f"**Description:** {detail}")
    if timestamp:
        description_parts.append(f"**Discovered:** {timestamp}")
    if evidence_file:
        description_parts.append(f"**Evidence File:** `{evidence_file}`")
    if evidence_hash:
        description_parts.append(f"**Evidence Hash (SHA-256):** `{evidence_hash}`")
    description_parts.append("")
    description_parts.append("---")
    description_parts.append("*Synced from ThreatSwarm evidence manifest*")

    subject = f"[{severity}] {title} — {target}"

    return {
        "subject": subject,
        "description": {
            "format": "markdown",
            "raw": "\n".join(description_parts),
        },
        "_links": {
            "type": {"href": f"/api/v3/types/{type_id}"},
            "project": {"href": f"/api/v3/projects/{project_id}"},
        },
        "priority": priority,
    }


def sync_findings(
    base_url: str,
    api_key: str,
    project_id: int,
    evidence_dir: str,
    type_id: int,
    dry_run: bool = False,
) -> dict:
    """Sync all findings from evidence manifest to OpenProject."""
    manifest = load_manifest(evidence_dir)
    findings = manifest.get("evidence", [])

    if not findings:
        return {"synced": 0, "skipped": 0, "errors": [], "message": "No findings in manifest"}

    synced = 0
    skipped = 0
    errors = []
    results = []

    for finding in findings:
        wp_payload = finding_to_work_package(finding, project_id, type_id)

        if dry_run:
            print(f"[DRY-RUN] Would create: {wp_payload['subject']}", file=sys.stderr)
            synced += 1
            results.append({"subject": wp_payload["subject"], "status": "dry-run"})
            continue

        try:
            response = _request(
                base_url, api_key, "POST", "/api/v3/work_packages", wp_payload
            )
            wp_id = response.get("id", "?")
            wp_url = response.get("_links", {}).get("self", {}).get("href", "")
            synced += 1
            results.append({
                "subject": wp_payload["subject"],
                "status": "created",
                "work_package_id": wp_id,
                "url": wp_url,
            })
            print(f"[OK] Created WP#{wp_id}: {wp_payload['subject']}", file=sys.stderr)

        except RuntimeError as exc:
            skipped += 1
            errors.append({"subject": wp_payload["subject"], "error": str(exc)})
            print(f"[ERROR] {wp_payload['subject']}: {exc}", file=sys.stderr)

    return {
        "synced": synced,
        "skipped": skipped,
        "total": len(findings),
        "errors": errors,
        "results": results,
    }


def verify_connection(base_url: str, api_key: str) -> dict:
    """Verify OpenProject API connection and credentials."""
    try:
        response = _request(base_url, api_key, "GET", "/api/v3")
        return {
            "connected": True,
            "instance": response.get("_type", "unknown"),
            "version": response.get("_links", {}).get("self", {}).get("href", ""),
        }
    except RuntimeError as exc:
        return {"connected": False, "error": str(exc)}


def main():
    parser = argparse.ArgumentParser(
        description="Sync ThreatSwarm findings to OpenProject work packages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify connection
  python3 sync.py --base-url https://openproject.example.com --api-key KEY --verify

  # Dry run
  python3 sync.py --base-url https://openproject.example.com --api-key KEY --project-id 42 --dry-run

  # Sync findings
  python3 sync.py --base-url https://openproject.example.com --api-key KEY --project-id 42 --evidence-dir ./evidence
        """,
    )
    parser.add_argument("--base-url", required=True, help="OpenProject base URL")
    parser.add_argument("--api-key", required=True, help="OpenProject API key")
    parser.add_argument("--project-id", type=int, required=True, help="OpenProject project ID")
    parser.add_argument("--evidence-dir", default=DEFAULT_EVIDENCE_DIR, help="ThreatSwarm evidence directory")
    parser.add_argument("--type-id", type=int, default=DEFAULT_TYPE_ID, help="OpenProject work package type ID (default: 7 = Task)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating work packages")
    parser.add_argument("--verify", action="store_true", help="Verify API connection and exit")

    args = parser.parse_args()

    if args.verify:
        result = verify_connection(args.base_url, args.api_key)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["connected"] else 1)

    result = sync_findings(
        base_url=args.base_url,
        api_key=args.api_key,
        project_id=args.project_id,
        evidence_dir=args.evidence_dir,
        type_id=args.type_id,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
