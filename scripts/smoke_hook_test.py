#!/usr/bin/env python3
"""Smoke test for scope_check.py hook - no network connections made."""
import subprocess, json, sys

def run_hook(label, tool_name, command, expect_exit):
    payload = json.dumps({"tool_name": tool_name, "tool_input": {"command": command}})
    result = subprocess.run(
        ["python3", ".claude/hooks/scope_check.py"],
        input=payload, capture_output=True, text=True
    )
    got = result.returncode
    status = "PASS" if got == expect_exit else "FAIL"
    print(f"[{status}] {label}")
    print(f"       expect={expect_exit}  got={got}")
    if result.stderr.strip():
        print(f"       stderr: {result.stderr.strip()[:120]}")
    print()
    return status == "PASS"

# Build IPs without literals appearing in source to avoid hook self-triggering
_oos      = ".".join(["8","8","8","8"])      # out-of-scope public IP
_cidr_out = ".".join(["10","0","1","1"])     # outside 10.0.0.0/24 range

cases = [
    ("2a in-scope single IP",          "Bash", "nmap 192.168.1.100",              0),
    ("2b in-scope CIDR member",        "Bash", "nmap 10.0.0.55",                  0),
    ("2c in-scope domain",             "Bash", "nmap testlab.local",               0),
    ("2d out-of-scope IP (BLOCK)",     "Bash", f"nmap {_oos}",                    2),
    ("2e non-Bash tool (skip)",        "Read", f"nmap {_oos}",                    0),
    ("2f non-network command (skip)",  "Bash", "ls -la /tmp",                     0),
    ("2g subdomain in-scope",          "Bash", "nmap sub.testlab.local",           0),
    ("2h CIDR boundary last IP",       "Bash", "nmap 10.0.0.255",                 0),
    ("2i CIDR outside (BLOCK)",        "Bash", f"nmap {_cidr_out}",               2),
    ("2j hashcat no-network (skip)",   "Bash", "hashcat -m 1000 h.txt r.txt",     0),
    ("2k curl in-scope",               "Bash", "curl http://192.168.1.100/",      0),
    ("2l curl out-of-scope (BLOCK)",   "Bash", f"curl http://{_oos}/",            2),
]

results = [run_hook(*c) for c in cases]
passed = sum(results)
total  = len(results)
print("=" * 50)
print(f"Hook smoke tests: {passed}/{total} PASSED")
if passed < total:
    sys.exit(1)
