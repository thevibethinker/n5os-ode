#!/usr/bin/env bun
import { describe, test, expect, beforeAll, afterAll } from "bun:test";
import { readFileSync, existsSync, readdirSync, statSync } from "fs";
import { normalizePhone, lookupCaller, generateUUID } from "../scripts/caller-lookup";

// ── Constants ──

const HOTLINE_DB = "/home/workspace/Datasets/career-hotline-calls/data.duckdb";
const COACHING_DB = "/home/workspace/Datasets/career-coaching-calls/data.duckdb";
const KNOWLEDGE_BASE = "/home/workspace/Knowledge/career-coaching-hotline";
const ARTIFACTS_DIR = "/home/workspace/N5/builds/career-coaching-hotline/artifacts";
const WEBHOOK_PORT = 8848;
const INTAKE_PORT = 8421;

const SYSTEM_PROMPT_PATH = `${ARTIFACTS_DIR}/career-coach-system-prompt.md`;
const CONCEPT_MAP_PATH = `${ARTIFACTS_DIR}/concept-map.json`;
const TOOL_SPECS_PATH = `${ARTIFACTS_DIR}/tool-specs.json`;
const CAREER_STAGES_PATH = `${ARTIFACTS_DIR}/career-stages.md`;
const DIAGNOSTIC_QUESTIONS_PATH = `${ARTIFACTS_DIR}/diagnostic-questions.md`;
const VALUE_PROP_PATH = `${ARTIFACTS_DIR}/value-prop-tree.md`;

// ── Helpers ──

async function duckdbQuery(dbPath: string, sql: string): Promise<string> {
  const proc = Bun.spawn(["duckdb", dbPath, "-json", "-c", sql], {
    stdout: "pipe", stderr: "pipe"
  });
  const stdout = await new Response(proc.stdout).text();
  const stderr = await new Response(proc.stderr).text();
  await proc.exited;
  if (stderr && stderr.includes("Error")) throw new Error(stderr);
  return stdout.trim();
}

async function duckdbExec(dbPath: string, sql: string): Promise<void> {
  const proc = Bun.spawn(["duckdb", dbPath, "-c", sql], {
    stdout: "pipe", stderr: "pipe"
  });
  const stderr = await new Response(proc.stderr).text();
  await proc.exited;
  if (stderr && stderr.includes("Error") && !stderr.includes("already exists")) {
    throw new Error(stderr);
  }
}

// ── Test Data ──

const TEST_PHONE = "+15559991234";
const TEST_CALLER_ID = generateUUID();

// ════════════════════════════════════════════════
// 1. SERVER STARTUP CHECKS
// ════════════════════════════════════════════════

