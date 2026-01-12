// Promo Code System for Am I Hired?
// Allows free passes for feedback/testing purposes

import db from "./db";

export interface PromoCode {
  code: string;
  created_at: string;
  expires_at: string;
  uses_remaining: number;
  uses_total: number;
  created_by: string;
  note?: string;
}

export interface PromoValidationResult {
  valid: boolean;
  reason?: string;
  code?: PromoCode;
}

// Initialize promo_codes table
db.run(`
  CREATE TABLE IF NOT EXISTS promo_codes (
    code TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    uses_remaining INTEGER NOT NULL DEFAULT 5,
    uses_total INTEGER NOT NULL DEFAULT 5,
    created_by TEXT DEFAULT 'system',
    note TEXT
  )
`);

// Validate a promo code
export function validatePromoCode(code: string): PromoValidationResult {
  if (!code || code.trim() === "") {
    return { valid: false, reason: "No code provided" };
  }

  const normalizedCode = code.trim().toUpperCase();
  
  const stmt = db.prepare("SELECT * FROM promo_codes WHERE code = ?");
  const promo = stmt.get(normalizedCode) as PromoCode | undefined;

  if (!promo) {
    return { valid: false, reason: "Code not found" };
  }

  // Check expiration
  const now = new Date();
  const expiresAt = new Date(promo.expires_at);
  if (now > expiresAt) {
    return { valid: false, reason: "Code has expired", code: promo };
  }

  // Check uses remaining
  if (promo.uses_remaining <= 0) {
    return { valid: false, reason: "Code has been fully redeemed", code: promo };
  }

  return { valid: true, code: promo };
}

// Redeem a promo code (decrement uses)
export function redeemPromoCode(code: string): boolean {
  const normalizedCode = code.trim().toUpperCase();
  
  const result = db.run(
    "UPDATE promo_codes SET uses_remaining = uses_remaining - 1 WHERE code = ? AND uses_remaining > 0",
    [normalizedCode]
  );

  return result.changes > 0;
}

// Create a new promo code
export function createPromoCode(options: {
  prefix?: string;
  usesTotal?: number;
  expiresInDays?: number;
  createdBy?: string;
  note?: string;
}): PromoCode {
  const {
    prefix = "THANKS",
    usesTotal = 5,
    expiresInDays = 90,
    createdBy = "system",
    note,
  } = options;

  // Generate code: PREFIX-XXXX (4 random chars)
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const suffix = Array.from({ length: 4 }, () =>
    chars[Math.floor(Math.random() * chars.length)]
  ).join("");
  const code = `${prefix}-${suffix}`;

  const now = new Date();
  const expiresAt = new Date(now.getTime() + expiresInDays * 24 * 60 * 60 * 1000);

  db.run(
    `INSERT INTO promo_codes (code, created_at, expires_at, uses_remaining, uses_total, created_by, note)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
    [
      code,
      now.toISOString(),
      expiresAt.toISOString(),
      usesTotal,
      usesTotal,
      createdBy,
      note || null,
    ]
  );

  return {
    code,
    created_at: now.toISOString(),
    expires_at: expiresAt.toISOString(),
    uses_remaining: usesTotal,
    uses_total: usesTotal,
    created_by: createdBy,
    note,
  };
}

// Get promo code stats
export function getPromoCodeStats(code: string): PromoCode | null {
  const normalizedCode = code.trim().toUpperCase();
  const stmt = db.prepare("SELECT * FROM promo_codes WHERE code = ?");
  return stmt.get(normalizedCode) as PromoCode | null;
}

// List all active promo codes (admin)
export function listActivePromoCodes(): PromoCode[] {
  const now = new Date().toISOString();
  const stmt = db.prepare(
    "SELECT * FROM promo_codes WHERE expires_at > ? AND uses_remaining > 0 ORDER BY created_at DESC"
  );
  return stmt.all(now) as PromoCode[];
}

