// Stage 4: Gap Analysis + Calibration
// Model: gpt-5.1 (deep reasoning for nuanced gap detection and calibration)

import { callOpenAI, MODELS } from "../openai";
import type { 
  Stage2Output, 
  Stage3Output, 
  Stage4Output,
  RequirementCoverage,
  CalibrationAnalysis,
  CoverageStatus,
  CalibrationDelta,
} from "../types/pipeline";

const STAGE4_SYSTEM_PROMPT = `You are an expert career coach analyzing interview performance. Your task is to:

1. **Gap Analysis**: Compare demonstrated competencies against job requirements
2. **Calibration**: Compare candidate's self-assessment against actual performance

## Gap Analysis Instructions

For each JD requirement, determine coverage status:
- **demonstrated**: Clear, specific evidence in their answers that they have this skill/experience
- **partially_covered**: Some evidence but incomplete, vague, or only tangentially related
- **not_addressed**: No evidence in their answers, or the topic wasn't covered

Map specific Q&A IDs to requirements as evidence. Be rigorous - only mark "demonstrated" if there's concrete proof.

## Calibration Instructions

Compare the candidate's self-assessment with what the interview evidence actually shows:

**Delta Categories:**
- **optimistic**: They think it went better than evidence suggests (common pattern: overlooking weaknesses, inflating performance)
- **realistic**: Their self-assessment aligns with the evidence (healthy self-awareness)
- **pessimistic**: They think it went worse than it actually did (common with anxious/humble candidates)

Look for specific mismatches between perception and reality. Be constructive but honest.

## Output Format (JSON)

{
  "requirementCoverage": [
    {
      "requirementId": "req_001",
      "requirement": "string - the requirement text",
      "status": "demonstrated" | "partially_covered" | "not_addressed",
      "evidenceQaIds": ["qa_001", "qa_003"],
      "evidenceSummary": "Brief description of how they demonstrated this (or why it's missing)"
    }
  ],
  "calibration": {
    "selfPerceptionSummary": "What the candidate said/implied about how the interview went",
    "actualPerformanceSummary": "What the evidence objectively shows about their performance",
    "delta": "optimistic" | "realistic" | "pessimistic",
    "insight": "A thoughtful, personalized observation about the gap between perception and reality. Be supportive but honest.",
    "specificMismatches": [
      {
        "theyThought": "What they believed",
        "actuallyWas": "What actually happened"
      }
    ]
  },
  "keyGaps": [
    "Top gap #1 - the most important competency or behavior to address",
    "Top gap #2",
    "Top gap #3"
  ]
}`;

