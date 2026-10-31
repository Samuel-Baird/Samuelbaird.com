"use client";

import { useActionState, useState } from "react";
import { startDonationCheckout, type DonateState } from "@/app/actions/donate";

const PRESETS = [5, 10, 25, 50];

const INITIAL: DonateState = { error: null };

const choiceBase =
  "inline-flex h-11 items-center justify-center rounded-[var(--radius)] border px-4 text-sm font-medium tabular-nums transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]";
const choiceOn =
  "border-[color:var(--accent)] bg-[color:var(--accent-soft)] text-[color:var(--accent)]";
const choiceOff =
  "border-[color:var(--border)] bg-[color:var(--surface)] text-[color:var(--foreground)] hover:bg-[color:var(--muted-soft)]";

export function StripeDonateForm() {
  const [state, formAction, pending] = useActionState(
    startDonationCheckout,
    INITIAL,
  );
  const [amount, setAmount] = useState("10");
  const [frequency, setFrequency] = useState<"once" | "monthly">("once");
  const dollars = Number(amount);

  return (
    <form action={formAction} className="space-y-5">
      <fieldset>
        <legend className="small-caps text-xs font-medium text-[color:var(--muted)]">
          Frequency
        </legend>
        <div className="mt-2 grid max-w-xs grid-cols-2 gap-2">
          {(["once", "monthly"] as const).map((f) => (
            <label
              key={f}
              className={`${choiceBase} cursor-pointer ${frequency === f ? choiceOn : choiceOff}`}
            >
              <input
                type="radio"
                name="frequency"
                value={f}
                checked={frequency === f}
                onChange={() => setFrequency(f)}
                className="sr-only"
              />
              {f === "once" ? "One time" : "Monthly"}
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend className="small-caps text-xs font-medium text-[color:var(--muted)]">
          Amount (USD)
        </legend>
        <div className="mt-2 flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <button
              key={p}
              type="button"
              aria-pressed={amount === String(p)}
              onClick={() => setAmount(String(p))}
              className={`${choiceBase} w-16 ${amount === String(p) ? choiceOn : choiceOff}`}
            >
              ${p}
            </button>
          ))}
          <label className="relative">
            <span className="sr-only">Custom amount in dollars</span>
            <span
              aria-hidden="true"
              className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm text-[color:var(--muted)]"
            >
              $
            </span>
            <input
              type="number"
              name="amount"
              inputMode="decimal"
              min={1}
              max={10000}
              step="0.01"
              required
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="h-11 w-28 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--surface)] pl-7 pr-3 text-sm tabular-nums focus:border-[color:var(--accent)] focus:outline-none"
            />
          </label>
        </div>
      </fieldset>

      <button
        type="submit"
        disabled={pending}
        className="inline-flex h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-60"
      >
        {pending
          ? "Opening checkout…"
          : `Donate${Number.isFinite(dollars) && dollars > 0 ? ` $${dollars % 1 === 0 ? dollars : dollars.toFixed(2)}` : ""}${frequency === "monthly" ? " / month" : ""} with card →`}
      </button>

      {state.error ? (
        <p role="alert" className="text-sm text-[color:var(--oxblood)]">
          {state.error}
        </p>
      ) : null}
    </form>
  );
}
