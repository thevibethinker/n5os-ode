// Stage 3: Answer Evaluation with 6Q Framework
// Model: gpt-5.1 (deep reasoning for nuanced evaluation)

import { callOpenAI, MODELS } from "../openai";
import type { 
  ExtractedQA, 
  AnalyzedQuestion, 
  Stage2Output,
  Stage3Output, 
  EvaluatedAnswer,
  SixQScore,
  AnswerFlag,
  AnswerGrade
} from "../types/pipeline";
import { readFileSync } from "fs";
import { join } from "path";

// Load coaching reference for 6Q framework
const COACHING_CONTENT = (() => {
  try {
    return readFileSync(
      join(import.meta.dir, "../../content/coaching-reference.md"),
      "utf-8"
    );
  } catch {
    return "";
  }
})();

const STAGE3_SYSTEM_PROMPT = `You are an expert interview coach evaluating candidate answers using the 6-Point "Art of The Brag" framework.

## The 6Q Framework (evaluate each behavioral/situational answer against these)

### 1. THE PROBLEM/CHALLENGE
- Did they clearly define the situation?
- Is the problem clear enough to explain to others?
- Did they avoid unnecessary background?

### 2. THE STAKES
- What was at risk if this went wrong?
- Were there real consequences (revenue, customers, team, reputation)?
- Did they make you *care* about the outcome?
- WITHOUT STAKES, THERE IS NO STORY - this is where STAR fails

### 3. THE THINKING (HIGHEST VALUE)
- Did they explain *why* they chose their approach?
- Did they show awareness of alternatives, constraints, trade-offs?
- Can you understand their decision-making process?
- THIS IS THE MOST IMPORTANT ELEMENT - actions can be taught, judgment cannot

### 4. THE ACTION
- Is it clear what *they specifically* contributed?
- "I" vs "We" test - were they a driver or passenger?
- Are actions concrete and specific?

### 5. THE RESULT
- Is the result specific and believable?
- Quantified when possible (%, $, time)?
- Does it connect to their actions?
- Includes human impact, not just metrics?

### 6. THE LESSON
- Did they articulate what they learned or would do differently?
- Is the lesson genuine, not generic?
- Shows growth mindset and self-awareness?

## Red Flags to Detect

| Code | Name | Pattern |
|------|------|---------|
| RF-1 | Invisible "I" | Overuse of "we" obscuring individual contribution |
| RF-2 | Stakes Vacuum | No explanation of why it mattered |
| RF-3 | Judgment Gap | Jumped from problem to action without reasoning |
| RF-4 | Vague Quantification | "improved significantly", "results were good" |
| RF-5 | Generic Lesson | "I learned teamwork is important" |
| RF-6 | Borrowed Glory | Taking credit for team/org success they didn't drive |
| RF-7 | Low-Stakes Selection | Chose a story where failure wouldn't have mattered |
| RF-8 | Deflection | Answered a different question than asked |
| RF-9 | Modesty Overload | Excessive hedging/minimizing |
| RF-10 | Time Trap | Rambling answer losing structure |

## Green Flags to Detect

| Code | Name | Pattern |
|------|------|---------|
| GF-1 | Clear Ownership | Strong "I" statements with specific contributions |
| GF-2 | Stakes Clarity | Made the consequences visceral and real |
| GF-3 | Reasoning Transparency | Explained alternatives considered and why chose this path |
| GF-4 | Quantified Impact | Specific numbers, percentages, dollar amounts |
| GF-5 | Genuine Reflection | Authentic lesson that changed future behavior |
| GF-6 | Concise Structure | Problem→Stakes→Thinking→Action→Result flow |
| GF-7 | Human Impact | Mentioned effect on people, not just metrics |
| GF-8 | Proactive Signal | Wove in relevant competencies naturally |

## Grading Scale

| Grade | Description |
|-------|-------------|
| A | Exceptional - all 6Q present, strong green flags, no red flags |
| B | Good - 4-5 of 6Q present, minor issues |
| C | Adequate - 3 of 6Q present, some red flags |
| D | Weak - 2 or fewer 6Q, significant red flags |
| F | Failed - missed the question or major red flags |
| N/A | Not applicable (technical/logistical question) |

For OUT_OF_SCOPE questions (technical/logistical), set sixQScore to null and grade to N/A.

Output JSON only. No markdown fences.`;

