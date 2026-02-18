#!/usr/bin/env bun

import { parsePhoneNumber } from "libphonenumber-js";
import { existsSync, mkdirSync } from "fs";
import { createHash } from "crypto";

const PORT = parseInt(process.env.CAREER_INTAKE_PORT || "8849");
const DB_PATH = "/home/workspace/Datasets/career-hotline-calls/data.duckdb";
const RESUME_INBOX = "/home/workspace/Careerspan/resumes/inbox";

// Fillout field IDs for the Career Coaching Hotline intake form (v39TcXUcw1us)
const FIELD_IDS = {
  name: "hQTk",
  email: "mKm1",
  phone: "44Lc",
  linkedin: "oQSj",
  resume: "tMXW",
  // Assistance matrix
  application_strategy: "mFnk",
  written_presentation: "2ehG",
  fit_articulation: "fx71",
  networking: "7xmK",
  interview_prep: "qoYZ",
  motivation: "47cZ",
  negotiation: "xmHh",
  career_growth: "axkf",
  // Consent
  consent_ai: "qiJ4",
  consent_transcription: "jsf5",
};

function normalizePhone(raw: string): string {
  if (!raw) return "";
  try {
    const parsed = parsePhoneNumber(raw, "US");
    return parsed ? parsed.format("E.164") : raw.replace(/\D/g, "");
  } catch {
    return raw.replace(/\D/g, "");
  }
}

function extractField(questions: any[], fieldId: string): any {
  const q = questions.find((q: any) => q.id === fieldId);
  return q?.value ?? null;
}

function extractFieldByName(questions: any[], nameIncludes: string[]): any {
  const q = questions.find((q: any) => {
    const n = String(q?.name || "").toLowerCase();
    return nameIncludes.some((needle) => n.includes(needle.toLowerCase()));
  });
  return q?.value ?? null;
}

function normalizePhoneValue(raw: any): string {
  if (raw == null) return "";
  if (typeof raw === "string" || typeof raw === "number") return normalizePhone(String(raw));
  if (typeof raw === "object") {
    const candidates = [
      raw.phone,
      raw.number,
      raw.e164,
      raw.value,
      raw.fullNumber,
      raw.nationalNumber
    ];
    for (const c of candidates) {
      if (c) return normalizePhone(String(c));
    }
  }
  return "";
}

function safeStringValue(raw: any): string {
  if (raw == null) return "";
  if (typeof raw === "string") return raw.trim();
  if (typeof raw === "number" || typeof raw === "boolean") return String(raw);
  if (typeof raw === "object") {
    if (typeof raw.value === "string") return raw.value.trim();
    return JSON.stringify(raw).slice(0, 500);
  }
  return String(raw).slice(0, 500);
}

function parseJsonFromText(raw: string): any | null {
  const text = (raw || "").trim();
  if (!text) return null;

  try {
    return JSON.parse(text);
  } catch {
    // continue to extraction
  }

  const lines = text.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const candidate = lines.slice(i).join("\n").trim();
    if (!candidate.startsWith("{") || !candidate.endsWith("}")) continue;
    try {
      return JSON.parse(candidate);
    } catch {
      // keep trying
    }
  }

  const firstBrace = text.indexOf("{");
  const lastBrace = text.lastIndexOf("}");
  if (firstBrace >= 0 && lastBrace > firstBrace) {
    const candidate = text.slice(firstBrace, lastBrace + 1);
    try {
      return JSON.parse(candidate);
    } catch {
      return null;
    }
  }
  return null;
}

function buildIntakeEventKey(rawBody: string, payload: any): { key: string; submissionId: string | null; formId: string } {
  const formId = String(payload?.formId || "unknown_form");
  const submissionIdRaw = payload?.submission?.submissionId || payload?.submissionId || "";
  const submissionId = String(submissionIdRaw || "").trim();

  if (submissionId) {
    return { key: `fillout:${formId}:${submissionId}`, submissionId, formId };
  }

  // Fallback for payloads missing submissionId: hash full body for retry-safe idempotency.
  const bodyHash = createHash("sha256").update(rawBody).digest("hex");
  return { key: `fillout:${formId}:raw:${bodyHash}`, submissionId: null, formId };
}

