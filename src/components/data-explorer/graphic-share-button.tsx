"use client";

import { Check, Share2 } from "lucide-react";
import { useState } from "react";

/** Shares (or copies) a link to a specific graphic's page, so a link
 * pasted elsewhere renders a pretty preview of the graphic itself (see
 * openGraph in the [graphicId] page's generateMetadata). */
export function GraphicShareButton({ path, title }: { path: string; title: string }) {
  const [copied, setCopied] = useState(false);

  async function share() {
    const url = new URL(path, window.location.origin).toString();

    if (navigator.share) {
      try {
        await navigator.share({ title, url });
      } catch (error) {
        // The user cancelling the native share sheet throws AbortError -
        // that's not a failure worth reporting or falling back on.
        if (error instanceof Error && error.name === "AbortError") return;
      }
      return;
    }

    try {
      await navigator.clipboard.writeText(url);
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
      onClick={share}
      className="inline-flex min-h-9 items-center gap-1.5 rounded-[var(--radius)] border border-[color:var(--border)] px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
    >
      {copied ? (
        <>
          <Check aria-hidden="true" size={13} className="text-[color:var(--accent)]" />
          Copied
        </>
      ) : (
        <>
          <Share2 aria-hidden="true" size={13} />
          Share
        </>
      )}
    </button>
  );
}
