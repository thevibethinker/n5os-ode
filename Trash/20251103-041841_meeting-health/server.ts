import { Hono } from "hono";
import { serveStatic } from "hono/bun";
import { readFile } from "fs/promises";
import { existsSync } from "fs";

const app = new Hono();

// API endpoint for health report
app.get("/api/health", async (c) => {
  const reportPath = "/home/workspace/N5/data/meeting_health_report.json";
  
  if (!existsSync(reportPath)) {
    return c.json({
      error: "Health report not found. Run health_scanner.py first.",
      generated_at: new Date().toISOString(),
      summary: {
        total_scanned: 0,
        critical_issues: 0,
        high_issues: 0,
        medium_issues: 0,
        healthy: 0
      },
      critical: [],
      high: [],
      medium: []
    });
  }
  
  const data = await readFile(reportPath, "utf-8");
  return c.json(JSON.parse(data));
});

// Serve static files
app.use("/*", serveStatic({ root: "./dist" }));
app.use("/*", serveStatic({ path: "./dist/index.html" }));

const port = parseInt(process.env.PORT || "50140");
console.log();

export default {
  port,
  fetch: app.fetch,
};
