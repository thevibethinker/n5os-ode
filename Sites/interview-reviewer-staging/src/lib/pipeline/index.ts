// Pipeline Orchestrator for Am I Hired? Multi-Stage Analysis
// Executes 5 stages sequentially with timing and error handling

import type {
  PipelineInput,
  PipelineResult,
  Stage1Output,
  Stage2Output,
  Stage3Output,
  Stage4Output,
  AnalysisReport,
  StageResult,
} from "../types/pipeline";
import { MODELS } from "../openai";
import { extractQAPairs } from "./stage1-extract";

// ============ Pipeline Entry Point ============

export async function runPipeline(input: PipelineInput): Promise<PipelineResult> {
  const startTime = Date.now();
  
  const result: PipelineResult = {
    success: false,
    stages: {
      stage1: null,
      stage2: null,
      stage3: null,
      stage4: null,
      stage5: null,
    },
    totalDurationMs: 0,
  };

  try {
    // Stage 1: Extract Q&A pairs (gpt-5.1-mini)
    console.log("[Pipeline] Stage 1: Extracting Q&A pairs...");
    const stage1 = await runStage1(input.transcript);
    result.stages.stage1 = stage1;
    if (!stage1.success) {
      throw new Error(`Stage 1 failed: ${stage1.error}`);
    }

    // Stage 2: Analyze Questions (gpt-5.1)
    console.log("[Pipeline] Stage 2: Analyzing questions...");
    const stage2 = await runStage2(stage1.data!, input.jobDescription);
    result.stages.stage2 = stage2;
    if (!stage2.success) {
      throw new Error(`Stage 2 failed: ${stage2.error}`);
    }

    // Stage 3: Evaluate Answers (gpt-5.1)
    console.log("[Pipeline] Stage 3: Evaluating answers...");
    const stage3 = await runStage3(stage1.data!, stage2.data!);
    result.stages.stage3 = stage3;
    if (!stage3.success) {
      throw new Error(`Stage 3 failed: ${stage3.error}`);
    }

    // Stage 4: Gap + Calibration Analysis (gpt-5.1)
    console.log("[Pipeline] Stage 4: Analyzing gaps and calibration...");
    const stage4 = await runStage4(stage2.data!, stage3.data!, input.jobDescription, input.selfAssessment);
    result.stages.stage4 = stage4;
    if (!stage4.success) {
      throw new Error(`Stage 4 failed: ${stage4.error}`);
    }

    // Stage 5: Synthesize Final Report (gpt-5.1)
    console.log("[Pipeline] Stage 5: Synthesizing final report...");
    const stage5 = await runStage5(input, stage1.data!, stage2.data!, stage3.data!, stage4.data!);
    result.stages.stage5 = stage5;
    if (!stage5.success) {
      throw new Error(`Stage 5 failed: ${stage5.error}`);
    }

    result.success = true;
    result.report = stage5.data;
    
  } catch (error) {
    result.error = error instanceof Error ? error.message : "Pipeline failed";
  }

  result.totalDurationMs = Date.now() - startTime;
  console.log(`[Pipeline] Complete in ${result.totalDurationMs}ms`);
  
  return result;
}

// ============ Stage 1: Extract Q&A (REAL IMPLEMENTATION) ============

async function runStage1(transcript: string): Promise<StageResult<Stage1Output>> {
  const startTime = Date.now();
  
  try {
    const data = await extractQAPairs(transcript);
    
    return {
      success: true,
      data,
      durationMs: Date.now() - startTime,
      model: MODELS.FAST,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Stage 1 extraction failed",
      durationMs: Date.now() - startTime,
      model: MODELS.FAST,
    };
  }
}

// ============ Stage 2: Question Analysis (STUB) ============

async function runStage2(stage1: Stage1Output, jobDescription: string): Promise<StageResult<Stage2Output>> {
  const startTime = Date.now();
  // STUB: Return synthetic data until real implementation
  return {
    success: true,
    data: {
      analyzedQuestions: stage1.extractedQAs.map((qa, idx) => ({
        qaId: qa.id,
        type: idx % 2 === 0 ? 'behavioral' : 'situational' as const,
        typeConfidence: 0.9,
        isOutOfScope: false,
        jdRequirementsMapped: ['req_001'],
        priority: 'important' as const,
        whatTheyreReallAsking: 'Stub: What they want to know',
      })),
      jdRequirements: [{ id: 'req_001', requirement: 'Leadership experience', category: 'Leadership', priority: 'must-have' as const }],
      questionTypeBreakdown: { behavioral: 3, situational: 2, competency: 0, cultural: 0, technical: 0, logistical: 0 },
      outOfScopeCount: 0,
    },
    durationMs: Date.now() - startTime,
    model: MODELS.THINKING,
  };
}

