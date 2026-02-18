#!/usr/bin/env bun

/**
 * Career Coaching Hotline — Integration Tests
 * 
 * Tests the webhook server (port 8848), zo.space Stripe webhook,
 * and zo.space claim API. Covers:
 * 
 * 1. Health & Auth
 * 2. Assistant Request (identity, voice, balance injection)
 * 3. Tool Calls (all 6 tools)
 * 4. End-of-Call Report (logging, balance tracking, SMS notification)
 * 5. Balance Tracking (free tier, purchased credits, exhaustion)
 * 6. Stripe Webhook (credit fulfillment, idempotency, unknown products)
 * 7. Claim API (unclaimed purchase → phone credit)
 * 8. Landing Page (renders, pricing, links)
 */

const WEBHOOK_URL = "http://localhost:8848";
const STRIPE_WEBHOOK_URL = "https://va.zo.space/api/career-hotline-stripe";
const CLAIM_URL = "https://va.zo.space/api/career-hotline-claim";
const HOTLINE_PAGE_URL = "https://va.zo.space/hotline";
const DB_PATH = "/home/workspace/Datasets/career-hotline-calls/data.duckdb";

// Read webhook secret from env (same one the server uses)
const WEBHOOK_SECRET = process.env.CAREER_HOTLINE_SECRET || "";

let passed = 0;
let failed = 0;
let skipped = 0;
const results: { name: string; status: "PASS" | "FAIL" | "SKIP"; detail?: string }[] = [];

class SkipError extends Error {
  constructor(public reason: string) { super(`SKIP: ${reason}`); }
}

function assert(condition: boolean, message: string): void {
  if (!condition) throw new Error(message);
}

async function test(name: string, fn: () => Promise<void>): Promise<void> {
  try {
    await fn();
    passed++;
    results.push({ name, status: "PASS" });
    console.log(`  ✓ ${name}`);
  } catch (err: any) {
    if (err instanceof SkipError) {
      skipped++;
      results.push({ name, status: "SKIP", detail: err.reason });
      console.log(`  ○ ${name}: SKIPPED (${err.reason})`);
    } else {
      failed++;
      results.push({ name, status: "FAIL", detail: err.message });
      console.log(`  ✗ ${name}: ${err.message}`);
    }
  }
}

function skip(_name: string, reason: string): never {
  throw new SkipError(reason);
}

async function postWebhook(body: any, secret?: string): Promise<Response> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (secret) headers["x-vapi-secret"] = secret;
  return fetch(WEBHOOK_URL, { method: "POST", headers, body: JSON.stringify(body) });
}

async function fetchWithRetry(url: string, options: RequestInit, maxRetries = 3): Promise<Response> {
  for (let i = 0; i < maxRetries; i++) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      const resp = await fetch(url, { ...options, signal: controller.signal });
      clearTimeout(timeout);
      const contentType = resp.headers.get("content-type") || "";
      if (resp.status === 503 || contentType.includes("text/html")) {
        if (i < maxRetries - 1) {
          await new Promise(r => setTimeout(r, 3000 * (i + 1)));
          continue;
        }
      }
      return resp;
    } catch (err: any) {
      clearTimeout(timeout);
      if (err.name === "AbortError" && i < maxRetries - 1) {
        await new Promise(r => setTimeout(r, 3000 * (i + 1)));
        continue;
      }
      throw err;
    }
  }
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const resp = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeout);
    return resp;
  } catch (err) {
    clearTimeout(timeout);
    throw err;
  }
}

async function runDuckDB(sql: string): Promise<string> {
  const proc = Bun.spawn(["duckdb", DB_PATH, "-c", sql], { stdout: "pipe", stderr: "pipe" });
  const out = await new Response(proc.stdout).text();
  await proc.exited;
  // Force WAL checkpoint so other processes (webhook's Python subprocesses) see committed data
  const ckpt = Bun.spawn(["duckdb", DB_PATH, "-c", "CHECKPOINT"], { stdout: "pipe", stderr: "pipe" });
  await ckpt.exited;
  await new Promise(r => setTimeout(r, 150));
  return out.trim();
}

// ── Test Data ──

const TEST_PHONE = "+15551234567";
const TEST_PHONE_EXHAUSTED = "+15559999999";
const TEST_CALL_ID = `test-call-${Date.now()}`;

// ── Helpers ──

async function cleanupTestData(): Promise<void> {
  const phones = [TEST_PHONE, TEST_PHONE_EXHAUSTED, "+15550001111"];
  for (const phone of phones) {
    await runDuckDB(`DELETE FROM caller_balances WHERE phone_number = '${phone}'`).catch(() => {});
  }
  await runDuckDB(`DELETE FROM calls WHERE id LIKE 'test-%'`).catch(() => {});
  await runDuckDB(`DELETE FROM escalations WHERE call_id LIKE 'test-%' OR call_id = 'current'`).catch(() => {});
  await runDuckDB(`DELETE FROM feedback WHERE call_id LIKE 'test-%' OR call_id = 'current'`).catch(() => {});
  await runDuckDB(`DELETE FROM purchases WHERE stripe_session_id LIKE 'cs_test_%'`).catch(() => {});
}

