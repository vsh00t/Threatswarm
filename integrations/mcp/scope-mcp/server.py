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
import os

# Add project root to path for shared lib imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

# Shared scope logic
from core.lib.scope_lib import (
    load_scope,
    extract_targets,
    is_localhost,
    check_scope,
    format_scope_result,
    is_network_command,
    SCOPE_FILE_DEFAULT,
)

import ipaddress


# ---------------------------------------------------------------------------
# read_message — supports both Content-Length framing and newline-delimited JSON
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# MCP tool implementations
# ---------------------------------------------------------------------------

def check_command_scope(command: str, scope_file: str = SCOPE_FILE_DEFAULT) -> dict:
    """Validate a command against scope. Returns result dict."""
    if not is_network_command(command):
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

    ips, hosts = extract_targets(command)
    all_targets = ips + hosts
    if not all_targets:
        return {
            "in_scope": True,
            "target": None,
            "match": None,
            "kind": "no_targets",
            "detail": "No network targets extracted from command",
        }

    in_scope_targets, out_of_scope = check_scope(all_targets, entries)

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
    "scope_check": lambda args: check_command_scope(args["command"], args.get("scope_file", SCOPE_FILE_DEFAULT)),
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
