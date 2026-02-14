#!/usr/bin/env bun

import { normalizePhone, generateUUID } from "./caller-lookup";

const DB_PATH = process.env.CAREER_HOTLINE_DB_PATH
  || "/home/workspace/Datasets/career-coaching-calls/data.duckdb";

const INTAKE_PORT = parseInt(process.env.CAREER_INTAKE_PORT || "8421");

const CAREER_STAGE_MAP: Record<string, string> = {
  "i'm just getting started": "groundwork",
  "just getting started": "groundwork",
  "figuring out what i want": "groundwork",
  "groundwork": "groundwork",
  "i'm working on my resume": "materials",
  "working on my resume": "materials",
  "application materials": "materials",
  "materials": "materials",
  "i'm actively applying": "outreach",
  "actively applying": "outreach",
  "searching": "outreach",
  "outreach": "outreach",
  "i'm getting interviews": "performance",
  "getting interviews": "performance",
  "not landing offers": "performance",
  "performance": "performance",
  "i'm changing careers": "transition",
  "changing careers": "transition",
  "recovering from a layoff": "transition",
  "transition": "transition",
};

function resolveCareerStage(raw: string | null): string | null {
  if (!raw) return null;
  const lower = raw.toLowerCase().trim();

  if (CAREER_STAGE_MAP[lower]) return CAREER_STAGE_MAP[lower];

  for (const [key, value] of Object.entries(CAREER_STAGE_MAP)) {
    if (lower.includes(key)) return value;
  }

  const stages = ["groundwork", "materials", "outreach", "performance", "transition"];
  for (const stage of stages) {
    if (lower.includes(stage)) return stage;
  }

  return raw;
}

interface FilloutQuestion {
  id: string;
  name: string;
  type: string;
  value: unknown;
}

interface FilloutPayload {
  submissionId: string;
  formId: string;
  formName: string;
  submittedAt: string;
  questions: FilloutQuestion[];
}

function extractField(questions: FilloutQuestion[], ...namePatterns: string[]): string | null {
  for (const pattern of namePatterns) {
    const lower = pattern.toLowerCase();
    const found = questions.find(q =>
      q.name.toLowerCase().includes(lower)
    );
    if (found && found.value != null) {
      if (typeof found.value === "string") return found.value;
      if (Array.isArray(found.value)) return JSON.stringify(found.value);
      return String(found.value);
    }
  }
  return null;
}

function extractFileUrl(questions: FilloutQuestion[]): string | null {
  const found = questions.find(q =>
    q.type === "FileUpload" || q.name.toLowerCase().includes("resume")
  );
  if (!found || !found.value) return null;

  if (Array.isArray(found.value) && found.value.length > 0) {
    const first = found.value[0] as { url?: string; name?: string };
    return first.url || null;
  }
  if (typeof found.value === "string") return found.value;
  return null;
}

async function downloadAndExtractResume(fileUrl: string): Promise<string | null> {
  try {
    const resp = await fetch(fileUrl);
    if (!resp.ok) {
      console.error(`[intake] Failed to download resume: ${resp.status}`);
      return null;
    }

    const buffer = await resp.arrayBuffer();
    const tmpPath = `/tmp/intake-resume-${Date.now()}`;
    const contentType = resp.headers.get("content-type") || "";
    const ext = contentType.includes("pdf") ? ".pdf"
      : contentType.includes("word") || contentType.includes("docx") ? ".docx"
      : fileUrl.toLowerCase().endsWith(".pdf") ? ".pdf"
      : fileUrl.toLowerCase().endsWith(".docx") ? ".docx"
      : ".pdf";
    const filePath = tmpPath + ext;
    await Bun.write(filePath, buffer);

    if (ext === ".pdf") {
      const proc = Bun.spawn(
        ["python3", "-c", `
import sys
try:
    import fitz
    doc = fitz.open("${filePath}")
    text = ""
    for page in doc:
        text += page.get_text()
    print(text[:8000])
except ImportError:
    import subprocess
    result = subprocess.run(["pdftotext", "${filePath}", "-"], capture_output=True, text=True)
    print(result.stdout[:8000])
`],
        { stdout: "pipe", stderr: "pipe" }
      );
      const text = await new Response(proc.stdout).text();
      await proc.exited;
      return text.trim() || null;
    }

    if (ext === ".docx") {
      const proc = Bun.spawn(
        ["python3", "-c", `
import subprocess, sys
result = subprocess.run(["pandoc", "${filePath}", "-t", "plain"], capture_output=True, text=True)
print(result.stdout[:8000])
`],
        { stdout: "pipe", stderr: "pipe" }
      );
      const text = await new Response(proc.stdout).text();
      await proc.exited;
      return text.trim() || null;
    }

    return null;
  } catch (error) {
    console.error(`[intake] Resume extraction failed:`, error);
    return null;
  }
}

