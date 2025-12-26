import { Database } from "bun:sqlite";

const db = new Database("event-registrations.db");

// Initialize the registrations table
db.run(`
  CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    company TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

export interface Registration {
  id: number;
  name: string;
  email: string;
  company: string | null;
  notes: string | null;
  created_at: string;
}

export function getRecentRegistrations(limit = 10): Registration[] {
  return db
    .query(
      "SELECT id, name, email, company, notes, created_at FROM registrations ORDER BY created_at DESC LIMIT ?",
    )
    .all(limit) as Registration[];
}

export function createRegistration(
  name: string,
  email: string,
  company?: string,
  notes?: string,
): Registration {
  const insert = db.prepare(`
    INSERT INTO registrations (name, email, company, notes)
    VALUES (?, ?, ?, ?)
  `);

  const result = insert.run(name, email, company || null, notes || null);

  return db
    .query("SELECT * FROM registrations WHERE id = ?")
    .get(result.lastInsertRowid) as Registration;
}

export default db;
