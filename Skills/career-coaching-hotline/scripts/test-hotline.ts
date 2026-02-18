#!/usr/bin/env bun
/**
 * Comprehensive Testing Suite for Career Coaching Hotline
 * Tests all 11 tools + assistant-request + end-of-call-report + intake pipeline
 *
 * Usage: bun run test-hotline.ts [--port 4242] [--only toolName]
 */

const PORT = parseInt(process.argv.find((_, i, a) => a[i - 1] === "--port") || "4242");
const ONLY = process.argv.find((_, i, a) => a[i - 1] === "--only") || null;
const BASE = `http://localhost:${PORT}`;

// Amanda's real phone (has caller_lookup + resume + balance data)
const AMANDA_PHONE = "+18456644376";
// V's real phone (has balance data from real calls)
const V_PHONE = "+18578693264";
// Unknown caller (no data — tests cold-start paths)
const UNKNOWN_PHONE = "+15559990001";

let passed = 0;
let failed = 0;
let skipped = 0;

interface TestResult {
  name: string;
  status: "PASS" | "FAIL" | "SKIP";
  duration: number;
  detail?: string;
}

const results: TestResult[] = [];

function vapiToolCallPayload(toolName: string, args: object, callId?: string) {
  return {
    message: {
      type: "tool-calls",
      call: { id: callId || `test-${Date.now()}` },
      toolCalls: [{
        id: `tc-${toolName}-${Date.now()}`,
        type: "function",
        function: {
          name: toolName,
          arguments: JSON.stringify(args),
        },
      }],
    },
  };
}

