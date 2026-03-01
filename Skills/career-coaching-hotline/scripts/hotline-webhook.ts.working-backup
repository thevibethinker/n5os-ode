#!/usr/bin/env bun

import { readFileSync, existsSync, readdirSync, statSync } from "fs";
import { generateUUID } from "./call-logger";
import { parsePhoneNumber } from "libphonenumber-js";

const PORT = parseInt(process.env.CAREER_HOTLINE_PORT || "8848");
const DB_PATH = "/home/workspace/Datasets/career-hotline-calls/data.duckdb";
const KNOWLEDGE_BASE = "/home/workspace/Knowledge/career-coaching-hotline";
const VOICE_ID = process.env.CAREER_HOTLINE_VOICE_ID || "";
const WEBHOOK_SECRET = process.env.CAREER_HOTLINE_SECRET || "";
const VERBOSITY = process.env.CAREER_HOTLINE_VERBOSITY || "normal";
const BOOKING_LINK = process.env.CAREER_HOTLINE_BOOKING_LINK || "https://mycareerspan.com/book";
const PURCHASE_URL = process.env.CAREER_HOTLINE_PURCHASE_URL || "https://mycareerspan.com/coaching-credits";
const RESUME_STORAGE = "/home/workspace/Datasets/career-hotline-calls/resumes";

const FREE_TIER_SECONDS = 900;

// Load system prompt
const systemPromptTemplate = readFileSync(
  "/home/workspace/N5/builds/career-coaching-hotline/artifacts/career-coach-system-prompt.md",
  "utf-8"
).replace(/^---[\s\S]*?---\s*/, "");

const systemPromptBase = systemPromptTemplate;

// Load concept map
const conceptMapRaw: Record<string, string> = JSON.parse(
  readFileSync(
    "/home/workspace/N5/builds/career-coaching-hotline/artifacts/concept-map.json",
    "utf-8"
  )
);

// Load tool specs
const toolSpecsRaw = JSON.parse(
  readFileSync(
    "/home/workspace/N5/builds/career-coaching-hotline/artifacts/tool-specs.json",
    "utf-8"
  )
);

function normalizePhone(raw: string): string {
  if (!raw) return "";
  try {
    const parsed = parsePhoneNumber(raw, "US");
    return parsed ? parsed.format("E.164") : raw.replace(/\D/g, "");
  } catch {
    return raw.replace(/\D/g, "");
  }
}

function getZoAuthHeader(): string | null {
  const token = process.env.ZO_CLIENT_IDENTITY_TOKEN;
  if (!token) return null;
  return token.startsWith("Bearer") ? token : `Bearer ${token}`;
}

