#!/usr/bin/env python3
"""
ThreatSwarm Scope Checker — Dual-mode hook and CLI tool.

Modes:
  1. Claude Code hook (default): reads JSON from stdin per Claude Code hooks spec.
     Exit code 0 = allow, exit code 2 = block tool call + show stderr to Claude.
  2. CLI mode (--check "<command>"): validates a shell command against scope.txt.
     Exit code 0 = pass, exit code 2 = fail. Useful for non-Claude integrations.
  3. CLI mode (--version): print version and exit.

Environment variables:
  SCOPE_FILE  — path to scope definition file (default: ./scope.txt)
"""

import json
import sys
import os
import argparse

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

__version__ = "1.0.0"


def is_in_scope(target: str, scope_entries: list) -> bool:
    """Check if target (IP string or hostname) is in scope. Backward-compatible wrapper."""
    if is_localhost(target):
        return True
    in_scope, _ = check_scope([target], scope_entries)
    return len(in_scope) > 0


def check_command(command: str, scope_file: str = SCOPE_FILE_DEFAULT) -> tuple:
    """
    Validate a command against scope rules.
    Returns (allowed: bool, message: str).
    Exit code 0 = pass, 2 = fail.
    """
    if not is_network_command(command):
        return True, "PASS: not a network command"

    scope_entries = load_scope(scope_file)

    if not scope_entries:
        return True, (
            f"WARNING: scope.txt at '{scope_file}' is empty or missing. "
            "All targets are currently unverified."
        )

    ips, hosts = extract_targets(command)
    all_targets = ips + hosts

    if not all_targets:
        return True, "PASS: no network targets found in command"

    violations = []
    for target in all_targets:
        if not is_in_scope(target, scope_entries):
            violations.append(target)

    if violations:
        msg = (
            f"SCOPE VIOLATION\n"
            f"Target(s) not in {scope_file}: {', '.join(violations)}\n"
            f"Command was: {command[:200]}{'...' if len(command) > 200 else ''}"
        )
        return False, msg

    return True, f"PASS: all targets in scope ({', '.join(all_targets)})"


def run_hook_mode():
    """Claude Code hook mode: reads JSON from stdin."""
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, EOFError, ValueError):
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    if tool_name != 'Bash':
        sys.exit(0)

    command = data.get('tool_input', {}).get('command', '')
    if not command:
        sys.exit(0)

    if not is_network_command(command):
        sys.exit(0)

    scope_file = os.environ.get('SCOPE_FILE', SCOPE_FILE_DEFAULT)
    scope_entries = load_scope(scope_file)

    if not scope_entries:
        print(
            f"[SCOPE WARNING] scope.txt at '{scope_file}' is empty or missing. "
            "All targets are currently unverified. Add targets to scope.txt.",
            file=sys.stderr
        )
        sys.exit(0)

    ips, hosts = extract_targets(command)
    all_targets = ips + hosts

    if not all_targets:
        sys.exit(0)

    violations = []
    for target in all_targets:
        if not is_in_scope(target, scope_entries):
            violations.append(target)

    if violations:
        msg = (
            f"SCOPE VIOLATION BLOCKED\n"
            f"Target(s) not in {scope_file}: {', '.join(violations)}\n"
            f"Add the target(s) to scope.txt before running.\n"
            f"Command was: {command[:200]}{'...' if len(command) > 200 else ''}"
        )
        print(msg, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="ThreatSwarm Scope Checker — validate commands against scope.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  (no args)     Claude Code hook mode (reads JSON from stdin)
  --check CMD   CLI mode: validate a shell command string
  --version     Print version and exit

Exit codes:
  0  Pass / allow
  2  Scope violation / block
        """
    )
    parser.add_argument('--check', metavar='CMD', help='Validate a shell command against scope.txt')
    parser.add_argument('--version', action='version', version=f'scope_check {__version__}')
    parser.add_argument('--scope-file', default=os.environ.get('SCOPE_FILE', SCOPE_FILE_DEFAULT),
                        help='Path to scope file (default: $SCOPE_FILE or ./scope.txt)')

    args = parser.parse_args()

    if args.check:
        allowed, message = check_command(args.check, args.scope_file)
        print(message)
        sys.exit(0 if allowed else 2)
    else:
        # Hook mode: read JSON from stdin
        run_hook_mode()


if __name__ == '__main__':
    main()
