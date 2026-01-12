import { Database } from "bun:sqlite";
import { join } from "path";
import { mkdirSync } from "fs";

// Database stored in data/ directory (gitignored)
const dataDir = join(import.meta.dir, "../../data");
mkdirSync(dataDir, { recursive: true });

const DB_PATH = join(dataDir, "sessions.db");
const db = new Database(DB_PATH);

// Initialize schema
db.exec(`
  CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    stripe_session_id TEXT,
    company TEXT,
    sentiment TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    report_summary TEXT
  );
  
  CREATE INDEX IF NOT EXISTS idx_sessions_stripe ON sessions(stripe_session_id);
  CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at);
`);

export interface Session {
  id: string;
  stripe_session_id: string | null;
  company: string;
  sentiment: string;
  created_at: string;
  report_summary: string | null;
}

export function createSession(
  id: string,
  company: string,
  sentiment: string
): void {
  const stmt = db.prepare(
    "INSERT INTO sessions (id, company, sentiment) VALUES (?, ?, ?)"
  );
  stmt.run(id, company, sentiment);
}

export function updateSessionStripe(
  id: string,
  stripeSessionId: string
): void {
  const stmt = db.prepare(
    "UPDATE sessions SET stripe_session_id = ? WHERE id = ?"
  );
  stmt.run(stripeSessionId, id);
}

export function updateSessionReport(
  id: string,
  reportSummary: string
): void {
  const stmt = db.prepare(
    "UPDATE sessions SET report_summary = ? WHERE id = ?"
  );
  stmt.run(reportSummary, id);
}

export function getSession(id: string): Session | undefined {
  const stmt = db.prepare("SELECT * FROM sessions WHERE id = ?");
  return stmt.get(id) as Session | undefined;
}

export function getSessionByStripe(stripeSessionId: string): Session | undefined {
  const stmt = db.prepare("SELECT * FROM sessions WHERE stripe_session_id = ?");
  return stmt.get(stripeSessionId) as Session | undefined;
}

export default db;

