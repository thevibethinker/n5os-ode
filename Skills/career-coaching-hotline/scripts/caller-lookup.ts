import { parsePhoneNumber, isValidPhoneNumber } from "libphonenumber-js";

export interface CallerProfile {
  id: string;
  name: string;
  phone: string;
  email: string | null;
  linkedin_url: string | null;
  career_stage: string | null;
  help_topic: string | null;
  resume_text: string | null;
  caller_brief: string | null;
  source: string | null;
  created_at: string;
  last_call_at: string | null;
  call_count: number;
}

const DB_PATH = process.env.CAREER_HOTLINE_DB_PATH
  || "/home/workspace/Datasets/career-coaching-calls/data.duckdb";

export function normalizePhone(raw: string): string | null {
  if (!raw || raw.trim().length === 0) return null;

  let cleaned = raw.trim();

  if (isValidPhoneNumber(cleaned, "US")) {
    const parsed = parsePhoneNumber(cleaned, "US");
    return parsed.format("E.164");
  }

  if (isValidPhoneNumber(cleaned)) {
    const parsed = parsePhoneNumber(cleaned);
    return parsed.format("E.164");
  }

  cleaned = cleaned.replace(/[\s\-\(\)\.]/g, "");
  if (/^\d{10}$/.test(cleaned)) {
    return `+1${cleaned}`;
  }
  if (/^\+?\d{11,15}$/.test(cleaned)) {
    if (!cleaned.startsWith("+")) cleaned = `+${cleaned}`;
    return cleaned;
  }

  return null;
}

export async function lookupCaller(phoneNumber: string): Promise<CallerProfile | null> {
  const normalized = normalizePhone(phoneNumber);
  if (!normalized) {
    console.error(`[caller-lookup] Invalid phone number: ${phoneNumber}`);
    return null;
  }

  const query = `
    SELECT id, name, phone, email, linkedin_url, career_stage,
           help_topic, resume_text, caller_brief, source,
           created_at::VARCHAR as created_at,
           last_call_at::VARCHAR as last_call_at,
           call_count
    FROM caller_profiles
    WHERE phone = '${normalized.replace(/'/g, "''")}'
    ORDER BY created_at DESC
    LIMIT 1;
  `;

  try {
    const proc = Bun.spawn(
      ["duckdb", DB_PATH, "-json", "-c", query],
      { stdout: "pipe", stderr: "pipe" }
    );
    const stdout = await new Response(proc.stdout).text();
    const stderr = await new Response(proc.stderr).text();
    await proc.exited;

    if (stderr && stderr.includes("Error")) {
      console.error(`[caller-lookup] DuckDB error: ${stderr}`);
      return null;
    }

    const rows = JSON.parse(stdout.trim() || "[]");
    if (rows.length === 0) return null;

    return rows[0] as CallerProfile;
  } catch (error) {
    console.error(`[caller-lookup] Failed to query DuckDB:`, error);
    return null;
  }
}

export async function updateCallerLastCall(phone: string): Promise<void> {
  const normalized = normalizePhone(phone);
  if (!normalized) return;

  const sql = `
    UPDATE caller_profiles
    SET last_call_at = CURRENT_TIMESTAMP,
        call_count = call_count + 1
    WHERE phone = '${normalized.replace(/'/g, "''")}';
  `;

  try {
    const proc = Bun.spawn(
      ["duckdb", DB_PATH, "-c", sql],
      { stdout: "pipe", stderr: "pipe" }
    );
    await proc.exited;
  } catch (error) {
    console.error(`[caller-lookup] Failed to update last_call_at:`, error);
  }
}

export function generateUUID(): string {
  return crypto.randomUUID();
}
