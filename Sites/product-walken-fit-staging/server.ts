import { serveStatic } from "hono/bun";
import type { ViteDevServer } from "vite";
import { createServer as createViteServer } from "vite";
import config from "./zosite.json";
import { Hono } from "hono";
import { getRecentRegistrations, createRegistration } from "./backend-lib/db";

type Mode = "development" | "production";
const app = new Hono();

const mode: Mode =
  process.env.NODE_ENV === "production" ? "production" : "development";

// --- User Quotes Store Helpers ---
const USER_QUOTES_PATH = "./src/data/quotes.json";

interface UserQuote {
  id: string;
  originalQuote: string;
  originalAuthor: string;
  source?: string;
  category: string;
  createdAt: string;
}

interface UserQuotesStore {
  schema: string;
  quotes: UserQuote[];
}

async function readUserQuotes(): Promise<UserQuotesStore> {
  try {
    const file = Bun.file(USER_QUOTES_PATH);
    const text = await file.text();
    return JSON.parse(text);
  } catch {
    return { schema: "keanu-to-market.quotes.user.v1", quotes: [] };
  }
}

function writeUserQuotes(store: UserQuotesStore): void {
  Bun.write(USER_QUOTES_PATH, JSON.stringify(store, null, 2));
}

function normalizeForDedupe(text: string): string {
  return text.toLowerCase().replace(/\s+/g, " ").trim();
}

const VALID_CATEGORIES = ["sales", "marketing", "product", "growth", "leadership", "strategy"];
const MAX_QUOTE_LENGTH = 2000;
const MAX_AUTHOR_LENGTH = 200;
const MAX_SOURCE_LENGTH = 500;

// --- API Routes ---

/**
 * Add any API routes here.
 */
app.get("/api/hello-zo", (c) => c.json({ msg: "Hello from Zo" }));

// Health endpoint
app.get("/api/health", (c) => {
  return c.json({
    ok: true,
    timestamp: new Date().toISOString(),
    version: "keanu-to-market"
  });
});

// Gated quote submission endpoint
app.post("/api/quotes", async (c) => {
  const writeKey = process.env.KEANU_TO_MARKET_WRITE_KEY;
  if (!writeKey) {
    return c.json({ error: "Write access not configured" }, 401);
  }

  const providedKey = c.req.header("x-keanu-write-key");
  if (!providedKey || providedKey !== writeKey) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  let body: Record<string, unknown>;
  try {
    body = await c.req.json();
  } catch {
    return c.json({ error: "Invalid JSON body" }, 400);
  }

  const { originalQuote, originalAuthor, source, category } = body;

  // Validate required fields
  if (!originalQuote || typeof originalQuote !== "string" || originalQuote.trim() === "") {
    return c.json({ error: "originalQuote is required and must be non-empty" }, 400);
  }
  if (!originalAuthor || typeof originalAuthor !== "string" || originalAuthor.trim() === "") {
    return c.json({ error: "originalAuthor is required and must be non-empty" }, 400);
  }
  if (!category || typeof category !== "string" || !VALID_CATEGORIES.includes(category)) {
    return c.json({ error: `category is required and must be one of: ${VALID_CATEGORIES.join(", ")}` }, 400);
  }

  // Validate max lengths
  if (originalQuote.length > MAX_QUOTE_LENGTH) {
    return c.json({ error: `originalQuote exceeds max length of ${MAX_QUOTE_LENGTH}` }, 400);
  }
  if (originalAuthor.length > MAX_AUTHOR_LENGTH) {
    return c.json({ error: `originalAuthor exceeds max length of ${MAX_AUTHOR_LENGTH}` }, 400);
  }
  if (source && typeof source === "string" && source.length > MAX_SOURCE_LENGTH) {
    return c.json({ error: `source exceeds max length of ${MAX_SOURCE_LENGTH}` }, 400);
  }

  const store = await readUserQuotes();

  // Dedupe check
  const normalizedQuote = normalizeForDedupe(originalQuote as string);
  const normalizedAuthor = normalizeForDedupe(originalAuthor as string);
  const isDuplicate = store.quotes.some(
    (q) =>
      normalizeForDedupe(q.originalQuote) === normalizedQuote &&
      normalizeForDedupe(q.originalAuthor) === normalizedAuthor
  );

  if (isDuplicate) {
    return c.json({ error: "This quote already exists" }, 409);
  }

  const newQuote: UserQuote = {
    id: crypto.randomUUID(),
    originalQuote: (originalQuote as string).trim(),
    originalAuthor: (originalAuthor as string).trim(),
    source: source && typeof source === "string" ? source.trim() : undefined,
    category: category as string,
    createdAt: new Date().toISOString()
  };

  store.quotes.push(newQuote);
  writeUserQuotes(store);

  return c.json({ success: true, quote: newQuote }, 201);
});

