# Contributing to ThreatSwarm

## Setup
```bash
git clone https://github.com/vsh00t/ThreatSwarm.git
cd ThreatSwarm
python3 scripts/build.py --all  # Generate all platform adapters
python3 scripts/smoke_test.sh   # Verify everything works
```

## Git Config
Set your identity before committing:
```bash
git config user.name "Your Name"
git config user.email "your@email.com"
```

## Making Changes
1. Edit files in `core/` (agents, rules, commands, hooks, skills, templates)
2. Run `python3 scripts/build.py --all` to regenerate all adapters
3. Run `bash scripts/smoke_test.sh` to verify
4. Commit and push

## Agent Guidelines
- Minimum 250 lines per agent
- Include real commands with placeholders ($TARGET, $LHOST, $LPORT)
- Reference NetExec (not CrackMapExec) for SMB/AD tools
- Map techniques to MITRE ATT&CK IDs