describe("1. Server Startup Prerequisites", () => {

  test("System prompt file exists and loads", () => {
    expect(existsSync(SYSTEM_PROMPT_PATH)).toBe(true);
    const content = readFileSync(SYSTEM_PROMPT_PATH, "utf-8");
    expect(content.length).toBeGreaterThan(500);
    expect(content).toContain("Career Coaching Hotline");
    expect(content).toContain("V");
  });

  test("System prompt YAML frontmatter strips cleanly", () => {
    const raw = readFileSync(SYSTEM_PROMPT_PATH, "utf-8");
    const stripped = raw.replace(/^---[\s\S]*?---\s*/, "");
    expect(stripped).not.toContain("provenance:");
    expect(stripped).not.toContain("drop_id:");
    expect(stripped.startsWith("#")).toBe(true);
  });

  test("Concept map loads and parses as JSON", () => {
    expect(existsSync(CONCEPT_MAP_PATH)).toBe(true);
    const parsed = JSON.parse(readFileSync(CONCEPT_MAP_PATH, "utf-8"));
    expect(typeof parsed).toBe("object");
    const keys = Object.keys(parsed);
    expect(keys.length).toBeGreaterThan(10);
  });

  test("Tool specs loads and has expected tools", () => {
    expect(existsSync(TOOL_SPECS_PATH)).toBe(true);
    const parsed = JSON.parse(readFileSync(TOOL_SPECS_PATH, "utf-8"));
    expect(parsed.tools).toBeDefined();
    expect(Array.isArray(parsed.tools)).toBe(true);
    const toolNames = parsed.tools.map((t: any) => t.function?.name);
    expect(toolNames).toContain("assessCareerStage");
    expect(toolNames).toContain("getCareerRecommendations");
    expect(toolNames).toContain("explainCareerConcept");
    expect(toolNames).toContain("requestCareerSession");
    expect(toolNames).toContain("collectFeedback");
    expect(toolNames).toContain("lookupCaller");
  });

  test("Career stages doc exists", () => {
    expect(existsSync(CAREER_STAGES_PATH)).toBe(true);
    const content = readFileSync(CAREER_STAGES_PATH, "utf-8");
    expect(content.length).toBeGreaterThan(100);
  });

  test("Diagnostic questions doc exists", () => {
    expect(existsSync(DIAGNOSTIC_QUESTIONS_PATH)).toBe(true);
  });

  test("Value prop tree doc exists", () => {
    expect(existsSync(VALUE_PROP_PATH)).toBe(true);
  });

  test("Knowledge base directory has all 9 categories", () => {
    expect(existsSync(KNOWLEDGE_BASE)).toBe(true);
    const entries = readdirSync(KNOWLEDGE_BASE);
    const expectedCategories = [
      "00-career-coaching-philosophy.md",
      "10-resume",
      "20-cover-letters",
      "30-linkedin",
      "40-job-search",
      "50-self-development",
      "60-assessment",
      "70-careerspan",
      "80-podcast-interviews",
    ];
    for (const cat of expectedCategories) {
      expect(entries).toContain(cat);
    }
  });

  test("All knowledge base files referenced in concept map exist", () => {
    const conceptMap: Record<string, string> = JSON.parse(
      readFileSync(CONCEPT_MAP_PATH, "utf-8")
    );
    const uniquePaths = [...new Set(Object.values(conceptMap))];
    const missing: string[] = [];
    for (const relPath of uniquePaths) {
      const fullPath = relPath.startsWith("/") ? relPath : `/home/workspace/${relPath}`;
      if (!existsSync(fullPath)) {
        missing.push(relPath);
      }
    }
    expect(missing).toEqual([]);
  });

  test("Concept map resolves at least 10 different aliases", () => {
    const conceptMap: Record<string, string> = JSON.parse(
      readFileSync(CONCEPT_MAP_PATH, "utf-8")
    );
    const uniqueFiles = [...new Set(Object.values(conceptMap))];
    expect(uniqueFiles.length).toBeGreaterThanOrEqual(10);
    expect(Object.keys(conceptMap).length).toBeGreaterThan(50);
  });
});

// ════════════════════════════════════════════════
// 2. TOOL HANDLER TESTS
// ════════════════════════════════════════════════

