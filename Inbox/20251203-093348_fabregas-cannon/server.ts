import { serveStatic } from "hono/bun";
import type { ViteDevServer } from "vite";
import { createServer as createViteServer } from "vite";
import config from "./zosite.json";
import { Hono } from "hono";
import { basicAuth } from "hono/basic-auth";
import { readdir, readFile, writeFile } from "fs/promises";
import { join, basename } from "path";
import { existsSync } from "fs";
import { $ } from "bun";

type Mode = "development" | "production";
const app = new Hono();

const mode: Mode =
  process.env.NODE_ENV === "production" ? "production" : "development";

const MEETINGS_PATH = "/home/workspace/Personal/Meetings";
const AUTH_USER = process.env.FC_USER || "v";
const AUTH_PASS = process.env.FC_PASS || "fabregas-cannon-2024";

// Basic auth for all routes except robots.txt
app.use("*", async (c, next) => {
  if (c.req.path === "/robots.txt") {
    return next();
  }
  return basicAuth({ username: AUTH_USER, password: AUTH_PASS })(c, next);
});

// Prevent indexing
app.get("/robots.txt", (c) => {
  return c.text("User-agent: *\nDisallow: /");
});

// Serve public folder files (logos, favicons, etc.)
app.use("/*", async (c, next) => {
  const path = c.req.path;
  // Check if file exists in public folder
  const publicPath = `./public${path}`;
  if (existsSync(publicPath)) {
    return serveStatic({ root: "./public" })(c, next);
  }
  return next();
});

// ============ API ROUTES ============

interface MeetingMeta {
  id: string;
  folder: string;
  date: string;
  title: string;
  status: string;
  meeting_type: string;
  cloaked: boolean;
  blocks: string[];
  has_transcript: boolean;
  manifest: Record<string, unknown> | null;
  done: boolean;
  tags: string[];
  // New action tracking fields
  needs_followup_email: boolean;
  needs_deliverables: boolean;
  needs_warm_intro: boolean;
  needs_blurb: boolean;
  days_since_meeting: number;
}

