#!/usr/bin/env python3
"""
ThreatSwarm Scope Library — shared scope checking logic.

Used by both core/hooks/scope_check.py (Claude Code hook) and
integrations/mcp/scope-mcp/server.py (MCP server).

No external dependencies — Python stdlib only.
"""

import ipaddress
import re
from typing import List, Tuple, Optional


SCOPE_FILE_DEFAULT = "./scope.txt"


def load_scope(scope_file: str) -> list:
    """Load scope entries from a scope file.

    Returns list of (kind, entry) tuples where:
      - kind='network', entry=ipaddress.ip_network
      - kind='domain', entry=str (lowercase domain)
    """
    entries = []
    try:
        with open(scope_file, encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                # Try CIDR / IP network first
                try:
                    network = ipaddress.ip_network(line, strict=False)
                    entries.append(("network", network))
                    continue
                except ValueError:
                    pass
                # Try single IP address
                try:
                    addr = ipaddress.ip_address(line)
                    entries.append(("network", ipaddress.ip_network(f"{addr}/32", strict=False)))
                    continue
                except ValueError:
                    pass
                # Treat as domain/hostname
                entries.append(("domain", line.lower()))
    except FileNotFoundError:
        pass
    return entries


def extract_targets(command: str) -> Tuple[List[str], List[str]]:
    """Extract IPv4 addresses and hostnames from a shell command string.

    Returns (ips, hostnames) lists.
    """
    # IPv4 addresses (strict: 0-255 per octet)
    ip_pattern = (
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.)"
        r"{3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
    )
    ips = re.findall(ip_pattern, command)

    # Hostnames / FQDNs — must have at least one dot and valid TLD-like suffix.
    host_pattern = (
        r"(?:(?<=\s)|(?<=\=)|(?<=\t)|(?:^))(?!-)"
        r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+"
        r"(?:[a-zA-Z]{2,})"
        r"(?=\s|$|/|:)"
    )
    hosts = re.findall(host_pattern, command, re.MULTILINE)

    # Filter out common false positives
    false_positive_patterns = [
        r"^\d+\.\d+$",              # version numbers like 3.1
        r"^\d+\.\d+\.\d+$",         # version numbers like 1.4.3
        r"^v\d",                    # v1.2.3
        r"\.(log|txt|py|sh|md|json|yaml|yml|conf|rule|xml|cfg|ini|toml|"
        r"rb|go|c|cpp|h|so|dll|exe|bin|pcap|cap|zip|gz|tar|bak|old|orig|swp)$",
        r"^\.",                     # dotfiles
        r"^localhost\.",            # localhost.localdomain
        r"^[a-z_][a-z_0-9]*\.[a-z_]",  # Python/code attr chains
    ]

    filtered = []
    for h in hosts:
        h = h.strip()
        if not h:
            continue
        if any(re.search(p, h, re.IGNORECASE) for p in false_positive_patterns):
            continue
        filtered.append(h)

    return ips, filtered


def is_localhost(target: str) -> bool:
    """Check if target is a loopback / local address."""
    local_vals = {"localhost", "127.0.0.1", "::1", "0.0.0.0", "127.0.0.0", "127.255.255.255"}
    if target in local_vals:
        return True
    try:
        addr = ipaddress.ip_address(target)
        return addr.is_loopback or addr == ipaddress.ip_address("0.0.0.0")
    except ValueError:
        return target.lower() in ("localhost", "localhost.localdomain")


def check_scope(targets: list, scope_entries: list) -> Tuple[list, list]:
    """Check which targets are in scope.

    Returns (in_scope_targets, out_of_scope_targets).
    """
    in_scope = []
    out_of_scope = []

    for target in targets:
        if is_localhost(target):
            in_scope.append(target)
            continue

        # Try IP-based matching
        found = False
        try:
            ip = ipaddress.ip_address(target)
            for kind, entry in scope_entries:
                if kind == "network" and ip in entry:
                    found = True
                    break
        except ValueError:
            pass

        # Domain matching (exact or subdomain)
        if not found:
            tgt_lower = target.lower().rstrip(".")
            for kind, entry in scope_entries:
                if kind == "domain":
                    if tgt_lower == entry or tgt_lower.endswith("." + entry):
                        found = True
                        break

        if found:
            in_scope.append(target)
        else:
            out_of_scope.append(target)

    return in_scope, out_of_scope


def format_scope_result(target: str, in_scope: bool, match: Optional[str], kind: str) -> dict:
    """Format a scope check result dict.

    Args:
        target: The target string (IP or hostname)
        in_scope: Whether the target is in scope
        match: Matching scope entry (if any)
        kind: Result kind — 'pass', 'violation', 'warning', 'not_network_command', 'no_targets'
    """
    if in_scope:
        return {
            "in_scope": True,
            "target": target,
            "match": match or target,
            "kind": kind,
        }
    return {
        "in_scope": False,
        "target": target,
        "match": match,
        "kind": kind,
    }


def is_network_command(command: str) -> bool:
    """Return True if the command likely makes network connections to external targets."""
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
