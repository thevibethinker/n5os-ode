// ZoBridge Parent->Child relay
// Fetches ParentZo outbox (to=ChildZo) and posts to ChildZo inbox

import { readFileSync } from "fs";
import { execSync } from "child_process";

function getSecret(): string {
  // Try secrets manager first (P34)
  try {
    const secret = execSync(
      'python3 /home/workspace/N5/scripts/n5_secrets.py get zobridge_secret',
      { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }
    ).trim();
    if (secret) {
      console.log("relay: loaded secret from N5 secrets manager");
      return secret;
    }
  } catch (e) {
    console.warn("relay: secrets manager unavailable, trying config file");
  }
  
  // Fallback to config file
  try {
    const cfg = JSON.parse(readFileSync("/home/workspace/N5/services/zobridge/zobridge.config.json", "utf-8"));
    if (cfg.secret) return cfg.secret;
  } catch (e) {
    console.warn("relay: failed to read secret from file, falling back to env", e);
  }
  
  // Final fallback to env
  return process.env.ZOBRIDGE_SECRET || "";
}

function getParentLocalBase(): string {
  try {
    const cfg = JSON.parse(readFileSync("/home/workspace/N5/config/zobridge.config.json", "utf-8"));
    const port = cfg.port || 3458;
    return `http://localhost:${port}`;
  } catch {
    return "http://localhost:3458";
  }
}

const PARENT_LOCAL_BASE = getParentLocalBase();
const CHILD_URL = process.env.CHILDZO_URL || "https://zobridge-vademonstrator.zocomputer.io";
const INTERVAL_MS = Number(process.env.P2C_POLL_INTERVAL_MS || "10000");
const TOKEN = getSecret();

const COMMON_HEADERS: Record<string, string> = {
  Authorization: `Bearer ${TOKEN}`,
  "User-Agent": "zobridge-relay/1.0",
  Accept: "application/json",
  "Cache-Control": "no-cache",
};

const seen = new Set<string>();

async function fetchParentOutbox() {
  const url = `${PARENT_LOCAL_BASE}/api/zobridge/outbox?to=ChildZo`;
  const res = await fetch(url, { headers: COMMON_HEADERS });
  if (!res.ok) {
    const t = await res.text();
    console.error("relay: outbox fetch error", res.status, t.slice(0, 200));
    return null as any;
  }
  return res.json();
}

async function postToChildInbox(message: any) {
  const url = `${CHILD_URL}/api/zobridge/inbox`;
  const res = await fetch(url, {
    method: "POST",
    headers: { ...COMMON_HEADERS, "Content-Type": "application/json" },
    body: JSON.stringify(message),
  });
  if (!res.ok) {
    const t = await res.text();
    console.error("relay: inbox post error", res.status, t.slice(0, 200));
    return false;
  }
  return true;
}

function jitter(ms: number) { return ms + Math.floor(Math.random() * 300); }

async function main() {
  console.log("zobridge-relay starting", { PARENT_LOCAL_BASE, CHILD_URL, INTERVAL_MS });
  let delay = INTERVAL_MS;
  const MAX_DELAY = 60000;
  for (;;) {
    try {
      const data = await fetchParentOutbox();
      if (data && Array.isArray(data.messages)) {
        for (const msg of data.messages) {
          if (!msg?.message_id) continue;
          if (seen.has(msg.message_id)) continue;
          const ok = await postToChildInbox(msg);
          if (ok) {
            seen.add(msg.message_id);
            console.log(`relay: delivered ${msg.message_id} -> ChildZo`);
          }
        }
      }
      delay = INTERVAL_MS;
    } catch (e) {
      console.error("relay: cycle error", e);
      delay = Math.min(delay * 1.5, MAX_DELAY);
    }
    await new Promise((r) => setTimeout(r, jitter(delay)));
  }
}

main().catch((e) => {
  console.error("relay: fatal", e);
  process.exit(1);
});
