#!/usr/bin/env python3
"""
ThreatSwarm Scope Validator

Validates scope definitions (scope.txt and scope.yaml) for pentest engagements.
Checks for overlapping CIDR ranges, invalid domain formats, and subnet size warnings.

Usage:
    python3 scope_validate.py [--scope-file scope.txt] [--scope-yaml scope.yaml]
    python3 scope_validate.py --scope-file scope.txt
"""

import argparse
import ipaddress
import re
import sys
from pathlib import Path

__version__ = "1.0.0"

# Domain validation regex (RFC 1035 compliant, practical subset)
DOMAIN_PATTERN = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)"
    r"+(?:[a-zA-Z]{2,})$"
)

# Wildcard domain pattern (*.example.com)
WILDCARD_DOMAIN_PATTERN = re.compile(
    r"^\*\.(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)"
    r"+(?:[a-zA-Z]{2,})$"
)

# Default subnet size warning threshold
DEFAULT_HOST_WARNING = 1024


class ScopeEntry:
    """Represents a single scope entry (network or domain)."""

    def __init__(self, raw: str, kind: str, line_num: int):
        self.raw = raw.strip()
        self.kind = kind  # "network" or "domain"
        self.line_num = line_num
        self.network = None
        self.domain = None
        self.errors = []

        if kind == "network":
            try:
                self.network = ipaddress.ip_network(self.raw, strict=False)
            except ValueError:
                self.errors.append(f"Invalid network/CIDR: '{self.raw}'")
        elif kind == "domain":
            self.domain = self.raw.lower()
            if not DOMAIN_PATTERN.match(self.domain) and not WILDCARD_DOMAIN_PATTERN.match(self.domain):
                self.errors.append(f"Invalid domain format: '{self.raw}'")

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    @property
    def host_count(self) -> int:
        if self.network:
            return self.network.num_addresses
        return 0

    def __repr__(self) -> str:
        return f"ScopeEntry({self.kind}: {self.raw})"


def classify_entry(line: str) -> str:
    """Classify a scope entry line as network, domain, or unknown."""
    line = line.strip()

    # Try CIDR / IP
    try:
        ipaddress.ip_network(line, strict=False)
        return "network"
    except ValueError:
        pass

    # Try single IP
    try:
        ipaddress.ip_address(line)
        return "network"
    except ValueError:
        pass

    # Domain patterns
    if DOMAIN_PATTERN.match(line) or WILDCARD_DOMAIN_PATTERN.match(line):
        return "domain"

    # FQDN with port or path (strip and retry)
    cleaned = re.split(r"[:/]", line)[0]
    if DOMAIN_PATTERN.match(cleaned):
        return "domain"

    return "unknown"