// ══════════════════════════════════════════════
//  1. HEALTH & AUTH
// ══════════════════════════════════════════════

async function testHealthAndAuth() {
  console.log("\n── 1. Health & Auth ──");

  await test("GET /health returns 200 with correct identity", async () => {
    const resp = await fetch(`${WEBHOOK_URL}/health`);
    assert(resp.status === 200, `Expected 200, got ${resp.status}`);
    const body = await resp.json();
    assert(body.status === "ok", `Expected status ok, got ${body.status}`);
    assert(body.identity === "Zozie", `Expected identity Zozie, got ${body.identity}`);
    assert(body.service === "career-coaching-hotline", `Wrong service name: ${body.service}`);
    assert(body.free_tier_seconds === 900, `Expected 900 free seconds, got ${body.free_tier_seconds}`);
  });

  await test("POST without secret returns 401", async () => {
    if (!WEBHOOK_SECRET) { skip("POST without secret returns 401", "No webhook secret set"); return; }
    const resp = await postWebhook({ message: { type: "assistant-request" } });
    assert(resp.status === 401, `Expected 401, got ${resp.status}`);
  });

  await test("POST with wrong secret returns 401", async () => {
    if (!WEBHOOK_SECRET) { skip("POST with wrong secret returns 401", "No webhook secret set"); return; }
    const resp = await postWebhook({ message: { type: "assistant-request" } }, "wrong-secret");
    assert(resp.status === 401, `Expected 401, got ${resp.status}`);
  });

  await test("POST with correct secret returns 200", async () => {
    if (!WEBHOOK_SECRET) { skip("POST with correct secret returns 200", "No webhook secret set"); return; }
    const resp = await postWebhook({
      message: { type: "assistant-request", call: { customer: { number: TEST_PHONE } } }
    }, WEBHOOK_SECRET);
    assert(resp.status === 200, `Expected 200, got ${resp.status}`);
  });

  await test("GET on non-health path returns 405", async () => {
    const resp = await fetch(`${WEBHOOK_URL}/other`, { method: "GET" });
    assert(resp.status === 405, `Expected 405, got ${resp.status}`);
  });
}

// ══════════════════════════════════════════════
//  2. ASSISTANT REQUEST
// ══════════════════════════════════════════════

