#!/usr/bin/env python3
"""
ThreatSwarm Scope MCP Server — JSON-RPC 2.0 over stdio.

Tools:
  scope_check  — validate a command against scope.txt
  scope_list   — list all scope entries
  scope_add    — add a target to scope.txt

No external dependencies — Python stdlib only.
"""

import json
import sys
import ipaddress
import os
import re


# ---------------------------------------------------------------------------
# Scope logic (adapted from core/hooks/scope_check.py)
# ---------------------------------------------------------------------------

SCOPE_FILE_DEFAULT = "./scope.txt"


def load_scope(scope_file: str) -> list:
    """Load scope entries, return list of (kind, entry) tuples."""
    entries = []
    try:
        with open(scope_file, encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    network = ipaddress.ip_network(line, strict=False)
                    entries.append(("network", network))
                    continue
                except ValueError:
                    pass
                try:
                    addr = ipaddress.ip_address(line)
                    entries.append(("network", ipaddress.ip_network(f"{addr}/32", strict=False)))
                    continue
                except ValueError:
                    pass
                entries.append(("domain", line.lower()))
    except FileNotFoundError:
        pass
    return entries


def _extract_targets(command: str) -> tuple:
    """Extract IPv4 addresses and hostnames from a shell command."""
    ip_pattern = (
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.)"
        r"{3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
    )
    ips = re.findall(ip_pattern, command)

    host_pattern = (
        r"(?:(?<=\s)|(?<=\=)|(?<=\t)|(?:^))(?!-)"
        r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+"
        r"(?:[a-zA-Z]{2,})"
        r"(?=\s|$|/|:)"
    )
    hosts = re.findall(host_pattern, command, re.MULTILINE)

    fp_patterns = [
        r"^\d+\.\d+$", r"^\d+\.\d+\.\d+$", r"^v\d",
        r"\.(log|txt|py|sh|md|json|yaml|yml|conf|rule|xml|cfg|ini|toml|"
        r"rb|go|c|cpp|h|so|dll|exe|bin|pcap|cap|zip|gz|tar|bak|old|orig|swp)$",
        r"^\.", r"^localhost\.", r"^[a-z_][a-z_0-9]*\.[a-z_]",
    ]
    filtered = []
    for h in hosts:
        h = h.strip()
        if not h:
            continue
        if any(re.search(p, h, re.IGNORECASE) for p in fp_patterns):
            continue
        filtered.append(h)
    return ips, filtered


def _is_localhost(target: str) -> bool:
    local_vals = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}
    if target in local_vals:
        return True
    try:
        addr = ipaddress.ip_address(target)
        return addr.is_loopback or addr == ipaddress.ip_address("0.0.0.0")
    except ValueError:
        return target.lower() in ("localhost", "localhost.localdomain")


def _is_in_scope(target: str, scope_entries: list) -> bool:
    if _is_localhost(target):
        return True
    try:
        ip = ipaddress.ip_address(target)
        for kind, entry in scope_entries:
            if kind == "network" and ip in entry:
                return True
        return False
    except ValueError:
        pass
    tgt = target.lower().rstrip(".")
    for kind, entry in scope_entries:
        if kind == "domain":
            if tgt == entry or tgt.endswith("." + entry):
                return True
    return False


def _is_network_command(command: str) -> bool:
    tools = [
        r"\bnmap\b", r"\bnuclei\b", r"\bhttpx\b", r"\bferoxbuster\b",
        r"\bffuf\b", r"\bgobuster\b", r"\bnikto\b", r"\bsqlmap\b",
        r"\bhydra\b", r"\bmedusa\b", r"\bcrackmapexec\b", r"\bcme\b",
        r"\bsmbclient\b", r"\brpcclient\b", r"\benum4linux\b",
        r"\bsubfinder\b", r"\bamass\b", r"\btheHarvester\b", r"\bshodan\b",
        r"\bresponder\b", r"\bbettercap\b", r"\barpspoof\b", r"\bntlmrelayx\b",
        r"\bbloodhound\b", r"\bcertipy\b", r"\bevil-winrm\b",
        r"\bwmiexec\b", r"\bpsexec\b", r"\bsmbexec\b",
        r"\bssh\b", r"\bsftp\b", r"\bftp\b", r"\btelnet\b",
        r"\bnetcat\b", r"\bncat\b", r"\bnc\b",
        r"\bcurl\b", r"\bwget\b", r"\bmsfconsole\b", r"\bmsfvenom\b",
        r"\bsliver\b", r"\bairodump-ng\b", r"\baireplay-ng\b",
        r"\breaver\b", r"\bhostapd\b", r"\btcpdump\b", r"\btshark\b",
        r"\bwireshark\b", r"\bfrida\b", r"\badb\b", r"\bmosquitto\b",
        r"\bimpacket-\w+", r"\bkerbrute\b", r"\bldapsearch\b",
        r"\bldapdomaindump\b", r"\brpcscan\b", r"\bsmbmap\b", r"\bnetexec\b",
        r"\bdalfox\b", r"\barjun\b", r"\bgrpcurl\b",
    ]
    cmd_lower = command.lower()
    return any(re.search(p, cmd_lower) for p in tools)