async function zoAsk(input: string, _outputFormat?: object): Promise<any> {
  const authHeader = getZoAuthHeader();
  if (!authHeader) throw new Error("ZO_CLIENT_IDENTITY_TOKEN not set");
  // Do NOT send output_format to Zo API — it causes 422 errors with complex schemas.
  // Instead, the prompt already says "Return ONLY valid JSON" and we parse the text response.
  const body: any = { input };

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 55000);

  try {
    const resp = await fetch("https://api.zo.computer/zo/ask", {
      method: "POST",
      headers: { authorization: authHeader, "content-type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (!resp.ok) {
      const errText = await resp.text().catch(() => "");
      console.error(`zoAsk: Zo API returned ${resp.status}: ${errText.slice(0, 200)}`);
      throw new Error(`Zo API returned ${resp.status}`);
    }
    const result = await resp.json().catch(() => null);
    const output = (result as any)?.output;
    if (!output) {
      console.error("zoAsk: Zo API returned empty output");
      return null;
    }

    // If already an object, return directly
    if (typeof output === "object") return output;

    // Parse JSON from text response (handles markdown code blocks)
    let text = String(output).trim();

    // Strip markdown code blocks
    if (text.startsWith("```")) {
      const lines = text.split("\n");
      const endIdx = lines.findLastIndex((l: string) => l.trim() === "```");
      text = lines.slice(1, endIdx > 0 ? endIdx : lines.length).join("\n").trim();
    }

    try {
      return JSON.parse(text);
    } catch {
      // Try extracting JSON object from surrounding text
      const braceStart = text.indexOf("{");
      const braceEnd = text.lastIndexOf("}");
      if (braceStart >= 0 && braceEnd > braceStart) {
        try {
          return JSON.parse(text.substring(braceStart, braceEnd + 1));
        } catch { /* fall through */ }
      }
      console.error(`zoAsk: could not parse JSON (${text.length} chars). First 300: ${text.slice(0, 300)}`);
      return null;
    }
  } catch (err: any) {
    clearTimeout(timeout);
    if (err.name === "AbortError") {
      console.error("zoAsk: request timed out after 55s");
      return null;
    }
    throw err;
  }
}

// ── Recent Call Context ──

async function getRecentCallContext(): Promise<string> {
  try {
    const script = `
import duckdb, json
con = duckdb.connect('${DB_PATH}')
try:
    rows = con.execute('''
        SELECT duration_seconds, started_at, raw_data
        FROM calls WHERE duration_seconds >= 60
        ORDER BY started_at DESC LIMIT 20
    ''').fetchall()
except:
    rows = []
summaries = []
for r in rows:
    raw = json.loads(r[2]) if r[2] else {}
    msg = raw.get('message', {})
    summary = msg.get('analysis', {}).get('summary', '')
    if not summary:
        transcript = msg.get('artifact', {}).get('transcript', '') or msg.get('transcript', '')
        if transcript:
            summary = transcript[:150]
    if summary:
        summaries.append(summary[:200])
con.close()
print(json.dumps(summaries))
`;
    const proc = Bun.spawn(["python3", "-c", script], { stdout: "pipe", stderr: "pipe" });
    const output = await new Response(proc.stdout).text();
    await proc.exited;
    const summaries: string[] = JSON.parse(output.trim());
    if (summaries.length === 0) return "";
    const bullets = summaries.map(s => `- ${s.replace(/\n/g, " ")}`).join("\n");
    return `\n\n---\n\n## Recent Caller Topics (Last ${summaries.length} Calls 1min+)\n\nUse this awareness to anticipate needs but don't reference these calls directly.\n\n${bullets}\n`;
  } catch (error) {
    console.error("Failed to load recent call context:", error);
    return "";
  }
}

let systemPrompt = systemPromptBase;
getRecentCallContext().then(context => {
  systemPrompt = systemPromptBase + context;
  if (context) console.log("Recent call context loaded into system prompt");
});

// ── Database Init ──

async function initDb() {
  try {
    const proc = Bun.spawn(["duckdb", DB_PATH, "-c", `
      CREATE TABLE IF NOT EXISTS calls (
        id VARCHAR PRIMARY KEY,
        phone_number VARCHAR,
        started_at TIMESTAMP,
        ended_at TIMESTAMP,
        duration_seconds INTEGER,
        topics_discussed TEXT,
        stage_assessed VARCHAR,
        escalation_requested BOOLEAN,
        raw_data JSON
      );
      -- Backfill: add phone_number column if table already exists without it
      ALTER TABLE calls ADD COLUMN IF NOT EXISTS phone_number VARCHAR;
      CREATE TABLE IF NOT EXISTS escalations (
        id VARCHAR PRIMARY KEY,
        call_id VARCHAR,
        name VARCHAR,
        contact VARCHAR,
        career_stage VARCHAR,
        reason TEXT,
        pain_points TEXT,
        created_at TIMESTAMP
      );
      CREATE TABLE IF NOT EXISTS feedback (
        id VARCHAR PRIMARY KEY,
        call_id VARCHAR,
        caller_name VARCHAR,
        helpful BOOLEAN,
        rating INTEGER,
        feedback_text TEXT,
        would_recommend BOOLEAN,
        created_at TIMESTAMP
      );
      -- Backfill: add caller_name column if feedback table already exists without it
      ALTER TABLE feedback ADD COLUMN IF NOT EXISTS caller_name VARCHAR;
      CREATE TABLE IF NOT EXISTS caller_lookup (
        id VARCHAR PRIMARY KEY,
        phone_number VARCHAR,
        caller_name VARCHAR,
        career_stage VARCHAR,
        primary_challenge TEXT,
        specific_questions TEXT,
        industry_targets TEXT,
        submitted_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
      CREATE TABLE IF NOT EXISTS caller_insights (
        id VARCHAR PRIMARY KEY,
        phone_number VARCHAR,
        call_count INTEGER DEFAULT 1,
        first_seen TIMESTAMP,
        last_seen TIMESTAMP,
        avg_satisfaction DOUBLE,
        last_stage VARCHAR,
        topics_history VARCHAR,
        notes VARCHAR
      );
      CREATE TABLE IF NOT EXISTS caller_balances (
        phone_number VARCHAR PRIMARY KEY,
        total_seconds_used INTEGER DEFAULT 0,
        total_seconds_purchased INTEGER DEFAULT 0,
        last_call_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
      CREATE TABLE IF NOT EXISTS caller_resumes (
        id VARCHAR PRIMARY KEY,
        phone_number VARCHAR,
        file_path VARCHAR,
        processed_data JSON,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP
      );
      CREATE TABLE IF NOT EXISTS caller_profiles (
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
      );
      CREATE TABLE IF NOT EXISTS intake_webhook_events (
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
      );
    `], { stdout: "pipe", stderr: "pipe" });
    await proc.exited;
    await backfillCallerProfiles();
    console.log("Database initialized successfully");
  } catch (error) {
    console.error("Failed to initialize database:", error);
  }
}

async function backfillCallerProfiles() {
  try {
    const script = `
import duckdb
con = duckdb.connect("/home/workspace/Datasets/career-hotline-calls/data.duckdb")
try:
    con.execute('''CREATE TABLE IF NOT EXISTS caller_profiles (
        phone_number VARCHAR PRIMARY KEY,
        caller_name VARCHAR,
        email VARCHAR,
        linkedin_url VARCHAR,
        primary_challenge TEXT,
        specific_questions TEXT,
        intake_count INTEGER DEFAULT 0,
        intake_last_submitted_at TIMESTAMP,
        last_resume_path VARCHAR,
        last_resume_processed_at TIMESTAMP,
        last_resume_stage VARCHAR,
        last_resume_bullet_quality VARCHAR,
        profile_summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Intake-side baseline
    con.execute('''
        INSERT INTO caller_profiles (
            phone_number, caller_name, primary_challenge, specific_questions,
            intake_count, intake_last_submitted_at, profile_summary
        )
        SELECT
            t.phone_number,
            t.caller_name,
            t.primary_challenge,
            t.specific_questions,
            t.intake_count,
            t.last_submitted_at,
            CASE
                WHEN COALESCE(t.primary_challenge, '') = '' THEN NULL
                ELSE 'Needs: ' || t.primary_challenge
            END
        FROM (
            SELECT
                phone_number,
                any_value(caller_name) AS caller_name,
                any_value(primary_challenge) AS primary_challenge,
                any_value(specific_questions) AS specific_questions,
                count(*) AS intake_count,
                max(submitted_at) AS last_submitted_at
            FROM caller_lookup
            WHERE COALESCE(phone_number, '') != ''
            GROUP BY phone_number
        ) t
        LEFT JOIN caller_profiles p ON p.phone_number = t.phone_number
        WHERE p.phone_number IS NULL
    ''')
    # Resume-side enrichment
    con.execute('''
        UPDATE caller_profiles p
        SET
            resume_count = r.resume_count,
            last_resume_path = r.last_resume_path,
            last_resume_processed_at = r.last_resume_processed_at,
            last_resume_stage = COALESCE(r.last_resume_stage, p.last_resume_stage),
            last_resume_bullet_quality = COALESCE(r.last_resume_bullet_quality, p.last_resume_bullet_quality),
            profile_summary = TRIM(
                COALESCE(
                    CASE
                        WHEN COALESCE(p.primary_challenge, '') = '' THEN ''
                        ELSE 'Needs: ' || p.primary_challenge
                    END,
                    ''
                ) ||
                CASE
                    WHEN COALESCE(r.last_resume_stage, '') = '' THEN ''
                    WHEN COALESCE(p.primary_challenge, '') = '' THEN 'Resume: ' || r.last_resume_stage
                    ELSE ' | Resume: ' || r.last_resume_stage
                END
            ),
            updated_at = CURRENT_TIMESTAMP
        FROM (
            SELECT
                phone_number,
                count(*) AS resume_count,
                any_value(file_path) AS last_resume_path,
                max(processed_at) AS last_resume_processed_at,
                any_value(json_extract_string(processed_data, '$.estimated_career_stage')) AS last_resume_stage,
                any_value(json_extract_string(processed_data, '$.aiss_quick_scan.overall_bullet_quality')) AS last_resume_bullet_quality
            FROM caller_resumes
            WHERE COALESCE(phone_number, '') != ''
            GROUP BY phone_number
        ) r
        WHERE p.phone_number = r.phone_number
    ''')
    print("OK")
except Exception as e:
    print(f"BACKFILL_ERROR: {e}")
finally:
    con.close()
`;
    const proc = Bun.spawn(["python3", "-c", script], { stdout: "pipe", stderr: "pipe" });
    const out = await new Response(proc.stdout).text();
    const err = await new Response(proc.stderr).text();
    await proc.exited;
    if (err.trim()) console.error("caller_profiles backfill stderr:", err.trim());
    if (out.includes("BACKFILL_ERROR")) {
      console.error("caller_profiles backfill output:", out.trim());
    }
  } catch (error) {
    console.error("caller_profiles backfill failed:", error);
  }
}

// ── Balance Tracking ──

async function getCallerBalance(phone: string): Promise<{ used: number; purchased: number; freeRemaining: number; totalAvailable: number }> {
  const normalized = normalizePhone(phone);
  if (!normalized) return { used: 0, purchased: 0, freeRemaining: FREE_TIER_SECONDS, totalAvailable: FREE_TIER_SECONDS };

  try {
    const script = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'], read_only=True)
try:
    row = con.execute('SELECT total_seconds_used, total_seconds_purchased FROM caller_balances WHERE phone_number = ?', [data['phone']]).fetchone()
    if row:
        print(json.dumps({"used": row[0], "purchased": row[1]}))
    else:
        print(json.dumps({"used": 0, "purchased": 0}))
except Exception as e:
    print(json.dumps({"used": 0, "purchased": 0}))
con.close()
`;
    const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe", stderr: "pipe" });
    proc.stdin.write(JSON.stringify({ db: DB_PATH, phone: normalized }));
    proc.stdin.end();
    const output = await new Response(proc.stdout).text();
    await proc.exited;
    const { used, purchased } = JSON.parse(output.trim());
    const freeRemaining = Math.max(0, FREE_TIER_SECONDS - used);
    const totalAvailable = freeRemaining + Math.max(0, purchased - Math.max(0, used - FREE_TIER_SECONDS));
    return { used, purchased, freeRemaining, totalAvailable };
  } catch (error) {
    console.error("Failed to get caller balance:", error);
    return { used: 0, purchased: 0, freeRemaining: FREE_TIER_SECONDS, totalAvailable: FREE_TIER_SECONDS };
  }
}

async function recordCallDuration(phone: string, durationSeconds: number): Promise<void> {
  const normalized = normalizePhone(phone);
  if (!normalized || durationSeconds <= 0) return;

  try {
    const script = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
now = data['now']
try:
    row = con.execute('SELECT phone_number FROM caller_balances WHERE phone_number = ?', [data['phone']]).fetchone()
    if row:
        con.execute('UPDATE caller_balances SET total_seconds_used = total_seconds_used + ?, last_call_at = ? WHERE phone_number = ?',
                     [data['duration'], now, data['phone']])
    else:
        con.execute('INSERT INTO caller_balances (phone_number, total_seconds_used, total_seconds_purchased, last_call_at, created_at) VALUES (?, ?, 0, ?, ?)',
                     [data['phone'], data['duration'], now, now])
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
con.close()
print("OK")
`;
    const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe" });
    proc.stdin.write(JSON.stringify({ db: DB_PATH, phone: normalized, duration: durationSeconds, now: new Date().toISOString() }));
    proc.stdin.end();
    await proc.exited;
  } catch (error) {
    console.error("Failed to record call duration:", error);
  }
}

// ── SMS Notification ──

function notifyV(message: string): void {
  const authHeader = getZoAuthHeader();
  if (!authHeader) {
    console.error("ZO_CLIENT_IDENTITY_TOKEN not set — cannot send SMS");
    return;
  }
  const truncated = message.substring(0, 500);
  fetch("https://api.zo.computer/zo/ask", {
    method: "POST",
    headers: { authorization: authHeader, "content-type": "application/json" },
    body: JSON.stringify({
      input: `SYSTEM NOTIFICATION RELAY\n\nSend V this SMS (using send_sms_to_user):\n\n${truncated}\n\nJust send the SMS. No commentary.`
    })
  }).catch(err => console.error("Failed to notify V:", err));
}

// ── Tool Implementations ──

async function assessCareerStage(params: {
  current_situation: string;
  efforts_so_far: string;
  desired_outcome: string;
  urgency_signals: string;
}): Promise<object> {
  const { current_situation, efforts_so_far, desired_outcome, urgency_signals } = params;

  if (!current_situation || !efforts_so_far || !desired_outcome) {
    return {
      error: "Need current_situation, efforts_so_far, and desired_outcome from diagnostic questions",
      instructions: "Run through the 3 diagnostic questions first"
    };
  }

  try {
    const result = await zoAsk(
      `You are a career stage classifier for a coaching hotline. Given a caller's situation, classify them.

Caller's current situation: ${current_situation}
Efforts so far: ${efforts_so_far}
Desired outcome: ${desired_outcome}
Urgency signals: ${urgency_signals || "none mentioned"}

Stage definitions:
- groundwork: Early stage, unclear direction, needs self-reflection and career inventory
- materials: Has direction but resume/LinkedIn/cover letters need work
- outreach: Materials exist but job search strategy and networking are weak
- performance: Getting interviews but not converting to offers
- transition: Career change, industry switch, or re-entering workforce

Pain points to detect (use any that apply):
"not_tailoring_resume", "no_networking", "interview_anxiety", "career_direction_unclear", "not_started", "strategy_fatigue", "over_relying_on_ai_tools", "single_channel_dependency", "weak_self_advocacy", "poor_targeting", "missing_bridge_story"

Return ONLY valid JSON.`,
      {
        type: "object",
        properties: {
          primary_stage: { type: "string", enum: ["groundwork", "materials", "outreach", "performance", "transition"] },
          secondary_concerns: { type: "array", items: { type: "string" } },
          pain_points: { type: "array", items: { type: "string" } },
          urgency: { type: "string", enum: ["low", "medium", "high", "crisis"] },
          effort_level: { type: "string", enum: ["minimal", "moderate", "high"] },
          calibration_needed: { type: "boolean" },
          coaching_note: { type: "string" }
        },
        required: ["primary_stage", "pain_points", "urgency", "effort_level", "coaching_note"]
      }
    );

    if (result && result.primary_stage) return result;
    throw new Error("Invalid response structure");
  } catch (error) {
    console.error("LLM career assessment failed, using fallback:", error);
    return {
      primary_stage: "groundwork",
      secondary_concerns: [],
      pain_points: [],
      urgency: urgency_signals ? "medium" : "low",
      effort_level: "moderate",
      calibration_needed: false,
      coaching_note: "Assessment service had an issue — ask follow-up questions to understand their stage better."
    };
  }
}

async function getCareerRecommendations(params: {
  primary_stage: string;
  pain_points: string[];
  urgency: string;
  efforts_so_far?: string;
}): Promise<object> {
  const { primary_stage, pain_points, urgency, efforts_so_far } = params;

  const recommendations: Record<string, { actions: string[]; timeframe: string; priority: string }> = {
    groundwork: {
      actions: [
        "Start with self-reflection — write down 10 specific professional stories where you made an impact",
        "Skills fingerprint: list your technical skills, industry knowledge, and soft skills separately",
        "Answer this: 'What do employers actually see when they look at my background?'",
        "Research 3 target roles — read 10 job descriptions and note patterns"
      ],
      timeframe: "2-3 weeks",
      priority: "Self-reflection and career inventory"
    },
    materials: {
      actions: [
        "Build a master resume — comprehensive inventory of everything, not a job-specific version",
        "Apply AISS to every bullet: Action verb, Impact metric, Scale indicator, Skill demonstrated",
        "Run the ATS check: does your resume format survive a text-only paste test?",
        "Tailor each application — 63% of recruiters want customized resumes"
      ],
      timeframe: "1-2 weeks",
      priority: "Master resume + AISS bullet construction"
    },
    outreach: {
      actions: [
        "Stop spray-and-pray — pick 10 target companies and research them deeply",
        "Find 3 people at each target company on LinkedIn, send personalized outreach",
        "Track your funnel: applications sent → responses → interviews → offers",
        "Ask for referrals — referred candidates are 4x more likely to be hired"
      ],
      timeframe: "ongoing weekly cadence",
      priority: "Strategic networking and targeted applications"
    },
    performance: {
      actions: [
        "Build a story bank — connect 8-10 stories in START format (Situation, Task, Action, Result, Takeaway)",
        "Practice your 'tell me about yourself' — 90 seconds, three acts: past, present, future",
        "Prepare 5 questions that show you've researched the company deeply",
        "Debrief every interview within 24 hours — what worked, what didn't, what to change"
      ],
      timeframe: "1-2 weeks prep, ongoing practice",
      priority: "Story bank and structured interview prep"
    },
    transition: {
      actions: [
        "Build your bridge story — connect where you've been to where you're going",
        "Identify 5 people who've made a similar transition — study their paths",
        "Map transferable skills: what abilities apply in the new context?",
        "Start with informational conversations, not applications"
      ],
      timeframe: "4-6 weeks",
      priority: "Bridge story and transferable skills mapping"
    }
  };

  const stageRecs = recommendations[primary_stage] || recommendations.groundwork;

  // Filter out actions the caller has already done based on their efforts
  let filteredActions = stageRecs.actions;
  if (efforts_so_far) {
    const effortsLower = efforts_so_far.toLowerCase();
    filteredActions = stageRecs.actions.filter(action => {
      const actionLower = action.toLowerCase();
      if (effortsLower.includes("networking") && actionLower.includes("networking")) return false;
      if (effortsLower.includes("master resume") && actionLower.includes("master resume")) return false;
      if (effortsLower.includes("story bank") && actionLower.includes("story bank")) return false;
      if (effortsLower.includes("target companies") && actionLower.includes("target companies")) return false;
      return true;
    });
    if (filteredActions.length === 0) filteredActions = stageRecs.actions;
  }

  let urgencyAdjustment = "";
  if (urgency === "high" || urgency === "crisis") {
    urgencyAdjustment = "Given your urgency, compress the timeline. Focus on the first two actions this week.";
  }

  const painPointAdvice: string[] = [];
  for (const pp of pain_points || []) {
    switch (pp) {
      case "not_tailoring_resume":
        painPointAdvice.push("Stop sending the same resume. Each application needs a tailored version from your master resume.");
        break;
      case "no_networking":
        painPointAdvice.push("Networking isn't optional. Start with 3 LinkedIn messages this week to people in your target roles.");
        break;
      case "interview_anxiety":
        painPointAdvice.push("Practice with story banking, not script memorization. Knowing your proof points cold reduces anxiety.");
        break;
      case "career_direction_unclear":
        painPointAdvice.push("Before anything else, do the skills fingerprint exercise. You can't market what you haven't inventoried.");
        break;
      case "over_relying_on_ai_tools":
        painPointAdvice.push("AI tools are a starting point, not the final product. Every AI-generated bullet needs your real stories and metrics.");
        break;
      case "single_channel_dependency":
        painPointAdvice.push("Job boards alone won't cut it. Add direct outreach and referral requests to your weekly routine.");
        break;
      case "strategy_fatigue":
        painPointAdvice.push("You've been working hard — now work differently. Pause volume, focus on 5 target companies with deep research.");
        break;
      case "weak_self_advocacy":
        painPointAdvice.push("You need to get comfortable talking about your wins. The Art of the Brag isn't boasting — it's self-advocacy backed by evidence.");
        break;
      case "poor_targeting":
        painPointAdvice.push("You're casting too wide a net. Narrow down to 10 target companies and learn everything about their hiring patterns.");
        break;
      case "missing_bridge_story":
        painPointAdvice.push("You need a bridge story that connects your past to your future. Without it, employers see a random pivot, not a strategic move.");
        break;
    }
  }

  const careerspan: Record<string, { offering: string; opening_hook: string; pitch: string; transition_phrase: string; key_stat: string }> = {
    groundwork: {
      offering: "Career Discovery Session",
      opening_hook: "Most people skip this step entirely — and it costs them months.",
      pitch: "Figuring out your direction takes real conversation — digging into your story, your experiences. That's what Careerspan coaching sessions are for.",
      transition_phrase: "I can give you the framework. If you want someone to help you apply it to YOUR specific background, that's coaching.",
      key_stat: "46% of new hires fail in 18 months. Most because of poor fit assessment upfront."
    },
    materials: {
      offering: "Resume & Materials Review",
      opening_hook: "Your resume is sending a signal right now. The question is whether it's the signal you intend.",
      pitch: "The principles are universal. But the real magic is when someone who's reviewed thousands of resumes looks at yours specifically and tells you exactly what to fix.",
      transition_phrase: "I can teach you the AISS framework. Having someone apply it to YOUR bullets — that's different.",
      key_stat: "75% of resumes are filtered by ATS before a human ever sees them."
    },
    outreach: {
      offering: "Job Search Strategy Session",
      opening_hook: "You're working hard. The question is whether you're working smart.",
      pitch: "You need someone who can look at your specific situation and build you a plan — who to reach out to, what to say, what your weekly rhythm should look like.",
      transition_phrase: "I can teach you the principles of strategic outreach. Building YOUR specific target list and outreach plan — that requires knowing YOUR network.",
      key_stat: "Referrals make candidates 4x more likely to get hired. Each job posting averages 250 applications."
    },
    performance: {
      offering: "Interview Coaching + Story Bank Build",
      opening_hook: "You're getting in the room. That's the hard part, and you're already past it.",
      pitch: "Building a real story bank — pulling apart your career, finding the proof points, structuring them for any question they throw at you — that's serious coaching work. I can teach you the START format, but building YOUR bank from YOUR stories? That's Careerspan.",
      transition_phrase: "I can give you the frameworks. Building your actual story bank and practicing delivery — that's where coaching changes everything.",
      key_stat: "89% of new hire failures are about attitude and fit, not skills."
    },
    transition: {
      offering: "Career Transition Strategy",
      opening_hook: "Career transitions are the hardest coaching work — and the most rewarding. You're not starting over. You're translating.",
      pitch: "The question isn't whether you're qualified, it's how you tell the story. That's not a 15-minute conversation — that's real coaching work.",
      transition_phrase: "I can teach you the concept of a bridge story. Building YOUR bridge story — that's coaching.",
      key_stat: "46% of new hires fail in 18 months, and 89% of those failures are attitudinal, not technical."
    }
  };

  const stageCareerspan = careerspan[primary_stage] || careerspan.groundwork;

  // Detect Careerspan referral triggers
  const referralTriggers: string[] = [];
  if (pain_points?.includes("interview_anxiety") || primary_stage === "performance") {
    referralTriggers.push("story_bank_build");
  }
  if (pain_points?.includes("weak_self_advocacy")) {
    referralTriggers.push("self_advocacy_coaching");
  }
  if (pain_points?.includes("missing_bridge_story")) {
    referralTriggers.push("bridge_story_development");
  }

  return {
    stage: primary_stage,
    timeframe: stageRecs.timeframe,
    priority: stageRecs.priority,
    actions: filteredActions,
    urgency_note: urgencyAdjustment || null,
    pain_point_advice: painPointAdvice.length > 0 ? painPointAdvice : null,
    careerspan_recommendation: {
      offering: stageCareerspan.offering,
      opening_hook: stageCareerspan.opening_hook,
      pitch: stageCareerspan.pitch,
      transition_phrase: stageCareerspan.transition_phrase,
      key_stat: stageCareerspan.key_stat,
      booking_link: BOOKING_LINK
    },
    careerspan_referral_triggers: referralTriggers.length > 0 ? {
      triggers: referralTriggers,
      note: "These areas are where Careerspan coaching adds the most value. Mention naturally if the caller seems receptive."
    } : null
  };
}

async function explainCareerConcept(params: { concept: string; caller_stage?: string }): Promise<object> {
  const { concept, caller_stage } = params;
  const normalized = concept.toLowerCase().replace(/\s+/g, "-");

  const filePath = conceptMapRaw[normalized] || conceptMapRaw[concept];

  if (!filePath) {
    const available = [...new Set(Object.values(conceptMapRaw))]
      .map(p => p.split("/").pop()?.replace(".md", ""))
      .filter(Boolean)
      .slice(0, 10);
    return {
      error: `Concept "${concept}" not found`,
      available_concepts: available,
      suggestion: "Try asking about: resume-customization, ats-systems, networking, linkedin-strategy, self-reflection, or art-of-the-brag"
    };
  }

  try {
    const fullPath = filePath.startsWith("/") ? filePath : `/home/workspace/${filePath}`;

    if (existsSync(fullPath) && fullPath.endsWith(".md")) {
      const content = readFileSync(fullPath, "utf-8").replace(/^---[\s\S]*?---\s*/, "");
      let truncated = content.substring(0, 2500);
      if (caller_stage) {
        truncated += `\n\n[Tailored for ${caller_stage} stage callers]`;
      }
      return { concept, content: truncated, type: "file_content" };
    } else if (existsSync(fullPath) && statSync(fullPath).isDirectory()) {
      const files = readdirSync(fullPath).filter(f => f.endsWith(".md"));
      const overview = files.map(f => f.replace(".md", "").replace(/-/g, " ")).join(", ");
      return {
        concept,
        content: `The ${concept} area covers: ${overview}`,
        type: "directory_overview",
        suggestion: `Ask about a specific topic: ${files.slice(0, 3).map(f => f.replace(".md", "")).join(", ")}`
      };
    }
  } catch (error) {
    console.error("Error reading concept file:", error);
  }

  return {
    error: `Could not load concept "${concept}"`,
    suggestion: "Try asking about: resume-customization, networking, or self-reflection"
  };
}

async function lookupCaller(params: { phone_number: string }): Promise<object> {
  const { phone_number } = params;
  if (!phone_number) return { found: false, message: "No phone number provided" };

  const normalized = normalizePhone(phone_number);

  const balance = await getCallerBalance(normalized);

  // Get intake form data
  let intakeData: any = null;
  try {
    const script = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    row = con.execute('''
        SELECT caller_name, career_stage, primary_challenge, specific_questions, industry_targets
        FROM caller_lookup WHERE phone_number = ? ORDER BY submitted_at DESC LIMIT 1
    ''', [data['phone']]).fetchone()
    if row:
        print(json.dumps({"name": row[0], "career_stage": row[1], "challenge": row[2], "questions": row[3], "targets": row[4]}))
    else:
        print(json.dumps(None))
except:
    print(json.dumps(None))
con.close()
`;
    const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe" });
    proc.stdin.write(JSON.stringify({ db: DB_PATH, phone: normalized }));
    proc.stdin.end();
    const output = await new Response(proc.stdout).text();
    await proc.exited;
    intakeData = JSON.parse(output.trim());
  } catch (error) {
    console.error("Intake lookup failed:", error);
  }

  // Get returning caller insights
  let callerInsights: any = null;
  try {
    const script = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    row = con.execute('''
        SELECT call_count, last_stage, topics_history, notes
        FROM caller_insights WHERE phone_number = ? LIMIT 1
    ''', [data['phone']]).fetchone()
    if row:
        print(json.dumps({"call_count": row[0], "last_stage": row[1], "topics": row[2], "notes": row[3]}))
    else:
        print(json.dumps(None))
except:
    print(json.dumps(None))
con.close()
`;
    const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe" });
    proc.stdin.write(JSON.stringify({ db: DB_PATH, phone: normalized }));
    proc.stdin.end();
    const output = await new Response(proc.stdout).text();
    await proc.exited;
    callerInsights = JSON.parse(output.trim());
  } catch (error) {
    console.error("Caller insights lookup failed:", error);
  }

  // Get consolidated caller profile
  let callerProfile: any = null;
  try {
    const script = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    row = con.execute('''
        SELECT caller_name, email, linkedin_url, primary_challenge, specific_questions,
               intake_count, resume_count, last_resume_stage, last_resume_bullet_quality, profile_summary
        FROM caller_profiles WHERE phone_number = ? LIMIT 1
    ''', [data['phone']]).fetchone()
    if row:
        print(json.dumps({
            "name": row[0],
            "email": row[1],
            "linkedin": row[2],
            "primary_challenge": row[3],
            "specific_questions": row[4],
            "intake_count": row[5],
            "resume_count": row[6],
            "resume_stage": row[7],
            "resume_bullet_quality": row[8],
            "summary": row[9]
        }))
    else:
        print(json.dumps(None))
except:
    print(json.dumps(None))
con.close()
`;
    const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe" });
    proc.stdin.write(JSON.stringify({ db: DB_PATH, phone: normalized }));
    proc.stdin.end();
    const output = await new Response(proc.stdout).text();
    await proc.exited;
    callerProfile = JSON.parse(output.trim());
  } catch (error) {
    console.error("Caller profile lookup failed:", error);
  }

  // Check for resume on file
  let hasResume = false;
  try {
    const script = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    row = con.execute('SELECT COUNT(*) FROM caller_resumes WHERE phone_number = ?', [data['phone']]).fetchone()
    print(json.dumps(row[0] > 0 if row else False))
except:
    print(json.dumps(False))
con.close()
`;
    const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe" });
    proc.stdin.write(JSON.stringify({ db: DB_PATH, phone: normalized }));
    proc.stdin.end();
    const output = await new Response(proc.stdout).text();
    await proc.exited;
    hasResume = JSON.parse(output.trim());
  } catch { /* non-critical */ }

  const result: any = {
    found: !!(intakeData || callerInsights),
    balance: {
      free_seconds_remaining: balance.freeRemaining,
      total_seconds_available: balance.totalAvailable,
      total_seconds_used: balance.used,
      purchased_seconds: balance.purchased,
      is_free_tier: balance.used < FREE_TIER_SECONDS,
      has_time_remaining: balance.totalAvailable > 0
    },
    has_resume_on_file: hasResume
  };

  if (!result.balance.has_time_remaining) {
    result.balance.message = `This caller has used all their free time and has no purchased credits. Let them know they can get more time at ${PURCHASE_URL}`;
  } else if (balance.freeRemaining > 0 && balance.freeRemaining < 120) {
    result.balance.message = `Caller has less than 2 minutes of free time remaining (${Math.round(balance.freeRemaining / 60)} min). Mention this naturally near the end.`;
  }

  if (hasResume) {
    result.resume_note = "This caller has a resume on file. You can use the pullCallerResume tool to retrieve their processed resume data for personalized coaching.";
  }

  if (intakeData) {
    result.intake = intakeData;
  }

  if (callerInsights) {
    result.returning_caller = callerInsights;
  }
  if (callerProfile) {
    result.profile = callerProfile;
  }

  const callHistory = await getCallerCallHistory(normalized);
  if (callHistory) {
    result.call_history = callHistory;
    result.returning_caller_context = `This is a RETURNING caller${callerInsights?.call_count ? ` (call #${callerInsights.call_count + 1})` : ""}. Their previous calls:\n${callHistory}\n\n${callerInsights?.notes ? `Coach's synthesis: ${callerInsights.notes}` : ""}\n\nUse this to personalize: reference what you discussed before, check on progress, avoid repeating the same advice.`;
  }

  return result;
}

async function requestCareerSession(params: {
  name: string;
  contact: string;
  career_stage: string;
  reason: string;
  pain_points?: string[];
}, vapiCallId: string = "current"): Promise<object> {
  const { name, contact, career_stage, reason, pain_points } = params;

  if (!name || !contact || !career_stage || !reason) {
    return {
      error: "Need name, contact, career_stage, and reason",
      example: "name: 'Jane Smith', contact: 'jane@example.com', career_stage: 'materials', reason: 'Need resume review'"
    };
  }

  try {
    const escalationId = generateUUID();
    const now = new Date().toISOString();

    const insertScript = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
con.execute('''
  INSERT INTO escalations (id, call_id, name, contact, career_stage, reason, pain_points, created_at)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', [data['id'], data['call_id'], data['name'], data['contact'], data['career_stage'], data['reason'], data['pain_points'], data['created_at']])
con.close()
print("SUCCESS")
`;

    const insertData = JSON.stringify({
      db: DB_PATH,
      id: escalationId,
      call_id: vapiCallId,
      name, contact, career_stage, reason,
      pain_points: JSON.stringify(pain_points || []),
      created_at: now
    });

    const proc = Bun.spawn(["python3", "-c", insertScript], { stdin: "pipe", stdout: "pipe" });
    proc.stdin.write(insertData);
    proc.stdin.end();
    await new Response(proc.stdout).text();
    await proc.exited;

    notifyV(`📞 Careerspan session request:\n• Name: ${name}\n• Contact: ${contact}\n• Stage: ${career_stage}\n• Reason: ${reason}${pain_points?.length ? `\n• Pain points: ${pain_points.join(", ")}` : ""}\n\nPlease reach out within 24 hours.`);

    return {
      success: true,
      message: `Got it, ${name}. I've logged your request and Vrijen will reach out soon. You can also book directly at: ${BOOKING_LINK}`,
      escalation_id: escalationId.substring(0, 8),
      booking_link: BOOKING_LINK
    };
  } catch (error) {
    console.error("Error logging session request:", error);
    return {
      error: "Failed to log session request",
      fallback: `You can find Vrijen on Twitter as @thevibethinker or on LinkedIn as Vrijen Attawar`
    };
  }
}

async function collectFeedback(params: {
  caller_name?: string;
  helpful?: boolean;
  rating?: number;
  feedback_text?: string;
  would_recommend?: boolean;
}, vapiCallId: string = "current"): Promise<object> {
  const { caller_name, helpful, rating, feedback_text, would_recommend } = params;

  if (helpful === undefined && !rating && !feedback_text && would_recommend === undefined && !caller_name) {
    return { success: true, message: "No worries at all. Thanks for calling!" };
  }

  try {
    const feedbackId = generateUUID();
    const now = new Date().toISOString();

    const insertScript = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
con.execute('''
  INSERT INTO feedback (id, call_id, caller_name, helpful, rating, feedback_text, would_recommend, created_at)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', [data['id'], data['call_id'], data['caller_name'], data['helpful'], data['rating'], data['feedback_text'], data['would_recommend'], data['created_at']])
con.close()
print("SUCCESS")
`;

    const feedbackData = JSON.stringify({
      db: DB_PATH,
      id: feedbackId,
      call_id: vapiCallId,
      caller_name: caller_name ?? null,
      helpful: helpful ?? null,
      rating: rating ?? null,
      feedback_text: feedback_text ?? null,
      would_recommend: would_recommend ?? null,
      created_at: now
    });

    const proc = Bun.spawn(["python3", "-c", insertScript], { stdin: "pipe", stdout: "pipe" });
    proc.stdin.write(feedbackData);
    proc.stdin.end();
    await proc.exited;

    const parts: string[] = [];
    if (caller_name) parts.push(`noted your name, ${caller_name}`);
    if (rating) parts.push(`rated ${rating}/5`);
    if (feedback_text) parts.push("noted your feedback");
    if (helpful !== undefined) parts.push(helpful ? "glad it helped" : "sorry it wasn't more useful");
    if (would_recommend) parts.push("and thanks for being willing to spread the word");

    return {
      success: true,
      message: parts.length > 0 ? `${parts.join(", ")}. Appreciate it!` : "Thanks!",
      referral_nudge: would_recommend ? "If you know someone who could use career coaching, share the hotline number with them. Word of mouth is how we grow." : null
    };
  } catch (error) {
    console.error("Error logging feedback:", error);
    return { success: true, message: "Thanks for the feedback." };
  }
}

// ── NEW TOOL: analyzeResumeBullet ──

async function analyzeResumeBullet(params: {
  bullet_text: string;
  target_role?: string;
}): Promise<object> {
  const { bullet_text, target_role } = params;

  if (!bullet_text || bullet_text.trim().length < 5) {
    return { error: "Need a resume bullet to analyze. Ask the caller to read one of their bullets." };
  }

  try {
    const result = await zoAsk(
      `You are applying the AISS resume bullet framework to analyze a caller's resume bullet on a live coaching call.

AISS Framework:
- Action: Strong past-tense verb (not "responsible for" or "helped with")
- Impact: Quantified result (revenue, cost savings, time saved, users served)
- Scale: Scope context (team size, budget, user base, geographic reach)
- Skill: Capability demonstrated that maps to target roles

Resume bullet to analyze: "${bullet_text}"
${target_role ? `Target role context: ${target_role}` : ""}

Score each AISS component 1-5 and provide a rewritten version. Return ONLY valid JSON.`,
      {
        type: "object",
        properties: {
          original: { type: "string" },
          scores: {
            type: "object",
            properties: {
              action: { type: "number" },
              impact: { type: "number" },
              scale: { type: "number" },
              skill: { type: "number" },
              overall: { type: "number" }
            },
            required: ["action", "impact", "scale", "skill", "overall"]
          },
          diagnosis: { type: "string" },
          rewrite: { type: "string" },
          coaching_tip: { type: "string" }
        },
        required: ["original", "scores", "diagnosis", "rewrite", "coaching_tip"]
      }
    );

    if (result && result.scores) {
      // Normalize nested {score, rationale} objects to flat numbers for VAPI
      for (const [key, val] of Object.entries(result.scores)) {
        if (val && typeof val === "object" && "score" in (val as any)) {
          (result.scores as any)[key] = (val as any).score;
        }
      }
      return result;
    }
    throw new Error("Invalid response");
  } catch (error) {
    console.error("analyzeResumeBullet failed:", error);
    return {
      error: "Analysis service is temporarily unavailable",
      fallback: "Ask the caller: Does this bullet have a strong action verb? A measurable impact? Context for scale? And does it demonstrate a skill the target role needs?"
    };
  }
}

// ── NEW TOOL: diagnoseSearchStrategy ──

async function diagnoseSearchStrategy(params: {
  signal_strength: string;
  system_fluency: string;
  execution: string;
  intelligence: string;
}): Promise<object> {
  const { signal_strength, system_fluency, execution, intelligence } = params;

  if (!signal_strength || !system_fluency || !execution || !intelligence) {
    return {
      error: "Need all four diagnostic dimensions",
      instructions: "Ask about: 1) How clearly they communicate their value, 2) How well they understand hiring systems, 3) How consistently they execute their search, 4) How well they research and target opportunities"
    };
  }

  try {
    const result = await zoAsk(
      `You are running a 4-dimension career search diagnostic on a coaching call.

The Four Dimensions:
1. Signal Strength: Is their professional value clearly communicated? (resume, LinkedIn, elevator pitch, stories)
2. System Fluency: Do they understand how hiring actually works? (ATS, recruiter incentives, hidden job market)
3. Execution: Are they putting in consistent, strategic effort? (weekly targets, follow-up, pipeline tracking)
4. Intelligence: Are they targeting the right opportunities? (company research, compensation benchmarks, insider connections)

Caller's responses:
- Signal Strength: ${signal_strength}
- System Fluency: ${system_fluency}
- Execution: ${execution}
- Intelligence: ${intelligence}

Score each dimension 1-5, identify the weakest, and recommend the specific fix. Return ONLY valid JSON.`,
      {
        type: "object",
        properties: {
          scores: {
            type: "object",
            properties: {
              signal_strength: { type: "number" },
              system_fluency: { type: "number" },
              execution: { type: "number" },
              intelligence: { type: "number" }
            },
            required: ["signal_strength", "system_fluency", "execution", "intelligence"]
          },
          weakest_dimension: { type: "string" },
          diagnosis: { type: "string" },
          primary_fix: { type: "string" },
          secondary_fix: { type: "string" },
          careerspan_relevant: { type: "boolean" }
        },
        required: ["scores", "weakest_dimension", "diagnosis", "primary_fix", "secondary_fix", "careerspan_relevant"]
      }
    );

    if (result && typeof result === "object") {
      // LLM may return flat structure or nested under "diagnostic" key — normalize both
      const diag = result.diagnostic || result;
      const normalized: any = {
        scores: diag.scores || diag.dimensions || diag.dimension_scores || {},
        weakest_dimension: diag.weakest_dimension || diag.weakest || "",
        diagnosis: diag.diagnosis || diag.caller_summary || diag.overall_assessment || "",
        primary_fix: diag.primary_fix || diag.primary_recommendation || "",
        secondary_fix: diag.secondary_fix || diag.secondary_recommendation || "",
        careerspan_relevant: diag.careerspan_relevant ?? false,
      };

      // Extract numeric scores from nested {score, rationale} objects if needed
      if (normalized.scores && typeof normalized.scores === "object") {
        for (const [key, val] of Object.entries(normalized.scores)) {
          if (val && typeof val === "object" && "score" in (val as any)) {
            (normalized.scores as any)[key] = (val as any).score;
          }
        }
      }

      if (normalized.scores && Object.keys(normalized.scores).length > 0) {
        if (normalized.careerspan_relevant) {
          normalized.careerspan_note = "This caller's issues go deeper than a single call can address. This is a natural Careerspan referral point — they need sustained coaching.";
        }
        return normalized;
      }
      console.error("diagnoseSearchStrategy: could not extract scores from:", JSON.stringify(result).slice(0, 300));
    } else {
      console.error("diagnoseSearchStrategy: zoAsk returned:", typeof result, result === null ? "null" : String(result).slice(0, 200));
    }
    throw new Error("Invalid response structure");
  } catch (error) {
    console.error("diagnoseSearchStrategy failed:", error);
    return {
      error: "Diagnostic service temporarily unavailable",
      fallback: "Walk through each dimension manually: Are they communicating value clearly? Do they understand the system? Are they executing consistently? Are they targeting intelligently?"
    };
  }
}

// ── NEW TOOL: scoreResumeSection ──

async function scoreResumeSection(params: {
  section_type: string;
  section_content: string;
  target_role?: string;
}): Promise<object> {
  const { section_type, section_content, target_role } = params;

  const validSections = ["summary", "experience", "skills", "education", "projects"];
  const normalizedSection = section_type.toLowerCase().trim();

  if (!validSections.includes(normalizedSection)) {
    return {
      error: `Section type must be one of: ${validSections.join(", ")}`,
      instructions: "Ask the caller which section of their resume they want feedback on."
    };
  }

  if (!section_content || section_content.trim().length < 10) {
    return { error: "Need the content of the resume section to score. Ask the caller to read or describe it." };
  }

  try {
    const result = await zoAsk(
      `You are scoring a resume section on a live coaching call. Be direct, specific, and actionable.

Section type: ${normalizedSection}
Section content: "${section_content}"
${target_role ? `Target role: ${target_role}` : ""}

Scoring criteria by section:
- summary: Does it position the candidate as a solution to employer problems? Is it tailored? Does it pass the "so what?" test?
- experience: AISS compliance of bullets, relevance to target, progression narrative
- skills: Hard skills vs soft skills balance, ATS keyword coverage, specificity
- education: Proper formatting for ATS parsing, relevant coursework/certifications highlighted
- projects: Impact demonstrated, technologies/methodologies shown, relevance to target

Return ONLY valid JSON.`,
      {
        type: "object",
        properties: {
          section: { type: "string" },
          score: { type: "number" },
          strengths: { type: "array", items: { type: "string" } },
          weaknesses: { type: "array", items: { type: "string" } },
          specific_fixes: { type: "array", items: { type: "string" } },
          ats_risk: { type: "string" },
          coaching_note: { type: "string" }
        },
        required: ["section", "score", "strengths", "weaknesses", "specific_fixes", "ats_risk", "coaching_note"]
      }
    );

    if (result && result.score !== undefined) return result;
    throw new Error("Invalid response");
  } catch (error) {
    console.error("scoreResumeSection failed:", error);
    return {
      error: "Scoring service temporarily unavailable",
      fallback: `For ${normalizedSection} sections, check: Is it ATS-parseable? Does every line demonstrate value? Would a hiring manager spending 6 seconds on it get the right signal?`
    };
  }
}

// ── NEW TOOL: pullCallerResume ──

async function pullCallerResume(params: {
  phone_number: string;
}): Promise<object> {
  const { phone_number } = params;
  if (!phone_number) return { found: false, message: "No phone number provided" };

  const normalized = normalizePhone(phone_number);

  try {
    const script = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    row = con.execute('''
        SELECT processed_data, file_path, submitted_at, processed_at
        FROM caller_resumes
        WHERE phone_number = ?
        ORDER BY submitted_at DESC LIMIT 1
    ''', [data['phone']]).fetchone()
    if row:
        processed = json.loads(row[0]) if row[0] else None
        print(json.dumps({
            "found": True,
            "processed_data": processed,
            "file_path": row[1],
            "submitted_at": str(row[2]) if row[2] else None,
            "processed_at": str(row[3]) if row[3] else None,
            "is_processed": processed is not None
        }))
    else:
        print(json.dumps({"found": False}))
except Exception as e:
    print(json.dumps({"found": False, "error": str(e)}), file=sys.stderr)
    print(json.dumps({"found": False}))
con.close()
`;
    const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe", stderr: "pipe" });
    proc.stdin.write(JSON.stringify({ db: DB_PATH, phone: normalized }));
    proc.stdin.end();
    const output = await new Response(proc.stdout).text();
    await proc.exited;

    const result = JSON.parse(output.trim());

    if (!result.found) {
      return {
        found: false,
        message: "No resume on file for this caller.",
        suggestion: "Let them know they can submit their resume through the intake form for personalized coaching on future calls."
      };
    }

    if (!result.is_processed) {
      return {
        found: true,
        processed: false,
        message: "Resume was submitted but hasn't been processed yet. Coach based on what the caller tells you directly.",
        submitted_at: result.submitted_at
      };
    }

    return {
      found: true,
      processed: true,
      resume_data: result.processed_data,
      submitted_at: result.submitted_at,
      processed_at: result.processed_at,
      coaching_note: "Use this resume data to give specific, personalized feedback. Reference their actual bullets, skills, and experience — don't coach generically."
    };
  } catch (error) {
    console.error("pullCallerResume failed:", error);
    return { found: false, error: "Failed to retrieve resume data" };
  }
}

// ── NEW TOOL: referToCareerspan ──

async function referToCareerspan(params: {
  reason: string;
  caller_stage?: string;
}): Promise<object> {
  const { reason, caller_stage } = params;

  const referralMap: Record<string, { service: string; pitch: string; transition: string }> = {
    story_bank: {
      service: "Story Bank Build + Interview Prep",
      pitch: "Building a real story bank — pulling apart your career, finding the proof points, structuring them for any question — that's serious coaching work. It's the kind of thing that changes your interview game completely.",
      transition: "I can teach you the START format right now. But building YOUR bank from YOUR actual career stories? That's Careerspan coaching."
    },
    resume_review: {
      service: "Resume & Materials Deep Review",
      pitch: "There's a limit to what I can do with resume feedback over the phone. A proper review means someone looking at your actual document, line by line, with your target roles in mind.",
      transition: "I've given you the AISS framework. Getting someone to apply it across your entire resume, that's different."
    },
    ongoing_accountability: {
      service: "Ongoing Coaching & Accountability",
      pitch: "What you need isn't more frameworks — it's someone in your corner week over week, keeping you on track and adjusting the plan as things change.",
      transition: "This call gives you a snapshot. Sustained coaching gives you a partner."
    },
    complex_transition: {
      service: "Career Transition Strategy",
      pitch: "Career pivots are the hardest coaching work because every piece has to connect — your bridge story, your positioning, your target list. That's multi-session work.",
      transition: "I can teach you the concept. Executing YOUR transition strategy — that needs coaching."
    },
    interview_practice: {
      service: "Live Interview Practice",
      pitch: "The gap between knowing the framework and delivering under pressure is practice with real feedback. You need someone watching you answer and telling you where you're losing people.",
      transition: "I can give you the prep structure. The actual practice with live feedback — that's Careerspan."
    },
    deep_self_reflection: {
      service: "Career Discovery & Self-Reflection",
      pitch: "You're trying to figure out your direction, and that's not something a 15-minute call can crack. That takes real digging — into your stories, your patterns, what actually energizes you.",
      transition: "I can point you in the right direction. Doing the deep excavation — that's coaching work."
    }
  };

  const reasonNormalized = reason.toLowerCase().replace(/[\s-]+/g, "_");
  const match = referralMap[reasonNormalized];

  if (match) {
    return {
      service: match.service,
      pitch: match.pitch,
      transition: match.transition,
      booking_link: BOOKING_LINK,
      tone_note: "Deliver this naturally, not as a script. If the caller seems receptive, mention booking. If not, just plant the seed and move on."
    };
  }

  // Generic referral for unmatched reasons
  return {
    service: "Careerspan Coaching",
    pitch: `What you're working on — ${reason} — is the kind of thing that benefits from sustained, personalized attention. That's what Careerspan coaching is built for.`,
    transition: "I'm giving you the framework. If you want someone to apply it to YOUR situation specifically, that's coaching.",
    booking_link: BOOKING_LINK,
    tone_note: "Deliver this naturally. No pressure."
  };
}

// ── Topic Classification ──

const TOPIC_TAXONOMY = [
  "resume", "cover_letter", "linkedin", "job_search", "networking",
  "interview_prep", "career_pivot", "salary_negotiation", "self_reflection",
  "ats_systems", "materials_review", "career_direction", "internship",
  "groundwork", "outreach", "performance", "transition", "escalation",
  "careerspan_inquiry", "resume_bullet_analysis", "search_diagnostic", "general"
];

function classifyTopicsAsync(callId: string, transcript: string): void {
  if (!transcript || transcript.length < 50) return;
  const authHeader = getZoAuthHeader();
  if (!authHeader) return;
  const taxonomyList = TOPIC_TAXONOMY.join(", ");

  fetch("https://api.zo.computer/zo/ask", {
    method: "POST",
    headers: { authorization: authHeader, "content-type": "application/json" },
    body: JSON.stringify({
      input: `Classify this career coaching phone call transcript into 1-3 topics from this taxonomy: ${taxonomyList}\n\nReturn ONLY a comma-separated list of matching topics, nothing else.\n\nTranscript (first 1500 chars):\n${transcript.substring(0, 1500)}`
    })
  }).then(async resp => {
    if (!resp.ok) return;
    const body = await resp.json().catch(() => null);
    const raw = (body as any)?.output || "";
    const topics = raw.split(",")
      .map((t: string) => t.trim().toLowerCase().replace(/[^a-z_]/g, ""))
      .filter((t: string) => TOPIC_TAXONOMY.includes(t));

    if (topics.length > 0) {
      const updateScript = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    con.execute('UPDATE calls SET topics_discussed = ? WHERE id = ?', [data['topics'], data['call_id']])
except:
    pass
con.close()
`;
      const proc = Bun.spawn(["python3", "-c", updateScript], { stdin: "pipe", stdout: "pipe" });
      proc.stdin.write(JSON.stringify({ db: DB_PATH, call_id: callId, topics: topics.join(",") }));
      proc.stdin.end();
    }
  }).catch(err => console.error("Topic classification failed:", err));
}

// ── Caller Insights ──

async function updateCallerInsightsAsync(
  phone: string,
  callId: string,
  durationSeconds: number,
  summary: string,
  topics: string,
  stage: string,
  rating: number | null
): Promise<void> {
  const normalized = normalizePhone(phone);
  if (!normalized) return;

  try {
    const script = `
import duckdb, json, sys, time
data = json.loads(sys.stdin.read())
now = data['now']
phone = data['phone']

for attempt in range(3):
    try:
        con = duckdb.connect(data['db'])
        row = con.execute('SELECT id, call_count, topics_history, avg_satisfaction, notes FROM caller_insights WHERE phone_number = ?', [phone]).fetchone()
        if row:
            old_count = row[1] or 0
            new_count = old_count + 1
            old_topics = row[2] or ""
            new_topics_list = list(set(filter(None, old_topics.split(",") + data['topics'].split(","))))[-20:]
            new_topics = ",".join(new_topics_list)
            old_avg = row[3] or 0
            new_avg = old_avg
            if data['rating']:
                new_avg = ((old_avg * old_count) + data['rating']) / new_count if old_count > 0 else data['rating']
            old_notes = row[4] or ""
            note_entry = f"[{now[:10]}] {data['summary'][:200]}" if data['summary'] else ""
            if note_entry:
                notes_list = old_notes.split("\\n") if old_notes else []
                notes_list.append(note_entry)
                notes_list = notes_list[-10:]
                new_notes = "\\n".join(notes_list)
            else:
                new_notes = old_notes
            con.execute('''UPDATE caller_insights SET
                call_count = ?, last_seen = ?, avg_satisfaction = ?,
                last_stage = ?, topics_history = ?, notes = ?
                WHERE phone_number = ?''',
                [new_count, now, new_avg, data['stage'] or row[3], new_topics, new_notes, phone])
            print(json.dumps({"action": "updated", "call_count": new_count}))
        else:
            import uuid
            new_id = str(uuid.uuid4())
            notes = f"[{now[:10]}] {data['summary'][:200]}" if data['summary'] else ""
            con.execute('''INSERT INTO caller_insights
                (id, phone_number, call_count, first_seen, last_seen, avg_satisfaction, last_stage, topics_history, notes)
                VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?)''',
                [new_id, phone, now, now, data['rating'] or 0, data['stage'] or 'unknown', data['topics'] or '', notes])
            print(json.dumps({"action": "created", "call_count": 1}))
        con.close()
        break
    except Exception as e:
        try: con.close()
        except: pass
        if attempt < 2 and "database is locked" in str(e).lower():
            time.sleep(0.5 * (attempt + 1))
            continue
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        print(json.dumps({"action": "error", "detail": str(e)}))
        break
`;
    const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe", stderr: "pipe" });
    proc.stdin.write(JSON.stringify({
      db: DB_PATH, phone: normalized, now: new Date().toISOString(),
      summary: summary || "", topics: topics || "", stage: stage || "", rating
    }));
    proc.stdin.end();
    const output = await new Response(proc.stdout).text();
    const errOutput = await new Response(proc.stderr).text();
    await proc.exited;

    if (errOutput) console.error(`[INSIGHTS] stderr: ${errOutput}`);
    const trimmed = output.trim();
    if (!trimmed) {
      console.error("[INSIGHTS] Empty output from Python script");
      return;
    }
    let result: any;
    try {
      result = JSON.parse(trimmed);
    } catch {
      console.error(`[INSIGHTS] Could not parse output: ${trimmed.slice(0, 200)}`);
      return;
    }
    console.log(`[INSIGHTS] ${result.action} for ${normalized.slice(-4)} (count: ${result.call_count || "?"})`);

    if (result.call_count && result.call_count >= 5 && result.call_count % 5 === 0) {
      compactCallerHistoryAsync(normalized);
    }
  } catch (error) {
    console.error("[INSIGHTS] Failed to update caller insights:", error);
  }
}

async function compactCallerHistoryAsync(phone: string): Promise<void> {
  const authHeader = getZoAuthHeader();
  if (!authHeader) return;

  try {
    const script = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    rows = con.execute('''
        SELECT started_at, duration_seconds, topics_discussed, stage_assessed, raw_data
        FROM calls
        WHERE phone_number = ?
        ORDER BY started_at ASC
    ''', [data['phone']]).fetchall()
    calls = []
    for r in rows:
        raw = json.loads(r[4]) if r[4] else {}
        msg = raw.get('message', {})
        summary = msg.get('analysis', {}).get('summary', '')
        if not summary:
            transcript = msg.get('artifact', {}).get('transcript', '') or msg.get('transcript', '')
            summary = transcript[:300] if transcript else ''
        calls.append({
            "date": str(r[0])[:10] if r[0] else "unknown",
            "duration_min": round((r[1] or 0) / 60, 1),
            "topics": r[2] or "",
            "stage": r[3] or "",
            "summary": summary[:300]
        })
    print(json.dumps(calls))
except:
    print(json.dumps([]))
con.close()
`;
    const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe" });
    proc.stdin.write(JSON.stringify({ db: DB_PATH, phone }));
    proc.stdin.end();
    const output = await new Response(proc.stdout).text();
    await proc.exited;

    const calls = JSON.parse(output.trim());
    if (calls.length < 3) return;

    const callSummaries = calls.map((c: any) =>
      `${c.date} (${c.duration_min}min): ${c.topics ? `[${c.topics}]` : ""} ${c.summary}`
    ).join("\n");

    const resp = await fetch("https://api.zo.computer/zo/ask", {
      method: "POST",
      headers: { authorization: authHeader, "content-type": "application/json" },
      body: JSON.stringify({
        input: `Synthesize this caller's career coaching call history into a concise profile (max 500 chars). Include: their career stage progression, recurring themes, what's working, what they're stuck on, and any personality notes relevant for a coach.

Call history (${calls.length} calls):
${callSummaries}

Return ONLY the synthesis paragraph, nothing else.`
      })
    });

    if (!resp.ok) return;
    const body = await resp.json().catch(() => null);
    const synthesis = (body as any)?.output || "";
    if (!synthesis || synthesis.length < 20) return;

    const updateScript = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    con.execute('''UPDATE caller_insights SET notes = ? WHERE phone_number = ?''',
        [data['notes'], data['phone']])
    print("COMPACTED")
except Exception as e:
    print(f"ERROR: {e}")
con.close()
`;
    const updateProc = Bun.spawn(["python3", "-c", updateScript], { stdin: "pipe", stdout: "pipe" });
    updateProc.stdin.write(JSON.stringify({ db: DB_PATH, phone, notes: synthesis.substring(0, 500) }));
    updateProc.stdin.end();
    const updateOutput = await new Response(updateProc.stdout).text();
    await updateProc.exited;
    console.log(`[COMPACTION] ${phone.slice(-4)}: ${updateOutput.trim()}`);

    if (calls.length > 2) {
      const archiveScript = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    con.execute('''
        UPDATE calls SET raw_data = NULL
        WHERE phone_number = ? AND raw_data IS NOT NULL
        AND id NOT IN (
            SELECT id FROM calls WHERE phone_number = ?
            ORDER BY started_at DESC LIMIT 2
        )
    ''', [data['phone'], data['phone']])
    affected = con.execute('SELECT changes()').fetchone()[0]
    print(f"ARCHIVED {affected} calls")
except Exception as e:
    print(f"ERROR: {e}")
con.close()
`;
      const archiveProc = Bun.spawn(["python3", "-c", archiveScript], { stdin: "pipe", stdout: "pipe" });
      archiveProc.stdin.write(JSON.stringify({ db: DB_PATH, phone }));
      archiveProc.stdin.end();
      const archiveOutput = await new Response(archiveProc.stdout).text();
      await archiveProc.exited;
      console.log(`[ARCHIVE] ${phone.slice(-4)}: ${archiveOutput.trim()}`);
    }
  } catch (error) {
    console.error("[COMPACTION] Failed:", error);
  }
}

// ── Caller History for System Prompt ──

async function getCallerCallHistory(phone: string): Promise<string> {
  const normalized = normalizePhone(phone);
  if (!normalized) return "";

  try {
    const script = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    rows = con.execute('''
        SELECT started_at, duration_seconds, topics_discussed, stage_assessed, raw_data
        FROM calls
        WHERE phone_number = ?
        ORDER BY started_at DESC LIMIT 5
    ''', [data['phone']]).fetchall()
    calls = []
    for r in rows:
        raw = json.loads(r[4]) if r[4] else {}
        msg = raw.get('message', {})
        summary = msg.get('analysis', {}).get('summary', '')
        if not summary:
            t = msg.get('artifact', {}).get('transcript', '') or msg.get('transcript', '')
            summary = t[:200] if t else ''
        calls.append({
            "date": str(r[0])[:10] if r[0] else "unknown",
            "duration_min": round((r[1] or 0) / 60, 1),
            "topics": r[2] or "",
            "summary": summary[:200]
        })
    print(json.dumps(calls))
except:
    print(json.dumps([]))
con.close()
`;
    const proc = Bun.spawn(["python3", "-c", script], { stdin: "pipe", stdout: "pipe" });
    proc.stdin.write(JSON.stringify({ db: DB_PATH, phone: normalized }));
    proc.stdin.end();
    const output = await new Response(proc.stdout).text();
    await proc.exited;

    const calls = JSON.parse(output.trim());
    if (calls.length === 0) return "";

    const bullets = calls.map((c: any) =>
      `- ${c.date} (${c.duration_min}min)${c.topics ? ` [${c.topics}]` : ""}: ${c.summary}`
    ).join("\n");

    return bullets;
  } catch {
    return "";
  }
}

// ── Call Logging ──

async function logCall(data: any): Promise<void> {
  try {
    const callId = data.message?.call?.id || generateUUID();
    const now = new Date().toISOString();
    const duration = Math.round(data.message?.durationSeconds || 0);
    const callerPhone = data.message?.call?.customer?.number || "";

    const insertScript = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    con.execute('DELETE FROM calls WHERE id = ?', [data['id']])
except:
    pass
con.execute('''
  INSERT INTO calls (id, phone_number, started_at, ended_at, duration_seconds, topics_discussed, stage_assessed, escalation_requested, raw_data)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', [data['id'], data['phone_number'], data['started_at'], data['ended_at'], data['duration'], data['topics'], data['stage'], data['escalation'], data['raw']])
con.close()
print("SUCCESS")
`;

    const callData = JSON.stringify({
      db: DB_PATH,
      id: callId,
      phone_number: callerPhone,
      started_at: data.message?.startedAt || now,
      ended_at: data.message?.endedAt || now,
      duration,
      topics: null,
      stage: null,
      escalation: false,
      raw: JSON.stringify(data)
    });

    const proc = Bun.spawn(["python3", "-c", insertScript], { stdin: "pipe", stdout: "pipe" });
    proc.stdin.write(callData);
    proc.stdin.end();
    await proc.exited;

    const transcript = data.message?.artifact?.transcript || data.message?.transcript || "";
    if (transcript) classifyTopicsAsync(callId, transcript);

    console.log(`Call logged: ${callId.substring(0, 8)} (${duration}s)`);
  } catch (error) {
    console.error("Failed to log call:", error);
  }
}

// ── Server ──

initDb();

Bun.serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);

    if (req.method === "GET" && url.pathname === "/health") {
      return new Response(JSON.stringify({
        status: "ok",
        service: "career-coaching-hotline",
        identity: "Zozie",
        port: PORT,
        free_tier_seconds: FREE_TIER_SECONDS,
        tools: ["lookupCaller", "assessCareerStage", "getCareerRecommendations", "explainCareerConcept", "requestCareerSession", "collectFeedback", "analyzeResumeBullet", "diagnoseSearchStrategy", "scoreResumeSection", "pullCallerResume", "referToCareerspan"]
      }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    if (req.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    try {
      if (WEBHOOK_SECRET) {
        const authHeader = req.headers.get("x-vapi-secret") || "";
        if (authHeader !== WEBHOOK_SECRET) {
          console.warn("Webhook auth failed — invalid secret");
          return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
        }
      }

      const rawBody = await req.text();
      const data = JSON.parse(rawBody);
      const messageType = data.message?.type || data.type;

      const logEntry = {
        ts: new Date().toISOString(),
        method: req.method,
        path: url.pathname,
        messageType,
        keys: Object.keys(data),
        messageKeys: data.message ? Object.keys(data.message) : [],
        callId: data.message?.call?.id || data.call?.id || "none",
        phoneNumber: data.message?.call?.customer?.number || "none"
      };
      console.log(`[VAPI] ${JSON.stringify(logEntry)}`);

      if (messageType === "assistant-request") {
        console.log("Assistant request received");

        const callerPhone = data.message?.call?.customer?.number || "";
        let balanceContext = "";
        if (callerPhone) {
          const balance = await getCallerBalance(callerPhone);
          if (!balance.totalAvailable || balance.totalAvailable <= 0) {
            balanceContext = `\n\n---\n\n## IMPORTANT: This caller has NO remaining time.\n\nTheir free 15-minute session is used up and they have no purchased credits. Greet them warmly, let them know their free session is used up, and direct them to ${PURCHASE_URL} to get more coaching time. Be brief and friendly — don't make them feel bad. If they have a quick question (under 1 minute), you can answer it, but don't start a full coaching session.`;
          } else if (balance.freeRemaining > 0 && balance.freeRemaining < 120) {
            balanceContext = `\n\n---\n\n## Note: This caller has less than 2 minutes of free time remaining (${Math.round(balance.freeRemaining / 60)} min). Mention this naturally near the end of your response window so they can wrap up or purchase more time at ${PURCHASE_URL}.`;
          }
        }

        const response = {
          assistant: {
            name: "Zozie (Career Coach)",
            firstMessage: "Hey — this is Zozie on the Careerspan Career Coaching Hotline. I'm an AI career coach built on a decade of real coaching expertise. This is a free resource to help you with whatever's going on in your career right now. If at any point you want deeper help, just say so and I'll connect you with the Careerspan team. So — what's going on?",

            transcriber: {
              provider: "deepgram",
              keywords: [
                "Careerspan:10",
                "Zozie:10",
                "resume:8",
                "LinkedIn:8",
                "coverletter:8",
                "interview:8",
                "ATS:8",
                "networking:8",
                "jobsearch:8",
                "career:8",
                "Vrijen:10",
                "AISS:8",
                "recruiter:6",
                "salary:6",
                "negotiation:6"
              ]
            },

            model: {
              provider: "anthropic",
              model: "claude-haiku-4-5-20251001",
              messages: [{ role: "system", content: systemPrompt + balanceContext }],
              tools: toolSpecsRaw.tools
            },

            voice: {
              provider: "11labs",
              voiceId: VOICE_ID,
              model: "eleven_flash_v2_5",
              stability: 0.45,
              similarityBoost: 0.75,
              style: 0.65,
              useSpeakerBoost: true,
              optimizeStreamingLatency: 4,
              chunkPlan: {
                enabled: true,
                minCharacters: 20,
                punctuationBoundaries: [".", "!", "?", ",", ";", ":"]
              }
            },

            startSpeakingPlan: {
              waitSeconds: 0.4,
              smartEndpointingEnabled: true,
              transcriptionEndpointingPlan: {
                onPunctuationSeconds: 0.1,
                onNoPunctuationSeconds: 0.8,
                onNumberSeconds: 0.4
              }
            },

            stopSpeakingPlan: {
              numWords: 0,
              voiceSeconds: 0.2,
              backoffSeconds: 1.0
            },

            backchannelingEnabled: true,
            backgroundSound: "off",

            voicemailMessage: "Hey, this is Zozie from the Careerspan Career Coaching Hotline. Leave a message or call back anytime.",
            endCallMessage: "Good luck out there. You've got this.",
            endCallPhrases: ["goodbye", "bye", "thanks", "talk to you later", "that's all", "I'm good"],

            responseDelaySeconds: 0.1,
            silenceTimeoutSeconds: 15,
            maxDurationSeconds: 1800,

            analysisPlan: {
              summaryPrompt: "Summarize this career coaching call in 2-3 sentences. Focus on: the caller's career situation, what coaching Zozie provided, whether the caller is within their free tier balance, and whether they left with actionable guidance.",
              structuredDataPrompt: "Extract the following from this career coaching call transcript. Be precise — if something wasn't discussed, leave it null.",
              structuredDataSchema: {
                type: "object",
                properties: {
                  call_category: {
                    type: "string",
                    enum: ["resume_review", "interview_prep", "career_transition", "job_search_strategy", "salary_negotiation", "networking", "general_coaching", "unclear"],
                    description: "Primary category of the coaching session"
                  },
                  caller_profession: {
                    type: "string",
                    description: "Caller's current role or industry if mentioned"
                  },
                  caller_experience_level: {
                    type: "string",
                    enum: ["early_career", "mid_career", "senior", "executive", "career_changer", "unknown"],
                    description: "Approximate career stage"
                  },
                  primary_challenge: {
                    type: "string",
                    description: "The main career challenge or question"
                  },
                  coaching_techniques_used: {
                    type: "array",
                    items: { type: "string" },
                    description: "Coaching approaches used (active listening, reframing, goal-setting, etc.)"
                  },
                  had_clear_next_step: {
                    type: "boolean",
                    description: "Did the caller leave with a concrete action item?"
                  },
                  balance_warning_triggered: {
                    type: "boolean",
                    description: "Was the caller notified about running low on free tier minutes?"
                  },
                  returning_caller: {
                    type: "boolean",
                    description: "Did the caller indicate they've called before?"
                  },
                  escalation_requested: {
                    type: "boolean",
                    description: "Did the caller ask for human follow-up?"
                  },
                  interruption_issues: {
                    type: "boolean",
                    description: "Were there noticeable turn-taking problems?"
                  }
                },
                required: ["call_category", "primary_challenge", "had_clear_next_step", "interruption_issues"]
              },
              successEvaluationPrompt: "Evaluate this career coaching call. A successful call means: (1) Zozie correctly identified the caller's coaching need, (2) provided actionable career guidance, (3) maintained a warm, professional coaching tone, (4) ended with a clear next step, (5) did NOT promise to connect with a human coach or offer services outside scope, (6) handled balance/timer notifications gracefully if applicable. Rate on a 1-10 scale. Deduct points for: generic advice, interruptions, overstepping scope, failing to establish rapport, or ending abruptly without a next step.",
              successEvaluationRubric: "NumericScale"
            },

            serverMessages: ["end-of-call-report", "tool-calls"]
          }
        };

        return new Response(JSON.stringify(response), {
          status: 200, headers: { "Content-Type": "application/json" }
        });
      }

      if (messageType === "tool-calls") {
        console.log("Tool-calls webhook received");
        const toolCalls = data.message?.toolCalls || data.message?.toolCallList || [];
        const vapiCallId = data.message?.call?.id || "current";
        const results = [];

        for (const toolCall of toolCalls) {
          const toolName = toolCall.function?.name;
          const rawParams = toolCall.function?.arguments || "{}";
          let params: any;
          try {
            params = typeof rawParams === "string" ? JSON.parse(rawParams) : rawParams;
          } catch {
            results.push({
              name: toolName,
              toolCallId: toolCall.id,
              result: JSON.stringify({ error: "Invalid JSON in tool arguments" })
            });
            continue;
          }
          const callId = toolCall.id;

          console.log(`Processing tool: ${toolName}`, JSON.stringify(params));

          let result;

          switch (toolName) {
            case "assessCareerStage":
              result = await assessCareerStage(params);
              break;
            case "getCareerRecommendations":
              result = await getCareerRecommendations(params);
              break;
            case "explainCareerConcept":
              result = await explainCareerConcept(params);
              break;
            case "requestCareerSession":
              result = await requestCareerSession(params, vapiCallId);
              break;
            case "lookupCaller":
              result = await lookupCaller(params);
              break;
            case "collectFeedback":
              result = await collectFeedback(params, vapiCallId);
              break;
            case "analyzeResumeBullet":
              result = await analyzeResumeBullet(params);
              break;
            case "diagnoseSearchStrategy":
              result = await diagnoseSearchStrategy(params);
              break;
            case "scoreResumeSection":
              result = await scoreResumeSection(params);
              break;
            case "pullCallerResume":
              result = await pullCallerResume(params);
              break;
            case "referToCareerspan":
              result = await referToCareerspan(params);
              break;
            default:
              result = {
                error: `Unknown tool: ${toolName}`,
                available_tools: ["assessCareerStage", "getCareerRecommendations", "explainCareerConcept", "requestCareerSession", "lookupCaller", "collectFeedback", "analyzeResumeBullet", "diagnoseSearchStrategy", "scoreResumeSection", "pullCallerResume", "referToCareerspan"]
              };
          }

          results.push({
            name: toolName,
            toolCallId: callId,
            result: JSON.stringify(result)
          });
        }

        console.log("Returning tool results:", results.length);
        return new Response(JSON.stringify({ results }), {
          status: 200, headers: { "Content-Type": "application/json" }
        });
      }

      if (messageType === "end-of-call-report") {
        console.log("End-of-call report received");
        await logCall(data);

        const call = data.message?.call || data.call || {};
        const callId = call.id || "";
        const durationSeconds = Math.round(data.message?.durationSeconds || 0);
        const endedReason = data.message?.endedReason || call.endedReason || "unknown";
        const transcript = data.message?.artifact?.transcript || data.message?.transcript || "";
        const summary = data.message?.analysis?.summary || "";

        const callerPhone = call.customer?.number || "";
        if (callerPhone && durationSeconds > 0) {
          await recordCallDuration(callerPhone, durationSeconds);
        }

        // Link feedback and escalation records from "current" to actual call_id
        if (callId) {
          try {
            const linkScript = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    con.execute("UPDATE feedback SET call_id = ? WHERE call_id = 'current'", [data['call_id']])
    con.execute("UPDATE escalations SET call_id = ? WHERE call_id = 'current'", [data['call_id']])
except:
    pass
con.close()
`;
            const linkProc = Bun.spawn(["python3", "-c", linkScript], { stdin: "pipe", stdout: "pipe" });
            linkProc.stdin.write(JSON.stringify({ db: DB_PATH, call_id: callId }));
            linkProc.stdin.end();
            await linkProc.exited;
          } catch (linkError) {
            console.error("Failed to link records to call:", linkError);
          }
        }

        const durationMin = Math.floor(durationSeconds / 60);
        const durationSec = durationSeconds % 60;
        const snippet = summary || (transcript ? transcript.substring(0, 200) + (transcript.length > 200 ? "..." : "") : "No transcript available");

        let balanceNote = "";
        if (callerPhone) {
          const balance = await getCallerBalance(callerPhone);
          balanceNote = `\n• Balance: ${Math.round(balance.totalAvailable / 60)}min remaining`;
        }

        let returningNote = "";
        if (callerPhone) {
          try {
            const insightScript = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    row = con.execute('SELECT call_count FROM caller_insights WHERE phone_number = ?', [data['phone']]).fetchone()
    print(json.dumps(row[0] if row else None))
except:
    print(json.dumps(None))
con.close()
`;
            const insightProc = Bun.spawn(["python3", "-c", insightScript], { stdin: "pipe", stdout: "pipe" });
            insightProc.stdin.write(JSON.stringify({ db: DB_PATH, phone: normalizePhone(callerPhone) }));
            insightProc.stdin.end();
            const insightOutput = await new Response(insightProc.stdout).text();
            await insightProc.exited;
            const callCount = JSON.parse(insightOutput.trim());
            if (callCount && callCount > 1) {
              returningNote = `\n• Returning caller (call #${callCount})`;
            }
          } catch { /* non-critical */ }
        }

        notifyV(`📞 Career Hotline call ended (${durationMin}m ${durationSec}s)\n• Reason: ${endedReason}${returningNote}${balanceNote}\n• Summary: ${snippet}`);

        return new Response(JSON.stringify({ success: true }), {
          status: 200, headers: { "Content-Type": "application/json" }
        });
      }

      console.log(`Unknown message type: ${messageType}`);
      return new Response(JSON.stringify({ success: true }), {
        status: 200, headers: { "Content-Type": "application/json" }
      });

    } catch (error: any) {
      console.error("Webhook error:", error);
      return new Response(JSON.stringify({ error: "Internal server error", message: error.message }), {
        status: 500, headers: { "Content-Type": "application/json" }
      });
    }
  }
});

console.log(`Career Coaching Hotline (Zozie) webhook running on port ${PORT}`);
console.log(`Database: ${DB_PATH}`);
console.log(`Knowledge base: ${KNOWLEDGE_BASE}`);
console.log(`Voice ID: ${VOICE_ID ? VOICE_ID.substring(0, 8) + "..." : "NOT SET"}`);
console.log(`Webhook auth: ${WEBHOOK_SECRET ? "ENABLED" : "DISABLED"}`);
console.log(`Free tier: ${FREE_TIER_SECONDS / 60} minutes per phone number`);
console.log(`Purchase URL: ${PURCHASE_URL}`);
console.log(`Tools: 11 (6 original + 5 new)`);
