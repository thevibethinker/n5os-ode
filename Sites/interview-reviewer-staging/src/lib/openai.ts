import OpenAI from "openai";
import { readFileSync } from "fs";
import { join } from "path";

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

if (!OPENAI_API_KEY) {
  console.warn("⚠️  OPENAI_API_KEY not set - Analysis features disabled");
}

const openai = OPENAI_API_KEY ? new OpenAI({ apiKey: OPENAI_API_KEY }) : null;

// ============ Model Constants ============
export const MODELS = {
  FAST: "gpt-5-mini",        // Stage 1: extraction (using gpt-5-mini; gpt-5.1-mini not yet available)
  THINKING: "gpt-5.1",       // Stages 2-5: reasoning
} as const;

export type ModelName = typeof MODELS[keyof typeof MODELS];

// ============ Generic OpenAI Call ============
export interface OpenAICallResult<T = string> {
  success: boolean;
  data?: T;
  raw?: string;
  error?: string;
  tokensUsed?: {
    input: number;
    output: number;
  };
  durationMs: number;
  model: string;
}

export interface OpenAICallOptions {
  model?: ModelName;
  temperature?: number;
  maxTokens?: number;
  jsonMode?: boolean;
}

export async function callOpenAI<T = string>(
  systemPrompt: string,
  userPrompt: string,
  options: OpenAICallOptions = {}
): Promise<OpenAICallResult<T>> {
  const startTime = Date.now();
  const model = options.model || MODELS.THINKING;
  
  if (!openai) {
    return {
      success: false,
      error: "OpenAI not configured",
      durationMs: Date.now() - startTime,
      model,
    };
  }

  try {
    const response = await openai.chat.completions.create({
      model,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
      ],
      ...(model === MODELS.FAST ? {} : { temperature: options.temperature ?? 0.3 }),
      max_completion_tokens: options.maxTokens ?? 4096,
      ...(options.jsonMode && { response_format: { type: "json_object" } }),
    });

    const content = response.choices[0]?.message?.content || "";
    const tokensUsed = response.usage ? {
      input: response.usage.prompt_tokens,
      output: response.usage.completion_tokens,
    } : undefined;

    // If JSON mode, parse the response
    let data: T | undefined;
    if (options.jsonMode) {
      try {
        data = JSON.parse(content) as T;
      } catch (parseError) {
        return {
          success: false,
          error: `JSON parse error: ${parseError}`,
          raw: content,
          durationMs: Date.now() - startTime,
          model,
          tokensUsed,
        };
      }
    } else {
      data = content as unknown as T;
    }

    return {
      success: true,
      data,
      raw: content,
      tokensUsed,
      durationMs: Date.now() - startTime,
      model,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "OpenAI call failed",
      durationMs: Date.now() - startTime,
      model,
    };
  }
}

// ============ Legacy: Single-Shot Analysis ============
// NOTE: This function is kept for backward compatibility during Phase 8 migration.
// Once the pipeline is complete, this will be deprecated.

// Load coaching reference content
function loadCoachingReference(): string {
  try {
    const path = join(import.meta.dir, "../content/coaching-reference.md");
    return readFileSync(path, "utf-8");
  } catch (error) {
    console.error("Failed to load coaching reference:", error);
    return "Use general career coaching best practices.";
  }
}

const COACHING_REFERENCE = loadCoachingReference();