def parse_scope_txt(scope_file: Path) -> list:
    """Parse scope.txt into ScopeEntry objects."""
    entries = []
    if not scope_file.exists():
        return entries

    with open(scope_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            kind = classify_entry(line)
            entry = ScopeEntry(line, kind, line_num)
            entries.append(entry)

    return entries


def parse_scope_yaml(scope_file: Path) -> list:
    """
    Parse scope.yaml (simple YAML subset, no external deps).

    Expected format:
      networks:
        - 10.0.0.0/24
        - 192.168.1.0/24
      domains:
        - example.com
        - *.test.example.com
      out_of_scope:
        - 10.0.0.100
    """
    entries = []
    if not scope_file.exists():
        return entries

    try:
        content = scope_file.read_text(encoding="utf-8")
    except OSError:
        return entries

    # Simple YAML parsing for our specific format
    current_section = None
    is_oos = False

    for line_num, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        # Section header
        section_match = re.match(r"^(networks|domains|hosts|targets|out_of_scope|exclusions):\s*$", stripped, re.IGNORECASE)
        if section_match:
            current_section = section_match.group(1).lower()
            is_oos = current_section in ("out_of_scope", "exclusions")
            continue

        # List item
        if stripped.startswith("- "):
            value = stripped[2:].strip()
            if not value:
                continue

            # Remove inline comments
            comment_pos = value.find(" #")
            if comment_pos != -1:
                value = value[:comment_pos].strip()

            kind = classify_entry(value)
            entry = ScopeEntry(value, kind, line_num)
            entry._is_out_of_scope = is_oos  # type: ignore
            entries.append(entry)
            continue

        # Key-value (e.g., cidr: 10.0.0.0/24)
        kv_match = re.match(r"^\s*[-\w]+\s*:\s*(.+)$", stripped)
        if kv_match and current_section:
            value = kv_match.group(1).strip().strip('"\'')
            kind = classify_entry(value)
            entry = ScopeEntry(value, kind, line_num)
            entry._is_out_of_scope = is_oos  # type: ignore
            entries.append(entry)

    return entries


def check_cidr_overlaps(entries: list) -> list:
    """Check for overlapping CIDR ranges. Returns list of overlap tuples."""
    networks = []
    for entry in entries:
        if entry.kind == "network" and entry.network and entry.is_valid:
            networks.append(entry)

    overlaps = []
    for i in range(len(networks)):
        for j in range(i + 1, len(networks)):
            a = networks[i].network
            b = networks[j].network

            if a.overlaps(b):
                # Determine which is the subnet
                if a.subnet_of(b):
                    smaller, larger = networks[i], networks[j]
                elif b.subnet_of(a):
                    smaller, larger = networks[j], networks[i]
                elif a == b:
                    smaller, larger = networks[i], networks[j]
                else:
                    smaller, larger = networks[i], networks[j]

                overlaps.append((smaller, larger))

    return overlaps


def check_subnet_sizes(entries: list, max_hosts: int = DEFAULT_HOST_WARNING) -> list:
    """Check for subnets larger than the warning threshold. Returns list of entries."""
    warnings = []
    for entry in entries:
        if entry.kind == "network" and entry.network and entry.is_valid:
            if entry.network.num_addresses > max_hosts:
                warnings.append(entry)
    return warnings


def check_domain_overlaps(entries: list) -> list:
    """Check for overlapping domain entries (subdomain of another). Returns list."""
    domains = []
    for entry in entries:
        if entry.kind == "domain" and entry.domain and entry.is_valid:
            domains.append(entry)

    overlaps = []
    for i in range(len(domains)):
        for j in range(i + 1, len(domains)):
            a = domains[i].domain.rstrip(".")
            b = domains[j].domain.rstrip(".")

            # Check if one is a subdomain of the other
            if a == b:
                overlaps.append((domains[i], domains[j], "duplicate"))
            elif a.endswith("." + b):
                overlaps.append((domains[i], domains[j], "subdomain"))
            elif b.endswith("." + a):
                overlaps.append((domains[j], domains[i], "subdomain"))

    return overlaps


def _is_yaml_content(content: str) -> bool:
    """Heuristic: check if content looks like YAML (has section headers with colons)."""
    for line in content.splitlines()[:20]:
        stripped = line.strip()
        if stripped.endswith(":") and not stripped.startswith("#") and " " not in stripped.rstrip(":"):
            return True
    return False


def validate(args: argparse.Namespace) -> None:
    """Run all validation checks."""
    errors = 0
    warnings = 0
    all_entries = []

    # Parse scope.txt
    scope_file = Path(args.scope_file)
    if scope_file.exists():
        # Auto-detect format: if the file looks like YAML, use YAML parser
        try:
            content = scope_file.read_text(encoding="utf-8")[:2000]
        except OSError:
            content = ""

        if scope_file.suffix in (".yaml", ".yml") or _is_yaml_content(content):
            txt_entries = parse_scope_yaml(scope_file)
        else:
            txt_entries = parse_scope_txt(scope_file)
        print(f"[SCOPE] Parsed {scope_file}: {len(txt_entries)} entries")
        all_entries.extend(txt_entries)
    else:
        print(f"[WARN] Scope file not found: {scope_file}")
        warnings += 1

    # Parse scope.yaml (if specified or exists, and not already parsed above)
    yaml_file = Path(args.scope_yaml) if args.scope_yaml else None
    if yaml_file is None:
        # Auto-detect
        for candidate in [scope_file.parent / "scope.yaml", scope_file.parent / "scope.yml"]:
            if candidate.exists() and candidate.resolve() != scope_file.resolve():
                yaml_file = candidate
                break

    if yaml_file and yaml_file.exists():
        yaml_entries = parse_scope_yaml(yaml_file)
        print(f"[SCOPE] Parsed {yaml_file}: {len(yaml_entries)} entries")
        all_entries.extend(yaml_entries)

    if not all_entries:
        print("[WARN] No scope entries found to validate.")
        return

    print(f"[SCOPE] Total entries to validate: {len(all_entries)}\n")

    # Section: Invalid entries
    print("=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    invalid_entries = [e for e in all_entries if not e.is_valid]
    if invalid_entries:
        print(f"\n❌ INVALID ENTRIES ({len(invalid_entries)}):\n")
        for entry in invalid_entries:
            source = args.scope_file if hasattr(entry, '_is_out_of_scope') is False else (args.scope_yaml or args.scope_file)
            print(f"  Line {entry.line_num}: {entry.raw}")
            for err in entry.errors:
                print(f"    ⤷ {err}")
            errors += 1
    else:
        print(f"\n✅ All entries have valid format")

    # Section: CIDR overlaps
    cidr_overlaps = check_cidr_overlaps(all_entries)
    if cidr_overlaps:
        print(f"\n⚠️  CIDR OVERLAPS ({len(cidr_overlaps)}):\n")
        for a, b in cidr_overlaps:
            print(f"  '{a.raw}' (line {a.line_num}) overlaps with '{b.raw}' (line {b.line_num})")
            print(f"    {a.network} ∩ {b.network}")
        warnings += len(cidr_overlaps)
    else:
        print(f"\n✅ No CIDR range overlaps detected")

    # Section: Subnet size warnings
    large_subnets = check_subnet_sizes(all_entries, args.host_warning)
    if large_subnets:
        print(f"\n⚠️  LARGE SUBNETS (>{args.host_warning} hosts) ({len(large_subnets)}):\n")
        for entry in large_subnets:
            print(f"  Line {entry.line_num}: {entry.raw} — {entry.host_count:,} hosts")
        warnings += len(large_subnets)
    else:
        print(f"\n✅ All subnets are within size limits (≤{args.host_warning} hosts)")

    # Section: Domain overlaps
    domain_overlaps = check_domain_overlaps(all_entries)
    if domain_overlaps:
        print(f"\n⚠️  DOMAIN OVERLAPS ({len(domain_overlaps)}):\n")
        for a, b, kind in domain_overlaps:
            print(f"  '{a.raw}' (line {a.line_num}) — {kind} of '{b.raw}' (line {b.line_num})")
        warnings += len(domain_overlaps)
    else:
        print(f"\n✅ No overlapping domain entries detected")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"SUMMARY: {errors} error(s), {warnings} warning(s)")
    print(f"{'=' * 60}")

    # Statistics
    by_kind = {}
    for entry in all_entries:
        by_kind[entry.kind] = by_kind.get(entry.kind, 0) + 1
    print(f"  Entries by type: {', '.join(f'{k}: {v}' for k, v in sorted(by_kind.items()))}")

    valid_entries = [e for e in all_entries if e.kind == "network" and e.is_valid]
    total_hosts = sum(e.host_count for e in valid_entries)
    print(f"  Total in-scope hosts: {total_hosts:,}")

    if errors > 0:
        sys.exit(1)
    elif warnings > 0:
        sys.exit(0)
    else:
        print("\n✅ Scope validation passed with no issues.")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        prog="scope_validate",
        description="ThreatSwarm Scope Validator — validate scope.txt and scope.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"scope_validate {__version__}")
    parser.add_argument("--scope-file", default="./scope.txt",
                        help="Path to scope.txt (default: ./scope.txt)")
    parser.add_argument("--scope-yaml", default=None,
                        help="Path to scope.yaml (auto-detected if omitted)")
    parser.add_argument("--host-warning", type=int, default=DEFAULT_HOST_WARNING,
                        help=f"Warn if subnet has more than N hosts (default: {DEFAULT_HOST_WARNING})")

    args = parser.parse_args()
    validate(args)


if __name__ == "__main__":
    main()
