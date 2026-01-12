import { Context } from "hono";
import { getStats } from "../lib/db";
import { logAudit } from "../lib/logger";

export function handleHealth(c: Context) {
  try {
    const stats = getStats();
    const status = {
      status: "healthy",
      timestamp: new Date().toISOString(),
      system: "ParentZo",
      stats,
      last_received_at: stats?.last_received_at || null,
      delivered_count: stats?.total_messages || 0,
    };

    return c.json(status);
  } catch (error: any) {
    logAudit("health_check_failed", { error: error.message });
    return c.json({
      status: "unhealthy",
      error: error.message,
    }, 500);
  }
}
