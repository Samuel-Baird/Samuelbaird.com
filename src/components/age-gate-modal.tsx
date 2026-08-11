"use client";

import { Loader2 } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { confirmAge } from "@/app/actions/account";

// COPPA: shown once, right after a user's first-ever sign-in (see
// /auth/callback, which appends `age_gate=1` to the post-login redirect when
// the profile has never confirmed its age). Deliberately has no close button,
// backdrop-dismiss, or Escape handling — unlike AuthPromptProvider's sign-in
// modal, this one must be resolved via the confirm button so every account
// ends up with an age_confirmed_at stamp.
export function AgeGateModal() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [confirmed, setConfirmed] = useState(false);
  const [pending, setPending] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  const open = !dismissed && searchParams.get("age_gate") === "1";

  async function onContinue() {
    setPending(true);
    try {
      await confirmAge();
    } catch (error) {
      console.error("confirmAge failed:", error);
    }
    setPending(false);
    setDismissed(true);

    const params = new URLSearchParams(searchParams.toString());
    params.delete("age_gate");
    const qs = params.toString();
    router.replace(qs ? `?${qs}` : window.location.pathname, {
      scroll: false,
    });
  }

  if (!open) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="age-gate-title"
    >
      <div className="absolute inset-0 bg-black/40" />
      <section className="relative w-full max-w-md rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--background)] p-7 shadow-lg">
        <h2
          id="age-gate-title"
          className="serif text-2xl font-semibold tracking-tight text-[color:var(--foreground)]"
        >
          One more thing
        </h2>
        <p className="mt-2 text-sm text-[color:var(--muted)]">
          Latter-day Stats accounts aren&apos;t available to anyone under 13.
          Please confirm your age to finish setting up your account.
        </p>

        <label className="mt-6 flex items-start gap-2.5 text-sm text-[color:var(--foreground)]">
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
            className="mt-0.5 h-4 w-4 shrink-0 rounded-sm border-[color:var(--border)] accent-[color:var(--accent)]"
          />
          <span>I confirm I am at least 13 years old.</span>
        </label>

        <button
          type="button"
          disabled={pending || !confirmed}
          onClick={onContinue}
          className="mt-6 inline-flex h-12 w-full items-center justify-center gap-2 rounded-[var(--radius)] bg-[color:var(--accent)] px-5 text-sm font-medium text-white transition-colors hover:bg-[color:var(--foreground)] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          Continue
        </button>
      </section>
    </div>
  );
}
