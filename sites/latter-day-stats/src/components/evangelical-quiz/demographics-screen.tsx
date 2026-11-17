"use client";

import { ArrowLeft, ArrowRight } from "lucide-react";
import { useState } from "react";
import {
  DEMOGRAPHICS_DISCLOSURE,
  DEMOGRAPHICS_PROVENANCE,
  EMPTY_DEMOGRAPHICS,
  validateDemographics,
  type Demographics,
} from "@/lib/evangelical-quiz/demographics";
import { DemographicsFields } from "./demographics-fields";

/**
 * The optional demographic intake, shown once before question 1. Every
 * field is optional and the whole screen is skippable; nothing here feeds
 * the score or appears on the results screen - it exists so results can
 * be analyzed in aggregate (e.g. self-reported religion vs. the tradition
 * the scoring assigns).
 *
 * The questions themselves are DemographicsFields, shared with the
 * account's editor at /me/quiz so the two can't drift apart.
 */
export function DemographicsScreen({
  onSubmit,
  onSkip,
  onBack,
}: {
  onSubmit: (d: Demographics) => void;
  onSkip: () => void;
  onBack: () => void;
}) {
  const [demographics, setDemographics] = useState<Demographics>(EMPTY_DEMOGRAPHICS);

  return (
    <div>
      <button
        type="button"
        onClick={onBack}
        className="inline-flex min-h-9 items-center gap-1.5 rounded-[var(--radius)] px-1 text-xs font-medium text-[color:var(--accent)] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
      >
        <ArrowLeft aria-hidden="true" size={13} />
        Back
      </button>

      <h2 className="serif mt-4 text-2xl font-semibold leading-snug tracking-tight sm:text-3xl">
        A few optional questions first
      </h2>
      <p className="mt-3 max-w-xl text-sm leading-relaxed text-[color:var(--muted)]">
        {DEMOGRAPHICS_DISCLOSURE}
      </p>
      <p className="mt-2 max-w-xl text-sm leading-relaxed text-[color:var(--muted)]">
        {DEMOGRAPHICS_PROVENANCE}
      </p>

      <div className="mt-8 max-w-2xl">
        <DemographicsFields value={demographics} onChange={setDemographics} />
      </div>

      <div className="mt-8 flex flex-wrap items-center gap-4">
        <button
          type="button"
          onClick={() => onSubmit(validateDemographics(demographics))}
          className="inline-flex min-h-11 items-center gap-2 rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
        >
          Continue
          <ArrowRight aria-hidden="true" size={15} />
        </button>
        <button
          type="button"
          onClick={onSkip}
          className="text-sm font-medium text-[color:var(--muted)] hover:text-[color:var(--foreground)] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
        >
          Skip — go to question 1
        </button>
      </div>

      <p className="mt-6 max-w-xl text-xs leading-relaxed text-[color:var(--muted)]">
        These answers never affect your score and are never shown with your result.
      </p>
    </div>
  );
}
