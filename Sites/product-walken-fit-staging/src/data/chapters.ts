/**
 * Chapter definitions - single source of truth for image/caption mapping
 * 3 quotes per chapter → 20 chapters for 58+ quotes
 */

export interface Chapter {
  chapter: number;
  image: string;
  caption: string;
}

export const CHAPTERS: Chapter[] = [
  { chapter: 1, image: "/images/walken-1.png", caption: "Walken is... aligning. On first principles. And calling it a go‑forward." },
  { chapter: 2, image: "/images/walken-2.png", caption: "Walken is SOCIALIZING the plan. Minimizing... stakeholder-induced scope." },
  { chapter: 3, image: "/images/walken-3.png", caption: "Walken is building... internal conviction. Without MANUFACTURING urgency." },
  { chapter: 4, image: "/images/walken-4.png", caption: "Walken is operationalizing. Calm. As a repeatable... motion." },
  { chapter: 5, image: "/images/walken-5.png", caption: "Walken is REINFORCING the narrative. Through consistent... execution." },
  { chapter: 6, image: "/images/walken-6.png", caption: "Walken is carrying the operating model. As a single source. Of TRUTH." },
  { chapter: 7, image: "/images/walken-7.png", caption: "Walken is establishing... signal hygiene. And accepting the COST of focus." },
  { chapter: 8, image: "/images/walken-8.png", caption: "Walken is turning AMBIGUITY... into a roadmap artifact." },
  { chapter: 9, image: "/images/walken-9.png", caption: "Walken is escalating. Without panic. And documenting... the WHY." },
  { chapter: 10, image: "/images/walken-10.png", caption: "Walken is running a CONTROLLED experiment. On reality." },
  { chapter: 11, image: "/images/walken-11.png", caption: "Walken is entering... a focus sprint. The KPI aura? Expected... behavior." },
  { chapter: 12, image: "/images/walken-12.png", caption: "Walken is consolidating DASHBOARDS. Into a coherent... worldview." },
  { chapter: 13, image: "/images/walken-13.png", caption: "Walken is shifting. From execution. To SYSTEMS thinking. No change in tone." },
  { chapter: 14, image: "/images/walken-14.png", caption: "Walken is validating the model. By OBSERVING... its side effects." },
  { chapter: 15, image: "/images/walken-15.png", caption: "Walken is managing MULTIPLE workstreams. With a single... facial expression." },
  { chapter: 16, image: "/images/walken-16.png", caption: "Walken is improving... CONVERSION. By raking the funnel. More intentionally." },
  { chapter: 17, image: "/images/walken-17.png", caption: "Walken has achieved... COVERAGE. Demand is arriving. Passively." },
  { chapter: 18, image: "/images/walken-18.png", caption: "Walken is validating signal quality. By OBSERVING it... in parallel." },
  { chapter: 19, image: "/images/walken-19.png", caption: "Walken has migrated. The system. He did NOT... schedule downtime." },
  { chapter: 20, image: "/images/walken-20.png", caption: "Walken has... closed the loop." },
];

/**
 * Get chapter index (1-20) for a quote id
 * 3 quotes per chapter: quotes 1-3 → chapter 1, quotes 4-6 → chapter 2, etc.
 */
export function getChapterIndexForQuoteId(quoteId: number): number {
  return Math.min(20, Math.ceil(quoteId / 3));
}

/**
 * Get full chapter data for a quote id
 */
export function getChapterForQuoteId(quoteId: number): Chapter {
  const chapterIndex = getChapterIndexForQuoteId(quoteId);
  return CHAPTERS[chapterIndex - 1];
}

/**
 * Get transcendence level (1-4) for a quote id
 * Maps 20 chapters to 4 transcendence levels:
 * - Level 1: Chapters 1-5 (quotes 1-15) - Early GTM learnings
 * - Level 2: Chapters 6-10 (quotes 16-30) - Building momentum
 * - Level 3: Chapters 11-15 (quotes 31-45) - Approaching enlightenment
 * - Level 4: Chapters 16-20 (quotes 46-58+) - Full GTM transcendence
 */
export function getTranscendenceLevel(quoteId: number): number {
  const chapter = getChapterIndexForQuoteId(quoteId);
  if (chapter <= 5) return 1;
  if (chapter <= 10) return 2;
  if (chapter <= 15) return 3;
  return 4;
}
