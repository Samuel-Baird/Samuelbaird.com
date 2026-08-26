"use client";

import { ArrowLeft, ArrowRight } from "lucide-react";
import { useState } from "react";
import {
  DEMOGRAPHICS_DISCLOSURE,
  GENDER_OPTIONS,
  TRADITION_OPTIONS,
  validateDemographics,
  type Demographics,
} from "@/lib/evangelical-quiz/demographics";

/**
 * The optional demographic intake, shown once before question 1. Every
 * field is optional and the whole screen is skippable; nothing here feeds
 * the score or appears on the results screen - it exists so results can
 * be analyzed in aggregate (e.g. self-reported tradition vs. the
 * tradition the scoring assigns).
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
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [traditionSlug, setTraditionSlug] = useState("");

  function submit() {
    const parsedAge = age.trim() === "" ? null : Number(age);
    onSubmit(
      validateDemographics({
        age: parsedAge !== null && Number.isFinite(parsedAge) ? Math.trunc(parsedAge) : null,
        gender: gender || null,
        traditionSlug: traditionSlug || null,
      }),
    );
  }

  const selectClass =
    "h-11 w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none";

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

      <div className="mt-8 max-w-md space-y-6">
        <div>
          <label htmlFor="eq-age" className="block text-sm font-medium">
            Age
          </label>
          <input
            id="eq-age"
            type="number"
            inputMode="numeric"
            min={1}
            max={110}
            value={age}
            onChange={(e) => setAge(e.target.value)}
            placeholder="Optional"
            className="mt-1.5 h-11 w-32 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm placeholder:text-[color:var(--muted)] focus:border-[color:var(--accent)] focus:outline-none"
          />
        </div>

        <div>
          <label htmlFor="eq-gender" className="block text-sm font-medium">
            Gender
          </label>
          <select
            id="eq-gender"
            value={gender}
            onChange={(e) => setGender(e.target.value)}
            className={`mt-1.5 ${selectClass}`}
          >
            <option value="">Optional — choose one</option>
            {GENDER_OPTIONS.map((g) => (
              <option key={g.slug} value={g.slug}>
                {g.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="eq-tradition" className="block text-sm font-medium">
            Which religious tradition do you identify with?
          </label>
          <select
            id="eq-tradition"
            value={traditionSlug}
            onChange={(e) => setTraditionSlug(e.target.value)}
            className={`mt-1.5 ${selectClass}`}
          >
            <option value="">Optional — choose one</option>
            {TRADITION_OPTIONS.map((t) => (
              <option key={t.slug} value={t.slug}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-8 flex flex-wrap items-center gap-4">
        <button
          type="button"
          onClick={submit}
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
