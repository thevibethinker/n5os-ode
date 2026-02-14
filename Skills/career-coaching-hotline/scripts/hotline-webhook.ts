#!/usr/bin/env bun

import { readFileSync, existsSync, readdirSync, statSync } from "fs";
import { generateUUID } from "./call-logger";

const PORT = parseInt(process.env.CAREER_HOTLINE_PORT || "8848");
const DB_PATH = "/home/workspace/Datasets/career-hotline-calls/data.duckdb";
const KNOWLEDGE_BASE = "/home/workspace/Knowledge/career-coaching-hotline";
const VOICE_ID = process.env.CAREER_HOTLINE_VOICE_ID || "";
const WEBHOOK_SECRET = process.env.CAREER_HOTLINE_SECRET || "";
const VERBOSITY = process.env.CAREER_HOTLINE_VERBOSITY || "normal";
const BOOKING_LINK = process.env.CAREER_HOTLINE_BOOKING_LINK || "https://mycareerspan.com/book";

const systemPromptTemplate = readFileSync(
  "/home/workspace/N5/builds/career-coaching-hotline/artifacts/career-coach-system-prompt.md",
  "utf-8"
).replace(/^---[\s\S]*?---\s*/, "");

const systemPromptBase = systemPromptTemplate;

const conceptMapRaw: Record<string, string> = JSON.parse(
  readFileSync(
    "/home/workspace/N5/builds/career-coaching-hotline/artifacts/concept-map.json",
    "utf-8"
  )
);

const careerStagesDoc = readFileSync(
  "/home/workspace/N5/builds/career-coaching-hotline/artifacts/career-stages.md",
  "utf-8"
).replace(/^---[\s\S]*?---\s*/, "");

const diagnosticQuestionsDoc = readFileSync(
  "/home/workspace/N5/builds/career-coaching-hotline/artifacts/diagnostic-questions.md",
  "utf-8"
).replace(/^---[\s\S]*?---\s*/, "");

const valuePropTreeDoc = readFileSync(
  "/home/workspace/N5/builds/career-coaching-hotline/artifacts/value-prop-tree.md",
  "utf-8"
).replace(/^---[\s\S]*?---\s*/, "");

const toolSpecsRaw = JSON.parse(
  readFileSync(
    "/home/workspace/N5/builds/career-coaching-hotline/artifacts/tool-specs.json",
    "utf-8"
  )
);

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
    return `\n\n---\n\n## Recent Caller Topics (Last ${summaries.length} Calls 1min+)\n\nThis is what callers have been asking about recently. Use this awareness to anticipate needs but don't reference these calls directly.\n\n${bullets}\n`;
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

async function initDb() {
  try {
    const proc = Bun.spawn(["duckdb", DB_PATH, "-c", `
      CREATE TABLE IF NOT EXISTS calls (
        id VARCHAR PRIMARY KEY,
        started_at TIMESTAMP,
        ended_at TIMESTAMP,
        duration_seconds INTEGER,
        topics_discussed TEXT,
        stage_assessed VARCHAR,
        escalation_requested BOOLEAN,
        raw_data JSON
      );
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
        helpful BOOLEAN,
        rating INTEGER,
        feedback_text TEXT,
        would_recommend BOOLEAN,
        created_at TIMESTAMP
      );
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
    `], { stdout: "pipe", stderr: "pipe" });
    await proc.exited;
    console.log("Database initialized successfully");
  } catch (error) {
    console.error("Failed to initialize database:", error);
  }
}

