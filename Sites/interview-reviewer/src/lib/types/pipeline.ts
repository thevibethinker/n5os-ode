// Pipeline Type Definitions for Am I Hired? Multi-Stage Analysis
// Version: 1.0 | PRD: N5/builds/interview-reviewer/PRD-MultiStage-Analysis.md

// ============ Input Types ============

export interface PipelineInput {
  transcript: string;
  company: string;
  jobDescription: string;
  selfAssessment: string;
  sessionId: string;
  customerName: string;          // Person being analyzed
}

// ============ Stage 1: Extract Q&A ============

export interface ExtractedQA {
  id: string;                    // qa_001, qa_002, etc.
  questionText: string;          // The interviewer's question
  answerText: string;            // The candidate's response
  questionIndex: number;         // Order in transcript (1-indexed)
  approximateTimestamp?: string; // If parseable from transcript
}

export interface Stage1Output {
  extractedQAs: ExtractedQA[];
  totalQuestions: number;
  transcriptWordCount: number;
  extractionNotes?: string;      // Any issues during extraction
}

// ============ Stage 2: Question Analysis ============

export type QuestionType = 
  | 'behavioral'    // "Tell me about a time when..."
  | 'situational'   // "What would you do if..."
  | 'competency'    // "Describe your experience with..."
  | 'cultural'      // "Why us?" / "What motivates you?"
  | 'technical'     // Coding, system design, domain-specific
  | 'logistical';   // Salary, availability, location

export interface JDRequirement {
  id: string;                    // req_001, req_002, etc.
  requirement: string;           // e.g., "5+ years leadership experience"
  category: string;              // e.g., "Leadership", "Technical Skills"
  priority: 'must-have' | 'nice-to-have' | 'inferred';
}

export interface AnalyzedQuestion {
  qaId: string;                  // Reference to ExtractedQA.id
  type: QuestionType;
  typeConfidence: number;        // 0-1 confidence in classification
  isOutOfScope: boolean;         // true for technical/logistical
  jdRequirementsMapped: string[]; // IDs of JD requirements this probes
  priority: 'critical' | 'important' | 'standard';
  whatTheyreReallAsking: string; // Plain-English interpretation
}

export interface Stage2Output {
  analyzedQuestions: AnalyzedQuestion[];
  jdRequirements: JDRequirement[];
  questionTypeBreakdown: Record<QuestionType, number>;
  outOfScopeCount: number;
}

// ============ Stage 3: Answer Evaluation ============

export interface SixQScore {
  problem: boolean;              // Did they establish the situation?
  stakes: boolean;               // Did they convey why it mattered?
  thinking: boolean;             // Did they show their reasoning?
  action: boolean;               // Did they describe what they did?
  result: boolean;               // Did they share the outcome?
  lesson: boolean;               // Did they reflect on what they learned?
}

export type FlagType = 'green' | 'red';

export interface AnswerFlag {
  type: FlagType;
  flag: string;                  // e.g., "Quantified impact" or "Blamed others"
  quote?: string;                // Supporting quote from transcript
}

export type AnswerGrade = 'A' | 'B' | 'C' | 'D' | 'F' | 'N/A';

export interface EvaluatedAnswer {
  qaId: string;                  // Reference to ExtractedQA.id
  sixQScore: SixQScore | null;   // null if question is OUT_OF_SCOPE
  sixQMissing: string[];         // Which components are missing
  flags: AnswerFlag[];
  grade: AnswerGrade;
  gradeRationale: string;
  strengthSummary: string;
  improvementSummary: string;
}

export interface Stage3Output {
  evaluatedAnswers: EvaluatedAnswer[];
  overallSixQProfile: {
    problem: number;             // % of applicable answers with this
    stakes: number;
    thinking: number;
    action: number;
    result: number;
    lesson: number;
  };
  greenFlagCount: number;
  redFlagCount: number;
  averageGrade: string;          // e.g., "B+"
}