async function generateCallerBrief(
  name: string,
  careerStage: string | null,
  helpTopic: string | null,
  resumeText: string | null
): Promise<string> {
  const token = process.env.ZO_CLIENT_IDENTITY_TOKEN;
  if (!token) {
    console.warn("[intake] ZO_CLIENT_IDENTITY_TOKEN not set, using fallback brief");
    return `${name} is at the ${careerStage || "unknown"} stage. They want help with: ${helpTopic || "not specified"}.`;
  }

  const authHeader = token.startsWith("Bearer") ? token : `Bearer ${token}`;

  const resumeSnippet = resumeText
    ? `\n\nResume excerpt (first 2000 chars):\n${resumeText.substring(0, 2000)}`
    : "";

  const prompt = `You are generating a concise caller brief for a career coaching hotline. The brief will be injected into the AI coach's system prompt when this person calls, so the coach can greet them by name and reference their background.

Caller info:
- Name: ${name}
- Self-assessed career stage: ${careerStage || "not provided"}
- What they want help with: ${helpTopic || "not specified"}${resumeSnippet}

Write a 2-3 sentence caller brief. Include:
1. Their name and where they seem to be in their career journey
2. Key career signals from their resume (if provided) — roles, industries, years of experience
3. What they specifically want help with

Keep it conversational and practical — this is a quick reference for the AI coach, not a formal report. Do NOT include any preamble or labels.`;

  try {
    const resp = await fetch("https://api.zo.computer/zo/ask", {
      method: "POST",
      headers: {
        "authorization": authHeader,
        "content-type": "application/json",
      },
      body: JSON.stringify({ input: prompt }),
    });

    if (!resp.ok) {
      console.error(`[intake] /zo/ask failed: ${resp.status}`);
      return `${name} is at the ${careerStage || "unknown"} stage. They want help with: ${helpTopic || "not specified"}.`;
    }

    const body = await resp.json();
    return body.output || body.response || `${name} — ${careerStage || "unknown"} stage.`;
  } catch (error) {
    console.error(`[intake] Brief generation failed:`, error);
    return `${name} is at the ${careerStage || "unknown"} stage. They want help with: ${helpTopic || "not specified"}.`;
  }
}

