---
title: "2025 Travel Wrapped"
description: "Generate a visual summary of your 2025 travels from your Gmail data. Uses a hybrid Python/LLM engine to scan flights, trains, and lodging, then renders an interactive dashboard."
tags: ["travel", "visualization", "dashboard", "gmail"]
tool: true
---

# 2025 Travel Wrapped

This prompt will help you generate a personalized "Spotify Wrapped" style dashboard for your 2025 travels.

## How it works
1. **Scans Gmail & Calendar:** Finds flight confirmations, train tickets, and hotel bookings.
2. **Normalizes Data:** Groups cities (e.g., JFK/LGA -> NYC), filters cancellations, and computes stats.
3. **Launches Dashboard:** Deploys a local dashboard to visualize your year.

## Instructions

1. **Initialize the Engine:**
   Run the following command to download the engine and start the scan.
   
   ```bash
   # Clone the engine
   git clone https://github.com/vrijenattawar/travel-wrapped-2025.git /home/workspace/travel-wrapped-2025
   
   # Run the extraction (this may take a moment)
   python3 /home/workspace/travel-wrapped-2025/travel_extractor.py
   ```

2. **Launch the Site:**
   
   ```bash
   cd /home/workspace/travel-wrapped-2025
   bun install
   bun run dev
   ```

3. **View Your Wrapped:**
   Open the 'Sites' tab in your Zo workspace and look for the `travel-wrapped-2025` service.

## Customization
- The data is stored in `travel_metrics.json`. You can edit this file manually if the scan missed anything.
- The dashboard code is in `src/pages/travel-wrapped.tsx`. Feel free to tweak the design!
