import { ETERNAL_INCREASE_FIGURES, ETERNAL_INCREASE_QUESTIONS } from "./eternal-increase";
import {
  BAPTISM_FIGURES,
  BAPTISM_QUESTIONS,
  FAMILY_FIGURES,
  FAMILY_QUESTIONS,
  SACRAMENT_FIGURES,
  SACRAMENT_QUESTIONS,
} from "./in-preparation";
import type { FigureScore, QuizFigure, QuizQuestion } from "./types";

export type { FigureScore, QuizFigure, QuizOption, QuizQuestion } from "./types";

/**
 * One section per timeline that has a quiz. Titles are held here rather than
 * read from the timeline registry on purpose: the registry imports every
 * sources.json, and this module is pulled into client components.
 */
export type QuizSection = {
  timeline: string;
  title: string;
  /** What answering this section tells you. */
  blurb: string;
  questions: QuizQuestion[];
  figures: QuizFigure[];
};

export const QUIZ_SECTIONS: QuizSection[] = [
  {
    timeline: "/eternal-increase-timeline",
    title: "Eternal regress & eternal increase",
    blurb:
      "Whether God the Father had a Father, whether the exalted become parents of spirits, and what may be said about either.",
    questions: ETERNAL_INCREASE_QUESTIONS,
    figures: ETERNAL_INCREASE_FIGURES,
  },
  {
    timeline: "/family-proclamation-timeline",
    title: "The Family: A Proclamation to the World",
    blurb:
      "Gender as an eternal characteristic, the family forms exaltation is said to require, and what kind of document the Proclamation is.",
    questions: FAMILY_QUESTIONS,
    figures: FAMILY_FIGURES,
  },
  {
    timeline: "/baptism-timeline",
    title: "Baptism",
    blurb:
      "Whether the ordinance works the new birth or witnesses to one already worked, who may receive it, and whose baptism counts.",
    questions: BAPTISM_QUESTIONS,
    figures: BAPTISM_FIGURES,
  },
  {
    timeline: "/sacrament-timeline",
    title: "The sacrament",
    blurb:
      "What the emblems are, how plainly or ceremonially the rite is kept, and what partaking is understood to do.",
    questions: SACRAMENT_QUESTIONS,
    figures: SACRAMENT_FIGURES,
  },
];

export const ALL_QUESTIONS: QuizQuestion[] = QUIZ_SECTIONS.flatMap((s) => s.questions);

const SECTION_BY_TIMELINE = new Map(QUIZ_SECTIONS.map((s) => [s.timeline, s]));

export function quizSectionFor(timeline: string): QuizSection | null {
  return SECTION_BY_TIMELINE.get(timeline) ?? null;
}

/** Valid question ids, for validating what comes back from the client. */
export const QUESTION_IDS = new Set(ALL_QUESTIONS.map((q) => q.id));

const OPTIONS_BY_QUESTION = new Map(
  ALL_QUESTIONS.map((q) => [q.id, new Set(q.options.map((o) => o.id))]),
);

export function isValidAnswer(questionId: string, optionId: string): boolean {
  return OPTIONS_BY_QUESTION.get(questionId)?.has(optionId) ?? false;
}

/** A reader's answers: question id → chosen option id. */
export type AnswerMap = Record<string, string>;

/**
 * Ranks a timeline's figures against the reader's answers.
 *
 * Only questions where *both* the reader and the figure have a position count
 * — a figure who never addressed a question is skipped rather than scored as
 * disagreeing, since silence is not the same as dissent. Ranking is by the
 * share matched, and a figure with more comparable questions wins a tie, so a
 * one-for-one match cannot beat five-for-six.
 */
export function scoreSection(section: QuizSection, answers: AnswerMap): FigureScore[] {
  return section.figures
    .map((figure) => {
      const agreements: string[] = [];
      const disagreements: string[] = [];
      for (const question of section.questions) {
        const mine = answers[question.id];
        const theirs = figure.answers[question.id];
        if (!mine || !theirs) continue;
        (mine === theirs ? agreements : disagreements).push(question.id);
      }
      const comparable = agreements.length + disagreements.length;
      return {
        figure,
        comparable,
        matches: agreements.length,
        affinity: comparable === 0 ? 0 : agreements.length / comparable,
        agreements,
        disagreements,
      };
    })
    .sort(
      (a, b) =>
        b.affinity - a.affinity ||
        b.comparable - a.comparable ||
        a.figure.name.localeCompare(b.figure.name),
    );
}

export function answeredCount(questions: QuizQuestion[], answers: AnswerMap): number {
  return questions.filter((q) => answers[q.id]).length;
}

/** The label a reader chose, for showing their own answer back to them. */
export function optionLabel(question: QuizQuestion, optionId: string | undefined): string | null {
  if (!optionId) return null;
  return question.options.find((o) => o.id === optionId)?.label ?? null;
}