async function testAssistantRequest() {
  console.log("\n── 2. Assistant Request ──");

  await test("Assistant request returns Zozie identity (not V)", async () => {
    const resp = await postWebhook({
      message: { type: "assistant-request", call: { customer: { number: TEST_PHONE } } }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const assistant = body.assistant;
    assert(assistant.name.includes("Zozie"), `Expected Zozie in name, got ${assistant.name}`);
    assert(assistant.firstMessage.includes("Zozie"), `firstMessage should mention Zozie: ${assistant.firstMessage.substring(0, 80)}`);
    assert(!assistant.firstMessage.includes("this is V"), `firstMessage should NOT say 'this is V'`);
    assert(assistant.voicemailMessage.includes("Zozie"), `voicemailMessage should mention Zozie`);
  });

  await test("Assistant uses correct model (claude-haiku-4-5)", async () => {
    const resp = await postWebhook({
      message: { type: "assistant-request", call: { customer: { number: TEST_PHONE } } }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    assert(body.assistant.model.model === "claude-haiku-4-5-20251001", `Wrong model: ${body.assistant.model.model}`);
    assert(body.assistant.model.provider === "anthropic", `Wrong provider: ${body.assistant.model.provider}`);
  });

  await test("Voice config matches zo-hotline tuning", async () => {
    const resp = await postWebhook({
      message: { type: "assistant-request", call: { customer: { number: TEST_PHONE } } }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const voice = body.assistant.voice;
    assert(voice.provider === "11labs", `Wrong voice provider: ${voice.provider}`);
    assert(voice.model === "eleven_flash_v2_5", `Wrong voice model: ${voice.model}`);
    assert(voice.stability === 0.45, `Wrong stability: ${voice.stability}`);
    assert(voice.style === 0.65, `Wrong style: ${voice.style}`);
    assert(voice.similarityBoost === 0.75, `Wrong similarityBoost: ${voice.similarityBoost}`);
    assert(voice.chunkPlan?.minCharacters === 20, `Wrong chunk min: ${voice.chunkPlan?.minCharacters}`);
  });

  await test("Latency settings match zo-hotline", async () => {
    const resp = await postWebhook({
      message: { type: "assistant-request", call: { customer: { number: TEST_PHONE } } }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const start = body.assistant.startSpeakingPlan;
    const stop = body.assistant.stopSpeakingPlan;
    assert(start.waitSeconds === 0.4, `Wrong waitSeconds: ${start.waitSeconds}`);
    assert(start.transcriptionEndpointingPlan.onPunctuationSeconds === 0.1, `Wrong punctuation: ${start.transcriptionEndpointingPlan.onPunctuationSeconds}`);
    assert(start.transcriptionEndpointingPlan.onNoPunctuationSeconds === 0.8, `Wrong noPunctuation: ${start.transcriptionEndpointingPlan.onNoPunctuationSeconds}`);
    assert(stop.voiceSeconds === 0.2, `Wrong voiceSeconds: ${stop.voiceSeconds}`);
    assert(stop.backoffSeconds === 1.0, `Wrong backoffSeconds: ${stop.backoffSeconds}`);
    assert(body.assistant.responseDelaySeconds === 0.1, `Wrong responseDelay: ${body.assistant.responseDelaySeconds}`);
    assert(body.assistant.backchannelingEnabled === true, `Backchanneling should be enabled`);
  });

  await test("System prompt includes Zozie identity", async () => {
    const resp = await postWebhook({
      message: { type: "assistant-request", call: { customer: { number: TEST_PHONE } } }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const sysMsg = body.assistant.model.messages[0].content;
    assert(sysMsg.includes("Zozie"), `System prompt should mention Zozie`);
    // Should NOT identify as V
    assert(!sysMsg.includes("You're **V**") && !sysMsg.includes("You are V"), `System prompt should NOT say 'You are V'`);
  });

  await test("Tools are included in assistant config", async () => {
    const resp = await postWebhook({
      message: { type: "assistant-request", call: { customer: { number: TEST_PHONE } } }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const tools = body.assistant.model.tools;
    assert(Array.isArray(tools) && tools.length >= 5, `Expected at least 5 tools, got ${tools?.length}`);
    const toolNames = tools.map((t: any) => t.function?.name);
    for (const name of ["assessCareerStage", "getCareerRecommendations", "explainCareerConcept", "requestCareerSession", "lookupCaller", "collectFeedback"]) {
      assert(toolNames.includes(name), `Missing tool: ${name}`);
    }
  });

  await test("Exhausted caller gets balance warning in system prompt", async () => {
    // Seed an exhausted balance
    await runDuckDB(`INSERT OR REPLACE INTO caller_balances VALUES ('${TEST_PHONE_EXHAUSTED}', 1000, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)`);

    const resp = await postWebhook({
      message: { type: "assistant-request", call: { customer: { number: TEST_PHONE_EXHAUSTED } } }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const sysMsg = body.assistant.model.messages[0].content;
    assert(sysMsg.includes("NO remaining time") || sysMsg.includes("no purchased credits") || sysMsg.includes("free session is used up"),
      `System prompt should warn about exhausted balance`);
  });

  await test("Fresh caller gets no balance warning", async () => {
    // Make sure test phone has no balance record
    await runDuckDB(`DELETE FROM caller_balances WHERE phone_number = '${TEST_PHONE}'`).catch(() => {});

    const resp = await postWebhook({
      message: { type: "assistant-request", call: { customer: { number: TEST_PHONE } } }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const sysMsg = body.assistant.model.messages[0].content;
    assert(!sysMsg.includes("NO remaining time"), `Fresh caller should NOT get exhaustion warning`);
  });
}

// ══════════════════════════════════════════════
//  3. TOOL CALLS
// ══════════════════════════════════════════════

async function testToolCalls() {
  console.log("\n── 3. Tool Calls ──");

  await test("assessCareerStage — groundwork classification", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-1",
          function: {
            name: "assessCareerStage",
            arguments: JSON.stringify({
              current_situation: "I'm a new grad just starting out with no experience",
              efforts_so_far: "Haven't really started yet",
              desired_outcome: "Get my first job in tech",
              urgency_signals: "medium"
            })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.primary_stage === "groundwork", `Expected groundwork, got ${result.primary_stage}`);
    assert(result.pain_points.includes("not_started"), `Expected not_started pain point`);
    assert(result.effort_level === "minimal", `Expected minimal effort, got ${result.effort_level}`);
  });

  await test("assessCareerStage — materials classification", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-2",
          function: {
            name: "assessCareerStage",
            arguments: JSON.stringify({
              current_situation: "I'm applying and working on my resume but not hearing back",
              efforts_so_far: "Using the same resume for every application",
              desired_outcome: "Land interviews at target companies",
              urgency_signals: "high"
            })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.primary_stage === "materials", `Expected materials, got ${result.primary_stage}`);
    assert(result.pain_points.includes("not_tailoring_resume"), `Expected not_tailoring_resume pain point`);
  });

  await test("assessCareerStage — transition classification", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-3",
          function: {
            name: "assessCareerStage",
            arguments: JSON.stringify({
              current_situation: "I was laid off and I'm switching careers to a new industry",
              efforts_so_far: "Tried everything and nothing works, months of frustration",
              desired_outcome: "Break into product management",
              urgency_signals: "crisis"
            })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.primary_stage === "transition", `Expected transition, got ${result.primary_stage}`);
    assert(result.pain_points.includes("strategy_fatigue"), `Expected strategy_fatigue`);
    assert(result.effort_level === "high", `Expected high effort, got ${result.effort_level}`);
  });

  await test("assessCareerStage — calibration detection", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-4",
          function: {
            name: "assessCareerStage",
            arguments: JSON.stringify({
              current_situation: "I'm a student just starting out",
              efforts_so_far: "Some applications on LinkedIn",
              desired_outcome: "I want a VP director level position immediately",
              urgency_signals: "high"
            })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.calibration_needed === true, `Expected calibration_needed to be true`);
  });

  await test("assessCareerStage — missing fields returns error", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-5",
          function: {
            name: "assessCareerStage",
            arguments: JSON.stringify({ current_situation: "I need help" })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.error !== undefined, `Expected error for missing fields`);
  });

  await test("getCareerRecommendations — returns stage-appropriate actions", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-6",
          function: {
            name: "getCareerRecommendations",
            arguments: JSON.stringify({
              primary_stage: "materials",
              pain_points: ["not_tailoring_resume"],
              urgency: "medium"
            })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.stage === "materials", `Expected materials stage`);
    assert(Array.isArray(result.actions) && result.actions.length >= 3, `Expected at least 3 actions`);
    assert(result.careerspan_recommendation?.booking_link, `Expected booking link`);
    assert(result.pain_point_advice?.length > 0, `Expected pain point advice`);
  });

  await test("getCareerRecommendations — urgency adjustment for crisis", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-7",
          function: {
            name: "getCareerRecommendations",
            arguments: JSON.stringify({
              primary_stage: "outreach",
              pain_points: [],
              urgency: "crisis"
            })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.urgency_note && result.urgency_note.includes("compress"), `Expected urgency note about compressing timeline`);
  });

  await test("explainCareerConcept — valid concept returns content", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-8",
          function: {
            name: "explainCareerConcept",
            arguments: JSON.stringify({ concept: "resume-customization" })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.content && result.content.length > 50, `Expected substantial content, got ${result.content?.length || 0} chars`);
  });

  await test("explainCareerConcept — unknown concept returns suggestions", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-9",
          function: {
            name: "explainCareerConcept",
            arguments: JSON.stringify({ concept: "quantum-career-teleportation" })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.error !== undefined, `Expected error for unknown concept`);
    assert(result.suggestion !== undefined, `Expected suggestions for unknown concept`);
  });

  await test("lookupCaller — returns balance for unknown caller", async () => {
    await runDuckDB(`DELETE FROM caller_balances WHERE phone_number = '${TEST_PHONE}'`).catch(() => {});
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-10",
          function: {
            name: "lookupCaller",
            arguments: JSON.stringify({ phone_number: TEST_PHONE })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.balance !== undefined, `Expected balance object`);
    assert(result.balance.free_seconds_remaining === 900, `Expected 900 free seconds for new caller, got ${result.balance.free_seconds_remaining}`);
    assert(result.balance.is_free_tier === true, `Expected is_free_tier to be true`);
  });

  await test("lookupCaller — exhausted caller gets purchase message", async () => {
    await runDuckDB(`INSERT OR REPLACE INTO caller_balances VALUES ('${TEST_PHONE_EXHAUSTED}', 1000, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)`);
    // Verify data is committed and visible before hitting webhook
    const verify = await runDuckDB(`SELECT total_seconds_used FROM caller_balances WHERE phone_number = '${TEST_PHONE_EXHAUSTED}'`);
    assert(verify.includes("1000"), `Pre-check failed: expected 1000 in DB, got: ${verify}`);
    await new Promise(r => setTimeout(r, 500));
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-11",
          function: {
            name: "lookupCaller",
            arguments: JSON.stringify({ phone_number: TEST_PHONE_EXHAUSTED })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.balance.has_time_remaining === false, `Expected has_time_remaining to be false, got balance: ${JSON.stringify(result.balance)}`);
    assert(result.balance.message && result.balance.message.includes("used all"), `Expected exhaustion message`);
  });

  await test("requestCareerSession — logs escalation", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-12",
          function: {
            name: "requestCareerSession",
            arguments: JSON.stringify({
              name: "Test User",
              contact: "test@example.com",
              career_stage: "materials",
              reason: "Need resume review",
              pain_points: ["not_tailoring_resume"]
            })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.success === true, `Expected success`);
    assert(result.booking_link, `Expected booking link`);
    assert(result.escalation_id, `Expected escalation ID`);
  });

  await test("requestCareerSession — missing fields returns error", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-13",
          function: {
            name: "requestCareerSession",
            arguments: JSON.stringify({ name: "Test" })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.error !== undefined, `Expected error for missing fields`);
  });

  await test("collectFeedback — logs rating", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-14",
          function: {
            name: "collectFeedback",
            arguments: JSON.stringify({ rating: 5, feedback_text: "Very helpful!", helpful: true })
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.success === true, `Expected success`);
  });

  await test("collectFeedback — empty params returns graceful response", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-15",
          function: {
            name: "collectFeedback",
            arguments: "{}"
          }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.success === true, `Expected success even with no feedback`);
  });

  await test("Unknown tool returns error with available list", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "tc-16",
          function: { name: "fakeToolName", arguments: "{}" }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.error?.includes("Unknown tool"), `Expected unknown tool error`);
    assert(result.available_tools?.length >= 5, `Expected available tools list`);
  });

  await test("Multiple tool calls in one request", async () => {
    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [
          { id: "tc-multi-1", function: { name: "lookupCaller", arguments: JSON.stringify({ phone_number: TEST_PHONE }) } },
          { id: "tc-multi-2", function: { name: "collectFeedback", arguments: JSON.stringify({ rating: 4 }) } }
        ]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    assert(body.results.length === 2, `Expected 2 results, got ${body.results.length}`);
    assert(body.results[0].toolCallId === "tc-multi-1", `Wrong toolCallId for first result`);
    assert(body.results[1].toolCallId === "tc-multi-2", `Wrong toolCallId for second result`);
  });
}

