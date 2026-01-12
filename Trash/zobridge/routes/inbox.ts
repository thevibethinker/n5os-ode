import { Context } from "hono";
import { storeMessage, checkRateLimit, markProcessed } from "../lib/db";
import { validateMessage, validateAuth } from "../lib/validator";
import { logMessage, logError, logProcessing } from "../lib/logger";
import { readFileSync } from "fs";

const config = JSON.parse(readFileSync("/home/workspace/N5/config/zobridge.config.json", "utf-8"));

export async function handleInbox(c: Context) {
  try {
    // Validate authentication
    const authHeader = c.req.header("Authorization");
    if (!validateAuth(authHeader || null)) {
      logError("inbox_auth_failed", { headers: c.req.header() });
      return c.json({ error: "Unauthorized" }, 401);
    }

    // Parse message
    const message = await c.req.json();

    // Validate message structure
    const validation = validateMessage(message);
    if (!validation.valid) {
      logError("inbox_validation_failed", { errors: validation.errors, message });
      return c.json({ error: "Invalid message", details: validation.errors }, 400);
    }

    // Verify this message is TO us
    if (message.to !== config.system_name) {
      logError("inbox_wrong_recipient", { expected: config.system_name, got: message.to });
      return c.json({ error: "Message not addressed to this system" }, 400);
    }

    // Check rate limit
    if (!checkRateLimit(message.from)) {
      logError("inbox_rate_limit", { from: message.from });
      return c.json({ error: "Rate limit exceeded" }, 429);
    }

    // Store message
    storeMessage(message);
    logMessage("received", message);
    logProcessing(message.message_id, "received_and_queued");

    return c.json({
      status: "received",
      message_id: message.message_id,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    logError("inbox_handler", error);
    return c.json({ error: "Internal server error", details: error.message }, 500);
  }
}
