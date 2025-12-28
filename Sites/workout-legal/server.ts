import { serveStatic } from "hono/bun";
import type { ViteDevServer } from "vite";
import { createServer as createViteServer } from "vite";
import config from "./zosite.json";
import { Hono } from "hono";
import { Database } from "bun:sqlite";

type Mode = "development" | "production";
const app = new Hono();

const mode: Mode =
  process.env.NODE_ENV === "production" ? "production" : "development";

const dbPath = "/home/workspace/Personal/Health/workouts.db";
const db = new Database(dbPath, { readonly: true });

// Bio-Log database for mood tracking
const bioDbPath = "/home/workspace/N5/data/journal.db";
const bioDb = new Database(bioDbPath, { readonly: true });

/**
 * Add any API routes here.
 */
app.get("/api/hello-zo", (c) => c.json({ msg: "Hello from Zo" }));

app.get("/api/health/summary", (c) => {
  try {
    // Get average RHR for last 7 days
    const rhrResult = db.query(`
      SELECT AVG(avg_hr) as avg_rhr 
      FROM workouts 
      WHERE date >= date('now', '-7 days')
      AND (primary_modality LIKE '%Sleep%' OR primary_modality IS NULL)
    `).get() as { avg_rhr: number };

    // Get average run distance for last 30 days
    const distResult = db.query(`
      SELECT AVG(distance_km) as avg_dist 
      FROM workouts 
      WHERE (primary_modality LIKE '%run%' OR primary_modality LIKE '%Run%')
      AND date >= date('now', '-30 days')
    `).get() as { avg_dist: number };

    // GET LONGEST RUN
    const longestRunResult = db.query(`
      SELECT MAX(distance_km) as max_dist 
      FROM workouts 
      WHERE (primary_modality LIKE '%run%' OR primary_modality LIKE '%Run%')
    `).get() as { max_dist: number };

    // GET BEST 10K TIME (if distance >= 9.9)
    const best10kResult = db.query(`
      SELECT MIN(duration_min) as min_duration
      FROM workouts
      WHERE (primary_modality LIKE '%run%' OR primary_modality LIKE '%Run%')
      AND distance_km >= 9.9
    `).get() as { min_duration: number | null };

    // Simple integrity mock for now
    const integrity = 0.85;

    return c.json({
      avgRhr: rhrResult.avg_rhr || 65,
      avgDistance: distResult.avg_dist || 0,
      maxDistance: longestRunResult.max_dist || 0,
      best10kTime: best10kResult.min_duration,
      integrity
    });
  } catch (error) {
    console.error(error);
    return c.json({ error: "Failed to fetch health summary" }, 500);
  }
});

app.get("/api/health/runs", (c) => {
  try {
    const runs = db.query("SELECT id, date, distance_km, duration_min, avg_hr FROM workouts WHERE primary_modality LIKE '%run%' OR primary_modality LIKE '%Run%' ORDER BY date DESC LIMIT 10").all();
    return c.json(runs);
  } catch (err) {
    console.error("Health runs error:", err);
    return c.json({ error: "Failed to fetch health runs" }, 500);
  }
});

app.get("/api/health/chart", (c) => {
  try {
    const last21Days = new Date();
    last21Days.setDate(last21Days.getDate() - 21);
    const dateStr = last21Days.toISOString().split("T")[0];

    const activity = db.query("SELECT date, steps, calories_out as calories FROM daily_activity_summary WHERE date >= ? ORDER BY date ASC").all(dateStr);
    return c.json(activity);
  } catch (err) {
    console.error("Health chart error:", err);
    return c.json({ error: "Failed to fetch activity chart data" }, 500);
  }
});