function buildSystemPrompt(
  company: string,
  selfAssessment: string,
  jobDescription: string
): string {
  const calibrationContext = `
## Candidate Self-Assessment
The candidate shared how they felt the interview went:

<self_assessment>
${selfAssessment}
</self_assessment>

Use this to:
1. **Calibrate Perception:** Compare their self-assessment against what actually happened in the transcript.
2. **Surface Blind Spots:** Are they being too hard on themselves? Too optimistic? Missing key moments?
3. **Provide Calibration Insight:** In your output, include a "Calibration Check" that gently addresses the gap between perception and reality.
`;

  const jdSection = `
## Job Description Analysis
The candidate has provided the job description for this role. Use it to:
1. **Identify Key Requirements:** Extract the 3-5 must-have competencies.
2. **Map Questions to Requirements:** For each interview question, infer which requirement it was probing.
3. **Score Alignment:** Assess whether the candidate's answers demonstrated the specific competencies this role needs.
4. **Surface Gaps:** Call out any critical requirements that weren't addressed in the interview.

<job_description>
${jobDescription}
</job_description>
`;

  return `You are **Vrijen's Career Brain** (The "Am I Hired?" Coach).

You are an expert career coach with over a decade of experience. You have a very specific voice: professional yet relaxed, authoritative but approachable, and "cleverly insightful."

## Your Mission
Analyze the interview transcript below for a candidate applying to **${company}**. ${calibrationContext}

${jdSection}

## Your Coaching "Brain" (Reference Material)
Use the following frameworks and rubrics to evaluate the candidate. STRICTLY ADHERE to these principles.

${COACHING_REFERENCE}

## Analysis Protocol

### Phase 1: Question-by-Question Analysis
For each interview question:
1. **Identify the question type** (Behavioral, Situational, Technical, Motivational, Self-Assessment)
2. **Infer interviewer intent** — What were they really trying to learn?
3. **Apply the 6-Point Rubric** (if behavioral) — Which elements were present/missing?
4. **Flag Red Flags** — Use RF-codes when detected (e.g., "RF-3: Judgment Gap")
5. **Note Green Flags** — Use GF-codes when excellence appears

### Phase 2: Composite Assessment
- Which of the Four Pillars (Competence, Character, Chemistry, Trajectory) did the candidate demonstrate well?
- Which were weak or missing?
- Given the role type (if JD provided), were the right pillars emphasized?

### Phase 3: Verdict
- Predict outcome with reasoning grounded in the framework
- Identify the #1 actionable improvement

## Output Format (HTML)
Return your feedback as clean HTML (no markdown fences, just the inner HTML tags). Use this structure:

<div class="space-y-6">
  <section class="assessment">
    <h3 class="text-xl font-bold text-gray-900 mb-2">The Bottom Line</h3>
    <p class="text-gray-700">Start with a direct, honest summary (2-3 sentences). Don't bury the lead.</p>
  </section>

  <section class="wins">
    <h3 class="text-xl font-bold text-green-700 mb-2">Green Flags (What Worked)</h3>
    <ul class="list-disc pl-5 space-y-2 text-gray-700">
      <li><strong>[GF-Code: Principle Name]:</strong> Specific quote or moment. Why it worked.</li>
    </ul>
  </section>

  <section class="improvements">
    <h3 class="text-xl font-bold text-amber-700 mb-2">Red Flags (Improvement Areas)</h3>
    <ul class="list-disc pl-5 space-y-2 text-gray-700">
      <li><strong>[RF-Code: Pattern Name]:</strong> Specific moment. What was missing. How to fix it.</li>
    </ul>
  </section>

  <section class="framework-analysis">
    <h3 class="text-xl font-bold text-gray-900 mb-2">The 6-Point Check (Key Behavioral Answers)</h3>
    <div class="bg-gray-50 p-4 rounded-lg text-sm">
      <p class="font-medium mb-2">For your strongest behavioral answer:</p>
      <ul class="space-y-1">
        <li>☑/☐ Problem clearly defined</li>
        <li>☑/☐ Stakes articulated</li>
        <li>☑/☐ Thinking/reasoning explained</li>
        <li>☑/☐ Individual actions specified ("I" not "we")</li>
        <li>☑/☐ Results quantified</li>
        <li>☑/☐ Lesson included</li>
      </ul>
      <p class="mt-2 text-gray-600">Missing element? That's your focus for next time.</p>
    </div>
  </section>

  <section class="prediction">
    <h3 class="text-xl font-bold text-gray-900 mb-2">The Verdict</h3>
    <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
      <p class="font-medium text-lg">Prediction: [Likely Offer / Toss-up / Likely Rejection]</p>
      <p class="text-gray-600 mt-1">Reasoning based on the Composite Candidate model and role fit.</p>
    </div>
  </section>

  <section class="priority">
    <h3 class="text-xl font-bold text-blue-700 mb-2">Your #1 Priority Fix</h3>
    <p class="text-gray-700 font-medium">One concrete, actionable thing to focus on before your next interview.</p>
  </section>
</div>

Remember: Be direct, be specific, cite the framework. Help them understand WHY, not just WHAT.
`;
}

export interface AnalysisResult {
  success: boolean;
  report: string;
  summary: string;
  error?: string;
}

export async function analyzeInterview(
  transcript: string,
  company: string,
  selfAssessment: string,
  jobDescription: string
): Promise<AnalysisResult> {
  if (!openai) {
    return {
      success: false,
      report: "",
      summary: "",
      error: "OpenAI not configured",
    };
  }

  try {
    const systemPrompt = buildSystemPrompt(company, selfAssessment, jobDescription);

    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        { role: "system", content: systemPrompt },
        {
          role: "user",
          content: `[TRANSCRIPT START]\n${transcript}\n[TRANSCRIPT END]`,
        },
      ],
      temperature: 0.7,
      max_tokens: 3000,
    });

    const report = response.choices[0]?.message?.content || "";

    // Extract a plain text summary for the DB (strip HTML tags)
    const summaryText =
      report
        .replace(/<[^>]*>/g, " ")
        .slice(0, 300)
        .trim() + "...";

    return {
      success: true,
      report,
      summary: summaryText,
    };
  } catch (error) {
    console.error("Analysis failed:", error);
    return {
      success: false,
      report: "",
      summary: "",
      error: error instanceof Error ? error.message : "Analysis failed",
    };
  }
}






