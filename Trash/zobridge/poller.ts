// ZoBridge Poller (ParentZo)
// Periodically polls ChildZo outbox and forwards messages to ParentZo inbox

import { readFileSync } from "fs";

// Read secret from local config file instead of process.env
function getSecret(): string {
  try {
    const configPath = "/home/workspace/N5/services/zobridge/zobridge.config.json";
    const localConfig = JSON.parse(readFileSync(configPath, "utf-8"));
    if (localConfig.secret) {
      return localConfig.secret;
    }
  } catch (e) {
    console.warn("Failed to read config file, falling back to env vars:", e);
  }
  return process.env.ZOBRIDGE_SECRET || process.env.ZOBRIDGE_TOKEN || "";
}

const CHILD_URL = process.env.CHILDZO_URL || "https://zobridge-vademonstrator.zocomputer.io";
const PARENT_URL = process.env.PARENTZO_URL || "https://zobridge-va.zocomputer.io";
const INTERVAL_MS = Number(process.env.POLL_INTERVAL_MS) || 10000;
const TOKEN = getSecret();

// NEW: In-memory dedupe of forwarded messages
const RECENT_MAX = 1000;
const recentMessageIds = new Set<string>();
function seenId(id: string): boolean { return recentMessageIds.has(id); }
function rememberId(id: string): void {
  if (recentMessageIds.has(id)) return;
  recentMessageIds.add(id);
  if (recentMessageIds.size > RECENT_MAX) {
    const first = recentMessageIds.values().next().value;
    if (first) recentMessageIds.delete(first);
  }
}

function isValidId(id: string | undefined): boolean {
  return !!id && /^(msg|resp)_[A-Za-z0-9_-]+$/.test(id);
}

function normalizeMessage(msg: any): any | null {
  const required = ["message_id", "timestamp", "from", "to", "type", "content"];
  for (const field of required) {
    if (!msg[field]) {
      console.warn(`Skipping message: missing required field ${field}`);
      return null;
    }
  }
  // Add timestamp if missing (unlikely according to spec)
  if (!msg.timestamp) {
    msg.timestamp = new Date().toISOString();
  }
  return msg;
}

async function pollOnce() {
  try {
    const res = await fetch(CHILD_URL + "/api/zobridge/outbox?to=ParentZo", {
      headers: {
        Authorization: `Bearer ${TOKEN}`,
        "User-Agent": "zobridge/1.0 (+parentzo)",
        Accept: "application/json",
        "Cache-Control": "no-store",
        Pragma: "no-cache",
      },
      cache: "no-store",
      redirect: "follow",
    });

    if (!res.ok) {
      const text = await res.text();
      console.error("Poll error", res.status, text.slice(0, 200));
      return { status: "error", code: res.status } as const;
    }
    
    const data = await res.json();
    const messages = data.messages || [];
    if (messages.length === 0) {
      return { status: "ok", forwarded: 0, encountered429: false } as const;
    }

    let forwarded = 0;
    let encountered429 = false;
    for (const msg of messages) {
      if (!isValidId(msg?.message_id)) {
        console.warn("Skipping malformed message_id", msg?.message_id);
        continue;
      }
      const normalized = normalizeMessage(msg);
      if (!normalized) continue;
      if (seenId(normalized.message_id)) {
        continue; // dedupe: already forwarded in this runtime
      }

      const postRes = await fetch(PARENT_URL + "/api/zobridge/inbox", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${TOKEN}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(normalized),
      });

      if (!postRes.ok) {
        const errorText = await postRes.text();
        console.error("Inbox post failed", postRes.status, errorText);
        if (postRes.status === 429) {
          encountered429 = true;
          break; // respect rate limit: stop forwarding this cycle
        }
      } else {
        forwarded++;
        rememberId(normalized.message_id);
        console.log(`Forwarded message_id=${normalized.message_id} type=${normalized.type}`);
      }
    }

    return { status: "ok", forwarded, encountered429 } as const;
  } catch (e) {
    console.error("Poll exception", e);
    return { status: "exception", encountered429: false } as const;
  }
}

async function main() {
  console.log("ZoBridge poller starting", { CHILD_URL, PARENT_URL, INTERVAL_MS });
  console.log("Using token:", TOKEN.substring(0, 20) + "...");

  // NEW: exponential backoff on 429
  let delay = INTERVAL_MS;
  const MAX_DELAY = 60000; // 60s cap

  function jitter(ms: number) { return ms + Math.floor(Math.random() * 500); }

  for (;;) {
    const res: any = await pollOnce();
    if (res && res.encountered429) {
      delay = Math.min(delay * 2, MAX_DELAY);
    } else if (res && res.status === "error") {
      delay = Math.min(delay * 1.5, MAX_DELAY);
    } else {
      delay = INTERVAL_MS;
    }
    await new Promise((r) => setTimeout(r, jitter(delay)));
  }
}

main().catch((e) => {
  console.error("Fatal", e);
  process.exit(1);
});
