# Telemetry + CI/CD Implementation Plan
**Conversation:** con_BD6xkpxbTZVbVKOt  
**Date:** 2025-10-26 19:47 ET  
**Status:** Research Complete → Ready for Implementation

---

## Research Summary

### Telemetry Tools Evaluated

**Open Source (Self-Hosted):**
1. **OpenTelemetry** - Industry standard, Python SDK, metrics/traces/logs
2. **Prometheus** - Time-series metrics, lightweight, battle-tested
3. **Grafana** - Visualization, dashboards, works with Prometheus
4. **SigNoz** - All-in-one (OpenTelemetry-based), metrics+traces+logs

**Paid/SaaS:**
1. **Datadog** - $15-31/host/month, full observability
2. **New Relic** - Usage-based, APM + monitoring
3. **Better Stack** - $10/month, logs + uptime monitoring

### CI/CD Tools Evaluated

**Open Source:**
1. **GitHub Actions** - Free for public repos, $0.008/min private
2. **GitLab CI/CD** - Built-in, self-hosted option
3. **Buildbot** - Python-native, highly customizable
4. **Tekton** - Kubernetes-native, cloud-native pipelines

**Code Quality (Integrate with CI):**
1. **SonarQube** - Static analysis, free Community Edition
2. **Pylint** - Python linting, free
3. **Black** - Python formatter, free
4. **Semgrep** - Custom rules, security scanning, free tier

---

## Recommendation: Hybrid Approach

### Why Not Full Enterprise Stack?

You don't need Datadog ($500+/month) or New Relic for n5OS. You're:
- Single user (not multi-team)
- 339 scripts (not 10K microservices)
- Need principle adherence, not distributed tracing

**Better fit:** Lightweight open-source + purpose-built custom tools

---

## Proposed Stack

### 1. Telemetry: Custom + Prometheus + Grafana

**Architecture:**
```
Custom Collectors (Python)
    ↓
Prometheus (metrics storage)
    ↓
Grafana (dashboards)
```

**What to Track:**
- **Flow Metrics:** Records → Knowledge rate, file age
- **Principle Adherence:** P0-P33 violations per script
- **System Health:** Empty files, orphans, stale items
- **Usage:** Command frequency, error rates, execution time

**Why This:**
- Prometheus: Industry standard, 50MB RAM, built-in time-series
- Grafana: Free, beautiful dashboards, alerting
- Custom collectors: YOUR principles, YOUR flows (not generic APM)

**Cost:** $0 (self-hosted on your Zo server)  
**Setup Time:** 6-8 hours

### 2. CI/CD: GitHub Actions + SonarQube

**Architecture:**
```
git push
    ↓
GitHub Actions (runner)
    ├─ Syntax Check (py_compile)
    ├─ Schema Validation (n5_schema_validation.py)
    ├─ Safety Check (n5_safety.py)
    ├─ SonarQube Scan (code quality + principles)
    └─ Tests (pytest)
    ↓
✅ Pass → Commit accepted
❌ Fail → Block + notify
```

**Why GitHub Actions:**
- Already using GitHub (vrijenattawar/n5-os-zo)
- Free for private repos (2000 min/month)
- YAML config, easy to understand
- You already have pre-commit hooks (n5_safety.py)

**Why SonarQube:**
- Free Community Edition
- Python support
- Custom rules (map P0-P33 to SonarQube rules)
- IDE integration (real-time feedback)

**Cost:** $0 (GitHub Actions free tier, SonarQube self-hosted)  
**Setup Time:** 4-6 hours

---

## Implementation Phases

### Phase 1: Quick Wins (Today, 1 hour)

**Goal:** Immediate visibility with zero infra

**Tasks:**
1. Health check script (30 min)
   ```python
   # N5/scripts/n5_health_check.py
   def check_health():
       return {
           "stale_records": count_old_files("Records/Temporary/", days=7),
           "empty_files": find_empty_files(["N5", "Knowledge", "Documents"]),
           "uncommitted": len(git_status()),
           "orphaned_tasks": scan_lists_for_stale()
       }
   ```

2. Command usage tracker (20 min)
   ```python
   # Add to all command entry points
   from pathlib import Path
   import json, datetime
   
   def track_usage(cmd, status="success", duration_ms=0):
       Path("N5/telemetry/usage.jsonl").open('a').write(
           json.dumps({
               "ts": datetime.now().isoformat(),
               "cmd": cmd,
               "status": status,
               "dur_ms": duration_ms
           }) + "\n"
       )
   ```

3. Daily email digest (10 min)
   - Scheduled task: Run health check at 8am
   - Email summary to you

**Output:** `N5/telemetry/daily_health.md` + email

---

### Phase 2: Telemetry Infrastructure (Week 1, 6-8 hours)

**Day 1: Install Prometheus + Grafana (2 hours)**

```bash
# Prometheus (metrics storage)
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
mv prometheus-* /opt/prometheus

# Grafana (dashboards)
wget https://dl.grafana.com/oss/release/grafana-10.2.2.linux-amd64.tar.gz
tar -zxvf grafana-*.tar.gz
mv grafana-* /opt/grafana

# Register as user services
# (Zo will run them automatically)
```

Configure Prometheus to scrape custom exporter on :9090

**Day 2-3: Build Custom Collectors (3 hours)**