// ============ Stage 4: Gap + Calibration ============

export type CoverageStatus = 'demonstrated' | 'partially-covered' | 'not-addressed';

export interface RequirementCoverage {
  requirementId: string;
  requirement: string;
  status: CoverageStatus;
  evidenceQaIds: string[];       // Which Q&As demonstrate this
  evidenceSummary?: string;
}

export type CalibrationDelta = 'optimistic' | 'realistic' | 'pessimistic';

export interface CalibrationAnalysis {
  selfPerceptionSummary: string; // What they said about how it went
  actualPerformanceSummary: string; // What the evidence shows
  delta: CalibrationDelta;
  insight: string;               // Personalized observation
  specificMismatches: Array<{
    theyThought: string;
    actuallyWas: string;
  }>;
}

export interface Stage4Output {
  requirementCoverage: RequirementCoverage[];
  coverageSummary: {
    demonstrated: number;
    partiallyCovered: number;
    notAddressed: number;
    coveragePercent: number;     // % of must-haves demonstrated
  };
  calibration: CalibrationAnalysis;
  keyGaps: string[];             // Top 3 gaps to address
}

// ============ Stage 5: Synthesis (Final Report) ============

export interface PieChartData {
  type: QuestionType;
  count: number;
  percentage: number;
  color: string;                 // Hex color for rendering
}

export interface AnswerFeedback {
  questionSummary: string;
  questionType: QuestionType;
  whatTheySaid: string;
  whatWasGood: string[];
  whatWasMissing: string[];
  howToImprove: string;
  grade: AnswerGrade;
}

export type HireLikelihood = 
  | 'low'           // < 30%
  | 'moderate-low'  // 30-50%
  | 'moderate'      // 50-65%
  | 'moderate-high' // 65-75%
  | 'high';         // > 75%

export interface Verdict {
  overallGrade: string;          // e.g., "B+"
  gradeDescription: string;      // e.g., "Strong with specific gaps"
  hireLikelihood: HireLikelihood;
  hireLikelihoodPercent: string; // e.g., "65-75%"
  keyRisk: string;
  keyStrength: string;
}

export interface AnalysisReport {
  sessionId: string;
  company: string;
  customerName: string;          // Person who submitted the interview
  role?: string;                 // Role being interviewed for (extracted from JD/context)
  generatedAt: string;           // ISO timestamp
  
  executiveSummary: string;      // 2-3 sentences
  
  // Q&A Pairs from Stage 1 - the actual questions and answers
  extractedQAs: Array<{
    questionText: string;
    answerText: string;
    questionIndex: number;
  }>;
  
  questionBreakdown: PieChartData[];
  
  jdCoverage: {
    demonstrated: string[];
    partiallyCovered: string[];
    notAddressed: string[];
  };
  
  topAnswerFeedback: AnswerFeedback[]; // Top 5 most important
  
  calibrationInsight: {
    userSaid: string;
    analysisFound: string;
    delta: CalibrationDelta;
    deltaEmoji: string;          // ↑ ↓ or →
  };
  
  topImprovements: string[];     // Top 3 actionable improvements
  
  verdict: Verdict;
  
  technicalQuestionsNote?: string; // If any were skipped
}

// ============ Pipeline Orchestration ============

export interface StageResult<T> {
  success: boolean;
  data?: T;
  error?: string;
  durationMs: number;
  model: string;
  tokensUsed?: {
    input: number;
    output: number;
  };
}

export interface PipelineResult {
  success: boolean;
  report?: AnalysisReport;
  error?: string;
  stages: {
    stage1: StageResult<Stage1Output> | null;
    stage2: StageResult<Stage2Output> | null;
    stage3: StageResult<Stage3Output> | null;
    stage4: StageResult<Stage4Output> | null;
    stage5: StageResult<AnalysisReport> | null;
  };
  totalDurationMs: number;
  totalCostEstimate?: number;
}



