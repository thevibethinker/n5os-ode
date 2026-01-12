import { Context } from "hono";
import { readFileSync, existsSync } from "fs";
import { logAudit } from "../lib/logger";

const PACKAGE_PATH = "/home/workspace/zobridge_childzo_deployment.zip";

export function handleBootstrap(c: Context) {
  try {
    if (!existsSync(PACKAGE_PATH)) {
      logAudit("bootstrap_package_not_found", { path: PACKAGE_PATH });
      return c.json({ error: "Bootstrap package not found" }, 404);
    }

    logAudit("bootstrap_package_requested", {
      path: PACKAGE_PATH,
      requestor: c.req.header("user-agent") || "unknown",
    });

    const packageData = readFileSync(PACKAGE_PATH);

    return new Response(packageData, {
      headers: {
        "Content-Type": "application/zip",
        "Content-Disposition": "attachment; filename=zobridge_childzo_deployment.zip",
        "Content-Length": packageData.length.toString(),
      },
    });
  } catch (error: any) {
    logAudit("bootstrap_error", { error: error.message });
    return c.json({ error: "Failed to serve bootstrap package", details: error.message }, 500);
  }
}

export function handleBootstrapInfo(c: Context) {
  try {
    if (!existsSync(PACKAGE_PATH)) {
      return c.json({ available: false });
    }

    const stats = require("fs").statSync(PACKAGE_PATH);

    return c.json({
      available: true,
      package: "ZoBridge ChildZo Deployment Package",
      size_bytes: stats.size,
      size_human: `${(stats.size / 1024).toFixed(1)} KB`,
      download_url: "/api/zobridge/bootstrap/package",
      instructions: [
        "1. Download: curl -O https://zobridge-va.zocomputer.io/api/zobridge/bootstrap/package",
        "2. Extract: unzip zobridge_childzo_deployment.zip",
        "3. Deploy: cd childzo_package && cat DEPLOY.md",
      ],
    });
  } catch (error: any) {
    return c.json({ error: error.message }, 500);
  }
}
