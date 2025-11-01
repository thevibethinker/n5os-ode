import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { serveStatic } from "hono/bun";

const app = new Hono();

app.use("*", logger());
app.use("*", cors());

app.use("/src/*", serveStatic({ root: "." }));
app.use("/assets/*", serveStatic({ root: "./public" }));
app.use("/public/*", serveStatic({ root: "." }));

app.get("*", async (c) => {
  const file = Bun.file("./index.html");
  return c.html(await file.text());
});

const port = parseInt(process.env.PORT || "50529");
const env = process.env.NODE_ENV || "development";

console.log();

export default {
  port,
  fetch: app.fetch,
};
