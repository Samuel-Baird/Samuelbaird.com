"use client";

import { useState, useTransition } from "react";
import { usePathname } from "next/navigation";
import { saveEvangelicalDemographics } from "@/app/actions/evangelical-quiz";
import {
  isEmptyDemographics,
  validateDemographics,
  type Demographics,
} from "@/lib/evangelical-quiz/demographics";
import { DemographicsFields } from "./demographics-fields";
import { BASE_PATH } from "@/lib/site";

/**
 * The account's own copy of the quiz intake, for changing an answer (or
 * clearing one) after the fact. Same questions as the intake screen, via
 * the same DemographicsFields.
 *
 * Saves are explicit rather than per-field: this is a form of nine
 * dropdowns, and firing nine server actions while someone works through it
 * would be both chattier and harder to reason about than one Save.
 */
export function DemographicsEditor({ initial }: { initial: Demographics }) {
  const pathname = usePathname();
  const [demographics, setDemographics] = useState<Demographics>(initial);
  const [saved, setSaved] = useState<Demographics | null>(initial);
  const [failed, setFailed] = useState(false);
  const [pending, startTransition] = useTransition();

  // Compared field by field rather than by identity: picking an option and
  // then putting it back should leave the button quiet.
  const dirty =
    saved === null ||
    (Object.keys(demographics) as (keyof Demographics)[]).some(
      (k) => demographics[k] !== saved[k],
    );

  function save() {
    const next = validateDemographics(demographics);
    setDemographics(next);
    setFailed(false);
    startTransition(async () => {
      try {
        await saveEvangelicalDemographics({ ...next, currentPath: pathname });
        setSaved(next);
      } catch (error) {
        console.error("Failed to save demographics:", error);
        setFailed(true);
      }
    });
  }

  return (
    <section className="mt-6 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6">
      <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
        About you
      </h2>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
        The optional questions from &ldquo;How evangelical are you?&rdquo; — the same
        ones Pew Research Center asks in its Religious Landscape Study, so answers here
        can be compared with a national sample. They never affect a score and are never
        shown with a result. Change any of them, or set one back to blank to withdraw it.
      </p>

      <div className="mt-6 max-w-2xl">
        <DemographicsFields
          value={demographics}
          onChange={setDemographics}
          idPrefix="me-demographics"
        />
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-4">
        <button
          type="button"
          onClick={save}
          disabled={pending || !dirty}
          className="inline-flex h-10 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
        >
          {pending ? "Saving…" : "Save"}
        </button>

        {failed ? (
          <span className="text-xs text-[color:var(--oxblood)]">
            Could not save — try again.
          </span>
        ) : dirty ? (
          <span className="text-xs text-[color:var(--muted)]">Unsaved changes.</span>
        ) : saved !== null && isEmptyDemographics(saved) ? (
          <span className="text-xs text-[color:var(--muted)]">
            Nothing recorded — every question is optional.
          </span>
        ) : (
          <span className="text-xs text-[color:var(--muted)]">Saved.</span>
        )}
      </div>

      <p className="mt-5 text-xs leading-relaxed text-[color:var(--muted)]">
        Answers already attached to a completed run stay with that run as a snapshot of
        what you said at the time; changing them here does not rewrite it. Deleting a run
        from{" "}
        <a
          href={`${BASE_PATH}/how-evangelical/history`}
          className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
        >
          your quiz history
        </a>{" "}
        removes its copy, and deleting your account removes everything.
      </p>
    </section>
  );
}
