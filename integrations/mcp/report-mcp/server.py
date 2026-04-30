#!/usr/bin/env python3
"""
ThreatSwarm Report MCP Server — JSON-RPC 2.0 over stdio.

Tools:
  report_generate       — generate a pentest report from evidence
  report_template_list  — list available report templates

No external dependencies — Python stdlib only.
"""

import json
import sys
import os
import datetime

# ---------------------------------------------------------------------------
# Template definitions
# ---------------------------------------------------------------------------

TEMPLATES = {
    "executive": {
        "name": "Executive Summary",
        "description": "High-level summary for management — risk overview, key findings, recommendations",
        "sections": ["Overview", "Risk Summary", "Key Findings", "Recommendations", "Conclusion"],
    },
    "technical": {
        "name": "Technical Findings",
        "description": "Detailed technical report with all findings, steps to reproduce, and remediation",
        "sections": [
            "Scope", "Methodology", "Findings", "Evidence",
            "Remediation Steps", "Tools Used", "Appendix",
        ],
    },
    "compliance": {
        "name": "Compliance Mapping",
        "description": "Findings mapped to compliance frameworks (PCI-DSS, SOC 2, ISO 27001)",
        "sections": [
            "Compliance Scope", "Control Mapping", "Gaps Identified",
            "Remediation Plan", "Evidence References",
        ],
    },
    "full": {
        "name": "Full Pentest Report",
        "description": "Complete pentest report with executive summary + technical details",
        "sections": [
            "Executive Summary", "Scope & Methodology", "Findings (by severity)",
            "Evidence", "Remediation", "Compliance Notes", "Appendix",
        ],
    },
}

EVIDENCE_DIR_DEFAULT = "./evidence"
REPORT_DIR_DEFAULT = "./reports"

# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)


