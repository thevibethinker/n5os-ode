import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { readFileSync } from "fs";
import { handleInbox } from "./routes/inbox";
import { handleOutbox } from "./routes/outbox";
import { handleHealth } from "./routes/health";
import { handleCheckpoint } from "./routes/checkpoint";
import { handleBootstrap, handleBootstrapInfo } from "./routes/bootstrap";
import { logAudit } from "./lib/logger";

const config = JSON.parse(readFileSync("/home/workspace/N5/config/zobridge.config.json", "utf-8"));

const app = new Hono();

// Middleware
app.use("*", logger());
app.use("*", cors());

// Routes
app.get("/", (c) => {
  return c.json({
    service: "ZoBridge",
    system: config.system_name,
    version: "1.0.0",
    endpoints: [
      "POST /api/zobridge/inbox",
      "POST /api/zobridge/outbox",
      "GET /api/zobridge/health",
      "POST /api/zobridge/checkpoint",
      "GET /api/zobridge/bootstrap",
      "GET /api/zobridge/bootstrap/package",
    ],
  });
});

app.post("/api/zobridge/inbox", handleInbox);
app.post("/api/zobridge/outbox", handleOutbox);
app.get("/api/zobridge/health", handleHealth);
app.post("/api/zobridge/checkpoint", handleCheckpoint);
app.get("/api/zobridge/bootstrap", handleBootstrapInfo);
app.get("/api/zobridge/bootstrap/package", handleBootstrap);

// Start server
const port = config.port;
logAudit("server_starting", { port, system: config.system_name });

console.log(`🌉 ZoBridge service starting...`);
console.log(`   System: ${config.system_name}`);
console.log(`   Port: ${port}`);
console.log(`   Database: ${config.database_path}`);
console.log(`   Audit log: ${config.audit_log_path}`);
console.log(`\n✓ Server ready at http://localhost:${port}`);
console.log(`✓ Health check: http://localhost:${port}/api/zobridge/health\n`);

export default {
  port,
  fetch: app.fetch,
};