async function storeCallerProfile(profile: {
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
}): Promise<boolean> {
  const esc = (v: string | null) => {
    if (v === null) return "NULL";
    return `'${v.replace(/'/g, "''")}'`;
  };

  const checkSql = `SELECT id FROM caller_profiles WHERE phone = ${esc(profile.phone)} LIMIT 1;`;
  const updateSql = `
    UPDATE caller_profiles SET
      name = ${esc(profile.name)},
      email = COALESCE(${esc(profile.email)}, email),
      linkedin_url = COALESCE(${esc(profile.linkedin_url)}, linkedin_url),
      career_stage = ${esc(profile.career_stage)},
      help_topic = ${esc(profile.help_topic)},
      resume_text = COALESCE(${esc(profile.resume_text)}, resume_text),
      caller_brief = ${esc(profile.caller_brief)},
      source = COALESCE(${esc(profile.source)}, source)
    WHERE phone = ${esc(profile.phone)};
  `;
  const insertSql = `
    INSERT INTO caller_profiles (id, name, phone, email, linkedin_url, career_stage, help_topic, resume_text, caller_brief, source)
    VALUES (
      ${esc(profile.id)},
      ${esc(profile.name)},
      ${esc(profile.phone)},
      ${esc(profile.email)},
      ${esc(profile.linkedin_url)},
      ${esc(profile.career_stage)},
      ${esc(profile.help_topic)},
      ${esc(profile.resume_text)},
      ${esc(profile.caller_brief)},
      ${esc(profile.source)}
    );
  `;

  try {
    const checkProc = Bun.spawn(
      ["duckdb", DB_PATH, "-json", "-c", checkSql],
      { stdout: "pipe", stderr: "pipe" }
    );
    const checkOut = await new Response(checkProc.stdout).text();
    await checkProc.exited;

    const existing = JSON.parse(checkOut.trim() || "[]");
    const sql = existing.length > 0 ? updateSql : insertSql;

    const proc = Bun.spawn(
      ["duckdb", DB_PATH, "-c", sql],
      { stdout: "pipe", stderr: "pipe" }
    );
    const stderr = await new Response(proc.stderr).text();
    const exitCode = await proc.exited;

    if (exitCode !== 0) {
      console.error(`[intake] DuckDB ${existing.length > 0 ? "update" : "insert"} failed: ${stderr}`);
      return false;
    }
    return true;
  } catch (error) {
    console.error(`[intake] Store failed:`, error);
    return false;
  }
}

async function notifyV(message: string): Promise<void> {
  const token = process.env.ZO_CLIENT_IDENTITY_TOKEN;
  if (!token) {
    console.warn("[intake] No ZO_CLIENT_IDENTITY_TOKEN — skipping SMS notification");
    return;
  }

  const authHeader = token.startsWith("Bearer") ? token : `Bearer ${token}`;

  try {
    await fetch("https://api.zo.computer/zo/ask", {
      method: "POST",
      headers: {
        "authorization": authHeader,
        "content-type": "application/json",
      },
      body: JSON.stringify({
        input: `SYSTEM NOTIFICATION RELAY — Send this SMS to V immediately using send_sms_to_user:\n\n${message}`,
      }),
    });
  } catch (error) {
    console.error(`[intake] SMS notification failed:`, error);
  }
}

async function ensureTable(): Promise<void> {
  const sql = `
    CREATE TABLE IF NOT EXISTS caller_profiles (
      id VARCHAR PRIMARY KEY,
      name VARCHAR NOT NULL,
      phone VARCHAR NOT NULL,
      email VARCHAR,
      linkedin_url VARCHAR,
      career_stage VARCHAR,
      help_topic TEXT,
      resume_text TEXT,
      caller_brief TEXT,
      source VARCHAR,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      last_call_at TIMESTAMP,
      call_count INTEGER DEFAULT 0
    );
    CREATE UNIQUE INDEX IF NOT EXISTS idx_caller_phone ON caller_profiles(phone);
  `;

  try {
    const proc = Bun.spawn(
      ["duckdb", DB_PATH, "-c", sql],
      { stdout: "pipe", stderr: "pipe" }
    );
    const stderr = await new Response(proc.stderr).text();
    await proc.exited;

    if (stderr && stderr.includes("Error") && !stderr.includes("already exists")) {
      console.error(`[intake] Table creation issue: ${stderr}`);
    }
  } catch (error) {
    console.error(`[intake] ensureTable failed:`, error);
  }
}

