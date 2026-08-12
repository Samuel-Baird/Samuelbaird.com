"use client";

import { useState } from "react";

export function MethodologyNote({
  className = "",
}: {
  className?: string;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className={className}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="small-caps inline-flex items-center gap-1 text-xs font-medium text-[color:var(--muted)] hover:text-[color:var(--accent)]"
      >
        <span
          aria-hidden
          className="flex h-4 w-4 items-center justify-center rounded-[var(--radius)] border border-current text-[10px] leading-none"
        >
          i
        </span>
        How &ldquo;expected views&rdquo; and &ldquo;priority&rdquo; are calculated
      </button>

      {open && (
        <div className="mt-2 max-w-2xl space-y-3 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)] p-4 text-sm leading-relaxed text-[color:var(--muted)]">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-[color:var(--foreground)]">
              Expected views
            </p>
            <p className="mt-1">
              The median view count of a channel&rsquo;s 15 most recent
              &ldquo;qualifying&rdquo; uploads — Shorts and anything under 14
              days old are excluded, since both would skew a baseline too
              low or too new to be meaningful. It&rsquo;s recomputed each
              time a channel is scanned, so it tracks a channel&rsquo;s
              current normal reach, not a fixed number.
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-[color:var(--foreground)]">
              Attention
            </p>
            <p className="mt-1">
              A video&rsquo;s view count divided by its channel&rsquo;s
              expected views — how many times more (or less) reach it&rsquo;s
              getting than that channel&rsquo;s normal upload.
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-[color:var(--foreground)]">
              Priority
            </p>
            <p className="mt-1">
              <code className="text-xs">attention × (debunkability ÷ 10) × recency</code>.
              Debunkability (1–10) is set during analysis — how worth an
              apologist&rsquo;s time the video is to respond to. Recency is
              an exponential decay from the video&rsquo;s publish date (a
              180-day half-life, with a floor so it never drops below 0.3×)
              — it pushes fresher claims above the backlog without fully
              burying an older video that&rsquo;s still genuinely getting a
              lot of attention.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