def _load_evidence(evidence_dir: str) -> dict:
    """Load evidence manifest if it exists."""
    manifest_path = os.path.join(evidence_dir, "evidence_manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    # Scan directory for evidence files
    evidence = []
    if os.path.isdir(evidence_dir):
        for fname in sorted(os.listdir(evidence_dir)):
            fpath = os.path.join(evidence_dir, fname)
            if os.path.isfile(fpath):
                evidence.append({"file": fname, "path": fpath})
    return {"evidence": evidence, "note": "No manifest — raw file listing"}


def _severity_counts(evidence: dict) -> dict:
    """Count findings by severity from evidence metadata."""
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for item in evidence.get("evidence", []):
        sev = item.get("severity", "").upper()
        if sev in counts:
            counts[sev] += 1
    return counts


def _build_report(
    report_type: str,
    evidence: dict,
    output_dir: str,
    timestamp: str,
) -> str:
    """Build markdown report content."""
    template = TEMPLATES.get(report_type, TEMPLATES["full"])
    severity = _severity_counts(evidence)

    lines = []
    lines.append(f"# ThreatSwarm — {template['name']}")
    lines.append(f"")
    lines.append(f"**Generated:** {timestamp}")
    lines.append(f"**Type:** {report_type}")
    lines.append(f"**Total Findings:** {sum(severity.values())}")
    lines.append(f"")

    # Severity summary
    lines.append("## Severity Distribution")
    lines.append("")
    for sev, count in severity.items():
        emoji = {
            "CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵", "INFO": "⚪",
        }.get(sev, "➖")
        lines.append(f"- {emoji} **{sev}:** {count}")
    lines.append("")

    # Template sections
    for section in template["sections"]:
        lines.append(f"## {section}")
        lines.append("")

        if section == "Overview" or section == "Executive Summary":
            lines.append("This penetration test was conducted using the ThreatSwarm framework. ")
            lines.append(f"The engagement identified **{sum(severity.values())}** findings across ")
            lines.append(f"{len(severity)} severity levels.")
            lines.append("")

        elif section == "Risk Summary":
            if severity["CRITICAL"] > 0:
                lines.append(f"> ⚠️ **{severity['CRITICAL']} CRITICAL** vulnerabilities require immediate attention.")
            if severity["HIGH"] > 0:
                lines.append(f"> **{severity['HIGH']} HIGH** severity findings should be addressed promptly.")
            lines.append("")

        elif section == "Key Findings" or section == "Findings" or section == "Findings (by severity)":
            items = evidence.get("evidence", [])
            if not items:
                lines.append("_No findings recorded in evidence directory._")
                lines.append("")
            else:
                # Sort by severity
                sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
                items_sorted = sorted(
                    items,
                    key=lambda x: sev_order.get(x.get("severity", "INFO").upper(), 5),
                )
                for item in items_sorted:
                    item_sev = item.get("severity", "INFO").upper()
                    target = item.get("target", item.get("file", "unknown"))
                    title = item.get("title", item.get("type", "Finding"))
                    desc = item.get("detail", item.get("description", ""))
                    lines.append(f"### [{item_sev}] {title}")
                    lines.append(f"**Target:** {target}")
                    if desc:
                        lines.append(f"")
                        lines.append(desc)
                    lines.append("")

        elif section == "Evidence":
            lines.append("Evidence files are referenced from the evidence directory.")
            lines.append("")
            for item in evidence.get("evidence", []):
                fname = item.get("file", "unknown")
                fhash = item.get("hash_sha256", "N/A")
                lines.append(f"- `{fname}` (SHA-256: `{fhash[:16]}...`)")
            lines.append("")

        elif section == "Remediation Steps" or section == "Remediation":
            lines.append("Review each finding and implement the recommended remediation.")
            lines.append("Prioritize CRITICAL and HIGH severity findings.")
            lines.append("")

        elif section == "Methodology":
            lines.append("Testing was conducted using the ThreatSwarm multi-agent framework.")
            lines.append("")
            lines.append("- **Reconnaissance:** Automated and manual reconnaissance")
            lines.append("- **Vulnerability Scanning:** Automated scanning with manual validation")
            lines.append("- **Exploitation:** Verified exploitation of identified vulnerabilities")
            lines.append("- **Post-Exploitation:** Impact assessment and lateral movement analysis")
            lines.append("")

        elif section == "Tools Used":
            lines.append("- ThreatSwarm framework")
            lines.append("- Custom agent tooling")
            lines.append("- Industry-standard security tools (nmap, nuclei, etc.)")
            lines.append("")

        elif section == "Scope":
            lines.append("See scope.txt for the definitive list of in-scope targets.")
            lines.append("")

        elif section == "Compliance Notes":
            lines.append("Cross-reference findings with applicable compliance frameworks.")
            lines.append("")

        elif section == "Appendix":
            lines.append("Evidence files and supporting documentation are in the evidence directory.")
            lines.append("")

        else:
            lines.append("_Section content pending._")
            lines.append("")

    return "\n".join(lines)


def generate_report(
    report_type: str,
    evidence_dir: str = EVIDENCE_DIR_DEFAULT,
    output_dir: str = REPORT_DIR_DEFAULT,
) -> dict:
    """Generate a report from evidence data."""
    if report_type not in TEMPLATES:
        return {
            "success": False,
            "error": f"Unknown report type: {report_type}. Available: {', '.join(TEMPLATES.keys())}",
        }

    abs_output = _ensure_dir(output_dir)
    abs_evidence = os.path.abspath(evidence_dir)
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    evidence = _load_evidence(abs_evidence)

    report_content = _build_report(report_type, evidence, output_dir, timestamp)

    filename = f"report_{report_type}_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join(abs_output, filename)

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(report_content)

    import hashlib
    file_hash = hashlib.sha256(report_content.encode("utf-8")).hexdigest()

    return {
        "success": True,
        "file": filepath,
        "filename": filename,
        "type": report_type,
        "template": TEMPLATES[report_type]["name"],
        "findings_count": sum(_severity_counts(evidence).values()),
        "hash_sha256": file_hash,
        "timestamp": timestamp,
    }


def template_list() -> dict:
    """List available report templates."""
    result = []
    for key, tmpl in TEMPLATES.items():
        result.append({
            "id": key,
            "name": tmpl["name"],
            "description": tmpl["description"],
            "sections": tmpl["sections"],
        })
    return {"templates": result, "count": len(result)}


# ---------------------------------------------------------------------------
# MCP Protocol (JSON-RPC 2.0 over stdio)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "report_generate",
        "description": "Generate a pentest report from evidence. Supported types: executive, technical, compliance, full.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Report type",
                    "enum": ["executive", "technical", "compliance", "full"],
                },
                "evidence_dir": {
                    "type": "string",
                    "description": "Evidence directory (default: ./evidence)",
                    "default": "./evidence",
                },
                "output_dir": {
                    "type": "string",
                    "description": "Output directory for report (default: ./reports)",
                    "default": "./reports",
                },
            },
            "required": ["type"],
        },
    },
    {
        "name": "report_template_list",
        "description": "List available report templates with descriptions and sections.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]

HANDLERS = {
    "report_generate": lambda args: generate_report(
        args["type"],
        args.get("evidence_dir", "./evidence"),
        args.get("output_dir", REPORT_DIR_DEFAULT),
    ),
    "report_template_list": lambda args: template_list(),
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
                "name": "threatswarm-report-mcp",
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


def read_message(reader):
    """Read a JSON-RPC message, supporting both Content-Length framing and newline-delimited JSON."""
    line = reader.readline()
    if not line:
        return None
    line = line.strip()

    # Check for Content-Length header
    if line.lower().startswith("content-length:"):
        length = int(line.split(":")[1].strip())
        # Read the empty line separator
        reader.readline()
        # Read exactly length bytes
        data = reader.read(length)
        return json.loads(data)

    # Fallback: newline-delimited JSON
    if line:
        return json.loads(line)
    return None


def main():
    reader = os.fdopen(sys.stdin.fileno(), "r", encoding="utf-8", buffering=1)

    while True:
        req = read_message(reader)
        if req is None:
            break
        response = handle_request(req)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