// List all meetings
app.get("/api/meetings", async (c) => {
  try {
    const entries = await readdir(MEETINGS_PATH, { withFileTypes: true });
    const meetings: MeetingMeta[] = [];

    // Directories to exclude (non-meeting folders)
    const excludeDirs = new Set([
      "Archive", "Inbox", "Reports", "_quarantine", "quarantine",
      "templates", "drafts", ".stversions", ".stfolder"
    ]);

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      if (entry.name.startsWith(".")) continue;
      if (excludeDirs.has(entry.name)) continue;
      
      // Only include folders that look like meetings (start with date pattern)
      const isValidMeeting = /^\d{4}-\d{2}-\d{2}/.test(entry.name);
      if (!isValidMeeting) continue;

      const folderPath = join(MEETINGS_PATH, entry.name);
      const manifestPath = join(folderPath, "manifest.json");

      let manifest: Record<string, unknown> | null = null;
      let cloaked = false;
      let status = "pending";
      let meetingType = "external";
      let meetingDate = "";

      if (existsSync(manifestPath)) {
        try {
          const raw = await readFile(manifestPath, "utf-8");
          manifest = JSON.parse(raw);
          cloaked = manifest?.cloaked === true;
          
          // Status handling with better defaults
          const rawStatus = (manifest?.status as string) || "";
          if (rawStatus) {
            status = rawStatus;
          } else if (manifest?.blocks_generated) {
            status = "processing";
          } else {
            status = "pending";
          }
          
          // Meeting type: prefer manifest, but infer from folder name as fallback
          const manifestType = (manifest?.meeting_type as string) || "";
          const folderLower = entry.name.toLowerCase();
          const folderIndicatesInternal = folderLower.includes("internal") || 
            folderLower.includes("standup") || 
            folderLower.includes("careerspan-team") ||
            folderLower.includes("co-founder");
          
          if (manifestType === "internal") {
            meetingType = "internal";
          } else if (folderIndicatesInternal) {
            // Folder name suggests internal, trust that over manifest
            meetingType = "internal";
          } else {
            meetingType = manifestType || "external";
          }
          
          meetingDate = (manifest?.meeting_date as string) || "";
        } catch {}
      }

      // Skip cloaked meetings
      if (cloaked) continue;

      // Get available blocks
      const files = await readdir(folderPath);
      const blocks = files.filter((f) => f.startsWith("B") && f.endsWith(".md"));
      const hasTranscript = files.some(
        (f) => f.includes("transcript") && (f.endsWith(".jsonl") || f.endsWith(".md"))
      );

      // Parse date from folder name (YYYY-MM-DD_...)
      const dateMatch = entry.name.match(/^(\d{4}-\d{2}-\d{2})/);
      const parsedDate = dateMatch ? dateMatch[1] : meetingDate;

      // Extract title from folder name
      const titlePart = entry.name.replace(/^\d{4}-\d{2}-\d{2}_/, "").replace(/_\[P\]$/, "");
      const title = titlePart.replace(/_/g, " ");

      // Auto-detect action needs
      let needsFollowupEmail = false;
      let needsDeliverables = false;
      let needsWarmIntro = false;
      let needsBlurb = false;

      // Check for FOLLOW_UP_EMAIL.md
      if (existsSync(join(folderPath, "FOLLOW_UP_EMAIL.md"))) {
        needsFollowupEmail = true;
      }

      // Check for B05_ACTION_ITEMS.md (deliverables)
      if (existsSync(join(folderPath, "B05_ACTION_ITEMS.md"))) {
        try {
          const actionItems = await readFile(join(folderPath, "B05_ACTION_ITEMS.md"), "utf-8");
          // Check if there are action items for Vrijen
          if (actionItems.toLowerCase().includes("vrijen") || actionItems.toLowerCase().includes("for v")) {
            needsDeliverables = true;
          }
        } catch {}
      }

      // Check for warm intro needs
      const warmIntroFiles = ["B07_WARM_INTRO_BIDIRECTIONAL.md", "B07_WARM_INTROS_REQUESTED.md"];
      for (const wf of warmIntroFiles) {
        if (existsSync(join(folderPath, wf))) {
          needsWarmIntro = true;
          break;
        }
      }
      // Also check manifest for intro signals
      if (manifest?.warm_intros_scanned) {
        const scanData = manifest.warm_intros_scanned as Record<string, unknown>;
        if ((scanData.intro_signals as number) > 0) {
          needsWarmIntro = true;
        }
      }

      // Check for blurb needs
      if (existsSync(join(folderPath, "B14_BLURBS_REQUESTED.md"))) {
        needsBlurb = true;
      }

      // Calculate days since meeting
      let daysSinceMeeting = 0;
      if (meetingDate) {
        const meetingDateObj = new Date(meetingDate);
        const now = new Date();
        daysSinceMeeting = Math.floor((now.getTime() - meetingDateObj.getTime()) / (1000 * 60 * 60 * 24));
      }

      // Add to meetings array with new fields
      meetings.push({
        id: entry.name,
        folder: entry.name,
        date: parsedDate,
        title,
        status,
        meeting_type: meetingType,
        cloaked,
        blocks,
        has_transcript: hasTranscript,
        manifest,
        done: (manifest?.done as boolean) || false,
        tags: (manifest?.tags as string[]) || [],
        needs_followup_email: needsFollowupEmail,
        needs_deliverables: needsDeliverables,
        needs_warm_intro: needsWarmIntro,
        needs_blurb: needsBlurb,
        days_since_meeting: daysSinceMeeting,
      });
    }

    // Sort by date descending
    meetings.sort((a, b) => b.date.localeCompare(a.date));

    return c.json({ meetings, count: meetings.length });
  } catch (error) {
    console.error("Error listing meetings:", error);
    return c.json({ error: "Failed to list meetings" }, 500);
  }
});

