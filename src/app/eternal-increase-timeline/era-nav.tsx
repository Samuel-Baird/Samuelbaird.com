"use client";

import { ArrowUp, ChevronDown } from "lucide-react";
import { useEffect, useState } from "react";
import type { Era } from "./constants";
import { scrollToId, scrollToTop } from "./scroll";

/**
 * Sticky jump bar for the five eras, plus the excerpt expand-all toggle.
 * The list is long enough (77 sources at full width) that scrolling to a
 * period by hand is the slowest thing on the page; these buttons and the
 * scrollspy underline replace that with one click and a you-are-here.
 */

export function EraNav({
  eras,
  expandAll,
  onToggleExpandAll,
}: {
  eras: { era: Era; count: number }[];
  expandAll: boolean;
  onToggleExpandAll: () => void;
}) {
  const [activeId, setActiveId] = useState<string | null>(null);

  // Re-observe whenever the visible era set changes: filtering can add or
  // remove whole sections from the DOM.
  const presentIds = eras
    .filter((e) => e.count > 0)
    .map((e) => e.era.id)
    .join(",");

  useEffect(() => {
    const ids = presentIds ? presentIds.split(",") : [];
    const sections = ids
      .map((id) => document.getElementById(`era-${id}`))
      .filter((el): el is HTMLElement => el != null);
    // Nothing to watch. Any stale id simply matches no button, so there is
    // no marker to clear.
    if (sections.length === 0) return;

    // The band is the middle ~5% of the viewport: whichever section straddles
    // it is the one being read. A wider band lets two sections qualify at once
    // and the active marker flickers between them.
    const observer = new IntersectionObserver(
      (records) => {
        const hit = records.find((r) => r.isIntersecting);
        if (hit) setActiveId(hit.target.id.replace(/^era-/, ""));
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 },
    );
    for (const section of sections) observer.observe(section);
    return () => observer.disconnect();
  }, [presentIds]);

  if (eras.length === 0) return null;

  return (
    <nav
      aria-label="Jump to era"
      className="sticky top-16 z-30 -mx-1 mb-6 flex items-center gap-3 border-b border-[color:var(--border)] bg-[color:var(--background)]/85 px-1 py-2 backdrop-blur print:hidden"
    >
      <ul className="flex min-w-0 flex-1 gap-1 overflow-x-auto whitespace-nowrap">
        {eras.map(({ era, count }) => {
          const active = activeId === era.id;
          return (
            <li key={era.id}>
              <button
                type="button"
                disabled={count === 0}
                aria-current={active ? "true" : undefined}
                onClick={() => scrollToId(`era-${era.id}`)}
                className={`small-caps inline-flex items-center gap-1.5 border-b-2 px-2 py-1.5 text-xs font-medium transition-colors ${
                  count === 0
                    ? "cursor-not-allowed border-transparent text-[color:var(--muted)] opacity-45"
                    : active
                      ? "border-[color:var(--accent)] text-[color:var(--accent)]"
                      : "border-transparent hover:text-[color:var(--accent)]"
                }`}
              >
                {era.label}
                <span className="tabular-nums text-[10px] text-[color:var(--muted)]">
                  {count}
                </span>
              </button>
            </li>
          );
        })}
      </ul>

      <button
        type="button"
        onClick={onToggleExpandAll}
        aria-expanded={expandAll}
        className="small-caps hidden shrink-0 items-center gap-1 text-xs font-medium text-[color:var(--accent)] hover:underline sm:inline-flex"
      >
        {expandAll ? "Collapse excerpts" : "Expand excerpts"}
        <ChevronDown
          aria-hidden="true"
          size={13}
          className={expandAll ? "rotate-180 transition-transform" : "transition-transform"}
        />
      </button>
    </nav>
  );
}

export function BackToTop() {
  const [shown, setShown] = useState(false);

  useEffect(() => {
    const onScroll = () => setShown(window.scrollY > 900);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (!shown) return null;

  return (
    <button
      type="button"
      aria-label="Back to top"
      onClick={scrollToTop}
      className="fixed bottom-5 right-5 z-30 inline-flex h-10 w-10 items-center justify-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white text-[color:var(--muted)] hover:text-[color:var(--accent)] print:hidden"
    >
      <ArrowUp aria-hidden="true" size={16} />
    </button>
  );
}