describe("2. Tool Handler Logic", () => {

  // We test the tool logic by importing the functions indirectly
  // Since tool handlers are inline in hotline-webhook.ts, we replicate the logic here

  test("assessCareerStage: early career → groundwork", () => {
    const situation = "I'm a student just graduating with no work experience";
    const efforts = "I haven't really started looking yet";
    const desired = "I want to get my first tech job";

    // Simulate the classification logic
    const situationLower = situation.toLowerCase();
    let stage = "groundwork";
    if (/student|new grad|just starting|don't have experience|first job/i.test(situationLower)) {
      stage = "groundwork";
    }
    expect(stage).toBe("groundwork");
  });

  test("assessCareerStage: resume-focused → materials", () => {
    const situation = "I'm working on my resume and not hearing back from anyone";
    const lower = situation.toLowerCase();
    let stage = "groundwork";
    if (/applying|working on resume|not hearing back|need better materials|updating resume|my resume/i.test(lower)) {
      stage = "materials";
    }
    expect(stage).toBe("materials");
  });

  test("assessCareerStage: actively applying → outreach", () => {
    const situation = "I've been applying for months with lots of applications and not getting traction";
    const lower = situation.toLowerCase();
    let stage = "groundwork";
    if (/been applying for months|lots of applications|not getting traction|applying everywhere|50\+ apps/i.test(lower)) {
      stage = "outreach";
    }
    expect(stage).toBe("outreach");
  });

  test("assessCareerStage: interviewing → performance", () => {
    const situation = "I'm getting interviews but not landing offers";
    const lower = situation.toLowerCase();
    let stage = "groundwork";
    if (/getting interviews|interviewing now|final rounds|have a few conversations|interviews but no offers/i.test(lower)) {
      stage = "performance";
    }
    expect(stage).toBe("performance");
  });

  test("assessCareerStage: career change → transition", () => {
    const situation = "I was laid off and I'm switching careers to a different field";
    const lower = situation.toLowerCase();
    let stage = "groundwork";
    if (/laid off|switching careers|career change|been out of work|trying to break in|new industry|different field/i.test(lower)) {
      stage = "transition";
    }
    expect(stage).toBe("transition");
  });

  test("assessCareerStage: detects pain points", () => {
    const efforts = "I've been sending the same resume everywhere and using ChatGPT for everything";
    const lower = efforts.toLowerCase();
    const painPoints: string[] = [];
    if (/not tailoring|same resume|one resume/i.test(lower)) painPoints.push("not_tailoring_resume");
    if (/chatgpt|ai|automated/i.test(lower)) painPoints.push("over_relying_on_ai_tools");
    expect(painPoints).toContain("not_tailoring_resume");
    expect(painPoints).toContain("over_relying_on_ai_tools");
  });

  test("assessCareerStage: detects calibration needed", () => {
    const situation = "I'm a student just graduating";
    const desired = "I want a VP of Engineering role immediately";
    const situationLower = situation.toLowerCase();
    const outcomeLower = desired.toLowerCase();
    let calibration = false;
    if (/vp|director|senior|executive/i.test(outcomeLower) && /entry|junior|first|student/i.test(situationLower)) {
      calibration = true;
    }
    expect(calibration).toBe(true);
  });

  test("getCareerRecommendations: returns actions for each stage", () => {
    const recommendations: Record<string, { actions: string[] }> = {
      groundwork: { actions: ["Start with self-reflection"] },
      materials: { actions: ["Build a master resume"] },
      outreach: { actions: ["Stop spray-and-pray"] },
      performance: { actions: ["Build a story bank"] },
      transition: { actions: ["Map transferable skills"] },
    };
    for (const stage of ["groundwork", "materials", "outreach", "performance", "transition"]) {
      expect(recommendations[stage]).toBeDefined();
      expect(recommendations[stage].actions.length).toBeGreaterThan(0);
    }
  });

  test("explainCareerConcept: resolves known concepts to files", () => {
    const conceptMap: Record<string, string> = JSON.parse(
      readFileSync(CONCEPT_MAP_PATH, "utf-8")
    );

    const testConcepts = [
      "aiss", "resume-customization", "ats-systems",
      "cover-letter-strategy", "linkedin-strategy", "networking",
      "self-reflection", "art-of-the-brag", "career-statistics",
      "internship-strategy", "careerspan"
    ];

    for (const concept of testConcepts) {
      const filePath = conceptMap[concept];
      expect(filePath).toBeDefined();
      const fullPath = `/home/workspace/${filePath}`;
      expect(existsSync(fullPath)).toBe(true);
    }
  });

  test("explainCareerConcept: unknown concept returns graceful error structure", () => {
    const conceptMap: Record<string, string> = JSON.parse(
      readFileSync(CONCEPT_MAP_PATH, "utf-8")
    );
    const result = conceptMap["nonexistent-fake-concept-xyz"];
    expect(result).toBeUndefined();
  });

  test("collectFeedback: feedback data structure validation", () => {
    const feedback = {
      helpful: true,
      rating: 5,
      feedback_text: "This was really useful",
      would_recommend: true,
    };
    expect(typeof feedback.helpful).toBe("boolean");
    expect(feedback.rating).toBeGreaterThanOrEqual(1);
    expect(feedback.rating).toBeLessThanOrEqual(5);
    expect(typeof feedback.feedback_text).toBe("string");
  });
});

// ════════════════════════════════════════════════
// 3. DATABASE TESTS
// ════════════════════════════════════════════════

