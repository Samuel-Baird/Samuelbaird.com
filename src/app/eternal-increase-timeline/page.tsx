import type { Metadata } from "next";
import { CATEGORY_META, HEARSAY_META, STATUS_META } from "./constants";
import { CATEGORY_IDS, CORRELATION_STATUSES, HEARSAY_GRADES, parseSources } from "./schema";
import rawSources from "./sources.json";
import { TimelineExplorer } from "./timeline-explorer";

export const metadata: Metadata = {
  title: "Eternal Increase — Source Timeline",
  description:
    "A working source timeline of Latter-day Saint teachings on divine regress, eternal increase, and spirit birth.",
  robots: { index: false, follow: false },
};

const CHASE_DOWN = [
  "Joseph F. Smith, Gospel Doctrine, on spirit birth (early 1900s)",
  "Bruce R. McConkie, Mormon Doctrine, “Eternal Progression” and “Spirit Children” entries (1958/1966) — never official but massively influential; its 2010 discontinuation is itself a retreat data point",
  "Achieving a Celestial Marriage manual (1976) — the “as our Father in Heaven once did” chart; possibly the peak of correlated forward + backward explicitness",
  "Spencer W. Kimball's 1976 Adam–God repudiation (boundary-setting on regress speculation)",
  "Encyclopedia of Mormonism (1992) — “God the Father,” “Spirit Body,” “Eternal Progression” entries as a semi-official snapshot",
  "Hugh B. Brown / David O. McKay-era General Conference uses of “eternal increase”",
  "Blake Ostler, “The Idea of Pre-existence in the Development of Mormon Thought,” Dialogue 15.1 (1982) — the standard taxonomy of tripartite vs. viviparous models",
  "Charley Harrell, “This Is My Doctrine”: The Development of Mormon Theology (2011) — chapter on theogony",
];

export default function EternalIncreaseTimelinePage() {
  const entries = parseSources(rawSources).sort((a, b) =>
    a.date.localeCompare(b.date),
  );

  return (
    <div className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Source timeline
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        Eternal regress &amp; eternal increase.
      </h1>
      <p className="mt-5 text-base leading-relaxed text-[color:var(--muted)]">
        A chronological gathering of primary and official sources on four
        related questions: whether God the Father had a Father, whether exalted
        humans become parents of spirits, how spirit birth was described, and
        how those teachings were reframed in correlated materials.
      </p>

      <p className="mt-6 rounded-2xl border border-[color:var(--border)] bg-[color:var(--muted-soft)]/60 p-4 text-sm leading-relaxed text-[color:var(--muted)]">
        Working research document. Categorizations are the author&apos;s
        analysis, not official characterizations.
      </p>

      <Section title="Hearsay & reliability scale">
        <p className="text-sm leading-relaxed text-[color:var(--muted)]">
          How directly the text traces to the speaker. This is a sourcing axis
          only — a low grade does not mean a teaching is unimportant, and a high
          grade does not mean it is currently taught.
        </p>
        <dl className="mt-4 space-y-3">
          {HEARSAY_GRADES.map((g) => (
            <div key={g} className="flex gap-3">
              <dt
                className={`inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold ring-1 ${HEARSAY_META[g].badge}`}
              >
                {g}
              </dt>
              <dd className="text-sm leading-relaxed">
                {HEARSAY_META[g].description}{" "}
                <span className="text-[color:var(--muted)]">
                  e.g. {HEARSAY_META[g].example}
                </span>
              </dd>
            </div>
          ))}
        </dl>
      </Section>

      <Section title="Correlation status">
        <p className="text-sm leading-relaxed text-[color:var(--muted)]">
          A separate axis from hearsay: whether the Church currently publishes
          or republishes the source. A King Follett excerpt in a 1971{" "}
          <em>Ensign</em> is high-correlation despite B-tier hearsay.
        </p>
        <ul className="mt-4 space-y-2">
          {CORRELATION_STATUSES.map((s) => (
            <li key={s} className="flex items-center gap-2 text-sm">
              <span
                aria-hidden="true"
                className={`inline-block h-1.5 w-1.5 rounded-full ${STATUS_META[s].dot}`}
              />
              {STATUS_META[s].label}
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Category definitions">
        <dl className="space-y-3">
          {CATEGORY_IDS.map((id) => (
            <div key={id}>
              <dt>
                <span
                  className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-medium ring-1 ${CATEGORY_META[id].pill}`}
                >
                  {CATEGORY_META[id].label}
                </span>
              </dt>
              <dd className="mt-1 text-sm leading-relaxed text-[color:var(--muted)]">
                {CATEGORY_META[id].definition}
              </dd>
            </div>
          ))}
        </dl>
      </Section>

      <TimelineExplorer entries={entries} />

      <Section title="To chase down">
        <ul className="space-y-2 text-sm leading-relaxed text-[color:var(--muted)]">
          {CHASE_DOWN.map((item) => (
            <li key={item} className="border-l-2 border-[color:var(--border)] pl-3">
              {item}
            </li>
          ))}
        </ul>
      </Section>
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="mt-12">
      <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        {title}
      </h2>
      <div className="mt-4 text-base leading-relaxed text-[color:var(--foreground)]">
        {children}
      </div>
    </section>
  );
}
