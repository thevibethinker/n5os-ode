// Stage 5: Final Report Synthesis
// Model: gpt-5.1 (thinking model)
// Synthesizes all previous stage outputs into a coherent, actionable report

import { callOpenAI, MODELS } from "../openai";
import type {
  PipelineInput,
  Stage1Output,
  Stage2Output,
  Stage3Output,
  Stage4Output,
  AnalysisReport,
  AnswerFeedback,
  PieChartData,
  Verdict,
  HireLikelihood,
  CalibrationDelta,
} from "../types/pipeline";

const STAGE5_SYSTEM_PROMPT = `You are a senior career coach synthesizing interview feedback into an actionable report.

Your task is to generate a FINAL ANALYSIS REPORT that is:
1. HONEST but KIND - tell the truth without being harsh
2. ACTIONABLE - every critique comes with a specific improvement
3. CALIBRATED - adjust tone based on their self-perception vs reality
4. MEMORABLE - use specific quotes and examples from their answers

You will receive structured data from previous analysis stages. Your job is to synthesize this into human-readable feedback.

OUTPUT FORMAT (JSON):
{
  "executiveSummary": "2-3 sentence overview of performance. Be direct but encouraging.",
  
  "topAnswerFeedback": [
    {
      "questionSummary": "Brief description of what was asked",
      "questionType": "behavioral|situational|competency|cultural",
      "whatTheySaid": "Brief paraphrase or key quote from their answer",
      "whatWasGood": ["Specific strength 1", "Specific strength 2"],
      "whatWasMissing": ["Gap 1", "Gap 2"],
      "howToImprove": "One specific, actionable suggestion",
      "grade": "A|B|C|D|F"
    }
  ],
  
  "calibrationInsight": {
    "deltaEmoji": "↑ if overconfident, ↓ if underconfident, → if realistic",
    "narrative": "2-3 sentence insight about their self-awareness. Be supportive."
  },
  
  "topImprovements": [
    "Specific, actionable improvement #1",
    "Specific, actionable improvement #2",
    "Specific, actionable improvement #3"
  ],
  
  "verdict": {
    "overallGrade": "A/B+/B/B-/C+/C/C-/D/F",
    "gradeDescription": "One sentence explaining the grade",
    "hireLikelihood": "strong|moderate|uncertain|unlikely",
    "hireLikelihoodPercent": "e.g., 60-70%",
    "keyRisk": "The main concern an interviewer would have",
    "keyStrength": "The standout positive from this interview"
  },
  
  "technicalQuestionsNote": "Only include if technical questions were skipped. Otherwise null."
}

GRADING GUIDELINES:
- A: Exceptional storytelling, hit all 6Q, strong evidence, no red flags
- B+: Strong overall, minor gaps in structure or depth
- B: Solid answers with noticeable gaps in stakes/results/lessons
- B-: Decent but missing key elements, some red flags
- C+: Passable but significant gaps, multiple red flags
- C: Below expectations, major structural issues
- D/F: Critical failures in communication or content

HIRE LIKELIHOOD:
- "strong" (70-85%): Clear fit, compelling answers, minor concerns only
- "moderate" (50-65%): Mixed signals, could go either way
- "uncertain" (35-50%): Significant concerns, would need strong referrals
- "unlikely" (<35%): Major red flags or fundamental mismatches

CALIBRATION DELTAS:
- ↑ (overconfident): They thought it went better than evidence shows
- ↓ (underconfident/pessimistic): They were harder on themselves than warranted
- → (realistic): Their self-assessment matches the evidence

Be SPECIFIC. Use actual quotes. Reference actual gaps from the data provided.`;