async function handleIntakeWebhook(req: Request): Promise<Response> {
  const ts = new Date().toISOString();

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  let payload: FilloutPayload;
  try {
    payload = await req.json() as FilloutPayload;
  } catch {
    console.error(`[intake] ${ts} Invalid JSON body`);
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (!payload.questions || !Array.isArray(payload.questions)) {
    console.error(`[intake] ${ts} Missing questions array`);
    return new Response(JSON.stringify({ error: "Missing questions array" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const name = extractField(payload.questions, "full name", "name");
  const rawPhone = extractField(payload.questions, "phone");
  const email = extractField(payload.questions, "email");
  const linkedinUrl = extractField(payload.questions, "linkedin");
  const rawStage = extractField(payload.questions, "career search", "career stage", "where are you");
  const helpTopic = extractField(payload.questions, "help with", "what do you want");
  const source = extractField(payload.questions, "hear about", "how did you");

  if (!name || !rawPhone) {
    console.error(`[intake] ${ts} Missing required fields: name=${!!name}, phone=${!!rawPhone}`);
    return new Response(JSON.stringify({ error: "Name and phone are required" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const phone = normalizePhone(rawPhone);
  if (!phone) {
    console.error(`[intake] ${ts} Invalid phone number: ${rawPhone}`);
    return new Response(JSON.stringify({ error: "Invalid phone number" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const careerStage = resolveCareerStage(rawStage);

  console.log(`[intake] ${ts} Processing submission: ${name} (${phone}) — stage: ${careerStage}`);

  let resumeText: string | null = null;
  const fileUrl = extractFileUrl(payload.questions);
  if (fileUrl) {
    console.log(`[intake] ${ts} Downloading resume from: ${fileUrl.substring(0, 80)}...`);
    resumeText = await downloadAndExtractResume(fileUrl);
    if (resumeText) {
      console.log(`[intake] ${ts} Resume extracted: ${resumeText.length} chars`);
    }
  }

  const callerBrief = await generateCallerBrief(name, careerStage, helpTopic, resumeText);
  console.log(`[intake] ${ts} Generated caller brief: ${callerBrief.substring(0, 100)}...`);

  const profileId = generateUUID();
  const stored = await storeCallerProfile({
    id: profileId,
    name,
    phone,
    email,
    linkedin_url: linkedinUrl,
    career_stage: careerStage,
    help_topic: helpTopic,
    resume_text: resumeText,
    caller_brief: callerBrief,
    source,
  });

  if (!stored) {
    console.error(`[intake] ${ts} Failed to store profile for ${name}`);
    return new Response(JSON.stringify({ error: "Storage failed" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }

  console.log(`[intake] ${ts} Stored profile: ${profileId} for ${name} (${phone})`);

  const stageLabel = careerStage
    ? careerStage.charAt(0).toUpperCase() + careerStage.slice(1)
    : "Unknown stage";
  const topicSnippet = helpTopic
    ? helpTopic.substring(0, 80) + (helpTopic.length > 80 ? "..." : "")
    : "not specified";

  notifyV(`📝 New career hotline intake: ${name} — ${stageLabel} — wants help with: ${topicSnippet}`);

  return new Response(JSON.stringify({
    success: true,
    profile_id: profileId,
    name,
    phone,
    career_stage: careerStage,
  }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

await ensureTable();

const server = Bun.serve({
  port: INTAKE_PORT,
  async fetch(req: Request) {
    const url = new URL(req.url);

    if (url.pathname === "/health") {
      return new Response(JSON.stringify({ status: "ok", service: "career-intake-webhook" }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    if (url.pathname === "/intake") {
      return handleIntakeWebhook(req);
    }

    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: { "Content-Type": "application/json" },
    });
  },
});

console.log(`[intake] Career Coaching Intake Webhook running on port ${INTAKE_PORT}`);
console.log(`[intake] Database: ${DB_PATH}`);
console.log(`[intake] POST /intake — Fillout webhook receiver`);
console.log(`[intake] GET  /health — Health check`);