```python
# N5/telemetry/collectors/flow_exporter.py
from prometheus_client import start_http_server, Gauge
import time

flow_rate = Gauge('n5_flow_rate', 'Records -> Knowledge movement rate')
stale_count = Gauge('n5_stale_records', 'Files older than 7 days in Records/')

def collect_metrics():
    while True:
        flow_rate.set(calculate_flow_rate())
        stale_count.set(count_stale_records())
        time.sleep(60)  # Update every minute

if __name__ == '__main__':
    start_http_server(8000)  # Expose metrics on :8000
    collect_metrics()
```

**Collectors to Build:**
- `flow_exporter.py` - Records → Knowledge flow
- `principle_scanner.py` - Scan code for P0-P33 violations
- `health_exporter.py` - Empty files, orphans, uncommitted
- `usage_exporter.py` - Parse usage.jsonl → metrics

**Day 4: Grafana Dashboards (2 hours)**

Create 3 dashboards:
1. **System Health** - Stale files, empty files, uncommitted changes
2. **Flow Efficiency** - Records processing rate, bottlenecks
3. **Principle Adherence** - P0-P33 violations by category

**Day 5: Alerting (1 hour)**

Configure Grafana alerts:
- Email when stale_records > 10
- Email when principle violations detected
- Email when flow_rate < 5 files/day

---

### Phase 3: CI/CD Setup (Week 2, 4-6 hours)

**Day 1: GitHub Actions Workflow (2 hours)**

Create `.github/workflows/n5-ci.yml`:

```yaml
name: n5OS CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.12
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pylint black
    
    - name: Syntax Check
      run: |
        echo "Checking Python syntax..."
        find N5/scripts -name "*.py" -exec python3 -m py_compile {} \;
    
    - name: Code Formatting Check
      run: |
        echo "Checking code formatting..."
        black --check N5/scripts/
    
    - name: Linting
      run: |
        echo "Running pylint..."
        pylint N5/scripts/*.py --exit-zero --reports=y > pylint-report.txt
        cat pylint-report.txt
    
    - name: Schema Validation
      run: |
        echo "Validating N5 schemas..."
        python3 N5/scripts/n5_schema_validation.py --all
    
    - name: Safety Check
      run: |
        echo "Running N5 safety checks..."
        python3 N5/scripts/n5_safety.py --dry-run
    
    - name: Run Tests
      run: |
        echo "Running pytest..."
        pytest N5/tests/ -v --tb=short
    
    - name: Upload Artifacts
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-reports
        path: |
          pylint-report.txt
          pytest-results.xml
```

**Day 2: SonarQube Setup (2 hours)**

```bash
# Install SonarQube Community Edition
cd /tmp
wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-10.3.0.82913.zip
unzip sonarqube-*.zip
mv sonarqube-* /opt/sonarqube

# Register as user service
# Access on http://localhost:9000
```

Create `sonar-project.properties`:
```properties
sonar.projectKey=n5os
sonar.projectName=n5 Operating System
sonar.sources=N5/scripts,N5/commands
sonar.python.version=3.12
sonar.exclusions=**/node_modules/**,**/*.test.py
```

**Day 3: Custom Principle Rules (1 hour)**

Map P0-P33 to SonarQube custom rules:
- P0 (Rule-of-Two) → Flag if >2 config files loaded
- P5 (Anti-Overwrite) → Flag direct overwrites without backup
- P15 (Complete Before Claiming) → Flag TODO/FIXME comments
- P21 (Document Assumptions) → Flag missing docstrings

**Day 4: Integration Testing (1 hour)**

Test full pipeline:
1. Make intentional errors
2. Verify CI catches them
3. Fix and verify pass

---

### Phase 4: Integration & Monitoring (Week 3, 2 hours)

**Link telemetry → CI/CD:**
- Fail CI if principle violations increase >10%
- Email alert when metrics degrade

**Documentation:**
- Update `Documents/System/guides/` with setup instructions
- Create troubleshooting guide

---

## Cost Analysis

| Component | Setup Time | Monthly Cost | Value |
|-----------|------------|--------------|-------|
| Health check script | 30 min | $0 | Immediate visibility |
| Command usage tracker | 20 min | $0 | Usage insights |
| Prometheus + Grafana | 2 hours | $0 (self-hosted) | Time-series metrics + dashboards |
| Custom collectors | 3 hours | $0 | YOUR principles tracked |
| GitHub Actions | 2 hours | $0 (free tier) | Automated CI |
| SonarQube | 2 hours | $0 (community) | Code quality gates |
| Custom rules | 1 hour | $0 | P0-P33 enforcement |
| **TOTAL** | **~12 hours** | **$0/month** | **Production-grade observability** |

**Alternative (Paid):**
- Datadog APM: $31/host/month = $372/year
- GitHub Actions (if exceed free tier): ~$5/month
- **Total:** ~$430/year

**Recommendation:** Start with $0 open-source stack. If it doesn't meet needs after 2 months, consider paid tools.

---

## Success Metrics

After implementation, you should have:

✅ **Daily email** with system health snapshot  
✅ **Grafana dashboard** showing flow efficiency, principle adherence  
✅ **CI/CD pipeline** blocking bad commits  
✅ **Real-time alerts** when metrics degrade  
✅ **Historical data** to track Zero-Touch alignment over time

---

## Next Steps

**Decision Points:**
1. Start with Phase 1 quick wins today? (1 hour)
2. Full telemetry infrastructure this week? (6-8 hours)
3. CI/CD setup next week? (4-6 hours)

**Alternative Fast Path:**
- Use **Grafana Cloud** (free tier: 10K metrics, 14-day retention)
- Skip self-hosted Prometheus
- Saves 2 hours setup, but less control

**Your call:** Which approach?

---

*v1.0 | Research complete | 2025-10-26 19:47 ET*