function classifyAssistanceLevel(questions: any[]): {
  primary_challenge: string;
  specific_questions: string;
} {
  const areas = [
    { id: FIELD_IDS.application_strategy, label: "Application strategy & reflection" },
    { id: FIELD_IDS.written_presentation, label: "Written presentation (resume, cover letter, LinkedIn)" },
    { id: FIELD_IDS.fit_articulation, label: "Fit articulation" },
    { id: FIELD_IDS.networking, label: "Networking" },
    { id: FIELD_IDS.interview_prep, label: "Interview preparation & performance" },
    { id: FIELD_IDS.motivation, label: "Motivation & confidence" },
    { id: FIELD_IDS.negotiation, label: "Negotiation & offer evaluation" },
    { id: FIELD_IDS.career_growth, label: "Proactive career growth" },
  ];

  const much: string[] = [];
  const some: string[] = [];

  for (const area of areas) {
    const val = extractField(questions, area.id);
    if (!val) continue;
    const sval = safeStringValue(val);
    if (sval.includes("Much")) much.push(area.label);
    else if (sval.includes("Some")) some.push(area.label);
  }

  const primary = much.length > 0
    ? much.join("; ")
    : some.length > 0
      ? some.join("; ")
      : "General career guidance";

  const details = [
    much.length > 0 ? `Much assistance: ${much.join(", ")}` : null,
    some.length > 0 ? `Some assistance: ${some.join(", ")}` : null,
  ].filter(Boolean).join(". ");

  return { primary_challenge: primary, specific_questions: details };
}

async function downloadResume(fileData: any[], callerName: string, phone: string): Promise<string | null> {
  if (!fileData || fileData.length === 0) return null;

  const file = fileData[0];
  const url = file.url;
  const originalFilename = file.filename || `${callerName}_resume.pdf`;

  // Sanitize filename
  const safeName = originalFilename.replace(/[^a-zA-Z0-9._\- ]/g, "_");
  const ext = (safeName.split(".").pop() || "pdf").toLowerCase();
  const base = safeName.replace(/\.[^.]+$/, "");
  const safePhone = phone.replace(/\D/g, "") || "unknown";
  const stamp = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14);
  const dedupe = createHash("sha1").update(`${safeName}:${file.url || ""}`).digest("hex").slice(0, 8);
  const finalName = `${safePhone}_${stamp}_${base.slice(0, 40)}_${dedupe}.${ext}`;
  const destPath = `${RESUME_INBOX}/${finalName}`;

  try {
    mkdirSync(RESUME_INBOX, { recursive: true });
    const resp = await fetch(url);
    if (!resp.ok) {
      console.error(`Failed to download resume: ${resp.status}`);
      return null;
    }
    const buffer = await resp.arrayBuffer();
    await Bun.write(destPath, buffer);
    console.log(`Resume downloaded: ${destPath}`);
    return destPath;
  } catch (err) {
    console.error("Resume download error:", err);
    return null;
  }
}