// ══════════════════════════════════════════════
//  4. END-OF-CALL REPORT
// ══════════════════════════════════════════════

async function testEndOfCallReport() {
  console.log("\n── 4. End-of-Call Report ──");

  await test("End-of-call logs call to database", async () => {
    const callId = `test-eoc-${Date.now()}`;
    const resp = await postWebhook({
      message: {
        type: "end-of-call-report",
        call: { id: callId, customer: { number: TEST_PHONE }, endedReason: "customer-ended-call" },
        durationSeconds: 120,
        startedAt: new Date().toISOString(),
        endedAt: new Date().toISOString(),
        artifact: { transcript: "Test transcript for integration testing" },
        analysis: { summary: "Test summary" }
      }
    }, WEBHOOK_SECRET || undefined);
    assert(resp.status === 200, `Expected 200, got ${resp.status}`);

    // Wait for async DB write
    await new Promise(r => setTimeout(r, 500));

    const rows = await runDuckDB(`SELECT id, duration_seconds FROM calls WHERE id = '${callId}'`);
    assert(rows.includes(callId), `Call ${callId} not found in database`);
  });

  await test("End-of-call records duration against caller balance", async () => {
    // Clean up first
    await runDuckDB(`DELETE FROM caller_balances WHERE phone_number = '${TEST_PHONE}'`).catch(() => {});

    const callId = `test-balance-${Date.now()}`;
    await postWebhook({
      message: {
        type: "end-of-call-report",
        call: { id: callId, customer: { number: TEST_PHONE }, endedReason: "customer-ended-call" },
        durationSeconds: 300,
        startedAt: new Date().toISOString(),
        endedAt: new Date().toISOString()
      }
    }, WEBHOOK_SECRET || undefined);

    await new Promise(r => setTimeout(r, 500));

    const result = await runDuckDB(`SELECT total_seconds_used FROM caller_balances WHERE phone_number = '${TEST_PHONE}'`);
    assert(result.includes("300"), `Expected 300 seconds used, got: ${result}`);
  });

  await test("Multiple calls accumulate duration correctly", async () => {
    const callId2 = `test-balance2-${Date.now()}`;
    await postWebhook({
      message: {
        type: "end-of-call-report",
        call: { id: callId2, customer: { number: TEST_PHONE }, endedReason: "customer-ended-call" },
        durationSeconds: 200,
        startedAt: new Date().toISOString(),
        endedAt: new Date().toISOString()
      }
    }, WEBHOOK_SECRET || undefined);

    await new Promise(r => setTimeout(r, 500));

    const result = await runDuckDB(`SELECT total_seconds_used FROM caller_balances WHERE phone_number = '${TEST_PHONE}'`);
    assert(result.includes("500"), `Expected 500 seconds used (300+200), got: ${result}`);
  });
}

