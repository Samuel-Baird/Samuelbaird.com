"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

type VersionOption = { id: string; label: string };

export function VersionPicker({
  docSlug,
  versions,
}: {
  docSlug: string;
  versions: VersionOption[];
}) {
  const router = useRouter();
  const [a, setA] = useState(versions[0]?.id ?? "");
  const [b, setB] = useState(versions[1]?.id ?? versions[0]?.id ?? "");

  if (versions.length < 2) return null;

  function handleCompare() {
    if (a && b && a !== b) {
      router.push(`/versions/${docSlug}/compare?a=${a}&b=${b}`);
    }
  }

  const selectClass =
    "h-10 rounded-full border border-[color:var(--border)] bg-white px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none";

  return (
    <div className="mt-8 rounded-2xl border border-[color:var(--border)] bg-[color:var(--muted-soft)] p-5">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Compare editions
      </p>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <select
          value={a}
          onChange={(e) => setA(e.target.value)}
          className={selectClass}
          aria-label="First edition"
        >
          {versions.map((v) => (
            <option key={v.id} value={v.id}>
              {v.label}
            </option>
          ))}
        </select>
        <span className="text-sm text-[color:var(--muted)]">vs</span>
        <select
          value={b}
          onChange={(e) => setB(e.target.value)}
          className={selectClass}
          aria-label="Second edition"
        >
          {versions.map((v) => (
            <option key={v.id} value={v.id}>
              {v.label}
            </option>
          ))}
        </select>
        <button
          onClick={handleCompare}
          disabled={!a || !b || a === b}
          className="inline-flex h-10 items-center rounded-full bg-[color:var(--accent)] px-5 text-sm font-medium text-white hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Compare →
        </button>
      </div>
      {a === b && a && (
        <p className="mt-2 text-xs text-[color:var(--muted)]">
          Select two different editions to compare.
        </p>
      )}
    </div>
  );
}
