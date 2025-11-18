import { serveStatic } from "hono/bun";
import type { ViteDevServer } from "vite";
import { createServer as createViteServer } from "vite";
import config from "./zosite.json";
import { Hono } from "hono";
import { readFileSync } from "fs";
import { spawn } from "child_process";

type Mode = "development" | "production";
const app = new Hono();

const mode: Mode =
  process.env.NODE_ENV === "production" ? "production" : "development";

/**
 * Add any API routes here.
 */
app.get("/api/hello-zo", (c) => c.json({ msg: "Hello from Zo" }));

app.get("/api/trip-status", (c) => {
  try {
    const dataPath = '/home/workspace/wheresv2-data/trips.jsonl';
    const fileContent = readFileSync(dataPath, 'utf-8');
    
    if (!fileContent.trim()) {
      return c.json({ error: 'No trip data found' }, 404);
    }
    
    const lines = fileContent.trim().split('\n');
    const lastLine = lines[lines.length - 1];
    const tripData = JSON.parse(lastLine);
    
    return c.json(tripData);
  } catch (error) {
    console.error('Error loading trip data:', error);
    return c.json({ error: 'Failed to load trip data' }, 500);
  }
});

app.post("/api/manual-update", async (c) => {
  try {
    const body = await c.req.json();
    const message = body.message;
    
    if (!message || typeof message !== 'string') {
      return c.json({ error: 'Message is required and must be a string' }, 400);
    }
    
    const scriptPath = '/home/workspace/wheresv2-data/scripts/manual_update_processor.py';
    
    return new Promise((resolve) => {
      const proc = spawn('python3', [scriptPath, message]);
      let stdout = '';
      let stderr = '';
      
      proc.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      proc.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      proc.on('close', (code) => {
        if (code === 0) {
          const dataPath = '/home/workspace/wheresv2-data/trips.jsonl';
          const fileContent = readFileSync(dataPath, 'utf-8');
          const lines = fileContent.trim().split('\n');
          const lastLine = lines[lines.length - 1];
          const tripData = JSON.parse(lastLine);
          
          resolve(c.json({
            success: true,
            message: 'Update processed successfully',
            trip_id: tripData.trip_id,
            current_stage: tripData.current_stage,
            manual_updates_count: tripData.manual_updates.length,
            latest_update: tripData.manual_updates[tripData.manual_updates.length - 1],
            processor_output: stdout
          }));
        } else {
          console.error('Processor error:', stderr);
          resolve(c.json({
            success: false,
            error: 'Failed to process update',
            details: stderr || stdout
          }, 500));
        }
      });
    });
  } catch (error) {
    console.error('API error:', error);
    return c.json({ error: 'Internal server error' }, 500);
  }
});

if (mode === "production") {
  configureProduction(app);
} else {
  await configureDevelopment(app);
}

const port =
  mode === "production"
    ? (config.publish?.published_port ?? config.local_port)
    : config.local_port;

export default { fetch: app.fetch, port };

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
      const file = Bun.file();
      if (await file.exists()) {
        return new Response(file);
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