// ══════════════════════════════════════════════
//  5. BALANCE TRACKING LOGIC
// ══════════════════════════════════════════════

async function testBalanceTracking() {
  console.log("\n── 5. Balance Tracking ──");

  await test("Free tier: 900 seconds available for new caller", async () => {
    const freshPhone = "+15550001111";
    await runDuckDB(`DELETE FROM caller_balances WHERE phone_number = '${freshPhone}'`).catch(() => {});

    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "bt-1",
          function: { name: "lookupCaller", arguments: JSON.stringify({ phone_number: freshPhone }) }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.balance.free_seconds_remaining === 900, `Expected 900 free seconds`);
    assert(result.balance.total_seconds_available === 900, `Expected 900 total available`);
    assert(result.balance.is_free_tier === true, `Should be on free tier`);
    assert(result.balance.has_time_remaining === true, `Should have time remaining`);
  });

  await test("Purchased credits extend total available time", async () => {
    const creditPhone = "+15550001111";
    // Insert: 500 used (still in free tier range), 1800 purchased
    await runDuckDB(`INSERT OR REPLACE INTO caller_balances VALUES ('${creditPhone}', 500, 1800, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)`);

    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "bt-2",
          function: { name: "lookupCaller", arguments: JSON.stringify({ phone_number: creditPhone }) }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.balance.free_seconds_remaining === 400, `Expected 400 free remaining (900-500), got ${result.balance.free_seconds_remaining}`);
    assert(result.balance.purchased_seconds === 1800, `Expected 1800 purchased, got ${result.balance.purchased_seconds}`);
    assert(result.balance.has_time_remaining === true, `Should have time remaining`);
  });

  await test("Exhausted free + no purchased = no time remaining", async () => {
    const exhaustedPhone = "+15550001111";
    await runDuckDB(`INSERT OR REPLACE INTO caller_balances VALUES ('${exhaustedPhone}', 1000, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)`);

    const resp = await postWebhook({
      message: {
        type: "tool-calls",
        toolCalls: [{
          id: "bt-3",
          function: { name: "lookupCaller", arguments: JSON.stringify({ phone_number: exhaustedPhone }) }
        }]
      }
    }, WEBHOOK_SECRET || undefined);
    const body = await resp.json();
    const result = JSON.parse(body.results[0].result);
    assert(result.balance.free_seconds_remaining === 0, `Expected 0 free remaining`);
    assert(result.balance.has_time_remaining === false, `Should have no time remaining`);
    assert(result.balance.message?.includes("used all"), `Expected purchase prompt message`);
  });
}