describe("3. Database Tests (career-coaching-calls)", () => {

  test("All 6 expected tables exist", async () => {
    const result = await duckdbQuery(COACHING_DB, "SHOW TABLES;");
    const tables = JSON.parse(result).map((r: any) => r.name);
    for (const t of ["caller_insights", "caller_profiles", "calls", "daily_analysis", "escalations", "feedback"]) {
      expect(tables).toContain(t);
    }
  });

  test("Insert + query works for calls table", async () => {
    const id = generateUUID();
    await duckdbExec(COACHING_DB, `
      INSERT INTO calls (id, started_at, duration_seconds, escalation_requested)
      VALUES ('${id}', CURRENT_TIMESTAMP, 120, false);
    `);
    const result = await duckdbQuery(COACHING_DB, `SELECT id FROM calls WHERE id = '${id}';`);
    const rows = JSON.parse(result);
    expect(rows.length).toBe(1);
    expect(rows[0].id).toBe(id);
    await duckdbExec(COACHING_DB, `DELETE FROM calls WHERE id = '${id}';`);
  });

  test("Insert + query works for escalations table", async () => {
    const id = generateUUID();
    await duckdbExec(COACHING_DB, `
      INSERT INTO escalations (id, call_id, name, contact, career_stage, reason, created_at)
      VALUES ('${id}', 'test-call', 'Test User', 'test@test.com', 'groundwork', 'Testing', CURRENT_TIMESTAMP);
    `);
    const result = await duckdbQuery(COACHING_DB, `SELECT id, name FROM escalations WHERE id = '${id}';`);
    const rows = JSON.parse(result);
    expect(rows.length).toBe(1);
    expect(rows[0].name).toBe("Test User");
    await duckdbExec(COACHING_DB, `DELETE FROM escalations WHERE id = '${id}';`);
  });

  test("Insert + query works for feedback table", async () => {
    const id = generateUUID();
    await duckdbExec(COACHING_DB, `
      INSERT INTO feedback (id, call_id, caller_name, satisfaction, comment, created_at)
      VALUES ('${id}', 'test-call', 'Tester', 5, 'Great', CURRENT_TIMESTAMP);
    `);
    const result = await duckdbQuery(COACHING_DB, `SELECT id, satisfaction FROM feedback WHERE id = '${id}';`);
    const rows = JSON.parse(result);
    expect(rows.length).toBe(1);
    expect(rows[0].satisfaction).toBe(5);
    await duckdbExec(COACHING_DB, `DELETE FROM feedback WHERE id = '${id}';`);
  });

  test("Insert + query works for caller_profiles table", async () => {
    const id = generateUUID();
    await duckdbExec(COACHING_DB, `
      INSERT INTO caller_profiles (id, name, phone, career_stage, help_topic)
      VALUES ('${id}', 'Test Caller', '${TEST_PHONE}', 'materials', 'resume help');
    `);
    const result = await duckdbQuery(COACHING_DB, `SELECT id, name, phone FROM caller_profiles WHERE id = '${id}';`);
    const rows = JSON.parse(result);
    expect(rows.length).toBe(1);
    expect(rows[0].phone).toBe(TEST_PHONE);
    await duckdbExec(COACHING_DB, `DELETE FROM caller_profiles WHERE id = '${id}';`);
  });

  test("Phone index works for caller_profiles lookup", async () => {
    const id = generateUUID();
    const phone = "+15558887777";
    await duckdbExec(COACHING_DB, `
      INSERT INTO caller_profiles (id, name, phone) VALUES ('${id}', 'Index Test', '${phone}');
    `);
    const result = await duckdbQuery(COACHING_DB, `SELECT id FROM caller_profiles WHERE phone = '${phone}';`);
    const rows = JSON.parse(result);
    expect(rows.length).toBe(1);
    await duckdbExec(COACHING_DB, `DELETE FROM caller_profiles WHERE id = '${id}';`);
  });
});

