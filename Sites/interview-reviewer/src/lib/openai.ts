import OpenAI from "openai";
import { readFileSync } from "fs";
import { join } from "path";

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

if (!OPENAI_API_KEY) {
  console.warn("⚠️  OPENAI_API_KEY not set - Analysis features disabled");
}

const openai = OPENAI_API_KEY ? new OpenAI({ apiKey: OPENAI_API_KEY }) : null;

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

function buildSystemPrompt(company: string, sentiment: string): string {
  const feelingContext =
    sentiment === "positive"
      ? "The candidate felt the interview went well."
      : "The candidate felt uncertain or that the interview didn't go well.";

  return `You are an expert career coach with over a decade of experience helping professionals succeed in interviews. You have helped hundreds of candidates land jobs at top companies.

## Your Task
Analyze the following interview transcript and provide actionable, specific feedback. The candidate interviewed at ${company}. ${feelingContext}

## Reference Framework
${COACHING_REFERENCE}

## Output Format
Structure your feedback as follows:

### Overall Assessment
A brief (2-3 sentence) summary of how the interview went.

### What Went Well
3-5 specific things the candidate did effectively, with quotes from the transcript.

### Areas for Improvement
3-5 specific areas where the candidate could improve, with concrete suggestions.

### Key Moments
2-3 pivotal moments in the interview that significantly impacted the outcome (positively or negatively).

### Actionable Next Steps
3-5 specific actions the candidate should take for their next interview.

### Prediction
Based on this transcript, your honest assessment of likely outcome and why.

## Guidelines
- Be direct and honest, but constructive
- Use specific quotes from the transcript to support your points
- Focus on what's actionable—things they can actually change
- Consider both content (what was said) and delivery (how it was said, if evident)
- Don't sugarcoat, but don't be harsh either—be a supportive coach`;
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
  sentiment: string
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
    const systemPrompt = buildSystemPrompt(company, sentiment);

    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        { role: "system", content: systemPrompt },
        {
          role: "user",
          content: `Here is the interview transcript to analyze:\n\n${transcript}`,
        },
      ],
      temperature: 0.7,
      max_tokens: 2500,
    });

    const report = response.choices[0]?.message?.content || "";

    // Extract a brief summary (first paragraph of Overall Assessment)
    const summaryMatch = report.match(
      /### Overall Assessment\n+([\s\S]*?)(?=\n###|$)/
    );
    const summary = summaryMatch
      ? summaryMatch[1].trim().slice(0, 500)
      : "Analysis complete.";

    return {
      success: true,
      report,
      summary,
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