// Bio-Log: Today's mood
app.get("/api/bio/today", (c) => {
  try {
    const today = new Date().toISOString().split("T")[0];
    const result = bioDb.query(`
      SELECT mood, notes, resting_hr, steps_so_far, time_period, created_at 
      FROM bio_snapshots 
      WHERE date(created_at) = ? 
      ORDER BY created_at DESC 
      LIMIT 1
    `).get(today) as { mood: string; notes: string; resting_hr: number; steps_so_far: number; time_period: string; created_at: string } | null;
    
    if (!result) {
      return c.json({ emoji: null, note: null, date: today, hasData: false });
    }
    
    return c.json({
      emoji: result.mood,
      note: result.notes,
      rhr: result.resting_hr,
      steps: result.steps_so_far,
      timePeriod: result.time_period,
      date: today,
      hasData: true
    });
  } catch (err) {
    console.error("Bio today error:", err);
    return c.json({ error: "Failed to fetch today's bio" }, 500);
  }
});

// Bio-Log: Last 7 days of mood (one emoji per day, most recent first)
app.get("/api/bio/week", (c) => {
  try {
    const results = bioDb.query(`
      SELECT date(created_at) as date, mood, time_period, created_at
      FROM bio_snapshots 
      WHERE created_at >= date('now', '-7 days')
      ORDER BY created_at DESC
    `).all() as { date: string; mood: string; time_period: string; created_at: string }[];
    
    // Dedupe by date (keep first = most recent entry per day), filter to only entries with emojis
    const seen = new Set<string>();
    const withEmojis = results
      .filter(r => {
        if (!r.mood || r.mood.trim() === "") return false;
        if (seen.has(r.date)) return false;
        seen.add(r.date);
        return true;
      })
      .slice(0, 7)
      .map(r => ({ date: r.date, emoji: r.mood, timePeriod: r.time_period }));
    
    return c.json(withEmojis);
  } catch (err) {
    console.error("Bio week error:", err);
    return c.json({ error: "Failed to fetch weekly bio" }, 500);
  }
});

// 10K Readiness Calculator
app.get("/api/goals/10k-readiness", (c) => {
  try {
    const targetDate = new Date("2026-02-23");
    const today = new Date();
    const weeksRemaining = Math.ceil((targetDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24 * 7));
    
    // Longest run in last 30 days
    const longestRun = db.query(`
      SELECT MAX(distance_km) as max_dist 
      FROM workouts 
      WHERE (primary_modality LIKE '%run%' OR primary_modality LIKE '%Run%')
      AND date >= date('now', '-30 days')
    `).get() as { max_dist: number } | null;
    
    // Weekly volume (last 7 days)
    const weeklyVolume = db.query(`
      SELECT SUM(distance_km) as total 
      FROM workouts 
      WHERE (primary_modality LIKE '%run%' OR primary_modality LIKE '%Run%')
      AND date >= date('now', '-7 days')
    `).get() as { total: number } | null;
    
    // Streak (consecutive days with workouts)
    const recentWorkouts = db.query(`
      SELECT DISTINCT date FROM workouts 
      WHERE date >= date('now', '-30 days') 
      ORDER BY date DESC
    `).all() as { date: string }[];
    
    let streak = 0;
    const todayStr = today.toISOString().split("T")[0];
    let checkDate = new Date(todayStr);
    for (const w of recentWorkouts) {
      const wDate = new Date(w.date);
      const diff = Math.floor((checkDate.getTime() - wDate.getTime()) / (1000 * 60 * 60 * 24));
      if (diff <= 1) {
        streak++;
        checkDate = wDate;
      } else {
        break;
      }
    }
    
    // RHR baseline (earliest) vs current (latest)
    const rhrBaseline = db.query(`SELECT resting_hr FROM daily_resting_hr ORDER BY date ASC LIMIT 1`).get() as { resting_hr: number } | null;
    const rhrCurrent = db.query(`SELECT resting_hr FROM daily_resting_hr ORDER BY date DESC LIMIT 1`).get() as { resting_hr: number } | null;
    const rhrDrop = (rhrBaseline?.resting_hr || 80) - (rhrCurrent?.resting_hr || 80);
    
    // Calculate readiness
    const longest = longestRun?.max_dist || 0;
    const volume = weeklyVolume?.total || 0;
    
    const readiness = Math.min(100, Math.round(
      (Math.min(longest / 10, 1) * 0.30 +
       Math.min(volume / 25, 1) * 0.25 +
       Math.min(streak / 14, 1) * 0.25 +
       Math.min(Math.max(rhrDrop, 0) / 15, 1) * 0.20) * 100
    ));
    
    // Next milestone logic
    let nextMilestone = "Start with a 2K run";
    if (longest >= 2 && longest < 5) nextMilestone = "Complete a 5K without stopping";
    else if (longest >= 5 && longest < 8) nextMilestone = "Build to 8K long run";
    else if (longest >= 8) nextMilestone = "Taper week - you're ready!";
    
    return c.json({
      percentage: readiness,
      longestRun: longest,
      weeklyVolume: volume,
      streak,
      rhrBaseline: rhrBaseline?.resting_hr || null,
      rhrCurrent: rhrCurrent?.resting_hr || null,
      rhrDrop,
      weeksRemaining,
      nextMilestone
    });
  } catch (err) {
    console.error("10K readiness error:", err);
    return c.json({ error: "Failed to calculate 10K readiness" }, 500);
  }
});