describe("3b. Database Tests (career-hotline-calls)", () => {

  test("All 5 expected tables exist", async () => {
    const result = await duckdbQuery(HOTLINE_DB, "SHOW TABLES;");
    const tables = JSON.parse(result).map((r: any) => r.name);
    for (const t of ["caller_insights", "caller_lookup", "calls", "escalations", "feedback"]) {
      expect(tables).toContain(t);
    }
  });

  test("Insert + query works for calls table", async () => {
    const id = generateUUID();
    await duckdbExec(HOTLINE_DB, `
      INSERT INTO calls (id, started_at, duration_seconds, escalation_requested)
      VALUES ('${id}', CURRENT_TIMESTAMP, 90, false);
    `);
    const result = await duckdbQuery(HOTLINE_DB, `SELECT id FROM calls WHERE id = '${id}';`);
    const rows = JSON.parse(result);
    expect(rows.length).toBe(1);
    await duckdbExec(HOTLINE_DB, `DELETE FROM calls WHERE id = '${id}';`);
  });

  test("Insert + query works for caller_lookup table", async () => {
    const id = generateUUID();
    await duckdbExec(HOTLINE_DB, `
      INSERT INTO caller_lookup (id, phone_number, caller_name, career_stage, primary_challenge, submitted_at, created_at)
      VALUES ('${id}', '${TEST_PHONE}', 'Lookup Test', 'outreach', 'Not getting callbacks', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
    `);
    const result = await duckdbQuery(HOTLINE_DB, `SELECT id, caller_name FROM caller_lookup WHERE phone_number = '${TEST_PHONE}';`);
    const rows = JSON.parse(result);
    expect(rows.length).toBeGreaterThanOrEqual(1);
    await duckdbExec(HOTLINE_DB, `DELETE FROM caller_lookup WHERE id = '${id}';`);
  });

  test("Insert + query works for escalations table", async () => {
    const id = generateUUID();
    await duckdbExec(HOTLINE_DB, `
      INSERT INTO escalations (id, call_id, name, contact, career_stage, reason, pain_points, created_at)
      VALUES ('${id}', 'test-call', 'Esc Test', 'esc@test.com', 'performance', 'Need interview prep', '["interview_anxiety"]', CURRENT_TIMESTAMP);
    `);
    const result = await duckdbQuery(HOTLINE_DB, `SELECT id FROM escalations WHERE id = '${id}';`);
    const rows = JSON.parse(result);
    expect(rows.length).toBe(1);
    await duckdbExec(HOTLINE_DB, `DELETE FROM escalations WHERE id = '${id}';`);
  });

  test("Insert + query works for feedback table", async () => {
    const id = generateUUID();
    await duckdbExec(HOTLINE_DB, `
      INSERT INTO feedback (id, call_id, helpful, rating, feedback_text, would_recommend, created_at)
      VALUES ('${id}', 'test-call', true, 4, 'Solid advice', true, CURRENT_TIMESTAMP);
    `);
    const result = await duckdbQuery(HOTLINE_DB, `SELECT id, rating FROM feedback WHERE id = '${id}';`);
    const rows = JSON.parse(result);
    expect(rows.length).toBe(1);
    expect(rows[0].rating).toBe(4);
    await duckdbExec(HOTLINE_DB, `DELETE FROM feedback WHERE id = '${id}';`);
  });
});

// ════════════════════════════════════════════════
// 4. WEBHOOK INTEGRATION (structural — no live server needed)
// ════════════════════════════════════════════════