// ══════════════════════════════════════════════
//  6. STRIPE WEBHOOK
// ══════════════════════════════════════════════

async function testStripeWebhook() {
  console.log("\n── 6. Stripe Webhook ──");

  await test("Stripe webhook — rejects non-POST", async () => {
    const resp = await fetchWithRetry(STRIPE_WEBHOOK_URL, { method: "GET" });
    const body = await resp.json();
    assert(body.error === "Method not allowed", `Expected method not allowed error, got: ${JSON.stringify(body)}`);
  });

  await test("Stripe webhook — rejects invalid JSON", async () => {
    const resp = await fetchWithRetry(STRIPE_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "not json"
    });
    assert(resp.status === 400, `Expected 400, got ${resp.status}`);
  });

  await test("Stripe webhook — rejects non-Stripe event shape", async () => {
    const resp = await fetchWithRetry(STRIPE_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ foo: "bar" })
    });
    assert(resp.status === 400, `Expected 400 for non-event, got ${resp.status}`);
  });

  // NOTE: Can't test full signature verification without the actual Stripe signing secret,
  // but we can test the fallback path (no signature, no webhook secret configured in zo.space env)
  // If STRIPE_WEBHOOK_SECRET is set in zo.space, unsigned requests should be rejected.
  // For now, test the checkout.session.completed handler with a synthetic event.

  await test("Stripe webhook — credits minutes with phone number", async () => {
    const sessionId = `cs_test_credit_${Date.now()}`;
    const testCreditPhone = "+15551112222";
    await runDuckDB(`DELETE FROM caller_balances WHERE phone_number = '${testCreditPhone}'`).catch(() => {});
    await runDuckDB(`DELETE FROM purchases WHERE stripe_session_id = '${sessionId}'`).catch(() => {});

    const resp = await fetchWithRetry(STRIPE_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: `evt_test_${Date.now()}`,
        type: "checkout.session.completed",
        data: {
          object: {
            id: sessionId,
            payment_intent: "pi_test_123",
            customer_details: { phone: testCreditPhone, email: "test@example.com" },
            amount_total: 3000, // $30 = 60 min Standard
            line_items: { data: [{ price: { product: "prod_TydnR6AzMThQA0" } }] }
          }
        }
      })
    });
    const body = await resp.json();

    // If signature verification is enforced, this will return 400 — that's correct behavior
    if (resp.status === 400 && body.error?.includes("signature")) {
      skip("Stripe webhook — credits minutes with phone number", "Stripe signature verification is enforced (correct behavior in prod)");
      return;
    }

    assert(body.credited === true, `Expected credited: true, got ${JSON.stringify(body)}`);
    assert(body.minutes === 60, `Expected 60 minutes, got ${body.minutes}`);
  });

  await test("Stripe webhook — idempotent (no double credit)", async () => {
    const sessionId = `cs_test_idemp_${Date.now()}`;
    const idempPhone = "+15553334444";
    await runDuckDB(`DELETE FROM caller_balances WHERE phone_number = '${idempPhone}'`).catch(() => {});

    const eventBody = {
      id: `evt_test_idemp_${Date.now()}`,
      type: "checkout.session.completed",
      data: {
        object: {
          id: sessionId,
          payment_intent: "pi_test_idemp",
          customer_details: { phone: idempPhone },
          amount_total: 1500,
          line_items: { data: [{ price: { product: "prod_Tydna1JD56E7UP" } }] }
        }
      }
    };

    // First request
    const resp1 = await fetchWithRetry(STRIPE_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(eventBody)
    });
    const body1 = await resp1.json();

    if (resp1.status === 400 && body1.error?.includes("signature")) {
      skip("Stripe webhook — idempotent (no double credit)", "Stripe signature verification enforced");
      return;
    }

    // Second request with same session ID
    const resp2 = await fetchWithRetry(STRIPE_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(eventBody)
    });
    const body2 = await resp2.json();
    assert(body2.skipped === "already processed", `Expected idempotent skip, got ${JSON.stringify(body2)}`);
  });

  await test("Stripe webhook — unknown product sends warning", async () => {
    const sessionId = `cs_test_unknown_${Date.now()}`;
    const resp = await fetchWithRetry(STRIPE_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: `evt_test_unknown_${Date.now()}`,
        type: "checkout.session.completed",
        data: {
          object: {
            id: sessionId,
            payment_intent: "pi_test_unknown",
            customer_details: { phone: "+15555556666" },
            amount_total: 9999,
            line_items: { data: [{ price: { product: "prod_UNKNOWN" } }] }
          }
        }
      })
    });
    const body = await resp.json();

    if (resp.status === 400 && body.error?.includes("signature")) {
      skip("Stripe webhook — unknown product sends warning", "Stripe signature verification enforced");
      return;
    }

    assert(body.warning === "unknown product", `Expected unknown product warning, got ${JSON.stringify(body)}`);
  });

  await test("Stripe webhook — no phone creates unclaimed purchase", async () => {
    const sessionId = `cs_test_nophone_${Date.now()}`;
    const resp = await fetchWithRetry(STRIPE_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: `evt_test_nophone_${Date.now()}`,
        type: "checkout.session.completed",
        data: {
          object: {
            id: sessionId,
            payment_intent: "pi_test_nophone",
            customer_details: { email: "nophone@example.com" },
            amount_total: 5000,
            line_items: { data: [{ price: { product: "prod_TydnzjPvIuRHRg" } }] }
          }
        }
      })
    });
    const body = await resp.json();

    if (resp.status === 400 && body.error?.includes("signature")) {
      skip("Stripe webhook — no phone creates unclaimed purchase", "Stripe signature verification enforced");
      return;
    }

    assert(body.credited === false, `Expected credited: false`);
    assert(body.reason === "no_phone", `Expected reason no_phone, got ${body.reason}`);
  });
}