async function upsertCallerProfileFromResume(data: {
  phone: string;
  resumePath: string;
  stage?: string | null;
  bulletQuality?: string | null;
  processed: boolean;
}): Promise<void> {
  const script = `
import duckdb, json, sys
d = json.loads(sys.stdin.read())
con = duckdb.connect(d['db'])
try:
    con.execute('''CREATE TABLE IF NOT EXISTS caller_profiles (
        phone_number VARCHAR PRIMARY KEY,
        caller_name VARCHAR,
        email VARCHAR,
        linkedin_url VARCHAR,
        primary_challenge TEXT,
        specific_questions TEXT,
        intake_count INTEGER DEFAULT 0,
        resume_count INTEGER DEFAULT 0,
        last_form_id VARCHAR,
        last_submission_id VARCHAR,
        intake_last_submitted_at TIMESTAMP,
        last_resume_path VARCHAR,
        last_resume_processed_at TIMESTAMP,
        last_resume_stage VARCHAR,
        last_resume_bullet_quality VARCHAR,
        profile_summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    row = con.execute("SELECT phone_number FROM caller_profiles WHERE phone_number = ?", [d['phone']]).fetchone()
    if row:
        con.execute('''
            UPDATE caller_profiles
            SET
                resume_count = COALESCE(resume_count, 0) + 1,
                last_resume_path = ?,
                last_resume_processed_at = CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE last_resume_processed_at END,
                last_resume_stage = COALESCE(?, last_resume_stage),
                last_resume_bullet_quality = COALESCE(?, last_resume_bullet_quality),
                profile_summary = TRIM(
                    COALESCE(primary_challenge, '') ||
                    CASE WHEN COALESCE(last_resume_stage, '') != '' OR COALESCE(?, '') != ''
                        THEN ' | Resume: ' || COALESCE(?, last_resume_stage, 'unknown stage')
                        ELSE '' END
                ),
                updated_at = CURRENT_TIMESTAMP
            WHERE phone_number = ?
        ''', [d['resume_path'], d['processed'], d.get('stage'), d.get('bullet_quality'), d.get('stage'), d.get('stage'), d['phone']])
    else:
        con.execute('''
            INSERT INTO caller_profiles (
                phone_number, resume_count, last_resume_path, last_resume_processed_at,
                last_resume_stage, last_resume_bullet_quality, profile_summary
            )
            VALUES (?, 1, ?, CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE NULL END, ?, ?, ?)
        ''', [
            d['phone'],
            d['resume_path'],
            d['processed'],
            d.get('stage'),
            d.get('bullet_quality'),
            f"Resume: {d.get('stage') or 'unknown stage'}"
        ])
    print("OK")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
finally:
    con.close()
`;

  const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe", stderr: "pipe" });
  proc.stdin.write(JSON.stringify({
    db: DB_PATH,
    phone: data.phone,
    resume_path: data.resumePath,
    stage: data.stage || null,
    bullet_quality: data.bulletQuality || null,
    processed: data.processed
  }));
  proc.stdin.end();
  const stderr = await new Response(proc.stderr).text();
  await proc.exited;
  if (stderr.trim()) console.error("Profile resume upsert stderr:", stderr.trim());
}

function triggerResumeProcessing(resumePath: string, phone: string, name: string): void {
  const script = "/home/workspace/Skills/career-coaching-hotline/scripts/resume_ingest.py";
  console.log(`[INTAKE] Triggering resume processing for ${name} (${phone})`);

  const proc = Bun.spawn(
    ["python3", script, "--file", resumePath, "--phone", phone, "--verbose", "--json"],
    { stdout: "pipe", stderr: "pipe" }
  );

  // Handle completion asynchronously
  (async () => {
    try {
      const stdout = await new Response(proc.stdout).text();
      const stderr = await new Response(proc.stderr).text();
      const exitCode = await proc.exited;

      if (exitCode === 0) {
        try {
          const result = parseJsonFromText(stdout);
          if (!result) throw new Error("No JSON object found in stdout");
          const quality = result?.decomposition?.aiss_quick_scan?.overall_bullet_quality || "unknown";
          const stage = result?.decomposition?.estimated_career_stage || "unknown";
          console.log(`[INTAKE] Resume processed for ${name}: quality=${quality}, stage=${stage}`);
          await upsertCallerProfileFromResume({
            phone,
            resumePath,
            stage,
            bulletQuality: quality,
            processed: true,
          });
        } catch {
          console.log(`[INTAKE] Resume processed for ${name} (output parse fallback)`);
          await upsertCallerProfileFromResume({
            phone,
            resumePath,
            processed: false,
          });
        }
      } else {
        console.error(`[INTAKE] Resume processing failed for ${name} (exit ${exitCode}): ${stderr.slice(0, 300)}`);
        await upsertCallerProfileFromResume({
          phone,
          resumePath,
          processed: false,
        });
      }
    } catch (err) {
      console.error(`[INTAKE] Resume processing error for ${name}:`, err);
    }
  })();
}