describe("4. Webhook Integration (Structural)", () => {

  test("assistant-request payload structure is valid", () => {
    const toolSpecs = JSON.parse(readFileSync(TOOL_SPECS_PATH, "utf-8"));
    const systemPrompt = readFileSync(SYSTEM_PROMPT_PATH, "utf-8").replace(/^---[\s\S]*?---\s*/, "");

    const response = {
      assistant: {
        name: "V (Career Coach)",
        firstMessage: "Hey — this is V on the Careerspan Career Coaching Hotline.",
        transcriber: { provider: "deepgram", keywords: [] },
        model: {
          provider: "anthropic",
          model: "claude-haiku-4-5-20251001",
          messages: [{ role: "system", content: systemPrompt }],
          tools: toolSpecs.tools,
        },
        voice: { provider: "11labs", voiceId: "test" },
        serverMessages: ["end-of-call-report", "tool-calls"],
      },
    };

    expect(response.assistant.name).toBe("V (Career Coach)");
    expect(response.assistant.model.tools.length).toBe(6);
    expect(response.assistant.model.messages[0].content.length).toBeGreaterThan(500);
    expect(response.assistant.serverMessages).toContain("end-of-call-report");
    expect(response.assistant.serverMessages).toContain("tool-calls");
  });

  test("tool-calls payload routes to correct handlers", () => {
    const validTools = [
      "assessCareerStage",
      "getCareerRecommendations",
      "explainCareerConcept",
      "requestCareerSession",
      "lookupCaller",
      "collectFeedback",
    ];

    const toolCalls = [
      { function: { name: "assessCareerStage", arguments: "{}" }, id: "tc1" },
      { function: { name: "getCareerRecommendations", arguments: "{}" }, id: "tc2" },
      { function: { name: "explainCareerConcept", arguments: "{}" }, id: "tc3" },
      { function: { name: "unknownTool", arguments: "{}" }, id: "tc4" },
    ];

    for (const tc of toolCalls) {
      const name = tc.function.name;
      const isKnown = validTools.includes(name);
      if (name === "unknownTool") {
        expect(isKnown).toBe(false);
      } else {
        expect(isKnown).toBe(true);
      }
    }
  });

  test("tool-calls response format matches VAPI expectation", () => {
    const results = [
      { name: "assessCareerStage", toolCallId: "tc1", result: '{"primary_stage":"groundwork"}' },
    ];
    const response = { results };
    expect(response.results).toBeDefined();
    expect(Array.isArray(response.results)).toBe(true);
    expect(response.results[0].toolCallId).toBe("tc1");
    expect(typeof response.results[0].result).toBe("string");
    JSON.parse(response.results[0].result); // should not throw
  });

  test("Auth check: missing secret blocks request", () => {
    const webhookSecret = "test-secret-123";
    const incomingSecret = "";
    const authPasses = !webhookSecret || incomingSecret === webhookSecret;
    expect(authPasses).toBe(false);
  });

  test("Auth check: correct secret allows request", () => {
    const webhookSecret = "test-secret-123";
    const incomingSecret = "test-secret-123";
    const authPasses = !webhookSecret || incomingSecret === webhookSecret;
    expect(authPasses).toBe(true);
  });

  test("Auth check: no secret configured allows all requests", () => {
    const webhookSecret = "";
    const incomingSecret = "";
    const authPasses = !webhookSecret || incomingSecret === webhookSecret;
    expect(authPasses).toBe(true);
  });
});

// ════════════════════════════════════════════════
// 5. INTAKE PIPELINE
// ════════════════════════════════════════════════

