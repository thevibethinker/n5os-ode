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
    self_assessment TEXT,
    customer_name TEXT,
    customer_email TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    report_summary TEXT
  );
  
  CREATE INDEX IF NOT EXISTS idx_sessions_stripe ON sessions(stripe_session_id);
  CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at);
`);

// Migration: Add new columns if they don't exist (for existing databases)
try {
  db.exec(`ALTER TABLE sessions ADD COLUMN customer_name TEXT`);
} catch (e) { /* column exists */ }
try {
  db.exec(`ALTER TABLE sessions ADD COLUMN customer_email TEXT`);
} catch (e) { /* column exists */ }

export interface Session {
  id: string;
  stripe_session_id: string | null;
  company: string;
  self_assessment: string;
  customer_name: string | null;
  customer_email: string | null;
  created_at: string;
  report_summary: string | null;
}

export function createSession(
  id: string,
  company: string,
  selfAssessment: string,
  customerName: string,
  customerEmail: string
): void {
  const stmt = db.prepare(
    "INSERT INTO sessions (id, company, self_assessment, customer_name, customer_email) VALUES (?, ?, ?, ?, ?)"
  );
  stmt.run(id, company, selfAssessment, customerName, customerEmail);
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



