# Phase 2: Grafana Cloud + Prometheus Setup

**Goal:** Rich dashboards for flow efficiency and principle adherence  
**Duration:** 2-3 hours  
**Cost:** $0 (free tier: 10K metrics, 14-day retention)

---

## Step 1: Grafana Cloud Setup (Manual - V Required)

**Action:** Sign up at https://grafana.com/auth/sign-up/create-user

**Free Tier Includes:**
- 10,000 series metrics
- 14-day retention
- 3 users
- Unlimited dashboards

**After signup:**
1. Note your Prometheus endpoint (e.g., `https://prometheus-xxx.grafana.net/api/prom/push`)
2. Generate API key (Settings → API Keys)
3. Note your instance ID

**I'll need from you:**
- `GRAFANA_ENDPOINT` 
- `GRAFANA_API_KEY`
- `GRAFANA_INSTANCE_ID`

---

## Step 2: Custom Collectors (Building Now)

While you sign up, I'm building:

1. **n5_metrics_collector.py** - Main collector exposing Prometheus metrics
2. **prometheus.yml** - Local Prometheus config
3. **grafana_dashboards.json** - Pre-built dashboard definitions

**Metrics to Track:**

### Flow Efficiency
- `n5_records_staging_count` - Files in Records/Temporary/
- `n5_records_stale_count` - Files >7 days old
- `n5_knowledge_growth_rate` - New files in Knowledge/ per day
- `n5_lists_pending_count` - Open items in Lists/

### Principle Adherence  
- `n5_empty_files_count` - Zero-byte files (P1: Human-Readable violation)
- `n5_uncommitted_count` - Dirty git state (P5: Anti-Overwrite risk)
- `n5_readme_duplication` - Multiple READMEs (P2: SSOT violation)
- `n5_script_complexity` - LOC per script (P8: Minimal Context)

### Command Usage
- `n5_command_invocations_total{command="X"}` - Counter per command
- `n5_command_duration_seconds{command="X"}` - Histogram of durations
- `n5_command_errors_total{command="X"}` - Error counter

---

## Step 3: Dashboard Design

**Dashboard 1: System Health**
- Stale files (gauge + trend)
- Empty files (gauge)
- Git health (clean vs dirty)
- Storage usage

**Dashboard 2: Flow Efficiency**
- Records → Knowledge flow rate
- Average residence time in staging
- Bottleneck detection
- Weekly throughput

**Dashboard 3: Principle Adherence**
- SSOT score (0-100)
- Complexity score (avg LOC/script)
- Safety score (git + backups)
- Trend over time

---

## Next Actions

1. **You:** Sign up for Grafana Cloud, provide credentials
2. **Me:** Build collectors + dashboards while you sign up
3. **Together:** Deploy and verify metrics flowing

**Ready?**