export async function analyzeGapsAndCalibration(
  stage2: Stage2Output,
  stage3: Stage3Output,
  jobDescription: string,
  selfAssessment: string
): Promise<Stage4Output> {
  
  // Build context from previous stages
  const requirementsContext = stage2.jdRequirements.map(r => 
    `[${r.id}] ${r.requirement} (${r.category}, ${r.priority})`
  ).join("\n");
  
  const answerEvidenceContext = stage3.evaluatedAnswers
    .filter(ea => ea.grade !== "N/A") // Skip out-of-scope
    .map(ea => {
      const question = stage2.analyzedQuestions.find(q => q.qaId === ea.qaId);
      const mappedReqs = question?.jdRequirementsMapped?.join(", ") || "none";
      return `[${ea.qaId}] Grade: ${ea.grade} | Mapped to: ${mappedReqs}
  Strength: ${ea.strengthSummary}
  Improvement: ${ea.improvementSummary}`;
    }).join("\n\n");
  
  const performanceSummary = `
Overall Grade: ${stage3.averageGrade}
Green Flags: ${stage3.greenFlagCount}
Red Flags: ${stage3.redFlagCount}
6Q Profile: Problem ${stage3.overallSixQProfile.problem}% | Stakes ${stage3.overallSixQProfile.stakes}% | Thinking ${stage3.overallSixQProfile.thinking}% | Action ${stage3.overallSixQProfile.action}% | Result ${stage3.overallSixQProfile.result}% | Lesson ${stage3.overallSixQProfile.lesson}%`;

  const userPrompt = `## Job Description
${jobDescription}

## JD Requirements Extracted
${requirementsContext}

## Candidate's Self-Assessment
"${selfAssessment}"

## Answer Performance Evidence
${answerEvidenceContext}

## Overall Performance Summary
${performanceSummary}

---

Analyze the gaps between JD requirements and demonstrated competencies.
Then calibrate the candidate's self-perception against the actual evidence.
Identify the top 3 most important gaps for them to address.

Return your analysis as JSON.`;

  const response = await callOpenAI(
    STAGE4_SYSTEM_PROMPT,
    userPrompt,
    {
      model: MODELS.THINKING,
      jsonMode: true,
      maxTokens: 4000,
    }
  );

  if (!response.success) {
    throw new Error(`Stage 4 failed: ${response.error || "Unknown error"}`);
  }

  const content = response.raw || (typeof response.data === "string" ? response.data : JSON.stringify(response.data));
  if (!content) {
    throw new Error(`Stage 4 failed: No content returned`);
  }

  let parsed: {
    requirementCoverage: Array<{
      requirementId: string;
      requirement: string;
      status: string;
      evidenceQaIds: string[];
      evidenceSummary?: string;
    }>;
    calibration: {
      selfPerceptionSummary: string;
      actualPerformanceSummary: string;
      delta: string;
      insight: string;
      specificMismatches: Array<{ theyThought: string; actuallyWas: string }>;
    };
    keyGaps: string[];
  };

  try {
    parsed = JSON.parse(content);
  } catch (e) {
    throw new Error(`Stage 4 failed to parse JSON: ${content.substring(0, 200)}...`);
  }

  // Normalize coverage status
  const normalizedCoverage: RequirementCoverage[] = parsed.requirementCoverage.map(rc => ({
    requirementId: rc.requirementId,
    requirement: rc.requirement,
    status: normalizeCoverageStatus(rc.status),
    evidenceQaIds: rc.evidenceQaIds || [],
    evidenceSummary: rc.evidenceSummary,
  }));

  // Calculate coverage summary
  const demonstrated = normalizedCoverage.filter(r => r.status === "demonstrated").length;
  const partiallyCovered = normalizedCoverage.filter(r => r.status === "partially_covered").length;
  const notAddressed = normalizedCoverage.filter(r => r.status === "not_addressed").length;
  
  // Coverage percent = % of must-have requirements that are demonstrated
  const mustHaves = stage2.jdRequirements.filter(r => r.priority === "must-have");
  const mustHaveIds = new Set(mustHaves.map(r => r.id));
  const demonstratedMustHaves = normalizedCoverage.filter(
    r => mustHaveIds.has(r.requirementId) && r.status === "demonstrated"
  ).length;
  const coveragePercent = mustHaves.length > 0 
    ? Math.round((demonstratedMustHaves / mustHaves.length) * 100)
    : 100;

  // Normalize calibration
  const calibration: CalibrationAnalysis = {
    selfPerceptionSummary: parsed.calibration.selfPerceptionSummary,
    actualPerformanceSummary: parsed.calibration.actualPerformanceSummary,
    delta: normalizeCalibrationDelta(parsed.calibration.delta),
    insight: parsed.calibration.insight,
    specificMismatches: parsed.calibration.specificMismatches || [],
  };

  return {
    requirementCoverage: normalizedCoverage,
    coverageSummary: {
      demonstrated,
      partiallyCovered,
      notAddressed,
      coveragePercent,
    },
    calibration,
    keyGaps: parsed.keyGaps.slice(0, 3), // Ensure max 3
  };
}

function normalizeCoverageStatus(status: string): CoverageStatus {
  const normalized = status.toLowerCase().replace(/_/g, "_");
  if (normalized === "demonstrated" || normalized === "covered") return "demonstrated";
  if (normalized.includes("partial")) return "partially_covered";
  return "not_addressed";
}

function normalizeCalibrationDelta(delta: string): CalibrationDelta {
  const normalized = delta.toLowerCase();
  if (normalized.includes("optim")) return "optimistic";
  if (normalized.includes("pessim")) return "pessimistic";
  return "realistic";
}

