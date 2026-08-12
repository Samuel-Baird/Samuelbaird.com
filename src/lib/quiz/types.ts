/**
 * The quiz asks the same questions a timeline asks of its sources, but of the
 * reader. Questions belong to exactly one timeline; taking a timeline's quiz
 * answers that timeline's questions, and the full quiz at /quiz runs the whole
 * bank. Answers are stored per question, so a question answered in one place
 * is already answered in the other.
 */

export type QuizOption = {
  id: string;
  /** The answer in the reader's voice, first person where it reads naturally. */
  label: string;
  /** One line of plain-language gloss, shown under the label. */
  note?: string;
};

export type QuizQuestion = {
  id: string;
  /** href of the timeline this question belongs to. */
  timeline: string;
  /** Short label for results tables and progress lists. */
  short: string;
  prompt: string;
  options: QuizOption[];
};

/**
 * Who a reader can come out closest to. For a researched timeline these are
 * real figures and every position is sourced on that timeline; for a timeline
 * still in preparation they are named theological positions rather than
 * people, so nothing is put in anyone's mouth ahead of the research.
 */
export type QuizFigure = {
  id: string;
  timeline: string;
  kind: "person" | "position";
  name: string;
  /** Dates for a person, tradition or family for a position. */
  qualifier?: string;
  /** One sentence on what matching this figure means. */
  blurb: string;
  /**
   * The figure's answer to each question, keyed by question id. A question the
   * figure never addressed is simply absent, and is skipped when scoring
   * rather than counted as a disagreement.
   */
  answers: Record<string, string>;
};

export type FigureScore = {
  figure: QuizFigure;
  /** Questions where both the reader and the figure have a position. */
  comparable: number;
  matches: number;
  /** matches / comparable, 0 when nothing is comparable. */
  affinity: number;
  agreements: string[];
  disagreements: string[];
};
