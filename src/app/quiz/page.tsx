import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { Quiz } from "@/components/quiz/quiz-section";
import { ALL_QUESTIONS, QUIZ_SECTIONS } from "@/lib/quiz";

export const metadata: Metadata = {
  title: "Where do you land?",
  description:
    "Answer the questions each timeline puts to its sources, and see which figures on that timeline you come out closest to.",
  robots: { index: false, follow: false },
};

// Reads the signed-in reader's saved answers.
export const dynamic = "force-dynamic";

export default function QuizPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href="/timelines"
        className="inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline"
      >
        <ArrowLeft aria-hidden="true" size={13} />
        Timelines
      </Link>

      <div className="mt-4 lg:grid lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:gap-14">
        <h1 className="serif text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          <DeseretTitle text="Where do you land?" />
        </h1>
        <p className="mt-5 text-base leading-relaxed text-[color:var(--muted)] lg:mt-2">
          Every timeline reads its sources against a handful of questions. This puts the
          same questions to you — all{" "}
          <span className="tabular-nums">{ALL_QUESTIONS.length}</span> of them, from all{" "}
          <span className="tabular-nums">{QUIZ_SECTIONS.length}</span> timelines — and tells
          you which figure on each one you come out closest to. Answer them here in one
          sitting, or answer a timeline&apos;s questions on its own page; it is the same set
          of answers either way.
        </p>
      </div>

      <p className="mt-6 max-w-3xl rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)]/60 p-4 text-sm leading-relaxed text-[color:var(--muted)]">
        A match means your answers line up with positions that figure took — not that they
        would have agreed with you about anything else, and not that any position here is
        the right one. Where a figure never addressed a question, that question is skipped
        rather than counted against them.
      </p>

      <div className="mt-12">
        <Quiz signInReason="Sign in to take the quiz." />
      </div>

      <div className="dinkus" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>

      <p className="mx-auto max-w-2xl text-center text-sm leading-relaxed text-[color:var(--muted)]">
        Answers are saved to your account as you give them. You can change any of them at
        any time, or clear them entirely — from here or from{" "}
        <Link
          href="/me/quiz"
          className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
        >
          your results page
        </Link>
        .
      </p>
    </div>
  );
}
