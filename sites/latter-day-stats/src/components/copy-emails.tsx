"use client";

import { useState } from "react";

export function CopyEmails({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);

  async function onCopy() {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore — user can still copy manually
    }
  }

  return (
    <div className="space-y-3">
      <textarea
        readOnly
        value={value}
        rows={6}
        className="w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-3 text-sm font-mono"
        onFocus={(e) => e.currentTarget.select()}
      />
      <button
        type="button"
        onClick={onCopy}
        disabled={!value}
        className="inline-flex h-10 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-4 text-sm font-medium text-white hover:opacity-90 disabled:opacity-60"
      >
        {copied ? "Copied!" : "Copy emails"}
      </button>
    </div>
  );
}