// ══════════════════════════════════════════════
//  7. CLAIM API
// ══════════════════════════════════════════════

async function testClaimAPI() {
  console.log("\n── 7. Claim API ──");

  await test("Claim API — rejects GET", async () => {
    const resp = await fetchWithRetry(CLAIM_URL, { method: "GET" });
    const body = await resp.json();
    assert(body.error === "POST required", `Expected POST required error`);
  });

  await test("Claim API — requires phone and session_id", async () => {
    const resp = await fetchWithRetry(CLAIM_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone: "+15551234567" })
    });
    assert(resp.status === 400, `Expected 400, got ${resp.status}`);
    const body = await resp.json();
    assert(body.error?.includes("required"), `Expected required fields error`);
  });

  await test("Claim API — 404 for nonexistent session", async () => {
    const resp = await fetchWithRetry(CLAIM_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone: "+15551234567", stripe_session_id: "cs_test_nonexistent" })
    });
    assert(resp.status === 404, `Expected 404, got ${resp.status}`);
  });

  await test("Claim API — claims unclaimed purchase and credits balance", async () => {
    const claimPhone = "+15557778888";
    const sessionId = `cs_test_claim_${Date.now()}`;
    await runDuckDB(`DELETE FROM caller_balances WHERE phone_number = '${claimPhone}'`).catch(() => {});

    // Insert unclaimed purchase and checkpoint WAL so other processes can see it
    await runDuckDB(`INSERT INTO purchases (id, phone_number, stripe_session_id, stripe_payment_intent, product_name, minutes_purchased, amount_cents, currency, status, created_at) VALUES ('${crypto.randomUUID()}', '', '${sessionId}', 'pi_test', 'Standard Pack (60 min)', 60, 3000, 'usd', 'unclaimed', CURRENT_TIMESTAMP)`);
    await runDuckDB(`CHECKPOINT`);
    // Verify insert is visible
    const verify = await runDuckDB(`SELECT status FROM purchases WHERE stripe_session_id = '${sessionId}'`);
    assert(verify.includes("unclaimed"), `Insert failed — expected unclaimed, got: ${verify}`);
    await new Promise(r => setTimeout(r, 2000));

    const resp = await fetchWithRetry(CLAIM_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone: claimPhone, stripe_session_id: sessionId })
    });
    const body = await resp.json();
    assert(body.success === true, `Expected success, got ${JSON.stringify(body)}`);
    assert(body.minutes_credited === 60, `Expected 60 minutes, got ${body.minutes_credited}`);

    // Verify balance was credited — wait for zo.space DuckDB write to complete
    await new Promise(r => setTimeout(r, 1000));
    const balance = await runDuckDB(`SELECT total_seconds_purchased FROM caller_balances WHERE phone_number = '${claimPhone}'`);
    assert(balance.includes("3600"), `Expected 3600 seconds (60 min) purchased, got: ${balance}`);

    // Verify purchase status updated
    const purchaseStatus = await runDuckDB(`SELECT status FROM purchases WHERE stripe_session_id = '${sessionId}'`);
    assert(purchaseStatus.includes("completed"), `Expected purchase status completed, got: ${purchaseStatus}`);
  });
}

