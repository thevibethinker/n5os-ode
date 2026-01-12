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
import { analyzeQuestions } from "./stage2-questions";
import { evaluateAnswers } from "./stage3-answers";
import { analyzeGapsAndCalibration } from "./stage4-gaps";
import { synthesizeReport } from "./stage5-synthesis";

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

// ============ Stage 2: Question Analysis (REAL IMPLEMENTATION) ============

async function runStage2(stage1: Stage1Output, jobDescription: string): Promise<StageResult<Stage2Output>> {
  const startTime = Date.now();
  
  try {
    const data = await analyzeQuestions(stage1.extractedQAs, jobDescription);
    
    return {
      success: true,
      data,
      durationMs: Date.now() - startTime,
      model: MODELS.THINKING,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Stage 2 analysis failed",
      durationMs: Date.now() - startTime,
      model: MODELS.THINKING,
    };
  }
}

// ============ Stage 3: Answer Evaluation (REAL IMPLEMENTATION) ============

async function runStage3(stage1: Stage1Output, stage2: Stage2Output): Promise<StageResult<Stage3Output>> {
  const startTime = Date.now();
  
  try {
    const data = await evaluateAnswers(stage1.extractedQAs, stage2);
    
    return {
      success: true,
      data,
      durationMs: Date.now() - startTime,
      model: MODELS.THINKING,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Stage 3 evaluation failed",
      durationMs: Date.now() - startTime,
      model: MODELS.THINKING,
    };
  }
}

// ============ Stage 4: Gap + Calibration (REAL IMPLEMENTATION) ============

async function runStage4(
  stage2: Stage2Output,
  stage3: Stage3Output,
  jobDescription: string,
  selfAssessment: string
): Promise<StageResult<Stage4Output>> {
  const startTime = Date.now();
  
  try {
    const data = await analyzeGapsAndCalibration(stage2, stage3, jobDescription, selfAssessment);
    
    return {
      success: true,
      data,
      durationMs: Date.now() - startTime,
      model: MODELS.THINKING,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Stage 4 gap analysis failed",
      durationMs: Date.now() - startTime,
      model: MODELS.THINKING,
    };
  }
}

// ============ Stage 5: Synthesis (REAL IMPLEMENTATION) ============

async function runStage5(
  input: PipelineInput,
  stage1: Stage1Output,
  stage2: Stage2Output,
  stage3: Stage3Output,
  stage4: Stage4Output
): Promise<StageResult<AnalysisReport>> {
  const startTime = Date.now();
  
  try {
    const data = await synthesizeReport(input, stage1, stage2, stage3, stage4);
    
    return {
      success: true,
      data,
      durationMs: Date.now() - startTime,
      model: MODELS.THINKING,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Stage 5 synthesis failed",
      durationMs: Date.now() - startTime,
      model: MODELS.THINKING,
    };
  }
}

// Helper to generate session IDs in AMH-XXXX-XXXX format
export function generateSessionId(): string {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // Avoid ambiguous chars
  const segment = () => Array.from({ length: 4 }, () => 
    chars[Math.floor(Math.random() * chars.length)]
  ).join("");
  return `AMH-${segment()}-${segment()}`;
}










