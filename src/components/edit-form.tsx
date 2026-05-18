"use client";

import { useActionState, useEffect, useState } from "react";
import { useFormStatus } from "react-dom";
import type { SaveResult } from "@/app/admin/actions";

type Action = (
  prevState: SaveResult | null,
  formData: FormData,
) => Promise<SaveResult>;

export function EditForm({
  action,
  children,
  className,
}: {
  action: Action;
  children: React.ReactNode;
  className?: string;
}) {
  const [state, formAction] = useActionState<SaveResult | null, FormData>(
    action,
    null,
  );

  return (
    <form action={formAction} className={className}>
      {children}
      <SaveBar state={state} />
    </form>
  );
}

function SaveBar({ state }: { state: SaveResult | null }) {
  const { pending } = useFormStatus();
  const [showSaved, setShowSaved] = useState(false);

  useEffect(() => {
    if (state?.ok) {
      setShowSaved(true);
      const timer = setTimeout(() => setShowSaved(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [state]);

  return (
    <div className="flex flex-wrap items-center gap-3">
      <button
        type="submit"
        disabled={pending}
        className="inline-flex h-10 items-center rounded-full bg-[color:var(--accent)] px-5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-60"
      >
        {pending ? (
          <>
            <Spinner />
            <span className="ml-2">Saving…</span>
          </>
        ) : (
          "Save changes"
        )}
      </button>
      {!pending && showSaved && state?.ok && (
        <span
          aria-live="polite"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-emerald-700"
        >
          <Check /> Saved
        </span>
      )}
      {!pending && state && !state.ok && (
        <span
          aria-live="polite"
          className="text-sm font-medium text-red-700"
        >
          {state.error}
        </span>
      )}
      {!pending && state?.ok && state.warnings.length > 0 && (
        <ul
          aria-live="polite"
          className="basis-full list-disc pl-5 text-xs text-amber-700"
        >
          {state.warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Spinner() {
  return (
    <svg
      aria-hidden
      className="h-4 w-4 animate-spin"
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeOpacity="0.25"
        strokeWidth="4"
      />
      <path
        d="M4 12a8 8 0 0 1 8-8"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
      />
    </svg>
  );
}

function Check() {
  return (
    <svg
      aria-hidden
      className="h-4 w-4"
      viewBox="0 0 20 20"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M4 10.5l4 4 8-9" />
    </svg>
  );
}