def check_command(command: str, scope_file: str = SCOPE_FILE_DEFAULT) -> dict:
    """Validate a command against scope. Returns result dict."""
    if not _is_network_command(command):
        return {
            "in_scope": True,
            "target": None,
            "match": None,
            "kind": "not_network_command",
            "detail": "Command does not appear to target external hosts",
        }

    entries = load_scope(scope_file)
    if not entries:
        return {
            "in_scope": True,
            "target": None,
            "match": None,
            "kind": "warning",
            "detail": f"Scope file '{scope_file}' is empty or missing — all targets unverified",
        }

    ips, hosts = _extract_targets(command)
    all_targets = ips + hosts
    if not all_targets:
        return {
            "in_scope": True,
            "target": None,
            "match": None,
            "kind": "no_targets",
            "detail": "No network targets extracted from command",
        }

    in_scope_targets = [t for t in all_targets if _is_in_scope(t, entries)]
    out_of_scope = [t for t in all_targets if not _is_in_scope(t, entries)]

    if out_of_scope:
        return {
            "in_scope": False,
            "target": ", ".join(out_of_scope),
            "match": ", ".join(in_scope_targets) if in_scope_targets else None,
            "kind": "violation",
            "detail": f"Target(s) not in scope: {', '.join(out_of_scope)}",
        }

    return {
        "in_scope": True,
        "target": ", ".join(in_scope_targets),
        "match": ", ".join(in_scope_targets),
        "kind": "pass",
        "detail": f"All targets in scope: {', '.join(in_scope_targets)}",
    }


def list_scope(scope_file: str = SCOPE_FILE_DEFAULT) -> dict:
    """List all scope entries."""
    entries = load_scope(scope_file)
    result = []
    for kind, entry in entries:
        if kind == "network":
            result.append({"kind": "network", "value": str(entry)})
        else:
            result.append({"kind": "domain", "value": entry})
    return {"entries": result, "count": len(result), "file": scope_file}


def add_target(target: str, scope_file: str = SCOPE_FILE_DEFAULT) -> dict:
    """Add a target to the scope file."""
    target = target.strip()
    if not target:
        return {"success": False, "error": "Empty target"}

    # Validate
    try:
        ipaddress.ip_network(target, strict=False)
        kind = "network"
    except ValueError:
        try:
            ipaddress.ip_address(target)
            kind = "network"
        except ValueError:
            kind = "domain"

    # Check for duplicates
    entries = load_scope(scope_file)
    for existing_kind, existing_entry in entries:
        if kind == "network" and str(existing_entry) == target:
            return {"success": False, "error": f"Target '{target}' already in scope"}
        if kind == "domain" and existing_entry == target.lower():
            return {"success": False, "error": f"Target '{target}' already in scope"}

    # Append
    with open(scope_file, "a", encoding="utf-8") as fh:
        fh.write(target + "\n")

    return {
        "success": True,
        "target": target,
        "kind": kind,
        "file": scope_file,
    }


# ---------------------------------------------------------------------------
# MCP Protocol (JSON-RPC 2.0 over stdio)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "scope_check",
        "description": (
            "Validate a shell command against the scope file (scope.txt). "
            "Returns whether targets in the command are in scope."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to validate",
                },
                "scope_file": {
                    "type": "string",
                    "description": "Path to scope file (default: ./scope.txt)",
                    "default": "./scope.txt",
                },
            },
            "required": ["command"],
        },
    },
    {
        "name": "scope_list",
        "description": "List all entries in the scope file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scope_file": {
                    "type": "string",
                    "description": "Path to scope file (default: ./scope.txt)",
                    "default": "./scope.txt",
                },
            },
        },
    },
    {
        "name": "scope_add",
        "description": "Add a target (IP, CIDR, or domain) to the scope file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Target to add (IP, CIDR range, or domain)",
                },
                "scope_file": {
                    "type": "string",
                    "description": "Path to scope file (default: ./scope.txt)",
                    "default": "./scope.txt",
                },
            },
            "required": ["target"],
        },
    },
]

HANDLERS = {
    "scope_check": lambda args: check_command(args["command"], args.get("scope_file", SCOPE_FILE_DEFAULT)),
    "scope_list": lambda args: list_scope(args.get("scope_file", SCOPE_FILE_DEFAULT)),
    "scope_add": lambda args: add_target(args["target"], args.get("scope_file", SCOPE_FILE_DEFAULT)),
}


def make_response(result, req_id):
    return {
        "jsonrpc": "2.0",
        "result": result,
        "id": req_id,
    }


def make_error(code, message, req_id):
    return {
        "jsonrpc": "2.0",
        "error": {"code": code, "message": message},
        "id": req_id,
    }


def handle_request(req):
    """Process a single JSON-RPC request."""
    method = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        return make_response({
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "threatswarm-scope-mcp",
                "version": "1.0.0",
            },
        }, req_id)

    if method == "notifications/initialized":
        return None  # No response for notifications

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
                "content": [
                    {"type": "text", "text": json.dumps(result, indent=2)}
                ],
            }, req_id)
        except Exception as exc:
            return make_error(-32603, f"Tool error: {exc}", req_id)

    return make_error(-32601, f"Unknown method: {method}", req_id)


def main():
    """MCP server main loop — read JSON-RPC from stdin, respond to stdout."""
    buf = ""
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
