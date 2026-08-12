"use client";

import { ChevronDown } from "lucide-react";
import { useId, useState, type ReactNode } from "react";

/**
 * A titled section that starts closed behind a button.
 *
 * The body stays in the DOM and is hidden with a class rather than with
 * `<details>` or conditional rendering — the same reason the timeline's
 * excerpts do (see docs/timelines/CONSTRUCTING.md §4): a closed `<details>`
 * cannot be forced open for printing, and anything unmounted is invisible to
 * in-page search. `print:block` puts every section back for a printout.
 *
 * Use `unmountWhenClosed` only where the body is genuinely expensive — the
 * 315-entry source list — accepting the loss of find-in-page for that one.
 */
export function CollapsibleSection({
  title,
  blurb,
  openLabel,
  closedLabel,
  meta,
  defaultOpen = false,
  unmountWhenClosed = false,
  children,
}: {
  title: string;
  blurb?: ReactNode;
  /** Button text when the section is closed, e.g. "Take the quiz". */
  closedLabel: string;
  /** Button text when it is open, e.g. "Hide the quiz". */
  openLabel: string;
  /** Small print alongside the button — a count, usually. */
  meta?: string;
  defaultOpen?: boolean;
  unmountWhenClosed?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const bodyId = useId();

  return (
    <section className="mt-12">
      <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white">
        <button
          type="button"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          aria-controls={bodyId}
          className="flex w-full items-start justify-between gap-5 p-5 text-left sm:p-6"
        >
          <span className="min-w-0">
            <span className="serif block text-xl font-semibold tracking-tight sm:text-2xl">
              {title}
            </span>
            {blurb && (
              <span className="mt-1.5 block max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
                {blurb}
              </span>
            )}
            {meta && (
              <span className="small-caps mt-2 block text-[11px] text-[color:var(--muted)]">
                {meta}
              </span>
            )}
          </span>
          <span className="mt-0.5 inline-flex shrink-0 items-center gap-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)] px-3 py-2 text-xs font-medium">
            <span className="hidden sm:inline">{open ? openLabel : closedLabel}</span>
            <ChevronDown
              aria-hidden="true"
              size={14}
              className={open ? "rotate-180 motion-safe:transition-transform" : "motion-safe:transition-transform"}
            />
          </span>
        </button>
      </div>

      <div id={bodyId} className={open ? "mt-8" : "mt-8 hidden print:block"}>
        {unmountWhenClosed && !open ? null : children}
      </div>
    </section>
  );
}
