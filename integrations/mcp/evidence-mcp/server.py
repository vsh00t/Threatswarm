#!/usr/bin/env python3
"""
ThreatSwarm Evidence MCP Server — JSON-RPC 2.0 over stdio.

Tools:
  evidence_capture_screenshot  — capture screenshot of a target (via import)
  evidence_verify              — verify evidence chain integrity
  evidence_list                — list all evidence files with metadata
  evidence_export              — package evidence into archive

No external dependencies — Python stdlib only.
"""

import json
import sys
import os
import hashlib
import subprocess
import zipfile
import tarfile
import datetime
import glob

# ---------------------------------------------------------------------------
# Evidence helpers
# ---------------------------------------------------------------------------

EVIDENCE_DIR_DEFAULT = "./evidence"


def _ensure_dir(path: str) -> str:
    """Ensure directory exists, return absolute path."""
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)


def _file_hash(filepath: str, algorithm: str = "sha256") -> str:
    """Compute hash of a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_manifest(evidence_dir: str) -> str:
    """Find or create evidence_manifest.json."""
    manifest_path = os.path.join(evidence_dir, "evidence_manifest.json")
    if os.path.exists(manifest_path):
        return manifest_path
    manifest = {
        "version": "1.0",
        "created": datetime.datetime.utcnow().isoformat() + "Z",
        "evidence": [],
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest_path


def _load_manifest(evidence_dir: str) -> dict:
    """Load evidence manifest."""
    path = _find_manifest(evidence_dir)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_manifest(evidence_dir: str, manifest: dict) -> None:
    """Save evidence manifest."""
    path = os.path.join(evidence_dir, "evidence_manifest.json")
    manifest["updated"] = datetime.datetime.utcnow().isoformat() + "Z"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


def capture_screenshot(target: str, evidence_dir: str = EVIDENCE_DIR_DEFAULT) -> dict:
    """Capture a screenshot of a target URL or hostname.

    Tries multiple approaches:
    1. If target is a URL, try curl-based capture (grabs page content, not pixel screenshot)
    2. Uses available system tools (screencapture on macOS, import on Linux)
    3. Falls back to recording the target info as evidence metadata

    Returns path + hash of the captured file.
    """
    abs_dir = _ensure_dir(evidence_dir)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_target = "".join(c if c.isalnum() or c in "-_." else "_" for c in target)
    filename = f"screenshot_{safe_target}_{timestamp}.png"
    filepath = os.path.join(abs_dir, filename)

    captured = False
    capture_method = None

    # Attempt 1: macOS screencapture (URL → open browser → capture)
    if sys.platform == "darwin":
        # For web URLs, open in browser and capture the window
        if target.startswith("http://") or target.startswith("https://"):
            try:
                # Try using macOS screencapture with window option
                subprocess.run(
                    ["screencapture", "-x", "-t", "png", filepath],
                    timeout=30,
                    check=False,
                )
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    captured = True
                    capture_method = "screencapture"
            except (subprocess.TimeoutExpired, OSError):
                pass
        else:
            # For non-URL targets, record as metadata evidence
            capture_method = "metadata_only"

    # Attempt 2: Check for common screenshot tools on Linux
    if not captured and sys.platform.startswith("linux"):
        for tool in ["gnome-screenshot", "scrot", "import"]:
            try:
                if tool == "import":
                    subprocess.run(
                        ["import", "-window", "root", filepath],
                        timeout=30,
                        check=False,
                    )
                else:
                    subprocess.run(
                        [tool, "-f", filepath],
                        timeout=30,
                        check=False,
                    )
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    captured = True
                    capture_method = tool
                    break
            except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
                continue

    # Fallback: create a metadata evidence file
    if not captured:
        filename = f"evidence_{safe_target}_{timestamp}.json"
        filepath = os.path.join(abs_dir, filename)
        evidence_data = {
            "type": "target_capture",
            "target": target,
            "timestamp": timestamp,
            "capture_method": "metadata_only",
            "note": "No screenshot tool available — evidence recorded as metadata",
        }
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(evidence_data, fh, indent=2)
        capture_method = "metadata_only"

    file_hash = _file_hash(filepath)

    # Update manifest
    manifest = _load_manifest(abs_dir)
    manifest["evidence"].append({
        "file": os.path.basename(filepath),
        "path": filepath,
        "hash_sha256": file_hash,
        "target": target,
        "type": "screenshot",
        "capture_method": capture_method,
        "timestamp": timestamp,
    })
    _save_manifest(abs_dir, manifest)

    return {
        "success": True,
        "file": filepath,
        "filename": os.path.basename(filepath),
        "hash_sha256": file_hash,
        "target": target,
        "capture_method": capture_method,
        "timestamp": timestamp,
    }


def verify_evidence(evidence_dir: str = EVIDENCE_DIR_DEFAULT) -> dict:
    """Verify evidence chain integrity — check hashes in manifest."""
    abs_dir = os.path.abspath(evidence_dir)
    manifest_path = os.path.join(abs_dir, "evidence_manifest.json")

    if not os.path.exists(manifest_path):
        return {
            "valid": False,
            "error": f"No evidence manifest found in {abs_dir}",
            "verified": 0,
            "failed": 0,
            "missing": 0,
        }

    manifest = _load_manifest(abs_dir)
    evidence_list = manifest.get("evidence", [])

    verified = 0
    failed = 0
    missing = 0
    details = []

    for item in evidence_list:
        filepath = item.get("path", os.path.join(abs_dir, item.get("file", "")))
        expected_hash = item.get("hash_sha256")

        if not os.path.exists(filepath):
            missing += 1
            details.append({"file": item.get("file"), "status": "missing"})
            continue

        actual_hash = _file_hash(filepath)
        if actual_hash == expected_hash:
            verified += 1
            details.append({"file": item.get("file"), "status": "ok", "hash": actual_hash})
        else:
            failed += 1
            details.append({
                "file": item.get("file"),
                "status": "tampered",
                "expected": expected_hash,
                "actual": actual_hash,
            })

    return {
        "valid": failed == 0 and missing == 0,
        "verified": verified,
        "failed": failed,
        "missing": missing,
        "total": len(evidence_list),
        "manifest": manifest_path,
        "details": details,
    }


def list_evidence(evidence_dir: str = EVIDENCE_DIR_DEFAULT) -> dict:
    """List all evidence files with metadata."""
    abs_dir = os.path.abspath(evidence_dir)
    if not os.path.isdir(abs_dir):
        return {"files": [], "count": 0, "directory": abs_dir, "error": "Directory does not exist"}

    manifest_path = os.path.join(abs_dir, "evidence_manifest.json")
    if os.path.exists(manifest_path):
        manifest = _load_manifest(abs_dir)
        evidence_list = manifest.get("evidence", [])
        for item in evidence_list:
            filepath = item.get("path", os.path.join(abs_dir, item.get("file", "")))
            if os.path.exists(filepath):
                stat = os.stat(filepath)
                item["size_bytes"] = stat.st_size
                item["size_human"] = _human_size(stat.st_size)
            else:
                item["size_bytes"] = 0
                item["missing"] = True
        return {
            "files": evidence_list,
            "count": len(evidence_list),
            "directory": abs_dir,
            "manifest_version": manifest.get("version", "unknown"),
        }

    # No manifest — list files directly
    files = []
    for fname in sorted(os.listdir(abs_dir)):
        fpath = os.path.join(abs_dir, fname)
        if os.path.isfile(fpath):
            stat = os.stat(fpath)
            files.append({
                "file": fname,
                "path": fpath,
                "size_bytes": stat.st_size,
                "size_human": _human_size(stat.st_size),
                "hash_sha256": _file_hash(fpath),
            })
    return {
        "files": files,
        "count": len(files),
        "directory": abs_dir,
        "manifest_version": None,
        "note": "No manifest found — listing raw files",
    }


def export_evidence(
    evidence_dir: str = EVIDENCE_DIR_DEFAULT,
    format: str = "zip",
    output_path: str = None,
) -> dict:
    """Package evidence directory into an archive."""
    abs_dir = os.path.abspath(evidence_dir)
    if not os.path.isdir(abs_dir):
        return {"success": False, "error": f"Directory does not exist: {abs_dir}"}

    if output_path is None:
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_path = f"evidence_export_{timestamp}.{format}"

    abs_output = os.path.abspath(output_path)

    try:
        if format == "zip":
            with zipfile.ZipFile(abs_output, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, filenames in os.walk(abs_dir):
                    for fname in filenames:
                        fpath = os.path.join(root, fname)
                        arcname = os.path.relpath(fpath, abs_dir)
                        zf.write(fpath, arcname)

        elif format == "tar.gz" or format == "tgz":
            with tarfile.open(abs_output, "w:gz") as tf:
                tf.add(abs_dir, arcname=os.path.basename(abs_dir))

        elif format == "tar":
            with tarfile.open(abs_output, "w") as tf:
                tf.add(abs_dir, arcname=os.path.basename(abs_dir))
        else:
            return {"success": False, "error": f"Unsupported format: {format}"}

        file_hash = _file_hash(abs_output)
        file_size = os.path.getsize(abs_output)

        return {
            "success": True,
            "output": abs_output,
            "format": format,
            "hash_sha256": file_hash,
            "size_bytes": file_size,
            "size_human": _human_size(file_size),
        }

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def _human_size(size_bytes: int) -> str:
    """Convert bytes to human-readable size."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


