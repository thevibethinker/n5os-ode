// Stage 1: Extract Q&A Pairs from Transcript
// Model: gpt-5.1-mini (fast, cheap, good at structured extraction)

import { callOpenAI, MODELS } from "../openai";
import type { ExtractedQA, Stage1Output } from "../types/pipeline";

const STAGE1_SYSTEM_PROMPT = `You are a transcript parser. Your job is to extract question-answer pairs from interview transcripts.

## Your Task
Parse the interview transcript and extract each question asked by the interviewer and the candidate's response.

## Rules
1. Focus on SUBSTANTIVE questions — skip pleasantries like "How are you?" or "Can you hear me?"
2. If a question has multiple parts, keep them together as one question
3. If the candidate's answer spans multiple turns (interrupted by "mm-hmm" or clarifying questions), combine into one answer
4. Include follow-up questions as separate Q&A pairs
5. Preserve the exact wording from the transcript (don't paraphrase)
6. If there's a timestamp in the transcript, include it

## Output Format
Return a JSON array of objects with this structure:
{
  "extractedQAs": [
    {
      "id": "qa_001",
      "questionText": "The exact question from the interviewer",
      "answerText": "The candidate's full response",
      "questionIndex": 1,
      "approximateTimestamp": "00:05:30" // or null if not available
    }
  ],
  "totalQuestions": 5,
  "parsingNotes": "Any issues encountered during parsing"
}

## What Counts as a Question
- Direct questions ("Tell me about...", "What would you do if...", "Why did you...")
- Prompts that expect a response ("Walk me through...", "Describe a time when...")
- Follow-ups ("Can you elaborate?", "What happened next?")

## What to Skip
- Small talk and pleasantries
- Technical setup ("Can you share your screen?")
- Interviewer monologues that don't require a response
- The candidate asking questions at the end (unless the interviewer answers)`;

export async function extractQAPairs(transcript: string): Promise<Stage1Output> {
  const userPrompt = `Parse this interview transcript and extract all question-answer pairs:

<transcript>
${transcript}
</transcript>

Return the JSON object with extractedQAs array.`;

  const response = await callOpenAI(
    STAGE1_SYSTEM_PROMPT,
    userPrompt,
    {
      model: MODELS.FAST,
      jsonMode: true,
      maxTokens: 8000,
    }
  );

  if (!response.success) {
    throw new Error(`Stage 1 failed: ${response.error || "Unknown error"}`);
  }

  // Get content from raw or data
  const content = response.raw || (typeof response.data === "string" ? response.data : JSON.stringify(response.data));
  if (!content) {
    throw new Error(`Stage 1 failed: No content returned`);
  }

  // Parse the JSON response
  let parsed: { extractedQAs: ExtractedQA[]; totalQuestions: number; parsingNotes?: string };
  
  try {
    parsed = JSON.parse(content);
  } catch (e) {
    throw new Error(`Stage 1 failed to parse JSON: ${content.substring(0, 200)}...`);
  }

  // Validate and normalize the output
  if (!Array.isArray(parsed.extractedQAs)) {
    throw new Error("Stage 1 returned invalid format: extractedQAs is not an array");
  }

  // Ensure all required fields are present
  const normalizedQAs: ExtractedQA[] = parsed.extractedQAs.map((qa, idx) => ({
    id: qa.id || `qa_${String(idx + 1).padStart(3, "0")}`,
    questionText: qa.questionText || "",
    answerText: qa.answerText || "",
    questionIndex: qa.questionIndex || idx + 1,
    approximateTimestamp: qa.approximateTimestamp || undefined,
  }));

  return {
    extractedQAs: normalizedQAs,
    totalQuestions: normalizedQAs.length,
    transcriptWordCount: transcript.split(/\s+/).length,
    extractionNotes: parsed.parsingNotes,
  };
}