function notifyV(message: string): void {
  const token = process.env.ZO_CLIENT_IDENTITY_TOKEN;
  if (!token) {
    console.error("ZO_CLIENT_IDENTITY_TOKEN not set — cannot send SMS");
    return;
  }
  const authHeader = token.startsWith("Bearer") ? token : `Bearer ${token}`;
  fetch("https://api.zo.computer/zo/ask", {
    method: "POST",
    headers: { authorization: authHeader, "content-type": "application/json" },
    body: JSON.stringify({
      input: `SYSTEM NOTIFICATION RELAY\n\nSend V this SMS (using send_sms_to_user):\n\n${message}\n\nJust send the SMS. No commentary.`
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

  const situationLower = current_situation.toLowerCase();
  const effortsLower = efforts_so_far.toLowerCase();
  const outcomeLower = desired_outcome.toLowerCase();

  let primary_stage = "groundwork";
  let secondary_concerns: string[] = [];
  let pain_points: string[] = [];
  let effort_level = "moderate";
  let calibration_needed = false;

  // Stage classification based on situation signals
  if (/student|new grad|just starting|don't have experience|first job|no experience/i.test(situationLower)) {
    primary_stage = "groundwork";
  } else if (/applying|working on resume|not hearing back|need better materials|updating resume|my resume/i.test(situationLower)) {
    primary_stage = "materials";
  } else if (/been applying for months|lots of applications|not getting traction|applying everywhere|50\+ apps/i.test(situationLower)) {
    primary_stage = "outreach";
  } else if (/getting interviews|interviewing now|final rounds|have a few conversations|interviews but no offers/i.test(situationLower)) {
    primary_stage = "performance";
  } else if (/laid off|switching careers|career change|been out of work|trying to break in|new industry|different field/i.test(situationLower)) {
    primary_stage = "transition";
  } else if (/employed but|thinking about|next move|want something better/i.test(situationLower)) {
    primary_stage = "groundwork";
    secondary_concerns.push("outreach");
  }

  // Pain point detection
  if (/not tailoring|same resume|one resume/i.test(effortsLower)) pain_points.push("not_tailoring_resume");
  if (/no networking|haven't networked|don't know anyone/i.test(effortsLower)) pain_points.push("no_networking");
  if (/freeze|nervous|anxiety|scared/i.test(effortsLower)) pain_points.push("interview_anxiety");
  if (/don't know what|unclear|not sure what/i.test(outcomeLower)) {
    pain_points.push("career_direction_unclear");
    if (primary_stage !== "transition") primary_stage = "groundwork";
  }
  if (/haven't really started|just thinking|not much/i.test(effortsLower)) {
    effort_level = "minimal";
    pain_points.push("not_started");
  }
  if (/tried everything|nothing works|months|frustrated/i.test(effortsLower)) {
    effort_level = "high";
    pain_points.push("strategy_fatigue");
  }
  if (/chatgpt|ai|automated/i.test(effortsLower)) pain_points.push("over_relying_on_ai_tools");
  if (/job boards only|indeed|linkedin apply/i.test(effortsLower)) pain_points.push("single_channel_dependency");

  // Calibration check
  if (/vp|director|senior|executive/i.test(outcomeLower) && /entry|junior|first|student/i.test(situationLower)) {
    calibration_needed = true;
  }
  if (/six figures|100k|immediately/i.test(outcomeLower) && /career change|new industry/i.test(situationLower)) {
    calibration_needed = true;
  }

  // Secondary concerns based on efforts
  if (primary_stage !== "materials" && /resume|cv|cover letter/i.test(effortsLower)) {
    secondary_concerns.push("materials");
  }
  if (primary_stage !== "outreach" && /networking|reaching out/i.test(effortsLower)) {
    secondary_concerns.push("outreach");
  }

  const urgency = urgency_signals || "medium";

  return {
    primary_stage,
    secondary_concerns: [...new Set(secondary_concerns)].slice(0, 2),
    pain_points: [...new Set(pain_points)],
    urgency,
    effort_level,
    calibration_needed,
    coaching_note: calibration_needed
      ? "Expectations may need recalibration — be direct but empathetic"
      : `Focus on ${primary_stage} stage priorities`
  };
}

async function getCareerRecommendations(params: {
  primary_stage: string;
  pain_points: string[];
  urgency: string;
}): Promise<object> {
  const { primary_stage, pain_points, urgency } = params;

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
        "Build a story bank: 8-10 stories in START format (Situation, Task, Action, Result, Takeaway)",
        "Practice your 'tell me about yourself' — 90 seconds, three acts: past, present, future",
        "Research the interview format at your target companies before you walk in",
        "After every interview, send a specific thank-you referencing something discussed"
      ],
      timeframe: "1 week intensive prep",
      priority: "Story bank development and delivery practice"
    },
    transition: {
      actions: [
        "Map your transferable skills — what you've done that applies regardless of industry",
        "Build your bridge narrative: 'I went from X to Y because Z, which means I can do W for you'",
        "Find 5 people who've made a similar transition — study their path",
        "Don't apologize for the pivot — own it as a strategic choice"
      ],
      timeframe: "4-6 weeks of active repositioning",
      priority: "Bridge narrative construction"
    }
  };

  const stageRecs = recommendations[primary_stage] || recommendations.groundwork;

  let urgencyAdjustment = "";
  if (urgency === "crisis") {
    urgencyAdjustment = "Given the urgency: focus on the first action item only this week. Stabilize before optimizing.";
  } else if (urgency === "high") {
    urgencyAdjustment = "With your timeline, prioritize items 1 and 2 this week. The others can follow.";
  }

  let painPointAdvice: string[] = [];
  if (pain_points.includes("not_tailoring_resume")) {
    painPointAdvice.push("Critical: stop sending the same resume everywhere. Even 15 minutes of customization per application dramatically improves your odds.");
  }
  if (pain_points.includes("no_networking")) {
    painPointAdvice.push("Networking isn't optional — it's one of 4 essential levers. Start with 3 outreach messages this week.");
  }
  if (pain_points.includes("interview_anxiety")) {
    painPointAdvice.push("Interview anxiety is normal. The fix is over-preparation on your stories, not relaxation techniques.");
  }
  if (pain_points.includes("over_relying_on_ai_tools")) {
    painPointAdvice.push("AI tools are great for drafting, but they create sameness. Your competitive edge is specificity — your stories, your numbers, your context.");
  }

  return {
    stage: primary_stage,
    timeframe: stageRecs.timeframe,
    priority: stageRecs.priority,
    actions: stageRecs.actions,
    urgency_note: urgencyAdjustment || null,
    pain_point_advice: painPointAdvice.length > 0 ? painPointAdvice : null,
    careerspan_hint: `When ready to go deeper on ${stageRecs.priority.toLowerCase()}, Careerspan sessions provide hands-on coaching with V.`
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
      let truncated = content.substring(0, 1200);
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

async function requestCareerSession(params: {
  name: string;
  contact: string;
  career_stage: string;
  reason: string;
  pain_points?: string[];
}): Promise<object> {
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
      call_id: "current",
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
      message: `Got it, ${name}. I've logged your request and V will reach out soon. You can also book directly at: ${BOOKING_LINK}`,
      escalation_id: escalationId.substring(0, 8),
      booking_link: BOOKING_LINK
    };
  } catch (error) {
    console.error("Error logging session request:", error);
    return {
      error: "Failed to log session request",
      fallback: `You can reach V directly at mycareerspan.com or on LinkedIn as Vrijen Attawar`
    };
  }
}

async function lookupCaller(params: { phone_number: string }): Promise<object> {
  const { phone_number } = params;

  if (!phone_number) {
    return { found: false, reason: "No phone number provided" };
  }

  try {
    const lookupScript = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
try:
    rows = con.execute('''
        SELECT caller_name, career_stage, primary_challenge, specific_questions, industry_targets, submitted_at
        FROM caller_lookup
        WHERE phone_number = ?
        ORDER BY submitted_at DESC LIMIT 1
    ''', [data['phone']]).fetchall()
except:
    rows = []

insights = []
try:
    insights = con.execute('''
        SELECT call_count, last_seen, last_stage, topics_history
        FROM caller_insights
        WHERE phone_number = ?
        ORDER BY last_seen DESC LIMIT 1
    ''', [data['phone']]).fetchall()
except:
    pass

con.close()

if rows:
    r = rows[0]
    result = {
        "found": True,
        "caller_name": r[0],
        "career_stage": r[1],
        "primary_challenge": r[2],
        "specific_questions": r[3],
        "industry_targets": r[4],
        "submitted_at": str(r[5]) if r[5] else None,
        "returning_caller": len(insights) > 0 and insights[0][0] > 1 if insights else False,
        "previous_calls": insights[0][0] if insights else 0
    }
else:
    result = {
        "found": False,
        "returning_caller": len(insights) > 0 and insights[0][0] > 0 if insights else False,
        "previous_calls": insights[0][0] if insights else 0,
        "last_stage": insights[0][2] if insights else None
    }
print(json.dumps(result))
`;

    const proc = Bun.spawn(["python3", "-c", lookupScript], { stdin: "pipe", stdout: "pipe", stderr: "pipe" });
    proc.stdin.write(JSON.stringify({ db: DB_PATH, phone: phone_number }));
    proc.stdin.end();
    const result = await new Response(proc.stdout).text();
    await proc.exited;

    try {
      return JSON.parse(result.trim());
    } catch {
      return { found: false, reason: "Lookup failed" };
    }
  } catch (error) {
    console.error("Error in lookupCaller:", error);
    return { found: false, reason: "Lookup error" };
  }
}

async function collectFeedback(params: {
  helpful: boolean;
  rating?: number;
  feedback_text?: string;
  would_recommend?: boolean;
}): Promise<object> {
  const { helpful, rating, feedback_text, would_recommend } = params;

  try {
    const feedbackId = generateUUID();
    const now = new Date().toISOString();

    const insertScript = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
con.execute('''
  INSERT INTO feedback (id, call_id, helpful, rating, feedback_text, would_recommend, created_at)
  VALUES (?, ?, ?, ?, ?, ?, ?)
''', [data['id'], data['call_id'], data['helpful'], data['rating'], data['feedback_text'], data['would_recommend'], data['created_at']])
con.close()
print("SUCCESS")
`;

    const fbData = JSON.stringify({
      db: DB_PATH,
      id: feedbackId,
      call_id: "current",
      helpful, rating: rating || null,
      feedback_text: feedback_text || null,
      would_recommend: would_recommend ?? null,
      created_at: now
    });

    const proc = Bun.spawn(["python3", "-c", insertScript], { stdin: "pipe", stdout: "pipe" });
    proc.stdin.write(fbData);
    proc.stdin.end();
    await proc.exited;

    const parts: string[] = [];
    if (helpful) parts.push("glad it was helpful");
    if (rating) parts.push(`rated ${rating}/5`);
    if (feedback_text) parts.push("noted your feedback");
    if (would_recommend) parts.push("appreciate the recommendation");

    return {
      success: true,
      message: parts.length > 0 ? `${parts.join(", ")}. Thanks!` : "Appreciate it!"
    };
  } catch (error) {
    console.error("Error logging feedback:", error);
    return { success: true, message: "Thanks for the feedback." };
  }
}

const TOPIC_TAXONOMY = [
  "resume", "cover_letter", "linkedin", "job_search", "networking",
  "interview_prep", "career_pivot", "salary_negotiation", "self_reflection",
  "ats_systems", "materials_review", "career_direction", "internship",
  "groundwork", "outreach", "performance", "transition", "escalation",
  "careerspan_inquiry", "general"
];

function classifyTopicsAsync(callId: string, transcript: string): void {
  if (!transcript || transcript.length < 50) return;
  const token = process.env.ZO_CLIENT_IDENTITY_TOKEN;
  if (!token) return;
  const authHeader = token.startsWith("Bearer") ? token : `Bearer ${token}`;
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

async function logCall(data: any): Promise<void> {
  try {
    const callId = data.message?.call?.id || generateUUID();
    const now = new Date().toISOString();
    const duration = Math.round(data.message?.durationSeconds || 0);

    const insertScript = `
import duckdb, json, sys
data = json.loads(sys.stdin.read())
con = duckdb.connect(data['db'])
con.execute('''
  INSERT OR REPLACE INTO calls (id, started_at, ended_at, duration_seconds, topics_discussed, stage_assessed, escalation_requested, raw_data)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', [data['id'], data['started_at'], data['ended_at'], data['duration'], data['topics'], data['stage'], data['escalation'], data['raw']])
con.close()
print("SUCCESS")
`;

    const callData = JSON.stringify({
      db: DB_PATH,
      id: callId,
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
      return new Response(JSON.stringify({ status: "ok", service: "career-coaching-hotline", port: PORT }), {
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

      const data = await req.json();
      const messageType = data.message?.type || data.type;

      if (messageType === "assistant-request") {
        console.log("Assistant request received");

        const response = {
          assistant: {
            name: "V (Career Coach)",
            firstMessage: "Hey — this is V on the Careerspan Career Coaching Hotline. I've been coaching professionals for over a decade, and this is a free resource to help you with whatever's going on in your career right now. If at any point you want deeper help, just say so and I'll connect you. So — what's going on?",

            transcriber: {
              provider: "deepgram",
              keywords: [
                "Careerspan:10",
                "resume:8",
                "LinkedIn:8",
                "cover letter:8",
                "interview:8",
                "ATS:8",
                "networking:8",
                "job search:8",
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
              messages: [{ role: "system", content: systemPrompt }],
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

            voicemailMessage: "Hey, this is V from the Careerspan Career Coaching Hotline. Leave a message or call back anytime.",
            endCallMessage: "Good luck out there. You've got this.",
            endCallPhrases: ["goodbye", "bye", "thanks", "talk to you later", "that's all", "I'm good"],

            responseDelaySeconds: 0.1,
            silenceTimeoutSeconds: 15,
            maxDurationSeconds: 1800,
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
        const results = [];

        for (const toolCall of toolCalls) {
          const toolName = toolCall.function?.name;
          const rawParams = toolCall.function?.arguments || "{}";
          const params = typeof rawParams === "string" ? JSON.parse(rawParams) : rawParams;
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
              result = await requestCareerSession(params);
              break;
            case "lookupCaller":
              result = await lookupCaller(params);
              break;
            case "collectFeedback":
              result = await collectFeedback(params);
              break;
            default:
              result = {
                error: `Unknown tool: ${toolName}`,
                available_tools: ["assessCareerStage", "getCareerRecommendations", "explainCareerConcept", "requestCareerSession", "lookupCaller", "collectFeedback"]
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

        const durationSeconds = Math.round(data.message?.durationSeconds || 0);
        const endedReason = data.message?.endedReason || data.message?.call?.endedReason || "unknown";
        const transcript = data.message?.artifact?.transcript || data.message?.transcript || "";
        const summary = data.message?.analysis?.summary || "";

        const durationMin = Math.floor(durationSeconds / 60);
        const durationSec = durationSeconds % 60;
        const snippet = summary || (transcript ? transcript.substring(0, 200) + (transcript.length > 200 ? "..." : "") : "No transcript available");

        notifyV(`📞 Career Hotline call ended (${durationMin}m ${durationSec}s)\n• Reason: ${endedReason}\n• Summary: ${snippet}`);

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

console.log(`Career Coaching Hotline webhook running on port ${PORT}`);
console.log(`Database: ${DB_PATH}`);
console.log(`Knowledge base: ${KNOWLEDGE_BASE}`);
console.log(`Voice ID: ${VOICE_ID ? VOICE_ID.substring(0, 8) + "..." : "NOT SET"}`);
console.log(`Webhook auth: ${WEBHOOK_SECRET ? "ENABLED" : "DISABLED"}`);
console.log(`Verbosity: ${VERBOSITY}`);