if (mode === "production") {
  configureProduction(app);
} else {
  await configureDevelopment(app);
}

/**
 * Determine port based on mode. In production, use the published_port if available.
 * In development, always use the local_port.
 * DO NOT edit this port manually. Ports are managed by the system via the zosite.json config.
 */
const port =
  mode === "production"
    ? (config.publish?.published_port ?? config.local_port)
    : config.local_port;

export default { fetch: app.fetch, port, idleTimeout: 255 };

/**
 * Configure routing for production builds.
 *
 * - Streams prebuilt assets from `dist`.
 * - Falls back to `index.html` for any other GET so the SPA router can resolve the request.
 */
function configureProduction(app: Hono) {
  app.use("/assets/*", serveStatic({ root: "./dist" }));
  app.use(async (c, next) => {
    if (c.req.method !== "GET") {
      return next();
    }

    const path = c.req.path;
    if (path.startsWith("/api/") || path.startsWith("/assets/")) {
      return next();
    }

    return serveStatic({ path: "./dist/index.html" })(c, next);
  });
}

/**
 * Configure routing for development builds.
 *
 * - Boots Vite in middleware mode for transforms.
 * - Mirrors production routing semantics so SPA routes behave consistently.
 */
async function configureDevelopment(app: Hono): Promise<ViteDevServer> {
  const vite = await createViteServer({
    server: { middlewareMode: true, hmr: false, ws: false },
    appType: "custom",
  });

  app.use("*", async (c, next) => {
    if (c.req.path.startsWith("/api/")) {
      return next();
    }

    const url = c.req.path;
    try {
      if (url === "/" || url === "/index.html") {
        let template = await Bun.file("./index.html").text();
        template = await vite.transformIndexHtml(url, template);
        return c.html(template);
      }

      let result;
      try {
        result = await vite.transformRequest(url);
      } catch {
        result = null;
      }

      if (result) {
        return new Response(result.code, {
          headers: {
            "Content-Type": "application/javascript",
            "Cache-Control": "no-cache",
          },
        });
      }
      const file = Bun.file(`.${url}`);
      if (await file.exists()) {
        return new Response(file, {
          headers: { "Cache-Control": "no-cache" },
        });
      }
      let template = await Bun.file("./index.html").text();
      template = await vite.transformIndexHtml("/", template);
      return c.html(template);
    } catch (error) {
      vite.ssrFixStacktrace(error as Error);
      console.error(error);
      return c.text("Internal Server Error", 500);
    }
  });

  return vite;
}