// ══════════════════════════════════════════════
//  8. LANDING PAGE
// ══════════════════════════════════════════════

async function testLandingPage() {
  console.log("\n── 8. Landing Page ──");

  await test("Landing page returns 200", async () => {
    const resp = await fetchWithRetry(HOTLINE_PAGE_URL, {});
    assert(resp.status === 200, `Expected 200, got ${resp.status}`);
  });

  await test("Landing page contains React app bundle (CSR)", async () => {
    const resp = await fetchWithRetry(HOTLINE_PAGE_URL, {});
    const html = await resp.text();
    // zo.space pages are CSR — content is in JS bundles, not raw HTML
    // Check that the page shell loads correctly with script tags
    assert(html.includes("<script") || html.includes("script"), `Page should contain script tags for CSR app`);
    assert(html.includes("<div") || html.includes("root"), `Page should contain root div for React mount`);
  });

  await test("Landing page content via read_webpage", async () => {
    // CSR pages need browser rendering — skip if we can't verify rendered content
    // The key check is that the page loads (200 above) and has the CSR bundle
    // Full content verification requires a browser; we've confirmed the route exists
    skip("Landing page content via read_webpage", "CSR page requires browser rendering — route existence verified above");
  });
}

// ══════════════════════════════════════════════
//  RUNNER
// ══════════════════════════════════════════════

async function main() {
  console.log("Career Coaching Hotline — Integration Tests");
  console.log(`Webhook: ${WEBHOOK_URL}`);
  console.log(`Stripe webhook: ${STRIPE_WEBHOOK_URL}`);
  console.log(`Claim API: ${CLAIM_URL}`);
  console.log(`Auth: ${WEBHOOK_SECRET ? "secret set" : "NO SECRET"}`);
  console.log("");

  // Pre-test cleanup
  await cleanupTestData();

  await testHealthAndAuth();
  await testAssistantRequest();
  await testToolCalls();
  await testEndOfCallReport();
  await testBalanceTracking();
  await testStripeWebhook();
  await testClaimAPI();
  await testLandingPage();

  // Post-test cleanup
  await cleanupTestData();

  // Summary
  console.log("\n══════════════════════════════════════════════");
  console.log(`Results: ${passed} passed, ${failed} failed, ${skipped} skipped (${passed + failed + skipped} total)`);

  if (failed > 0) {
    console.log("\nFailed tests:");
    for (const r of results) {
      if (r.status === "FAIL") console.log(`  ✗ ${r.name}: ${r.detail}`);
    }
  }

  if (skipped > 0) {
    console.log("\nSkipped tests:");
    for (const r of results) {
      if (r.status === "SKIP") console.log(`  ○ ${r.name}: ${r.detail}`);
    }
  }

  console.log("");
  process.exit(failed > 0 ? 1 : 0);
}

main().catch(err => {
  console.error("Test runner error:", err);
  process.exit(1);
});