// Get single meeting details
app.get("/api/meetings/:id", async (c) => {
  const id = c.req.param("id");
  const folderPath = join(MEETINGS_PATH, id);

  if (!existsSync(folderPath)) {
    return c.json({ error: "Meeting not found" }, 404);
  }

  try {
    const files = await readdir(folderPath);
    const blocks: Record<string, string> = {};

    for (const file of files) {
      if (file.startsWith("B") && file.endsWith(".md")) {
        const content = await readFile(join(folderPath, file), "utf-8");
        blocks[file] = content;
      }
    }

    let manifest = null;
    const manifestPath = join(folderPath, "manifest.json");
    if (existsSync(manifestPath)) {
      manifest = JSON.parse(await readFile(manifestPath, "utf-8"));
    }

    let transcript = null;
    const transcriptFile = files.find(
      (f) => f.includes("transcript") && f.endsWith(".md")
    );
    if (transcriptFile) {
      transcript = await readFile(join(folderPath, transcriptFile), "utf-8");
    }

    let followUpEmail = null;
    if (files.includes("FOLLOW_UP_EMAIL.md")) {
      followUpEmail = await readFile(join(folderPath, "FOLLOW_UP_EMAIL.md"), "utf-8");
    }

    return c.json({
      id,
      blocks,
      manifest,
      transcript,
      follow_up_email: followUpEmail,
      files,
    });
  } catch (error) {
    console.error("Error getting meeting:", error);
    return c.json({ error: "Failed to get meeting" }, 500);
  }
});

// Get specific block content
app.get("/api/meetings/:id/blocks/:block", async (c) => {
  const id = c.req.param("id");
  const block = c.req.param("block");
  const filePath = join(MEETINGS_PATH, id, block);

  if (!existsSync(filePath)) {
    return c.json({ error: "Block not found" }, 404);
  }

  try {
    const content = await readFile(filePath, "utf-8");
    return c.json({ block, content });
  } catch (error) {
    return c.json({ error: "Failed to read block" }, 500);
  }
});

// Cloak/uncloak a meeting
app.post("/api/meetings/:id/cloak", async (c) => {
  const id = c.req.param("id");
  const manifestPath = join(MEETINGS_PATH, id, "manifest.json");

  try {
    let manifest: Record<string, unknown> = {};
    if (existsSync(manifestPath)) {
      manifest = JSON.parse(await readFile(manifestPath, "utf-8"));
    }

    manifest.cloaked = true;
    manifest.cloaked_at = new Date().toISOString();

    await writeFile(manifestPath, JSON.stringify(manifest, null, 2));
    return c.json({ success: true, cloaked: true });
  } catch (error) {
    console.error("Error cloaking meeting:", error);
    return c.json({ error: "Failed to cloak meeting" }, 500);
  }
});

app.post("/api/meetings/:id/uncloak", async (c) => {
  const id = c.req.param("id");
  const manifestPath = join(MEETINGS_PATH, id, "manifest.json");

  try {
    let manifest: Record<string, unknown> = {};
    if (existsSync(manifestPath)) {
      manifest = JSON.parse(await readFile(manifestPath, "utf-8"));
    }

    manifest.cloaked = false;
    delete manifest.cloaked_at;

    await writeFile(manifestPath, JSON.stringify(manifest, null, 2));
    return c.json({ success: true, cloaked: false });
  } catch (error) {
    return c.json({ error: "Failed to uncloak meeting" }, 500);
  }
});

// Toggle meeting done status
app.post("/api/meetings/:id/done", async (c) => {
  try {
    const { id } = c.req.param();
    const { done } = await c.req.json();
    const folderPath = join(MEETINGS_PATH, id);
    const manifestPath = join(folderPath, "manifest.json");
    
    let manifest: Record<string, unknown> = {};
    if (existsSync(manifestPath)) {
      manifest = JSON.parse(await readFile(manifestPath, "utf-8"));
    }
    
    manifest.done = done;
    manifest.done_timestamp = new Date().toISOString();
    
    await writeFile(manifestPath, JSON.stringify(manifest, null, 2));
    return c.json({ success: true, done });
  } catch (error) {
    console.error("Error updating done status:", error);
    return c.json({ error: "Failed to update done status" }, 500);
  }
});