export async function synthesizeReport(
  input: PipelineInput,
  stage1: Stage1Output,
  stage2: Stage2Output,
  stage3: Stage3Output,
  stage4: Stage4Output
): Promise<AnalysisReport> {
  
  // Build context from all stages
  const context = buildSynthesisContext(input, stage1, stage2, stage3, stage4);
  
  const userPrompt = `Synthesize the following interview analysis into a final report:

## INTERVIEW CONTEXT
- Company: ${input.company}
- Total Questions: ${stage1.totalQuestions}
- Transcript Length: ${stage1.transcriptWordCount} words

## CANDIDATE'S SELF-ASSESSMENT
"${input.selfAssessment}"

## QUESTION TYPE BREAKDOWN
${Object.entries(stage2.questionTypeBreakdown)
  .filter(([_, count]) => count > 0)
  .map(([type, count]) => `- ${type}: ${count}`)
  .join("\n")}
${stage2.outOfScopeCount > 0 ? `- OUT OF SCOPE (technical): ${stage2.outOfScopeCount}` : ""}

## JD REQUIREMENTS ANALYSIS
${stage4.requirementCoverage.map(rc => 
  `[${rc.status.toUpperCase()}] ${rc.requirement}\n  Evidence: ${rc.evidenceSummary || "None"}`
).join("\n\n")}

Coverage: ${stage4.coverageSummary.demonstrated} demonstrated, ${stage4.coverageSummary.partiallyCovered} partial, ${stage4.coverageSummary.notAddressed} not addressed
Must-Have Coverage: ${stage4.coverageSummary.coveragePercent}%

## ANSWER EVALUATIONS (for topAnswerFeedback)
${stage3.evaluatedAnswers.map((ea, idx) => {
  const question = stage1.extractedQAs.find(q => q.id === ea.qaId);
  const analyzed = stage2.analyzedQuestions.find(q => q.qaId === ea.qaId);
  if (!question || !analyzed || ea.grade === "N/A") return null;
  const responseExcerpt = question.answerText ? question.answerText.substring(0, 300) : "[No response recorded]";
  return `
### Answer ${idx + 1}: ${analyzed.type || "unknown"} question (Grade: ${ea.grade})
Question: "${question.questionText || "[Question not found]"}"
Response excerpt: "${responseExcerpt}..."
Strength: ${ea.strengthSummary || "N/A"}
Improvement: ${ea.improvementSummary || "N/A"}
6Q Missing: ${ea.sixQMissing?.join(", ") || "None"}
Flags: ${ea.flags?.map(f => `[${f.type}] ${f.flag}`).join(", ") || "None"}`;
}).filter(Boolean).join("\n")}

## 6Q PROFILE (Overall)
- Problem Definition: ${stage3.overallSixQProfile.problem}%
- Stakes/Consequences: ${stage3.overallSixQProfile.stakes}%
- Thinking/Reasoning: ${stage3.overallSixQProfile.thinking}%
- Action Taken: ${stage3.overallSixQProfile.action}%
- Results Achieved: ${stage3.overallSixQProfile.result}%
- Lessons Learned: ${stage3.overallSixQProfile.lesson}%

## FLAGS SUMMARY
- Green Flags: ${stage3.greenFlagCount}
- Red Flags: ${stage3.redFlagCount}

## CALIBRATION ANALYSIS
Self-Perception: ${stage4.calibration.selfPerceptionSummary}
Actual Performance: ${stage4.calibration.actualPerformanceSummary}
Delta: ${stage4.calibration.delta.toUpperCase()}
Insight: ${stage4.calibration.insight}

Specific Mismatches:
${stage4.calibration.specificMismatches.map(m => 
  `- They thought: "${m.theyThought}"\n  Actually: "${m.actuallyWas}"`
).join("\n")}

## KEY GAPS IDENTIFIED
${stage4.keyGaps.map((g, i) => `${i + 1}. ${g}`).join("\n")}

---

Generate the final report JSON. Include only the TOP 3-5 most important answer feedback items (prioritize critical/important questions and those with most learning potential).`;

  const response = await callOpenAI(
    STAGE5_SYSTEM_PROMPT,
    userPrompt,
    {
      model: MODELS.THINKING,
      jsonMode: true,
      maxTokens: 4000,
    }
  );

  if (!response.success) {
    throw new Error(`Stage 5 synthesis failed: ${response.error}`);
  }

  const content = response.raw || (typeof response.data === "string" ? response.data : JSON.stringify(response.data));
  if (!content) {
    throw new Error("Stage 5 synthesis returned no content");
  }

  let parsed: any;
  try {
    parsed = JSON.parse(content);
  } catch (e) {
    throw new Error(`Stage 5 failed to parse JSON: ${content.substring(0, 200)}...`);
  }

  // Build the final report
  const report: AnalysisReport = {
    sessionId: input.sessionId,
    company: input.company,
    generatedAt: new Date().toISOString(),
    
    executiveSummary: parsed.executiveSummary || "Analysis complete.",
    
    questionBreakdown: buildQuestionBreakdown(stage2),
    
    jdCoverage: {
      demonstrated: stage4.requirementCoverage
        .filter(rc => rc.status === "demonstrated")
        .map(rc => rc.requirement),
      partiallyCovered: stage4.requirementCoverage
        .filter(rc => rc.status === "partially-covered")
        .map(rc => rc.requirement),
      notAddressed: stage4.requirementCoverage
        .filter(rc => rc.status === "not-addressed")
        .map(rc => rc.requirement),
    },
    
    topAnswerFeedback: (parsed.topAnswerFeedback || []).map((af: any) => ({
      questionSummary: af.questionTextSummary || "",
      questionType: af.questionTextType || "behavioral",
      whatTheySaid: af.whatTheySaid || "",
      whatWasGood: af.whatWasGood || [],
      whatWasMissing: af.whatWasMissing || [],
      howToImprove: af.howToImprove || "",
      grade: af.grade || "C",
    } as AnswerFeedback)),
    
    calibrationInsight: {
      userSaid: stage4.calibration.selfPerceptionSummary,
      analysisFound: stage4.calibration.actualPerformanceSummary,
      delta: stage4.calibration.delta as CalibrationDelta,
      deltaEmoji: parsed.calibrationInsight?.deltaEmoji || getDeltaEmoji(stage4.calibration.delta),
    },
    
    topImprovements: parsed.topImprovements || stage4.keyGaps.slice(0, 3),
    
    verdict: {
      overallGrade: parsed.verdict?.overallGrade || stage3.averageGrade,
      gradeDescription: parsed.verdict?.gradeDescription || "Performance analysis complete.",
      hireLikelihood: (parsed.verdict?.hireLikelihood || "moderate") as HireLikelihood,
      hireLikelihoodPercent: parsed.verdict?.hireLikelihoodPercent || "50-65%",
      keyRisk: parsed.verdict?.keyRisk || stage4.keyGaps[0] || "No major risks identified",
      keyStrength: parsed.verdict?.keyStrength || "Clear communication",
    },
  };

  // Add technical questions note if any were skipped
  if (stage2.outOfScopeCount > 0) {
    report.technicalQuestionsNote = parsed.technicalQuestionsNote || 
      `${stage2.outOfScopeCount} technical question(s) were identified but not evaluated for behavioral content. This tool focuses on soft-skill/behavioral questions. Technical assessments should be evaluated separately.`;
  }

  return report;
}