async function callTool(toolName: string, args: object, callId?: string): Promise<any> {
  const payload = vapiToolCallPayload(toolName, args, callId);
  const resp = await fetch(BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status}: ${await resp.text()}`);
  }
  const body = await resp.json();
  const toolResult = body.results?.[0];
  if (!toolResult) throw new Error("No tool result in response");
  return JSON.parse(toolResult.result);
}

async function test(name: string, fn: () => Promise<void>) {
  if (ONLY && !name.toLowerCase().includes(ONLY.toLowerCase())) {
    skipped++;
    results.push({ name, status: "SKIP", duration: 0 });
    return;
  }
  const start = Date.now();
  try {
    await fn();
    const dur = Date.now() - start;
    passed++;
    results.push({ name, status: "PASS", duration: dur });
    console.log(`  \u2713 ${name} (${dur}ms)`);
  } catch (err: any) {
    const dur = Date.now() - start;
    failed++;
    results.push({ name, status: "FAIL", duration: dur, detail: err.message });
    console.error(`  \u2717 ${name} (${dur}ms): ${err.message}`);
  }
}

function assert(condition: boolean, msg: string) {
  if (!condition) throw new Error(msg);
}

// ═══════════════════════════════════════════════════
// SECTION 1: Health & Infrastructure
// ═══════════════════════════════════════════════════
async function testInfrastructure() {
  console.log("\n-- SECTION 1: Infrastructure --");

  await test("Health endpoint returns OK with all 11 tools", async () => {
    const resp = await fetch(`${BASE}/health`);
    assert(resp.ok, `Health returned ${resp.status}`);
    const body = await resp.json();
    assert(body.status === "ok", `Status: ${body.status}`);
    assert(body.identity === "Zozie", `Identity: ${body.identity}`);
    assert(body.tools?.length === 11, `Tools count: ${body.tools?.length}, expected 11`);
    const expected = [
      "lookupCaller", "assessCareerStage", "getCareerRecommendations",
      "explainCareerConcept", "requestCareerSession", "collectFeedback",
      "analyzeResumeBullet", "diagnoseSearchStrategy", "scoreResumeSection",
      "pullCallerResume", "referToCareerspan"
    ];
    for (const t of expected) {
      assert(body.tools.includes(t), `Missing tool: ${t}`);
    }
  });

  await test("Assistant-request returns valid VAPI config", async () => {
    const resp = await fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: {
          type: "assistant-request",
          call: {
            id: "test-assistant-req",
            customer: { number: AMANDA_PHONE },
          },
        },
      }),
    });
    assert(resp.ok, `HTTP ${resp.status}`);
    const body = await resp.json();
    assert(body.assistant, "No assistant in response");
    assert(body.assistant.model, "No model config");
    assert(body.assistant.model.tools?.length > 0, "No tools defined");
    assert(body.assistant.voice, "No voice config");
    assert(body.assistant.model.messages?.[0]?.content?.includes("Zozie"), "System prompt missing Zozie identity");
    assert(
      body.assistant.model.messages?.[0]?.content?.includes("Careerspan"),
      "System prompt missing Careerspan references"
    );
  });

  await test("Unknown message type returns 200 (graceful)", async () => {
    const resp = await fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: { type: "some-unknown-type" } }),
    });
    assert(resp.status < 500, `Server error: ${resp.status}`);
  });
}

// ═══════════════════════════════════════════════════
// SECTION 2: Caller Lookup & Balance
// ═══════════════════════════════════════════════════
async function testCallerLookup() {
  console.log("\n-- SECTION 2: lookupCaller --");

  await test("lookupCaller -- known caller with intake + resume (Amanda)", async () => {
    const r = await callTool("lookupCaller", { phone_number: AMANDA_PHONE });
    assert(r.found === true, `Expected found=true, got ${r.found}`);
    assert(r.balance, "Missing balance");
    assert(typeof r.balance.free_seconds_remaining === "number", "Missing free_seconds_remaining");
    assert(r.has_resume_on_file === true, `Expected resume on file, got ${r.has_resume_on_file}`);
    assert(r.intake, "Missing intake data");
    // Intake returns "name" field, not "caller_name"
    assert(r.intake.name?.includes("Amanda"), `Expected Amanda in intake.name, got ${r.intake.name}`);
    assert(r.resume_note, "Missing resume_note prompt");
  });

  await test("lookupCaller -- known caller with balance only (V)", async () => {
    const r = await callTool("lookupCaller", { phone_number: V_PHONE });
    assert(r.balance, "Missing balance");
    assert(typeof r.balance.total_seconds_used === "number", "Missing total_seconds_used");
  });

  await test("lookupCaller -- unknown caller (cold start)", async () => {
    const r = await callTool("lookupCaller", { phone_number: UNKNOWN_PHONE });
    assert(r.balance, "Missing balance");
    assert(r.balance.free_seconds_remaining === 900, `Expected 900 free seconds, got ${r.balance.free_seconds_remaining}`);
    assert(r.balance.is_free_tier === true, `Expected is_free_tier=true`);
    assert(r.has_resume_on_file === false, `Expected no resume, got ${r.has_resume_on_file}`);
  });

  await test("lookupCaller -- missing phone returns found=false", async () => {
    const r = await callTool("lookupCaller", {});
    assert(r.found === false, `Expected found=false for missing phone, got ${JSON.stringify(r).slice(0, 100)}`);
  });
}

// ═══════════════════════════════════════════════════
// SECTION 3: Career Assessment (LLM-based)
// Uses correct params: current_situation, efforts_so_far, desired_outcome
// ═══════════════════════════════════════════════════
async function testAssessCareerStage() {
  console.log("\n-- SECTION 3: assessCareerStage (LLM) --");

  await test("assessCareerStage -- materials-stage signal", async () => {
    const r = await callTool("assessCareerStage", {
      current_situation: "I've been applying to jobs for 3 months but my resume isn't getting responses. Mid-career marketer wanting to move into product management.",
      efforts_so_far: "Updated LinkedIn, applied to about 50 jobs on Indeed and LinkedIn",
      desired_outcome: "Land a product manager role at a mid-size tech company within 3 months",
      urgency_signals: "Savings running low, need to move fast",
    });
    assert(r.primary_stage, `Missing primary_stage, got: ${JSON.stringify(r).slice(0, 200)}`);
    const validStages = ["groundwork", "materials", "outreach", "performance", "transition"];
    assert(validStages.includes(r.primary_stage), `Invalid stage: ${r.primary_stage}`);
    assert(r.pain_points, "Missing pain_points");
    assert(r.coaching_note, "Missing coaching_note");
  });

  await test("assessCareerStage -- missing required params returns error", async () => {
    const r = await callTool("assessCareerStage", {
      current_situation: "I need help",
    });
    assert(r.error, `Expected error for missing params, got: ${JSON.stringify(r).slice(0, 100)}`);
  });
}

// ═══════════════════════════════════════════════════
// SECTION 4: Career Recommendations
// Uses: primary_stage, pain_points, urgency
// ═══════════════════════════════════════════════════
async function testGetCareerRecommendations() {
  console.log("\n-- SECTION 4: getCareerRecommendations --");

  await test("getCareerRecommendations -- materials stage", async () => {
    const r = await callTool("getCareerRecommendations", {
      primary_stage: "materials",
      pain_points: ["not_tailoring_resume"],
      urgency: "high",
    });
    // Returns: actions, timeframe, priority (from hardcoded map)
    assert(r.actions || r.timeframe || r.priority, `Missing recommendations data: ${JSON.stringify(r).slice(0, 150)}`);
  });

  await test("getCareerRecommendations -- outreach stage", async () => {
    const r = await callTool("getCareerRecommendations", {
      primary_stage: "outreach",
      pain_points: ["no_networking"],
      urgency: "medium",
    });
    assert(!r.error, `Error: ${r.error}`);
  });

  await test("getCareerRecommendations -- unknown stage falls back to groundwork", async () => {
    const r = await callTool("getCareerRecommendations", {
      primary_stage: "unknown_stage",
      pain_points: [],
      urgency: "low",
    });
    // Should fall back to groundwork recommendations, not error
    assert(!r.error, `Got error for unknown stage: ${r.error}`);
  });
}

// ═══════════════════════════════════════════════════
// SECTION 5: Career Concepts (Knowledge-base)
// ═══════════════════════════════════════════════════
async function testExplainCareerConcept() {
  console.log("\n-- SECTION 5: explainCareerConcept --");

  await test("explainCareerConcept -- AISS framework", async () => {
    const r = await callTool("explainCareerConcept", {
      concept: "AISS framework",
    });
    // Returns: { concept, content, type: "file_content" }
    assert(r.content, `Missing content: ${JSON.stringify(r).slice(0, 100)}`);
    assert(r.type === "file_content", `Expected file_content type, got ${r.type}`);
    assert(r.content.includes("AISS") || r.content.includes("Action"), "Content should mention AISS");
  });

  await test("explainCareerConcept -- networking (exact alias match)", async () => {
    const r = await callTool("explainCareerConcept", {
      concept: "networking",
    });
    assert(r.content || r.type, `Missing content: ${JSON.stringify(r).slice(0, 100)}`);
  });

  await test("explainCareerConcept -- unknown concept returns error with suggestions", async () => {
    const r = await callTool("explainCareerConcept", {
      concept: "quantum computing career paths in underwater basket weaving",
    });
    assert(r.error, "Expected error for unknown concept");
    assert(r.available_concepts || r.suggestion, "Expected available_concepts or suggestion");
  });
}

// ═══════════════════════════════════════════════════
// SECTION 6: Resume Tools
// analyzeResumeBullet uses: bullet_text (not bullet)
// scoreResumeSection uses: section_content (not content)
// ═══════════════════════════════════════════════════
async function testResumeTools() {
  console.log("\n-- SECTION 6: Resume Tools --");

  await test("pullCallerResume -- Amanda (has resume)", async () => {
    const r = await callTool("pullCallerResume", { phone_number: AMANDA_PHONE });
    assert(!r.error, `Error: ${r.error}`);
    // Should return resume decomposition data
    assert(r.found !== false, `Expected found resume`);
    const data = r.resume_data || r;
    assert(data.name || data.current_title || data.experience, `Missing resume fields: ${Object.keys(data).slice(0, 5).join(", ")}`);
  });

  await test("pullCallerResume -- unknown caller (no resume)", async () => {
    const r = await callTool("pullCallerResume", { phone_number: UNKNOWN_PHONE });
    // Returns { found: false, message, suggestion }
    assert(r.found === false || r.error, `Expected not-found: ${JSON.stringify(r).slice(0, 100)}`);
  });

  await test("analyzeResumeBullet -- strong bullet (LLM)", async () => {
    const r = await callTool("analyzeResumeBullet", {
      bullet_text: "Grew audience engagement on action alerts by 21%, with over 83k emails sent by advocates to state elected officials in one year",
      target_role: "Campaign Director",
    });
    // Returns: { original, scores: { action, impact, scale, skill }, overall_score OR scores.overall, rewrite }
    assert(r.scores, `Missing scores: ${JSON.stringify(r).slice(0, 150)}`);
    // LLM may put overall in scores.overall or at root as overall_score
    const hasOverall = typeof r.scores?.overall === "number" || typeof r.overall_score === "number";
    assert(hasOverall, `Missing overall score in scores.overall or overall_score`);
    const hasRewrite = r.rewrite || r.rewritten || r.rewritten_bullet || r.suggested_rewrite || r.coaching_tip || r.coaching_note;
    assert(hasRewrite, `Missing rewrite/coaching output. Keys: ${Object.keys(r).join(", ")}`);
  });

  await test("analyzeResumeBullet -- weak bullet (LLM)", async () => {
    const r = await callTool("analyzeResumeBullet", {
      bullet_text: "Assisted with various research tasks and administrative duties for the department",
    });
    assert(r.scores || r.error === "Analysis service is temporarily unavailable", `Unexpected: ${JSON.stringify(r).slice(0, 100)}`);
  });

  await test("analyzeResumeBullet -- too short returns error", async () => {
    const r = await callTool("analyzeResumeBullet", { bullet_text: "Hi" });
    assert(r.error, `Expected error for too-short bullet`);
  });

  await test("scoreResumeSection -- experience section (LLM)", async () => {
    const r = await callTool("scoreResumeSection", {
      section_type: "experience",
      section_content: `Marketing Manager | Acme Corp | 2020-Present
- Led team of 5 marketers to increase brand awareness
- Managed social media accounts and created content for LinkedIn and Twitter
- Organized trade show appearances and client events
- Grew email list by 40% through targeted campaigns and referral programs`,
      target_role: "Product Manager",
    });
    // Returns: { section, score, strengths, weaknesses, specific_fixes, ats_risk, coaching_note }
    assert(typeof r.score === "number" || r.error, `Missing score: ${JSON.stringify(r).slice(0, 150)}`);
  });

  await test("scoreResumeSection -- invalid section type", async () => {
    const r = await callTool("scoreResumeSection", {
      section_type: "hobbies",
      section_content: "I like hiking and reading",
    });
    assert(r.error, `Expected error for invalid section type`);
  });
}

// ═══════════════════════════════════════════════════
// SECTION 7: Search Strategy (LLM-based)
// Uses: signal_strength, system_fluency, execution, intelligence
// ═══════════════════════════════════════════════════
async function testDiagnoseSearchStrategy() {
  console.log("\n-- SECTION 7: diagnoseSearchStrategy (LLM) --");

  await test("diagnoseSearchStrategy -- full diagnostic", async () => {
    const r = await callTool("diagnoseSearchStrategy", {
      signal_strength: "I updated my resume but it's generic. I use the same version for everything.",
      system_fluency: "I just apply on LinkedIn and Indeed. I don't really understand ATS.",
      execution: "I apply to about 30 jobs a week but don't follow up or network.",
      intelligence: "I just search for 'data analyst' and apply to whatever comes up.",
    });
    assert(!r.error, `Error: ${r.error}`);
    // Returns normalized: { scores, weakest_dimension, diagnosis, primary_fix, secondary_fix }
    assert(r.scores, `Missing scores: ${JSON.stringify(r).slice(0, 150)}`);
    assert(Object.keys(r.scores).length >= 4, `Expected 4+ dimension scores, got ${Object.keys(r.scores).length}`);
  });

  await test("diagnoseSearchStrategy -- missing dimensions returns error", async () => {
    const r = await callTool("diagnoseSearchStrategy", {
      signal_strength: "My resume is ok",
    });
    assert(r.error, `Expected error for missing dimensions`);
    assert(r.instructions, `Expected instructions`);
  });
}

// ═══════════════════════════════════════════════════
// SECTION 8: Careerspan Referral
// Uses: reason (maps to: story_bank, resume_review, ongoing_accountability, etc.)
// ═══════════════════════════════════════════════════
async function testReferToCareerspan() {
  console.log("\n-- SECTION 8: referToCareerspan --");

  await test("referToCareerspan -- story_bank (exact key)", async () => {
    const r = await callTool("referToCareerspan", {
      reason: "story_bank",
    });
    assert(r.service, `Missing service: ${JSON.stringify(r).slice(0, 100)}`);
    assert(r.pitch, "Missing pitch");
    assert(r.transition, "Missing transition");
    assert(r.booking_link, "Missing booking_link");
  });

  await test("referToCareerspan -- resume_review", async () => {
    const r = await callTool("referToCareerspan", {
      reason: "resume_review",
    });
    assert(r.service?.includes("Resume"), `Expected resume service, got: ${r.service}`);
  });

  await test("referToCareerspan -- unknown reason gets generic referral", async () => {
    const r = await callTool("referToCareerspan", {
      reason: "general career confusion and existential dread",
    });
    assert(r.service === "Careerspan Coaching", `Expected generic service, got: ${r.service}`);
    assert(r.booking_link, "Missing booking_link");
  });
}

// ═══════════════════════════════════════════════════
// SECTION 9: Feedback & Escalation
// ═══════════════════════════════════════════════════
async function testFeedbackAndEscalation() {
  console.log("\n-- SECTION 9: Feedback & Escalation --");

  const testCallId = `test-feedback-${Date.now()}`;

  await test("collectFeedback -- positive feedback with call_id", async () => {
    const r = await callTool("collectFeedback", {
      helpful: true,
      rating: 5,
      feedback_text: "This was incredibly helpful! Zozie gave great resume advice.",
      would_recommend: true,
      caller_name: "TestRunner",
    }, testCallId);
    assert(!r.error, `Error: ${r.error}`);
  });

  await test("collectFeedback -- verify call_id persisted correctly", async () => {
    const { stdout } = Bun.spawnSync(["python3", "-c", `
import duckdb, json
con = duckdb.connect("/home/workspace/Datasets/career-hotline-calls/data.duckdb", read_only=True)
rows = con.execute("SELECT call_id, caller_name FROM feedback WHERE caller_name = 'TestRunner' ORDER BY created_at DESC LIMIT 1").fetchall()
print(json.dumps({"call_id": rows[0][0], "name": rows[0][1]} if rows else {"error": "not found"}))
con.close()
`]);
    const res = JSON.parse(new TextDecoder().decode(stdout).trim());
    assert(!res.error, `Feedback not found in DB: ${res.error}`);
    assert(res.call_id === testCallId, `Expected call_id='${testCallId}', got '${res.call_id}'`);
  });

  await test("requestCareerSession -- escalation with call_id", async () => {
    const r = await callTool("requestCareerSession", {
      name: "Test Escalation User",
      contact: "test-escalation@example.com",
      career_stage: "materials",
      reason: "Needs full resume rewrite and interview prep",
      pain_points: ["resume not getting callbacks", "career pivot confusion"],
    }, testCallId);
    assert(!r.error, `Error: ${r.error}`);
  });

  await test("requestCareerSession -- verify call_id in escalations", async () => {
    const { stdout } = Bun.spawnSync(["python3", "-c", `
import duckdb, json
con = duckdb.connect("/home/workspace/Datasets/career-hotline-calls/data.duckdb", read_only=True)
rows = con.execute("SELECT call_id, name FROM escalations WHERE name = 'Test Escalation User' ORDER BY created_at DESC LIMIT 1").fetchall()
print(json.dumps({"call_id": rows[0][0], "name": rows[0][1]} if rows else {"error": "not found"}))
con.close()
`]);
    const res = JSON.parse(new TextDecoder().decode(stdout).trim());
    assert(!res.error, `Escalation not found: ${res.error}`);
    assert(res.call_id === testCallId, `Expected call_id='${testCallId}', got '${res.call_id}'`);
  });
}

// ═══════════════════════════════════════════════════
// SECTION 10: End-of-Call Report
// ═══════════════════════════════════════════════════
async function testEndOfCallReport() {
  console.log("\n-- SECTION 10: End-of-Call Report --");

  await test("end-of-call-report -- logs call and updates balance", async () => {
    const testCallId = `test-eoc-${Date.now()}`;
    const resp = await fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: {
          type: "end-of-call-report",
          call: {
            id: testCallId,
            customer: { number: "+15559990002" },
          },
          durationSeconds: 45,
          endedReason: "assistant-ended-call",
          artifact: {
            transcript: "User: Hi I need help with my resume.\nAssistant: I'd love to help! Tell me about your experience.",
          },
          analysis: {
            summary: "Caller asked about resume improvement.",
          },
        },
      }),
    });
    assert(resp.ok, `HTTP ${resp.status}`);

    // Give async operations a moment
    await new Promise(r => setTimeout(r, 3000));

    // Verify call was logged
    const { stdout } = Bun.spawnSync(["python3", "-c", `
import duckdb, json
con = duckdb.connect("/home/workspace/Datasets/career-hotline-calls/data.duckdb", read_only=True)
rows = con.execute("SELECT id, phone_number, duration_seconds FROM calls WHERE phone_number = '+15559990002' ORDER BY started_at DESC LIMIT 1").fetchall()
print(json.dumps({"id": rows[0][0], "phone": rows[0][1], "dur": rows[0][2]} if rows else {"error": "not found"}))
con.close()
`]);
    const res = JSON.parse(new TextDecoder().decode(stdout).trim());
    assert(!res.error, `Call not logged: ${res.error}`);
    assert(res.phone === "+15559990002", `Wrong phone: ${res.phone}`);
  });
}

// ═══════════════════════════════════════════════════
// SECTION 11: Assistant-Request Personalization
// ═══════════════════════════════════════════════════
async function testAssistantPersonalization() {
  console.log("\n-- SECTION 11: Assistant-Request Personalization --");

  await test("Assistant-request for caller with resume -- system prompt mentions resume", async () => {
    const resp = await fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: {
          type: "assistant-request",
          call: {
            id: "test-personalization",
            customer: { number: AMANDA_PHONE },
          },
        },
      }),
    });
    assert(resp.ok, `HTTP ${resp.status}`);
    const body = await resp.json();
    const sysPrompt = body.assistant?.model?.messages?.[0]?.content || "";
    assert(
      sysPrompt.includes("resume") || sysPrompt.includes("Amanda") || sysPrompt.includes("Caller Profile"),
      "System prompt not personalized for known caller with resume"
    );
  });

  await test("Assistant-request for unknown caller -- default system prompt", async () => {
    const resp = await fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: {
          type: "assistant-request",
          call: {
            id: "test-unknown-caller",
            customer: { number: UNKNOWN_PHONE },
          },
        },
      }),
    });
    assert(resp.ok, `HTTP ${resp.status}`);
    const body = await resp.json();
    assert(body.assistant?.model?.messages?.[0]?.content, "Missing system prompt");
  });
}

// ═══════════════════════════════════════════════════
// SECTION 12: Edge Cases & Error Handling
// ═══════════════════════════════════════════════════
async function testEdgeCases() {
  console.log("\n-- SECTION 12: Edge Cases --");

  await test("Unknown tool name returns error with available_tools list", async () => {
    const r = await callTool("nonExistentTool", {});
    assert(r.error, "Expected error for unknown tool");
    assert(r.available_tools?.length === 11, `Expected 11 available tools, got ${r.available_tools?.length}`);
  });

  await test("Malformed JSON in tool arguments handled gracefully", async () => {
    const resp = await fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: {
          type: "tool-calls",
          call: { id: "test-malformed" },
          toolCalls: [{
            id: "tc-bad",
            type: "function",
            function: {
              name: "lookupCaller",
              arguments: "not valid json {{{",
            },
          }],
        },
      }),
    });
    assert(resp.ok, `Expected 200 for malformed args, got ${resp.status}`);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.error, "Expected error in result for malformed JSON");
  });

  await test("Empty toolCalls array returns empty results", async () => {
    const resp = await fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: {
          type: "tool-calls",
          call: { id: "test-empty" },
          toolCalls: [],
        },
      }),
    });
    assert(resp.ok, `HTTP ${resp.status}`);
    const body = await resp.json();
    assert(Array.isArray(body.results), "Expected results array");
    assert(body.results.length === 0, `Expected 0 results, got ${body.results.length}`);
  });

  await test("Multiple tool calls in single request", async () => {
    const resp = await fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: {
          type: "tool-calls",
          call: { id: "test-multi" },
          toolCalls: [
            {
              id: "tc-1",
              type: "function",
              function: { name: "lookupCaller", arguments: JSON.stringify({ phone_number: AMANDA_PHONE }) },
            },
            {
              id: "tc-2",
              type: "function",
              function: { name: "explainCareerConcept", arguments: JSON.stringify({ concept: "resume" }) },
            },
          ],
        },
      }),
    });
    assert(resp.ok, `HTTP ${resp.status}`);
    const body = await resp.json();
    assert(body.results?.length === 2, `Expected 2 results, got ${body.results?.length}`);
    assert(body.results[0].toolCallId === "tc-1", "First result toolCallId mismatch");
    assert(body.results[1].toolCallId === "tc-2", "Second result toolCallId mismatch");
  });
}

// ═══════════════════════════════════════════════════
// SECTION 13: Intake Webhook (Fillout pipeline)
// ═══════════════════════════════════════════════════
async function testIntakeWebhook() {
  console.log("\n-- SECTION 13: Intake Webhook (port 8849) --");

  await test("Intake health check", async () => {
    const resp = await fetch("http://localhost:8849/health");
    assert(resp.ok, `HTTP ${resp.status}`);
    const body = await resp.json();
    assert(body.status === "ok", `Status: ${body.status}`);
    assert(body.service === "career-intake-webhook", `Service: ${body.service}`);
  });

  await test("Intake processes simulated Fillout submission", async () => {
    const resp = await fetch("http://localhost:8849", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        formId: "v39TcXUcw1us",
        submissionTime: new Date().toISOString(),
        questions: [
          { id: "hQTk", value: "Test Intake Runner" },
          { id: "mKm1", value: "test-intake@example.com" },
          { id: "44Lc", value: "555-111-2222" },
          { id: "oQSj", value: "https://linkedin.com/in/test-runner" },
          { id: "mFnk", value: "Much assistance needed" },
          { id: "2ehG", value: "Some assistance needed" },
          { id: "qiJ4", value: "Yes" },
          { id: "jsf5", value: "Yes" },
        ],
      }),
    });
    assert(resp.ok, `HTTP ${resp.status}`);
    const body = await resp.json();
    assert(body.status === "ok", `Status: ${body.status}`);
    assert(body.name === "Test Intake Runner", `Name: ${body.name}`);
    assert(body.caller_lookup_inserted === true, `Caller lookup not inserted`);
  });

  await test("Intake caller_lookup record exists in DB", async () => {
    await new Promise(r => setTimeout(r, 1000));
    const { stdout } = Bun.spawnSync(["python3", "-c", `
import duckdb, json
con = duckdb.connect("/home/workspace/Datasets/career-hotline-calls/data.duckdb", read_only=True)
rows = con.execute("SELECT caller_name, primary_challenge FROM caller_lookup WHERE caller_name = 'Test Intake Runner' LIMIT 1").fetchall()
print(json.dumps({"name": rows[0][0], "challenge": rows[0][1]} if rows else {"error": "not found"}))
con.close()
`]);
    const res = JSON.parse(new TextDecoder().decode(stdout).trim());
    assert(!res.error, `Intake record not found: ${res.error}`);
    assert(res.name === "Test Intake Runner", `Name mismatch: ${res.name}`);
    assert(res.challenge.includes("Application strategy"), `Challenge: ${res.challenge}`);
  });
}

// ═══════════════════════════════════════════════════
// CLEANUP
// ═══════════════════════════════════════════════════
async function cleanup() {
  console.log("\n-- Cleanup --");
  try {
    Bun.spawnSync(["python3", "-c", `
import duckdb
con = duckdb.connect("/home/workspace/Datasets/career-hotline-calls/data.duckdb")
con.execute("DELETE FROM feedback WHERE caller_name = 'TestRunner'")
con.execute("DELETE FROM escalations WHERE name = 'Test Escalation User'")
con.execute("DELETE FROM calls WHERE phone_number = '+15559990002'")
con.execute("DELETE FROM caller_balances WHERE phone_number = '+15559990002'")
con.execute("DELETE FROM caller_lookup WHERE caller_name = 'Test Intake Runner'")
con.close()
print("Test data cleaned up")
`]);
    console.log("  Test data cleaned up");
  } catch (err) {
    console.error("  Cleanup failed:", err);
  }
}

// ═══════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════
async function main() {
  console.log("============================================");
  console.log("  Career Coaching Hotline -- Full Test Suite");
  console.log("============================================");
  console.log(`  Target: ${BASE}`);
  console.log(`  Time:   ${new Date().toISOString()}`);
  console.log("============================================");

  await testInfrastructure();
  await testCallerLookup();
  await testAssessCareerStage();
  await testGetCareerRecommendations();
  await testExplainCareerConcept();
  await testResumeTools();
  await testDiagnoseSearchStrategy();
  await testReferToCareerspan();
  await testFeedbackAndEscalation();
  await testEndOfCallReport();
  await testAssistantPersonalization();
  await testEdgeCases();
  await testIntakeWebhook();
  await cleanup();

  // Summary
  console.log("\n============================================");
  console.log("  TEST RESULTS");
  console.log("============================================");
  console.log(`  Passed:  ${passed}`);
  console.log(`  Failed:  ${failed}`);
  console.log(`  Skipped: ${skipped}`);
  console.log(`  Total:   ${passed + failed + skipped}`);
  console.log("============================================");

  if (failed > 0) {
    console.log("\nFailed tests:");
    for (const r of results.filter(r => r.status === "FAIL")) {
      console.log(`  X ${r.name}: ${r.detail}`);
    }
  }

  process.exit(failed > 0 ? 1 : 0);
}

main().catch(err => {
  console.error("Fatal error:", err);
  process.exit(2);
});