// Debug endpoint (only when DEBUG_MODE=1)
app.get("/api/debug", async (c) => {
  if (process.env.DEBUG_MODE !== "1") {
    return c.json({ error: "Not found" }, 404);
  }

  const store = await readUserQuotes();
  return c.json({
    writeEnabled: !!process.env.KEANU_TO_MARKET_WRITE_KEY,
    userQuotesCount: store.quotes.length
  });
});

// Event registration endpoints (namespaced under _zo to avoid conflicts)
app.get("/api/_zo/demo/registrations", (c) => {
  const registrations = getRecentRegistrations();
  return c.json(registrations);
});

app.post("/api/_zo/demo/register", async (c) => {
  const body = await c.req.json();
  const { name, email, company, notes } = body;

  if (!name || !email) {
    return c.json({ error: "Name and email are required" }, 400);
  }

  const registration = createRegistration(name, email, company, notes);
  return c.json(registration, 201);
});

if (mode === "production") {
  configureProduction(app);
} else {
  await configureDevelopment(app);
}

/**
 * Determine port based on mode. In production, use the published_port if available.
 * In development, always use the local_port.
 * Ports are managed by the system and injected via the PORT environment variable.
 */
const port = process.env.PORT
  ? parseInt(process.env.PORT, 10)
  : mode === "production"
    ? (config.publish?.published_port ?? config.local_port)
    : config.local_port;

export default { fetch: app.fetch, port, idleTimeout: 255 };

/**
 * Configure routing for production builds.
 *
 * - Streams prebuilt assets from `dist`.
 * - Static files from `public/` are copied to `dist/` by Vite and served at root paths.
 * - Falls back to `index.html` for any other GET so the SPA router can resolve the request.
 */
function configureProduction(app: Hono) {
  app.use("/assets/*", serveStatic({ root: "./dist" }));
  app.get("/favicon.ico", (c) => c.redirect("/favicon.svg", 302));
  app.use(async (c, next) => {
    if (c.req.method !== "GET") return next();

    const path = c.req.path;
    if (path.startsWith("/api/") || path.startsWith("/assets/")) return next();

    const file = Bun.file(`./dist${path}`);
    if (await file.exists()) {
      const stat = await file.stat();
      if (stat && !stat.isDirectory()) {
        return new Response(file);
      }
    }

    return serveStatic({ path: "./dist/index.html" })(c, next);
  });
}

/**
 * Configure routing for development builds.
 *
 * - Boots Vite in middleware mode for transforms.
 * - Static files from `public/` are served at root paths (matching Vite convention).
 * - Mirrors production routing semantics so SPA routes behave consistently.
 */
async function configureDevelopment(app: Hono): Promise<ViteDevServer> {
  const vite = await createViteServer({
    server: { middlewareMode: true, hmr: false, ws: false },
    appType: "custom",
  });

  app.use("*", async (c, next) => {
    if (c.req.path.startsWith("/api/")) return next();
    if (c.req.path === "/favicon.ico") return c.redirect("/favicon.svg", 302);

    const url = c.req.path;
    try {
      if (url === "/" || url === "/index.html") {
        let template = await Bun.file("./index.html").text();
        template = await vite.transformIndexHtml(url, template);
        return c.html(template);
      }

      const publicFile = Bun.file(`./public${url}`);
      if (await publicFile.exists()) {
        const stat = await publicFile.stat();
        if (stat && !stat.isDirectory()) {
          return new Response(publicFile, {
            headers: { "Cache-Control": "no-cache" },
          });
        }
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