function buildSynthesisContext(
  input: PipelineInput,
  stage1: Stage1Output,
  stage2: Stage2Output,
  stage3: Stage3Output,
  stage4: Stage4Output
): string {
  return JSON.stringify({
    company: input.company,
    totalQuestions: stage1.totalQuestions,
    questionTypes: stage2.questionTypeBreakdown,
    averageGrade: stage3.averageGrade,
    coveragePercent: stage4.coverageSummary.coveragePercent,
    calibrationDelta: stage4.calibration.delta,
  });
}

function buildQuestionBreakdown(stage2: Stage2Output): PieChartData[] {
  const colors: Record<string, string> = {
    behavioral: "#3b82f6",    // blue
    situational: "#8b5cf6",   // purple
    competency: "#10b981",    // green
    cultural: "#f59e0b",      // amber
    technical: "#6b7280",     // gray
    logistical: "#94a3b8",    // slate
  };

  const total = Object.values(stage2.questionTypeBreakdown).reduce((a, b) => a + b, 0);
  
  return Object.entries(stage2.questionTypeBreakdown)
    .filter(([_, count]) => count > 0)
    .map(([type, count]) => ({
      type: type as any,
      count,
      percentage: total > 0 ? Math.round((count / total) * 100) : 0,
      color: colors[type] || "#6b7280",
    }));
}

function getDeltaEmoji(delta: string): string {
  switch (delta) {
    case "overconfident": return "↑";
    case "pessimistic": return "↓";
    case "realistic": return "→";
    default: return "→";
  }
}


