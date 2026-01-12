// Transcript storage using SQLite for persistence
// Transcripts auto-expire after 30 minutes for privacy

import { Database } from "bun:sqlite";
import { join } from "path";
import { mkdirSync } from "fs";

// Database stored in data/ directory (gitignored)
const dataDir = join(import.meta.dir, "../../data");
mkdirSync(dataDir, { recursive: true });

const DB_PATH = join(dataDir, "transcripts.db");
const db = new Database(DB_PATH);

// Initialize schema
db.exec(`
  CREATE TABLE IF NOT EXISTS transcripts (
    session_id TEXT PRIMARY KEY,
    transcript TEXT NOT NULL,
    company TEXT NOT NULL,
    job_description TEXT NOT NULL,
    self_assessment TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    created_at INTEGER NOT NULL
  );
  
  CREATE INDEX IF NOT EXISTS idx_transcripts_created ON transcripts(created_at);
`);

const EXPIRY_MS = 30 * 60 * 1000; // 30 minutes

export interface TranscriptEntry {
  transcript: string;
  company: string;
  jobDescription: string;
  selfAssessment: string;
  customerName: string;
  customerEmail: string;
  createdAt: number;
}

export function storeTranscript(
  sessionId: string,
  transcript: string,
  company: string,
  jobDescription: string,
  selfAssessment: string,
  customerName: string,
  customerEmail: string
): void {
  // Clean expired entries first
  cleanExpired();

  const stmt = db.prepare(`
    INSERT OR REPLACE INTO transcripts 
    (session_id, transcript, company, job_description, self_assessment, customer_name, customer_email, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(sessionId, transcript, company, jobDescription, selfAssessment, customerName, customerEmail, Date.now());
}

export function getTranscript(sessionId: string): TranscriptEntry | undefined {
  const stmt = db.prepare(`
    SELECT transcript, company, job_description, self_assessment, customer_name, customer_email, created_at 
    FROM transcripts WHERE session_id = ?
  `);
  const row = stmt.get(sessionId) as {
    transcript: string;
    company: string;
    job_description: string;
    self_assessment: string;
    customer_name: string;
    customer_email: string;
    created_at: number;
  } | null;
  
  if (!row) return undefined;

  // Check if expired
  if (Date.now() - row.created_at > EXPIRY_MS) {
    deleteTranscript(sessionId);
    return undefined;
  }

  return {
    transcript: row.transcript,
    company: row.company,
    jobDescription: row.job_description,
    selfAssessment: row.self_assessment,
    customerName: row.customer_name,
    customerEmail: row.customer_email,
    createdAt: row.created_at,
  };
}

export function deleteTranscript(sessionId: string): void {
  const stmt = db.prepare("DELETE FROM transcripts WHERE session_id = ?");
  stmt.run(sessionId);
}

function cleanExpired(): void {
  const cutoff = Date.now() - EXPIRY_MS;
  const stmt = db.prepare("DELETE FROM transcripts WHERE created_at < ?");
  const result = stmt.run(cutoff);
  if (result.changes > 0) {
    console.log(`[Transcript Cleanup] Deleted ${result.changes} expired transcripts`);
  }
}

// Run cleanup every 5 minutes
setInterval(cleanExpired, 5 * 60 * 1000);

// Also run cleanup on startup
cleanExpired();