// ============ Stage 3: Answer Evaluation (STUB) ============

async function runStage3(stage1: Stage1Output, stage2: Stage2Output): Promise<StageResult<Stage3Output>> {
  const startTime = Date.now();
  return {
    success: true,
    data: {
      evaluatedAnswers: stage1.extractedQAs.map(qa => ({
        qaId: qa.id,
        sixQScore: { problem: true, stakes: true, thinking: false, action: true, result: true, lesson: false },
        sixQMissing: ['thinking', 'lesson'],
        flags: [{ type: 'green' as const, flag: 'Specific examples' }],
        grade: 'B' as const,
        gradeRationale: 'Stub rationale',
        strengthSummary: 'Stub strength',
        improvementSummary: 'Stub improvement',
      })),
      overallSixQProfile: { problem: 80, stakes: 70, thinking: 50, action: 90, result: 80, lesson: 40 },
      greenFlagCount: 3,
      redFlagCount: 1,
      averageGrade: 'B',
    },
    durationMs: Date.now() - startTime,
    model: MODELS.THINKING,
  };
}

// ============ Stage 4: Gap + Calibration (STUB) ============

async function runStage4(
  stage2: Stage2Output,
  stage3: Stage3Output,
  jobDescription: string,
  selfAssessment: string
): Promise<StageResult<Stage4Output>> {
  const startTime = Date.now();
  return {
    success: true,
    data: {
      requirementCoverage: stage2.jdRequirements.map(req => ({
        requirementId: req.id,
        requirement: req.requirement,
        status: 'demonstrated' as const,
        evidenceQaIds: ['qa_001'],
        evidenceSummary: 'Stub evidence',
      })),
      coverageSummary: { demonstrated: 3, partiallyCovered: 1, notAddressed: 1, coveragePercent: 60 },
      calibration: {
        selfPerceptionSummary: selfAssessment.substring(0, 100),
        actualPerformanceSummary: 'Stub: performed well overall',
        delta: 'realistic' as const,
        insight: 'Your self-assessment aligns with the evidence.',
        specificMismatches: [],
      },
      keyGaps: ['Missing: stakeholder management examples', 'Could improve: quantifying impact'],
    },
    durationMs: Date.now() - startTime,
    model: MODELS.THINKING,
  };
}

// ============ Stage 5: Synthesis (STUB) ============

async function runStage5(
  input: PipelineInput,
  stage1: Stage1Output,
  stage2: Stage2Output,
  stage3: Stage3Output,
  stage4: Stage4Output
): Promise<StageResult<AnalysisReport>> {
  const startTime = Date.now();
  return {
    success: true,
    data: {
      sessionId: input.sessionId,
      company: input.company,
      generatedAt: new Date().toISOString(),
      executiveSummary: `You demonstrated solid interview skills with ${stage1.totalQuestions} questions answered. Key areas to improve include your storytelling structure.`,
      questionBreakdown: Object.entries(stage2.questionTypeBreakdown).map(([type, count]) => ({
        type: type as any,
        count,
        percentage: Math.round((count / stage1.totalQuestions) * 100),
        color: '#3b82f6',
      })),
      jdCoverage: {
        demonstrated: ['Leadership experience'],
        partiallyCovered: ['Project management'],
        notAddressed: ['Budget management'],
      },
      topAnswerFeedback: [],
      calibrationInsight: {
        userSaid: stage4.calibration.selfPerceptionSummary,
        analysisFound: stage4.calibration.actualPerformanceSummary,
        delta: stage4.calibration.delta,
        deltaEmoji: '→',
      },
      topImprovements: stage4.keyGaps,
      verdict: {
        overallGrade: stage3.averageGrade,
        gradeDescription: 'Solid performance with room for improvement',
        hireLikelihood: 'moderate' as const,
        hireLikelihoodPercent: '50-65%',
        keyRisk: 'Storytelling could be stronger',
        keyStrength: 'Clear communication style',
      },
    },
    durationMs: Date.now() - startTime,
    model: MODELS.THINKING,
  };
}

// Helper to generate session IDs in AMH-XXXX-XXXX format
export function generateSessionId(): string {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // Avoid ambiguous chars
  const segment = () => Array.from({ length: 4 }, () => 
    chars[Math.floor(Math.random() * chars.length)]
  ).join("");
  return `AMH-${segment()}-${segment()}`;
}