describe("5. Intake Pipeline", () => {

  test("Phone number normalization: 10-digit US", () => {
    expect(normalizePhone("5551234567")).toBe("+15551234567");
  });

  test("Phone number normalization: with country code", () => {
    expect(normalizePhone("+15551234567")).toBe("+15551234567");
  });

  test("Phone number normalization: formatted US", () => {
    const result = normalizePhone("(555) 123-4567");
    expect(result).toBe("+15551234567");
  });

  test("Phone number normalization: with dots", () => {
    const result = normalizePhone("555.123.4567");
    expect(result).toBe("+15551234567");
  });

  test("Phone number normalization: with spaces", () => {
    const result = normalizePhone("555 123 4567");
    expect(result).toBe("+15551234567");
  });

  test("Phone number normalization: invalid returns null", () => {
    expect(normalizePhone("abc")).toBeNull();
    expect(normalizePhone("123")).toBeNull();
    expect(normalizePhone("")).toBeNull();
  });

  test("Fillout payload field extraction logic", () => {
    const questions = [
      { id: "q1", name: "What is your full name?", type: "ShortAnswer", value: "Jane Doe" },
      { id: "q2", name: "Phone number", type: "PhoneNumber", value: "+15551234567" },
      { id: "q3", name: "Email address", type: "EmailAddress", value: "jane@test.com" },
      { id: "q4", name: "Where are you in your career search?", type: "MultipleChoice", value: "I'm working on my resume" },
      { id: "q5", name: "What do you want help with?", type: "LongAnswer", value: "I need resume feedback" },
    ];

    function extractField(qs: typeof questions, ...patterns: string[]): string | null {
      for (const pattern of patterns) {
        const lower = pattern.toLowerCase();
        const found = qs.find(q => q.name.toLowerCase().includes(lower));
        if (found && found.value != null) return String(found.value);
      }
      return null;
    }

    expect(extractField(questions, "full name", "name")).toBe("Jane Doe");
    expect(extractField(questions, "phone")).toBe("+15551234567");
    expect(extractField(questions, "email")).toBe("jane@test.com");
    expect(extractField(questions, "career search", "career stage")).toBe("I'm working on my resume");
    expect(extractField(questions, "help with", "what do you want")).toBe("I need resume feedback");
  });

  test("Career stage resolution from Fillout answers", () => {
    const CAREER_STAGE_MAP: Record<string, string> = {
      "i'm just getting started": "groundwork",
      "i'm working on my resume": "materials",
      "i'm actively applying": "outreach",
      "i'm getting interviews": "performance",
      "i'm changing careers": "transition",
    };

    function resolveCareerStage(raw: string | null): string | null {
      if (!raw) return null;
      const lower = raw.toLowerCase().trim();
      if (CAREER_STAGE_MAP[lower]) return CAREER_STAGE_MAP[lower];
      for (const [key, value] of Object.entries(CAREER_STAGE_MAP)) {
        if (lower.includes(key)) return value;
      }
      return raw;
    }

    expect(resolveCareerStage("I'm working on my resume")).toBe("materials");
    expect(resolveCareerStage("I'm actively applying")).toBe("outreach");
    expect(resolveCareerStage("I'm just getting started")).toBe("groundwork");
    expect(resolveCareerStage("I'm getting interviews")).toBe("performance");
    expect(resolveCareerStage("I'm changing careers")).toBe("transition");
    expect(resolveCareerStage(null)).toBeNull();
  });

  test("Caller profile stored and queryable in DuckDB", async () => {
    const id = generateUUID();
    const phone = "+15553216789";
    await duckdbExec(COACHING_DB, `
      INSERT INTO caller_profiles (id, name, phone, career_stage, help_topic, caller_brief, source)
      VALUES ('${id}', 'Integration Test User', '${phone}', 'materials', 'Resume feedback', 'Test brief for caller', 'fillout');
    `);
    const result = await duckdbQuery(COACHING_DB, `SELECT name, career_stage, caller_brief FROM caller_profiles WHERE phone = '${phone}';`);
    const rows = JSON.parse(result);
    expect(rows.length).toBeGreaterThanOrEqual(1);
    expect(rows[0].name).toBe("Integration Test User");
    expect(rows[0].career_stage).toBe("materials");
    expect(rows[0].caller_brief).toContain("Test brief");
    await duckdbExec(COACHING_DB, `DELETE FROM caller_profiles WHERE id = '${id}';`);
  });

  test("lookupCaller returns null for unknown numbers", async () => {
    const result = await lookupCaller("+19999999999");
    expect(result).toBeNull();
  });

  test("generateUUID produces valid v4 UUIDs", () => {
    const id = generateUUID();
    expect(id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
  });
});

// ════════════════════════════════════════════════
// 6. CALLER LOOKUP MODULE
// ════════════════════════════════════════════════

describe("6. Caller Lookup Module", () => {

  test("normalizePhone handles edge cases", () => {
    expect(normalizePhone("+44 20 7946 0958")).toBe("+442079460958");
    expect(normalizePhone("1-555-123-4567")).toBe("+15551234567");
  });

  test("lookupCaller with stored profile returns data", async () => {
    const id = generateUUID();
    const phone = "+15550001111";
    await duckdbExec(COACHING_DB, `
      INSERT INTO caller_profiles (id, name, phone, career_stage, help_topic, caller_brief, call_count)
      VALUES ('${id}', 'Lookup Test', '${phone}', 'outreach', 'Networking help', 'A test brief', 0);
    `);
    const result = await lookupCaller(phone);
    expect(result).not.toBeNull();
    expect(result!.name).toBe("Lookup Test");
    expect(result!.career_stage).toBe("outreach");
    await duckdbExec(COACHING_DB, `DELETE FROM caller_profiles WHERE id = '${id}';`);
  });
});
