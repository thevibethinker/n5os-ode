# Grafana Cloud Setup Guide

**Status:** Metrics collector running locally  
**Next:** Connect to Grafana Cloud for visualization

---

## Step 1: Sign Up for Grafana Cloud

1. Go to https://grafana.com/auth/sign-up/create-user
2. Create free account (no credit card required)
3. Choose "Free" tier:
   - 10,000 metrics series
   - 14-day retention
   - 3 users
   - Unlimited dashboards

---

## Step 2: Get Your Credentials

After signup, in Grafana Cloud portal:

1. **Get Prometheus Endpoint:**
   - Navigate to: Connections → Add new connection → Hosted Prometheus
   - Copy the "Remote Write Endpoint" (e.g., `https://prometheus-prod-xx-xxx.grafana.net/api/prom/push`)

2. **Generate API Key:**
   - Navigate to: Security → Service Accounts → Create service account
   - Name it "n5-metrics-pusher"
   - Add role: "MetricsPublisher"
   - Generate token
   - **SAVE THIS TOKEN** - you won't see it again

3. **Note Your Instance ID:**
   - Found in URL: `https://YOURINSTANCE.grafana.net`

---

## Step 3: Configure Local Push

Create `N5/telemetry/.env`:

```bash
GRAFANA_ENDPOINT=https://prometheus-prod-xx-xxx.grafana.net/api/prom/push
GRAFANA_USERNAME=your_instance_id
GRAFANA_API_KEY=your_generated_token
```

**Security:** Add `.env` to `.gitignore`

---

## Step 4: Run Prometheus with Remote Write

We'll use Prometheus to scrape our local collector and push to Grafana Cloud.

**Install Prometheus:**
```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-2.45.0.linux-amd64.tar.gz
mv prometheus-2.45.0.linux-amd64 /opt/prometheus
```

**Configure** (`/opt/prometheus/prometheus.yml`):
```yaml
global:
  scrape_interval: 60s
  external_labels:
    instance: 'n5os'
    environment: 'production'

scrape_configs:
  - job_name: 'n5-metrics'
    static_configs:
      - targets: ['localhost:8000']

remote_write:
  - url: 'GRAFANA_ENDPOINT'
    basic_auth:
      username: 'GRAFANA_USERNAME'
      password: 'GRAFANA_API_KEY'
```

**Start Prometheus:**
```bash
/opt/prometheus/prometheus --config.file=/opt/prometheus/prometheus.yml
```

---

## Step 5: Start N5 Metrics Collector

```bash
python3 /home/workspace/N5/telemetry/n5_metrics_collector.py --port 8000 --interval 60
```

**Or as a service** (recommended):
```bash
# Register as Zo user service
# This keeps it running in background
```

---

## Step 6: Import Dashboard

1. In Grafana Cloud, go to Dashboards → Import
2. Upload `N5/telemetry/grafana_dashboard_n5_health.json`
3. Select your Prometheus data source
4. Click "Import"

---

## Step 7: Verify Metrics Flowing

1. In Grafana, go to Explore
2. Select Prometheus data source
3. Query: `n5_records_staging_count`
4. Should see data points!

---

## Metrics Available

### Flow Efficiency
- `n5_records_staging_count` - Files in staging
- `n5_records_stale_count` - Files >7 days old
- `n5_knowledge_files_total` - Total knowledge files
- `n5_lists_pending_count` - Pending list items

### Principle Adherence
- `n5_empty_files_count` - Empty files (P1 violation)
- `n5_uncommitted_count` - Git dirty state (P5 risk)
- `n5_readme_duplication` - Multiple READMEs (P2 violation)
- `n5_script_complexity_avg` - Avg LOC per script (P8)
- `n5_script_count_total` - Total scripts

### Command Usage
- `n5_command_invocations_total{command, status}` - Invocation counter
- `n5_command_duration_seconds{command}` - Duration histogram

### System Health
- `n5_health_check_success` - Last check status
- `n5_last_health_check_timestamp` - Last check time

---

## Alternative: Local Grafana (No Cloud)

If you prefer self-hosted:

```bash
docker run -d -p 3000:3000 grafana/grafana
# Access at http://localhost:3000 (admin/admin)
# Add Prometheus data source pointing to localhost:9090
```

---

## Current Status

✅ **Metrics collector built and tested**  
✅ **Exposing 15+ metrics on localhost:8001**  
✅ **Dashboard JSON created**  
⏳ **Waiting for:** Grafana Cloud credentials from V  
⏳ **Next:** Configure remote write + import dashboard

---

**Ready to proceed when you provide credentials!**
