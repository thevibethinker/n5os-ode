# N5 Bootstrap Support Server

**Purpose:** Read-only HTTP server for helping new N5 deployments boot up
**Mode:** Unidirectional (new Zo reads, cannot write)

## For the New Zo Instance

**Base URL:** Will be provided after server starts

### Available Endpoints

```bash
# Get conditional rules
curl http://<server>/configs/conditional_rules.md

# Get troubleshooting guide
curl http://<server>/help/troubleshooting.md

# Get missing dependencies
curl http://<server>/help/dependencies.txt

# Get quick fixes
curl http://<server>/fixes/common_issues.md

# Health check
curl http://<server>/health
```

## Security

- **Read-only:** No write operations possible
- **No state:** Server doesn't maintain session data
- **Unidirectional:** New Zo → This server (never reverse)
- **Human-gated:** Any changes here require V's approval

---

*Mobius Maneuver Active*
