# Grafana Cloud Quick Setup - Step by Step

**Current:** You're at the data source selection screen  
**Next:** Select Prometheus and configure

---

## Step 1: Select Prometheus ✅ (You're here)

Click **"Prometheus"** (first option with flame icon)

---

## Step 2: Configure Connection

After clicking Prometheus, you'll see a setup wizard. Choose:

**Option: "Run Prometheus locally and push metrics"**

This will show you:
1. Your Prometheus remote_write endpoint URL
2. Your username (looks like a number, e.g., `1234567`)
3. Instructions to generate an API key

**Write down these values - you'll need them!**

---

## Step 3: Generate API Key

In the Grafana Cloud UI:
1. Look for a button like "Generate API Key" or "Create Token"
2. Name it: `n5-metrics-push`
3. Role: **MetricsPublisher** 
4. Click "Create"
5. **COPY THE KEY IMMEDIATELY** (you can't see it again!)

It will look like: `glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Step 4: Paste Values Here

Once you have them, paste in this chat:

```
Endpoint URL: (something like https://prometheus-prod-XX-xxx.grafana.net/api/prom/push)
Username: (number like 1234567)
API Key: glc_xxxxx...
```

---

## Step 5: I'll Configure Everything

Once you give me those 3 values, I will:
1. Install Prometheus on your Zo server
2. Configure remote_write with your credentials
3. Start pushing metrics to Grafana Cloud
4. Import the N5 dashboard
5. Show you the live dashboard URL

**Estimated time after you give me credentials: 10 minutes**

---

## What to Expect

After setup, you'll have:
- 📊 Beautiful dashboards showing your n5OS health
- 📈 Time-series graphs of all 15+ metrics
- 🔍 Ability to query and explore your data
- 📱 Access from anywhere (mobile, desktop)

---

**Current Status:** Waiting for you to click Prometheus and gather the 3 values above!