const buildUserPrompt = (
  qas: ExtractedQA[],
  analyzedQuestions: AnalyzedQuestion[]
): string => {
  const qaMap = new Map(qas.map(qa => [qa.id, qa]));
  
  const questionsForEval = analyzedQuestions.map(aq => {
    const qa = qaMap.get(aq.qaId);
    return {
      qaId: aq.qaId,
      questionType: aq.type,
      isOutOfScope: aq.isOutOfScope,
      whatTheyreAsking: aq.whatTheyreReallAsking,
      questionText: qa?.questionText || "",
      answerText: qa?.answerText || "",
    };
  });

  return `Evaluate each answer below using the 6Q framework.

For OUT_OF_SCOPE questions (isOutOfScope: true), skip 6Q evaluation and set grade to "N/A".

## Questions and Answers to Evaluate

${JSON.stringify(questionsForEval, null, 2)}

## Required Output Format

{
  "evaluatedAnswers": [
    {
      "qaId": "qa_001",
      "sixQScore": {
        "problem": true/false,
        "stakes": true/false,
        "thinking": true/false,
        "action": true/false,
        "result": true/false,
        "lesson": true/false
      },
      "sixQMissing": ["stakes", "thinking"],
      "flags": [
        {"type": "red", "flag": "RF-2: Stakes Vacuum - no explanation of consequences"},
        {"type": "green", "flag": "GF-4: Quantified Impact - mentioned 23% improvement"}
      ],
      "grade": "B",
      "gradeRationale": "Good answer with clear problem and action, but missing stakes and reasoning",
      "strengthSummary": "Clear ownership and quantified results",
      "improvementSummary": "Add context on why this mattered and explain your reasoning process"
    }
  ],
  "overallObservations": "Summary of patterns across all answers"
}

For OUT_OF_SCOPE questions, use this format:
{
  "qaId": "qa_003",
  "sixQScore": null,
  "sixQMissing": [],
  "flags": [],
  "grade": "N/A",
  "gradeRationale": "Technical/logistical question - 6Q framework not applicable",
  "strengthSummary": "N/A",
  "improvementSummary": "N/A"
}`;
};

export async function evaluateAnswers(
  qas: ExtractedQA[],
  stage2: Stage2Output
): Promise<Stage3Output> {
  const userPrompt = buildUserPrompt(qas, stage2.analyzedQuestions);

  const response = await callOpenAI(
    STAGE3_SYSTEM_PROMPT,
    userPrompt,
    {
      model: MODELS.THINKING,
      jsonMode: true,
      maxTokens: 12000,
    }
  );

  if (!response.success) {
    throw new Error(`Stage 3 failed: ${response.error || "Unknown error"}`);
  }

  const content = response.raw || (typeof response.data === "string" ? response.data : JSON.stringify(response.data));
  if (!content) {
    throw new Error(`Stage 3 failed: No content returned`);
  }

  let parsed: any;
  try {
    parsed = JSON.parse(content);
  } catch (e) {
    throw new Error(`Stage 3 failed to parse JSON: ${content.substring(0, 200)}...`);
  }

  // Process and normalize results
  const evaluatedAnswers: EvaluatedAnswer[] = parsed.evaluatedAnswers.map((ea: any) => ({
    qaId: ea.qaId,
    sixQScore: ea.sixQScore,
    sixQMissing: ea.sixQMissing || [],
    flags: (ea.flags || []).map((f: any) => ({
      type: f.type as 'red' | 'green',
      flag: f.flag,
    })),
    grade: ea.grade as AnswerGrade,
    gradeRationale: ea.gradeRationale,
    strengthSummary: ea.strengthSummary,
    improvementSummary: ea.improvementSummary,
  }));

  // Calculate overall 6Q profile (only for answers that have 6Q scores)
  const scoredAnswers = evaluatedAnswers.filter(ea => ea.sixQScore !== null);
  const totalScored = scoredAnswers.length || 1; // Avoid division by zero

  const overallSixQProfile = {
    problem: Math.round((scoredAnswers.filter(ea => ea.sixQScore?.problem).length / totalScored) * 100),
    stakes: Math.round((scoredAnswers.filter(ea => ea.sixQScore?.stakes).length / totalScored) * 100),
    thinking: Math.round((scoredAnswers.filter(ea => ea.sixQScore?.thinking).length / totalScored) * 100),
    action: Math.round((scoredAnswers.filter(ea => ea.sixQScore?.action).length / totalScored) * 100),
    result: Math.round((scoredAnswers.filter(ea => ea.sixQScore?.result).length / totalScored) * 100),
    lesson: Math.round((scoredAnswers.filter(ea => ea.sixQScore?.lesson).length / totalScored) * 100),
  };

  // Count flags
  const greenFlagCount = evaluatedAnswers.reduce(
    (sum, ea) => sum + ea.flags.filter(f => f.type === 'green').length, 
    0
  );
  const redFlagCount = evaluatedAnswers.reduce(
    (sum, ea) => sum + ea.flags.filter(f => f.type === 'red').length, 
    0
  );

  // Calculate average grade
  const gradeValues: Record<string, number> = { 'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0 };
  const gradedAnswers = evaluatedAnswers.filter(ea => ea.grade !== 'N/A');
  const avgGradeValue = gradedAnswers.length > 0
    ? gradedAnswers.reduce((sum, ea) => sum + (gradeValues[ea.grade] || 2), 0) / gradedAnswers.length
    : 2;
  
  const gradeFromValue = (v: number): string => {
    if (v >= 3.5) return 'A';
    if (v >= 2.5) return 'B';
    if (v >= 1.5) return 'C';
    if (v >= 0.5) return 'D';
    return 'F';
  };

  return {
    evaluatedAnswers,
    overallSixQProfile,
    greenFlagCount,
    redFlagCount,
    averageGrade: gradeFromValue(avgGradeValue),
  };
}