async function insertCallerLookup(data: {
  eventKey: string;
  formId: string;
  submissionId: string | null;
  phone: string;
  name: string;
  email: string;
  linkedin: string | null;
  primary_challenge: string;
  specific_questions: string;
  submittedAt: string;
}): Promise<boolean> {
  const id = crypto.randomUUID();
  const script = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    con.execute('''CREATE TABLE IF NOT EXISTS caller_lookup (
        id VARCHAR PRIMARY KEY,
        source_event_key VARCHAR,
        source_form_id VARCHAR,
        source_submission_id VARCHAR,
        phone_number VARCHAR,
        caller_name VARCHAR,
        career_stage VARCHAR,
        primary_challenge TEXT,
        specific_questions TEXT,
        industry_targets TEXT,
        submitted_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    con.execute("ALTER TABLE caller_lookup ADD COLUMN IF NOT EXISTS source_event_key VARCHAR")
    con.execute("ALTER TABLE caller_lookup ADD COLUMN IF NOT EXISTS source_form_id VARCHAR")
    con.execute("ALTER TABLE caller_lookup ADD COLUMN IF NOT EXISTS source_submission_id VARCHAR")
    con.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_caller_lookup_source_event_key ON caller_lookup(source_event_key)")
    existing = con.execute("SELECT id FROM caller_lookup WHERE source_event_key = ?", [data['event_key']]).fetchone()
    if existing:
        print("OK")
        con.close()
        raise SystemExit(0)
    con.execute('''
        INSERT INTO caller_lookup (id, source_event_key, source_form_id, source_submission_id, phone_number, caller_name, career_stage, primary_challenge, specific_questions, industry_targets, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [data['id'], data['event_key'], data['form_id'], data['submission_id'], data['phone'], data['name'], 'intake', data['primary_challenge'], data['specific_questions'], data['linkedin'], data['submitted_at']])
    print("OK")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    print("FAIL")
con.close()
`;

  const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe", stderr: "pipe" });
  proc.stdin.write(JSON.stringify({
    db: DB_PATH,
    id,
    event_key: data.eventKey,
    form_id: data.formId,
    submission_id: data.submissionId || "",
    phone: data.phone,
    name: data.name,
    primary_challenge: data.primary_challenge,
    specific_questions: data.specific_questions,
    linkedin: data.linkedin || "",
    submitted_at: data.submittedAt,
  }));
  proc.stdin.end();
  const output = await new Response(proc.stdout).text();
  const stderr = await new Response(proc.stderr).text();
  await proc.exited;

  if (stderr) console.error("DB stderr:", stderr);
  return output.trim() === "OK";
}

async function registerIntakeWebhookEvent(data: {
  eventKey: string;
  formId: string;
  submissionId: string | null;
  phone: string;
  name: string;
  submittedAt: string;
}): Promise<{ duplicate: boolean; eventId: string }> {
  const eventId = crypto.randomUUID();
  const script = `
import duckdb, json, sys
d = json.loads(sys.stdin.read())
con = duckdb.connect(d['db'])
try:
    con.execute('''CREATE TABLE IF NOT EXISTS intake_webhook_events (
        id VARCHAR PRIMARY KEY,
        event_key VARCHAR UNIQUE,
        form_id VARCHAR,
        submission_id VARCHAR,
        phone_number VARCHAR,
        caller_name VARCHAR,
        submitted_at TIMESTAMP,
        first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        duplicate_count INTEGER DEFAULT 0
    )''')
    existing = con.execute("SELECT id, duplicate_count FROM intake_webhook_events WHERE event_key = ?", [d['event_key']]).fetchone()
    if existing:
        con.execute('''
            UPDATE intake_webhook_events
            SET duplicate_count = COALESCE(duplicate_count, 0) + 1,
                last_seen_at = CURRENT_TIMESTAMP
            WHERE event_key = ?
        ''', [d['event_key']])
        print(json.dumps({"duplicate": True, "event_id": existing[0]}))
    else:
        con.execute('''
            INSERT INTO intake_webhook_events (
                id, event_key, form_id, submission_id, phone_number, caller_name, submitted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [d['id'], d['event_key'], d['form_id'], d['submission_id'], d['phone'], d['name'], d['submitted_at']])
        print(json.dumps({"duplicate": False, "event_id": d['id']}))
except Exception as e:
    print(json.dumps({"duplicate": False, "event_id": d['id'], "error": str(e)}))
finally:
    con.close()
`;
  const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe", stderr: "pipe" });
  proc.stdin.write(JSON.stringify({
    db: DB_PATH,
    id: eventId,
    event_key: data.eventKey,
    form_id: data.formId,
    submission_id: data.submissionId,
    phone: data.phone,
    name: data.name,
    submitted_at: data.submittedAt,
  }));
  proc.stdin.end();
  const output = await new Response(proc.stdout).text();
  const stderr = await new Response(proc.stderr).text();
  await proc.exited;
  if (stderr.trim()) console.error("Idempotency stderr:", stderr.trim());
  try {
    const parsed = JSON.parse(output.trim());
    return { duplicate: !!parsed.duplicate, eventId: parsed.event_id || eventId };
  } catch {
    return { duplicate: false, eventId };
  }
}

async function upsertCallerProfileFromIntake(data: {
  phone: string;
  name: string;
  email: string;
  linkedin: string | null;
  primaryChallenge: string;
  specificQuestions: string;
  submittedAt: string;
  formId: string;
  submissionId: string | null;
}): Promise<void> {
  const script = `
import duckdb, json, sys
d = json.loads(sys.stdin.read())
con = duckdb.connect(d['db'])
try:
    con.execute('''CREATE TABLE IF NOT EXISTS caller_profiles (
        phone_number VARCHAR PRIMARY KEY,
        caller_name VARCHAR,
        email VARCHAR,
        linkedin_url VARCHAR,
        primary_challenge TEXT,
        specific_questions TEXT,
        intake_count INTEGER DEFAULT 0,
        resume_count INTEGER DEFAULT 0,
        last_form_id VARCHAR,
        last_submission_id VARCHAR,
        intake_last_submitted_at TIMESTAMP,
        last_resume_path VARCHAR,
        last_resume_processed_at TIMESTAMP,
        last_resume_stage VARCHAR,
        last_resume_bullet_quality VARCHAR,
        profile_summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    row = con.execute("SELECT phone_number, resume_count, last_resume_stage FROM caller_profiles WHERE phone_number = ?", [d['phone']]).fetchone()
    summary = f"Needs: {d['primary_challenge']}"
    if row and row[2]:
        summary += f" | Resume: {row[2]}"
    if row:
        con.execute('''
            UPDATE caller_profiles
            SET
                caller_name = COALESCE(NULLIF(?, ''), caller_name),
                email = COALESCE(NULLIF(?, ''), email),
                linkedin_url = COALESCE(NULLIF(?, ''), linkedin_url),
                primary_challenge = COALESCE(NULLIF(?, ''), primary_challenge),
                specific_questions = COALESCE(NULLIF(?, ''), specific_questions),
                intake_count = COALESCE(intake_count, 0) + 1,
                last_form_id = COALESCE(NULLIF(?, ''), last_form_id),
                last_submission_id = COALESCE(NULLIF(?, ''), last_submission_id),
                intake_last_submitted_at = ?,
                profile_summary = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE phone_number = ?
        ''', [d['name'], d['email'], d['linkedin'], d['primary_challenge'], d['specific_questions'], d['form_id'], d['submission_id'], d['submitted_at'], summary, d['phone']])
    else:
        con.execute('''
            INSERT INTO caller_profiles (
                phone_number, caller_name, email, linkedin_url, primary_challenge, specific_questions,
                intake_count, resume_count, last_form_id, last_submission_id, intake_last_submitted_at, profile_summary
            ) VALUES (?, ?, ?, ?, ?, ?, 1, 0, ?, ?, ?, ?)
        ''', [d['phone'], d['name'], d['email'], d['linkedin'], d['primary_challenge'], d['specific_questions'], d['form_id'], d['submission_id'], d['submitted_at'], summary])
    print("OK")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
finally:
    con.close()
`;
  const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe", stderr: "pipe" });
  proc.stdin.write(JSON.stringify({
    db: DB_PATH,
    phone: data.phone,
    name: data.name,
    email: data.email,
    linkedin: data.linkedin || "",
    primary_challenge: data.primaryChallenge,
    specific_questions: data.specificQuestions,
    submitted_at: data.submittedAt,
    form_id: data.formId,
    submission_id: data.submissionId || "",
  }));
  proc.stdin.end();
  const stderr = await new Response(proc.stderr).text();
  await proc.exited;
  if (stderr.trim()) console.error("Profile intake upsert stderr:", stderr.trim());
}

function notifyV(message: string): void {
  const token = process.env.ZO_CLIENT_IDENTITY_TOKEN;
  if (!token) {
    console.error("ZO_CLIENT_IDENTITY_TOKEN not set");
    return;
  }
  const authHeader = token.startsWith("Bearer") ? token : `Bearer ${token}`;
  fetch("https://api.zo.computer/zo/ask", {
    method: "POST",
    headers: { authorization: authHeader, "content-type": "application/json" },
    body: JSON.stringify({
      input: `SYSTEM NOTIFICATION RELAY\n\nSend V this SMS (using send_sms_to_user):\n\n${message.substring(0, 500)}\n\nJust send the SMS. No commentary.`
    })
  }).catch(err => console.error("Failed to notify V:", err));
}

// Server
Bun.serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);

    if (req.method === "GET" && url.pathname === "/health") {
      return new Response(JSON.stringify({
        status: "ok",
        service: "career-intake-webhook",
        port: PORT,
      }), { headers: { "Content-Type": "application/json" } });
    }

    if (req.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    try {
      const rawBody = await req.text();
      const payload = JSON.parse(rawBody);

      console.log(`[INTAKE] Received webhook: ${JSON.stringify({ keys: Object.keys(payload), formId: payload.formId })}`);

      // Fillout schemas observed:
      // 1) Legacy/direct: { questions: [...] }
      // 2) Nested submission: { submission: { questions: [...] } }
      // 3) Legacy batch: { responses: [{ questions: [...] }] }
      const questions =
        payload.questions ||
        payload.submission?.questions ||
        payload.responses?.[0]?.questions ||
        [];

      if (questions.length === 0) {
        console.warn("[INTAKE] No questions found in payload");
        return new Response(JSON.stringify({ status: "ok", warning: "no questions found" }), {
          status: 200, headers: { "Content-Type": "application/json" }
        });
      }

      // Extract fields
      const name = safeStringValue(extractField(questions, FIELD_IDS.name) ?? extractFieldByName(questions, ["name"])) || "Unknown";
      const email = safeStringValue(extractField(questions, FIELD_IDS.email) ?? extractFieldByName(questions, ["email"]));
      const rawPhone = extractField(questions, FIELD_IDS.phone) ?? extractFieldByName(questions, ["phone", "mobile", "account #", "account number"]);
      const phone = normalizePhoneValue(rawPhone);
      const linkedin = safeStringValue(extractField(questions, FIELD_IDS.linkedin) ?? extractFieldByName(questions, ["linkedin"]));
      const resumeFiles = extractField(questions, FIELD_IDS.resume);
      const submittedAt =
        payload.submissionTime ||
        payload.submission?.submissionTime ||
        new Date().toISOString();
      const intakeEvent = buildIntakeEventKey(rawBody, payload);

      console.log(`[INTAKE] Processing: ${name} | ${email} | ${phone}`);
      if (!phone) {
        console.warn(`[INTAKE] Missing/invalid phone for ${name}. Skipping persistence.`);
        return new Response(JSON.stringify({
          status: "ok",
          warning: "missing phone",
        }), { status: 200, headers: { "Content-Type": "application/json" } });
      }

      // Classify assistance needs
      const { primary_challenge, specific_questions } = classifyAssistanceLevel(questions);

      const eventRegistration = await registerIntakeWebhookEvent({
        eventKey: intakeEvent.key,
        formId: intakeEvent.formId,
        submissionId: intakeEvent.submissionId,
        phone,
        name,
        submittedAt,
      });
      if (eventRegistration.duplicate) {
        console.log(`[INTAKE] Duplicate webhook ignored for ${name} (${phone}) event=${eventRegistration.eventId}`);
        return new Response(JSON.stringify({
          status: "ok",
          duplicate: true,
          event_id: eventRegistration.eventId
        }), { status: 200, headers: { "Content-Type": "application/json" } });
      }

      // Insert into caller_lookup
      const inserted = await insertCallerLookup({
        eventKey: intakeEvent.key,
        formId: intakeEvent.formId,
        submissionId: intakeEvent.submissionId,
        phone, name, email, linkedin,
        primary_challenge, specific_questions,
        submittedAt,
      });

      if (inserted) {
        console.log(`[INTAKE] caller_lookup record created for ${name} (${phone})`);
        await upsertCallerProfileFromIntake({
          phone,
          name,
          email,
          linkedin,
          primaryChallenge: primary_challenge,
          specificQuestions: specific_questions,
          submittedAt,
          formId: intakeEvent.formId,
          submissionId: intakeEvent.submissionId,
        });
      } else {
        console.error(`[INTAKE] Failed to insert caller_lookup for ${name}`);
      }

      // Download resume
      let resumePath: string | null = null;
      if (resumeFiles) {
        resumePath = await downloadResume(resumeFiles, name, phone);
      }

      // Trigger resume pre-processing in background (non-blocking)
      if (resumePath) {
        triggerResumeProcessing(resumePath, phone, name);
      }

      // Notify V
      const assistanceSummary = [
        primary_challenge ? `Needs: ${primary_challenge}` : null,
      ].filter(Boolean).join("\n");

      notifyV(
        `📋 New Career Hotline intake!\n` +
        `• ${name} (${email})\n` +
        `• Phone: ${rawPhone}\n` +
        `${assistanceSummary}\n` +
        `${resumePath ? `• Resume saved — processing for coaching insights` : "• No resume uploaded"}\n` +
        `Ready to call the hotline.`
      );

      return new Response(JSON.stringify({
        status: "ok",
        name,
        phone,
        caller_lookup_inserted: inserted,
        resume_downloaded: !!resumePath,
        resume_processing: !!resumePath,
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      });

    } catch (error: any) {
      console.error("[INTAKE] Error:", error);
      return new Response(JSON.stringify({ error: "Internal server error", message: error.message }), {
        status: 500, headers: { "Content-Type": "application/json" }
      });
    }
  }
});

console.log(`Career Intake Webhook running on port ${PORT}`);
console.log(`Database: ${DB_PATH}`);
console.log(`Resume inbox: ${RESUME_INBOX}`);
