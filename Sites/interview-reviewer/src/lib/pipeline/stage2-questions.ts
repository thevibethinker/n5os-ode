// Stage 2: Question Analysis
// Model: gpt-5.1 (deep reasoning for classification and JD mapping)

import { callOpenAI, MODELS } from "../openai";
import type { 
  ExtractedQA, 
  Stage2Output, 
  AnalyzedQuestion, 
  JDRequirement,
  QuestionType 
} from "../types/pipeline";

const STAGE2_SYSTEM_PROMPT = `You are an expert interview analyst. Your task is to:

1. PARSE the job description to extract key requirements
2. CLASSIFY each interview question by type
3. MAP questions to the JD requirements they probe
4. FLAG technical questions as out-of-scope (we don't evaluate technical correctness)

## Question Types

- **behavioral**: Past experience questions ("Tell me about a time when...", "Describe a situation where...")
- **situational**: Hypothetical scenarios ("What would you do if...", "How would you handle...")
- **competency**: Skills/experience probing ("Describe your experience with...", "What tools do you use for...")
- **cultural**: Values/motivation questions ("Why us?", "What motivates you?", "Where do you see yourself...")
- **technical**: Coding, system design, domain-specific knowledge (algorithms, architecture, etc.)
- **logistical**: Salary, availability, location, start date, references

## Classification Rules

1. Questions starting with "Tell me about a time" → behavioral (high confidence)
2. Questions with "What would you do if" → situational (high confidence)
3. Questions about past projects/experience → competency or behavioral (check for specific example request)
4. Questions about culture fit, motivation, career goals → cultural
5. Questions requiring domain expertise to answer correctly → technical (mark as OUT_OF_SCOPE)
6. Questions about logistics → logistical (mark as OUT_OF_SCOPE)

## Priority Assignment

- **critical**: Questions that directly probe must-have JD requirements
- **important**: Questions probing nice-to-have requirements or core competencies
- **standard**: General questions, culture fit, motivation

## Output Format

Return JSON with this exact structure:
{
  "jdRequirements": [
    {
      "id": "req_001",
      "requirement": "5+ years of leadership experience",
      "category": "Leadership",
      "priority": "must-have"
    }
  ],
  "analyzedQuestions": [
    {
      "qaId": "qa_001",
      "type": "behavioral",
      "typeConfidence": 0.95,
      "isOutOfScope": false,
      "jdRequirementsMapped": ["req_001", "req_003"],
      "priority": "critical",
      "whatTheyreReallAsking": "Can you lead teams through difficult situations?"
    }
  ],
  "analysisNotes": "Optional notes about the analysis"
}`;

export async function analyzeQuestions(
  extractedQAs: ExtractedQA[],
  jobDescription: string
): Promise<Stage2Output> {
  
  const userPrompt = `## Job Description

${jobDescription}

## Interview Questions to Analyze

${extractedQAs.map(qa => `[${qa.id}] ${qa.questionText}`).join('\n\n')}

---

Analyze these questions against the job description. Extract JD requirements first, then classify and map each question.`;

  const response = await callOpenAI(
    STAGE2_SYSTEM_PROMPT,
    userPrompt,
    {
      model: MODELS.THINKING,
      jsonMode: true,
      maxTokens: 8000,
    }
  );

  if (!response.success) {
    throw new Error(`Stage 2 failed: ${response.error || "Unknown error"}`);
  }

  const content = response.raw || (typeof response.data === "string" ? response.data : JSON.stringify(response.data));
  if (!content) {
    throw new Error(`Stage 2 failed: No content returned`);
  }

  let parsed: {
    jdRequirements: JDRequirement[];
    analyzedQuestions: Array<{
      qaId: string;
      type: string;
      typeConfidence: number;
      isOutOfScope: boolean;
      jdRequirementsMapped: string[];
      priority: string;
      whatTheyreReallAsking: string;
    }>;
    analysisNotes?: string;
  };

  try {
    parsed = JSON.parse(content);
  } catch (e) {
    throw new Error(`Stage 2 failed to parse JSON: ${content.substring(0, 200)}...`);
  }

  // Validate and normalize the response
  const validTypes: QuestionType[] = ['behavioral', 'situational', 'competency', 'cultural', 'technical', 'logistical'];
  const validPriorities = ['critical', 'important', 'standard'] as const;
  
  const analyzedQuestions: AnalyzedQuestion[] = parsed.analyzedQuestions.map(aq => ({
    qaId: aq.qaId,
    type: (validTypes.includes(aq.type as QuestionType) ? aq.type : 'competency') as QuestionType,
    typeConfidence: Math.max(0, Math.min(1, aq.typeConfidence || 0.8)),
    isOutOfScope: aq.isOutOfScope || aq.type === 'technical' || aq.type === 'logistical',
    jdRequirementsMapped: aq.jdRequirementsMapped || [],
    priority: (validPriorities.includes(aq.priority as any) ? aq.priority : 'standard') as 'critical' | 'important' | 'standard',
    whatTheyreReallAsking: aq.whatTheyreReallAsking || 'Understanding your fit for this role',
  }));

  // Calculate question type breakdown
  const questionTypeBreakdown: Record<QuestionType, number> = {
    behavioral: 0,
    situational: 0,
    competency: 0,
    cultural: 0,
    technical: 0,
    logistical: 0,
  };

  for (const q of analyzedQuestions) {
    questionTypeBreakdown[q.type]++;
  }

  const outOfScopeCount = analyzedQuestions.filter(q => q.isOutOfScope).length;

  return {
    analyzedQuestions,
    jdRequirements: parsed.jdRequirements || [],
    questionTypeBreakdown,
    outOfScopeCount,
  };
}