// Update meeting tags
app.post("/api/meetings/:id/tags", async (c) => {
  try {
    const { id } = c.req.param();
    const { tags } = await c.req.json();
    const folderPath = join(MEETINGS_PATH, id);
    const manifestPath = join(folderPath, "manifest.json");
    
    let manifest: Record<string, unknown> = {};
    if (existsSync(manifestPath)) {
      manifest = JSON.parse(await readFile(manifestPath, "utf-8"));
    }
    
    manifest.tags = tags;
    manifest.tags_updated = new Date().toISOString();
    
    await writeFile(manifestPath, JSON.stringify(manifest, null, 2));
    return c.json({ success: true, tags });
  } catch (error) {
    console.error("Error updating tags:", error);
    return c.json({ error: "Failed to update tags" }, 500);
  }
});

// Trigger Zo action (uses zo CLI)
app.post("/api/meetings/:id/action", async (c) => {
  const id = c.req.param("id");
  const body = await c.req.json();
  const { action, block } = body;

  const meetingPath = join(MEETINGS_PATH, id);
  if (!existsSync(meetingPath)) {
    return c.json({ error: "Meeting not found" }, 404);
  }

  let prompt = "";

  switch (action) {
    case "generate_followup":
      prompt = `Generate a follow-up email for the meeting at ${meetingPath}. Use the Follow-Up Email Generator prompt. Save the result to ${meetingPath}/FOLLOW_UP_EMAIL.md`;
      break;
    case "generate_warm_intro":
      prompt = `Generate warm introduction drafts for the meeting at ${meetingPath}. Use the warm intro generator workflow.`;
      break;
    case "regenerate_block":
      if (!block) {
        return c.json({ error: "Block name required" }, 400);
      }
      prompt = `Regenerate the intelligence block ${block} for the meeting at ${meetingPath}. Read the transcript and regenerate this specific block following the block generation guidelines.`;
      break;
    case "export_to_drive":
      const { file } = body;
      if (!file) {
        return c.json({ error: "File name required" }, 400);
      }
      prompt = `Export the file ${file} from ${meetingPath} to Google Drive, making it ready to share. Use the Google Drive integration to upload it.`;
      break;
    default:
      return c.json({ error: "Unknown action" }, 400);
  }

  try {
    // Call zo CLI
    const result = await $`zo ${prompt}`.quiet();
    const output = JSON.parse(result.stdout.toString());

    return c.json({
      success: true,
      action,
      conversation_id: output.conversation_id,
      output: output.output,
    });
  } catch (error) {
    console.error("Error executing zo action:", error);
    return c.json({
      error: "Failed to execute action",
      details: String(error),
    }, 500);
  }
});

// Health check
app.get("/api/health", (c) => {
  return c.json({ status: "ok", timestamp: new Date().toISOString() });
});

// ============ FRONTEND ROUTING ============

if (mode === "production") {
  configureProduction(app);
} else {
  await configureDevelopment(app);
}

const port =
  mode === "production"
    ? (config.publish?.published_port ?? config.local_port)
    : config.local_port;

export default { fetch: app.fetch, port, idleTimeout: 255 };

function configureProduction(app: Hono) {
  // Serve all static files from dist (including assets/, favicon, logos, etc.)
  app.use("/*", async (c, next) => {
    const path = c.req.path;
    
    // Skip API routes
    if (path.startsWith("/api/")) {
      return next();
    }
    
    // Try to serve static file from dist
    const filePath = `./dist${path}`;
    if (existsSync(filePath) && !path.endsWith("/")) {
      const file = Bun.file(filePath);
      if (await file.exists()) {
        const contentType = getContentType(path);
        return new Response(file, {
          headers: { "Content-Type": contentType }
        });
      }
    }
    
    // Fall back to index.html for SPA routing
    return serveStatic({ path: "./dist/index.html" })(c, next);
  });
}

// Helper to determine content type
function getContentType(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase();
  const types: Record<string, string> = {
    'html': 'text/html',
    'css': 'text/css',
    'js': 'application/javascript',
    'json': 'application/json',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'webp': 'image/webp',
    'svg': 'image/svg+xml',
    'ico': 'image/x-icon',
    'woff': 'font/woff',
    'woff2': 'font/woff2',
  };
  return types[ext || ''] || 'application/octet-stream';
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







