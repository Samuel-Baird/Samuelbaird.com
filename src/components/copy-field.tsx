"use client";

import { Check, Copy } from "lucide-react";
import { useState } from "react";

type Props = {
  value: string;
  /** Short label shown before the value (e.g. a connection name). */
  label?: string;
  /** Wrap long text (prompts) instead of one monospace line (URLs). */
  wrap?: boolean;
};

// A value with a Copy button. Used for the MCP address and the example prompts
// on /connect.
export function CopyField({ value, label, wrap = false }: Props) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      // Clipboard blocked: leave the text selectable so it can be copied by hand.
    }
  }

  return (
    <div className="flex items-center gap-3 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 py-3">
      {label ? (
        <span className="small-caps shrink-0 text-xs font-medium text-[color:var(--muted)]">
          {label}
        </span>
      ) : null}
      <code
        className={`min-w-0 flex-1 text-sm text-[color:var(--foreground)] ${
          wrap ? "whitespace-normal leading-relaxed" : "truncate"
        }`}
      >
        {value}
      </code>
      <button
        type="button"
        onClick={copy}
        className="inline-flex h-9 shrink-0 items-center gap-1.5 rounded-[var(--radius)] border border-[color:var(--border)] px-3 text-xs font-medium text-[color:var(--foreground)] hover:bg-[color:var(--muted-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
        aria-label={`Copy ${label ?? "text"}`}
      >
        {copied ? (
          <Check aria-hidden="true" size={14} />
        ) : (
          <Copy aria-hidden="true" size={14} />
        )}
        {copied ? "Copied" : "Copy"}
      </button>
      <span className="sr-only" role="status">
        {copied ? "Copied to clipboard" : ""}
      </span>
    </div>
  );
}
