"use client";

import { Check, Share2 } from "lucide-react";
import { useState } from "react";

export function ShareButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API can be unavailable (no permission, insecure context).
      // Nothing useful to recover into beyond not crashing.
    }
  }

  return (
    <button
      type="button"
      onClick={copy}
      className="inline-flex min-h-10 items-center gap-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm font-medium hover:bg-[color:var(--muted-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
    >
      {copied ? (
        <>
          <Check aria-hidden="true" size={15} className="text-[color:var(--accent)]" />
          Copied
        </>
      ) : (
        <>
          <Share2 aria-hidden="true" size={15} />
          Share result
        </>
      )}
    </button>
  );
}
