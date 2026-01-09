# Copilot Instructions - Cooling Tower System

## Core Principle
**UNDERSTAND FIRST. VERIFY SOURCES. NEVER GUESS.**

## Before Making ANY Changes

1. **Read the README.md** - Understand the full architecture
2. **Verify what's running** - Check processes, ports, file locations
3. **Identify the source of truth**:
   - Files in GitHub = restore from `origin/master` (latest commit)
   - Files NOT in GitHub = backup before changing
4. **Ask questions** if unclear - don't make assumptions

## System Architecture (Quick Reference)

- **Digital Ocean Droplet** (159.89.150.146): Caddy reverse proxy
- **Raspberry Pi** (100.89.57.3): Flask (8001) + FastAPI (8000)
- **Flask**: `/home/max/old_dashboard/` - imports from `/home/max/`
- **VFD Control**: Flask has direct hardware access, FastAPI proxies Flask

## Deployment

**ALWAYS use the deployment script for ANY code changes:**

```bash
./deploy.sh
```

This script:
- Deploys backend Python files to Pi
- Deploys Flask dashboard to Pi
- Builds and deploys React frontend to DO droplet
- Restarts Flask and FastAPI services
- Warns about uncommitted changes

**Never manually copy files to servers.** The deployment script ensures everything goes to the correct location.

## Restoring Files from GitHub (Emergency Only)

Only use manual restore if deployment script fails:

```bash
# Extract latest from GitHub
cd "/Users/max/insider workspace"
git show origin/master:path/to/file.py > /tmp/file_latest.py

# Copy to server
scp /tmp/file_latest.py max@100.89.57.3:/target/path/

# Restart affected services
```


## When User Reports Issues

1. Get specific symptoms (not just "errors" or "delays")
2. Check logs first: `/tmp/flask.log`, `/tmp/fastapi.log`
3. Verify current state before attempting fixes
4. If working = don't "optimize" without measuring first

## Never

- Use local git repos on servers (only use GitHub remote)
- Pull from old commits (always use latest/HEAD)
- Manually copy files to servers (use `./deploy.sh` instead)
- Create files when told not to
- Continue when instructed to stop
- Make changes without understanding dependencies