# ---------------------------------------------------------------------------
# MCP Protocol (JSON-RPC 2.0 over stdio)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "evidence_capture_screenshot",
        "description": (
            "Capture a screenshot or evidence record of a target (URL or hostname). "
            "Uses system screenshot tools if available, falls back to metadata recording."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Target URL or hostname to capture",
                },
                "evidence_dir": {
                    "type": "string",
                    "description": "Evidence directory path (default: ./evidence)",
                    "default": "./evidence",
                },
            },
            "required": ["target"],
        },
    },
    {
        "name": "evidence_verify",
        "description": (
            "Verify evidence chain integrity by checking file hashes against the manifest."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "evidence_dir": {
                    "type": "string",
                    "description": "Evidence directory path (default: ./evidence)",
                    "default": "./evidence",
                },
            },
        },
    },
    {
        "name": "evidence_list",
        "description": "List all evidence files with metadata (size, hash, type).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "evidence_dir": {
                    "type": "string",
                    "description": "Evidence directory path (default: ./evidence)",
                    "default": "./evidence",
                },
            },
        },
    },
    {
        "name": "evidence_export",
        "description": "Package all evidence into a zip or tar archive.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "evidence_dir": {
                    "type": "string",
                    "description": "Evidence directory path (default: ./evidence)",
                    "default": "./evidence",
                },
                "format": {
                    "type": "string",
                    "description": "Archive format: zip, tar.gz, tar (default: zip)",
                    "enum": ["zip", "tar.gz", "tar"],
                    "default": "zip",
                },
                "output_path": {
                    "type": "string",
                    "description": "Output file path (default: evidence_export_<timestamp>.<format>)",
                },
            },
        },
    },
]

