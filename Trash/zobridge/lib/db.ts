import { Database } from "bun:sqlite";
import { readFileSync } from "fs";

const configPath = "/home/workspace/N5/config/zobridge.config.json";
const config = JSON.parse(readFileSync(configPath, "utf-8"));

export const db = new Database(config.database_path);

// Initialize schema
db.run(`
  CREATE TABLE IF NOT EXISTS messages (
    message_id TEXT PRIMARY KEY,
    thread_id TEXT,
    from_system TEXT NOT NULL,
    to_system TEXT NOT NULL,
    type TEXT NOT NULL,
    content_json TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    processed BOOLEAN DEFAULT 0,
    response_id TEXT,
    created_at TEXT DEFAULT (datetime('now'))
  )
`);

db.run(`
  CREATE TABLE IF NOT EXISTS threads (
    thread_id TEXT PRIMARY KEY,
    subject TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    message_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active'
  )
`);

db.run(`
  CREATE TABLE IF NOT EXISTS rate_limits (
    system TEXT NOT NULL,
    hour_bucket TEXT NOT NULL,
    minute_bucket TEXT NOT NULL,
    hour_count INTEGER DEFAULT 0,
    minute_count INTEGER DEFAULT 0,
    PRIMARY KEY (system, hour_bucket, minute_bucket)
  )
`);

db.run(`
  CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id)
`);

db.run(`
  CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)
`);

export interface ZoBridgeMessage {
  message_id: string;
  timestamp: string;
  from: string;
  to: string;
  thread_id?: string;
  in_reply_to?: string;
  type: string;
  content: any;
  expects_reply?: boolean;
  notes?: string;
}

// Returns true if inserted, false if duplicate ignored
export function storeMessage(msg: ZoBridgeMessage): boolean {
  try {
    const result = db.run(
      `INSERT OR IGNORE INTO messages (message_id, thread_id, from_system, to_system, type, content_json, timestamp)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [
        msg.message_id,
        msg.thread_id || null,
        msg.from,
        msg.to,
        msg.type,
        JSON.stringify(msg.content),
        msg.timestamp,
      ]
    );

    const inserted = Number((result as any).changes || 0) > 0;

    if (inserted && msg.thread_id) {
      db.run(
        `INSERT INTO threads (thread_id, subject, message_count)
         VALUES (?, ?, 1)
         ON CONFLICT(thread_id) DO UPDATE SET message_count = message_count + 1`,
        [msg.thread_id, (msg as any).content?.subject || "Untitled"]
      );
    }

    return inserted;
  } catch (e: any) {
    if (String(e?.message || e).includes("UNIQUE constraint failed: messages.message_id")) {
      return false;
    }
    throw e;
  }
}

export function getMessage(messageId: string): ZoBridgeMessage | null {
  const row = db
    .query(
      `SELECT message_id, thread_id, from_system, to_system, type, content_json, timestamp
       FROM messages WHERE message_id = ?`
    )
    .get(messageId) as any;

  if (!row) return null;

  return {
    message_id: row.message_id,
    timestamp: row.timestamp,
    from: row.from_system,
    to: row.to_system,
    thread_id: row.thread_id,
    type: row.type,
    content: JSON.parse(row.content_json),
  };
}

export function getThreadMessages(threadId: string): ZoBridgeMessage[] {
  const rows = db
    .query(
      `SELECT message_id, thread_id, from_system, to_system, type, content_json, timestamp
       FROM messages WHERE thread_id = ? ORDER BY timestamp ASC`
    )
    .all(threadId) as any[];

  return rows.map((row) => ({
    message_id: row.message_id,
    timestamp: row.timestamp,
    from: row.from_system,
    to: row.to_system,
    thread_id: row.thread_id,
    type: row.type,
    content: JSON.parse(row.content_json),
  }));
}

export function markProcessed(messageId: string, responseId?: string): void {
  db.run(
    `UPDATE messages SET processed = 1, response_id = ? WHERE message_id = ?`,
    [responseId || null, messageId]
  );
}

export function checkRateLimit(system: string): boolean {
  const now = new Date();
  const hourBucket = now.toISOString().slice(0, 13); // YYYY-MM-DDTHH
  const minuteBucket = now.toISOString().slice(0, 16); // YYYY-MM-DDTHH:MM

  // Get or create rate limit record
  db.run(
    `INSERT INTO rate_limits (system, hour_bucket, minute_bucket, hour_count, minute_count)
     VALUES (?, ?, ?, 0, 0)
     ON CONFLICT(system, hour_bucket, minute_bucket) DO NOTHING`,
    [system, hourBucket, minuteBucket]
  );

  // Get current counts
  const row = db
    .query(
      `SELECT hour_count, minute_count FROM rate_limits
       WHERE system = ? AND hour_bucket = ? AND minute_bucket = ?`
    )
    .get(system, hourBucket, minuteBucket) as any;

  if (!row) return true;

  // Check limits
  if (row.hour_count >= config.rate_limit.max_per_hour) return false;
  if (row.minute_count >= config.rate_limit.max_per_minute) return false;

  // Increment counts
  db.run(
    `UPDATE rate_limits SET hour_count = hour_count + 1, minute_count = minute_count + 1
     WHERE system = ? AND hour_bucket = ? AND minute_bucket = ?`,
    [system, hourBucket, minuteBucket]
  );

  return true;
}

export function getStats() {
  const totalMessages = db.query(`SELECT COUNT(*) as count FROM messages`).get() as any;
  const activeThreads = db.query(`SELECT COUNT(*) as count FROM threads WHERE status = 'active'`).get() as any;
  const processedMessages = db.query(`SELECT COUNT(*) as count FROM messages WHERE processed = 1`).get() as any;
  const lastReceived = db.query(`SELECT created_at as ts FROM messages ORDER BY created_at DESC LIMIT 1`).get() as any;

  return {
    total_messages: totalMessages.count,
    active_threads: activeThreads.count,
    processed_messages: processedMessages.count,
    unprocessed_messages: totalMessages.count - processedMessages.count,
    last_received_at: lastReceived?.ts || null,
  };
}
