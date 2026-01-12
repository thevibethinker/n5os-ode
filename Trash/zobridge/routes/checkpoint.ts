import { Context } from "hono";
import { getThreadMessages, getStats } from "../lib/db";
import { validateAuth } from "../lib/validator";
import { logAudit } from "../lib/logger";

export async function handleCheckpoint(c: Context) {
  try {
    // Validate authentication
    const authHeader = c.req.header("Authorization");
    if (!validateAuth(authHeader || null)) {
      return c.json({ error: "Unauthorized" }, 401);
    }

    const body = await c.req.json();
    const threadId = body.thread_id;

    if (!threadId) {
      return c.json({ error: "thread_id required" }, 400);
    }

    const messages = getThreadMessages(threadId);
    const stats = getStats();

    logAudit("checkpoint_requested", { thread_id: threadId, message_count: messages.length });

    return c.json({
      status: "checkpoint",
      thread_id: threadId,
      message_count: messages.length,
      messages,
      system_stats: stats,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    logAudit("checkpoint_failed", { error: error.message });
    return c.json({ error: "Internal server error", details: error.message }, 500);
  }
}