HANDLERS = {
    "evidence_capture_screenshot": lambda args: capture_screenshot(
        args["target"], args.get("evidence_dir", EVIDENCE_DIR_DEFAULT)
    ),
    "evidence_verify": lambda args: verify_evidence(
        args.get("evidence_dir", EVIDENCE_DIR_DEFAULT)
    ),
    "evidence_list": lambda args: list_evidence(
        args.get("evidence_dir", EVIDENCE_DIR_DEFAULT)
    ),
    "evidence_export": lambda args: export_evidence(
        args.get("evidence_dir", EVIDENCE_DIR_DEFAULT),
        args.get("format", "zip"),
        args.get("output_path"),
    ),
}


def make_response(result, req_id):
    return {"jsonrpc": "2.0", "result": result, "id": req_id}


def make_error(code, message, req_id):
    return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": req_id}


def handle_request(req):
    method = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        return make_response({
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "threatswarm-evidence-mcp",
                "version": "1.0.0",
            },
        }, req_id)

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return make_response({"tools": TOOLS}, req_id)

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        handler = HANDLERS.get(tool_name)
        if not handler:
            return make_error(-32601, f"Unknown tool: {tool_name}", req_id)
        try:
            result = handler(arguments)
            return make_response({
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
            }, req_id)
        except Exception as exc:
            return make_error(-32603, f"Tool error: {exc}", req_id)

    return make_error(-32601, f"Unknown method: {method}", req_id)


def main():
    reader = os.fdopen(sys.stdin.fileno(), "r", encoding="utf-8", buffering=1)
    for line in reader:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as exc:
            response = make_error(-32700, f"Parse error: {exc}", None)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            continue

        response = handle_request(req)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
