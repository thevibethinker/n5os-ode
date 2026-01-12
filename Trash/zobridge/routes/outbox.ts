import { Context } from "hono";
import { storeMessage, checkRateLimit } from "../lib/db";
import { validateMessage, validateAuth } from "../lib/validator";
import { logMessage, logError } from "../lib/logger";
import { readFileSync } from "fs";

const config = JSON.parse(readFileSync("/home/workspace/N5/config/zobridge.config.json", "utf-8"));

export async function handleOutbox(c: Context) {
  try {
    // Validate authentication
    const authHeader = c.req.header("Authorization");
    if (!validateAuth(authHeader || null)) {
      logError("outbox_auth_failed", { headers: c.req.header() });
      return c.json({ error: "Unauthorized" }, 401);
    }

    // Parse message
    const message = await c.req.json();

    // Validate message structure
    const validation = validateMessage(message);
    if (!validation.valid) {
      logError("outbox_validation_failed", { errors: validation.errors, message });
      return c.json({ error: "Invalid message", details: validation.errors }, 400);
    }

    // Verify this message is FROM us
    if (message.from !== config.system_name) {
      logError("outbox_wrong_sender", { expected: config.system_name, got: message.from });
      return c.json({ error: "Message must be from this system" }, 400);
    }

    // Check rate limit
    if (!checkRateLimit(message.to)) {
      logError("outbox_rate_limit", { to: message.to });
      return c.json({ error: "Rate limit exceeded" }, 429);
    }

    // Store message
    storeMessage(message);
    logMessage("sent", message);

    // Return the message for delivery
    return c.json({
      status: "ready_to_send",
      message,
    });
  } catch (error: any) {
    logError("outbox_handler", error);
    return c.json({ error: "Internal server error", details: error.message }, 500);
  }
}
