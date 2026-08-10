import type { Metadata } from "next";
import {
  CATEGORY_META,
  HEARSAY_META,
  REFERENT_META,
  SOURCE_TYPE_META,
  STATUS_META,
} from "./constants";
import {
  CATEGORY_IDS,
  CORRELATION_STATUSES,
  HEARSAY_GRADES,
  REFERENTS,
  SOURCE_TYPES,
  parseSources,
} from "./schema";
import rawSources from "./sources.json";
import { TimelineExplorer } from "./timeline-explorer";

export const metadata: Metadata = {
  title: "Eternal Increase — Source Timeline",
  description:
    "A working source timeline of Latter-day Saint teachings on divine regress, eternal increase, and spirit birth.",
  robots: { index: false, follow: false },
};

const PRINCIPLES = [
  {
    title: "No retrojection",
    body: "A source is tagged only for what it states, not for what later frameworks read into it. This is why Moses 1 is “many worlds” rather than an infinite chain, and why the three-stage intelligence → spirit → body model is filed under B. H. Roberts rather than Abraham 3.",
  },
  {
    title: "Referent discipline",
    body: "Every backward-direction claim is checked for whether its “God” is demonstrably the Father, plausibly the Son, or genuinely ambiguous. This is the most important control in the dataset: the Father-referent claims are the doctrinally distinctive ones, and they are rarer than the corpus first appears.",
  },
  {
    title: "Original vs. citation",
    body: "Each source is typed as a first attestation or as a later source quoting one. Collapsing citations shows what is actually attested, independently, and when.",
  },
  {
    title: "Quote-level tagging",
    body: "A single talk or manual can make several distinct doctrinal moves. Each excerpt carries its own categories, its own referent, and where provenance differs, its own hearsay grade.",
  },
];

const CHASE_DOWN = [
  "Joseph F. Smith, Gospel Doctrine, on spirit birth (early 1900s)",
  "Hugh B. Brown / David O. McKay-era General Conference uses of “eternal increase”",
  "Encyclopedia of Mormonism (1992) — “God the Father,” “Spirit Body,” “Eternal Progression” entries as a semi-official snapshot",
  "Blake Ostler, “The Idea of Pre-existence in the Development of Mormon Thought,” Dialogue 15.1 (1982) — the standard taxonomy of tripartite vs. viviparous models",
  "Charley Harrell, “This Is My Doctrine”: The Development of Mormon Theology (2011) — chapter on theogony",
  "The fuller transcript question on the 1997 Time interview — Hinckley later indicated context had been trimmed",
];

export default function EternalIncreaseTimelinePage() {
  const entries = parseSources(rawSources).sort((a, b) =>
    a.date.localeCompare(b.date),
  );

  return (
    <div className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Source timeline · v2
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

      <Section title="Method">
        <dl className="space-y-4">
          {PRINCIPLES.map((p) => (
            <div key={p.title}>
              <dt className="text-sm font-semibold">{p.title}</dt>
              <dd className="mt-1 text-sm leading-relaxed text-[color:var(--muted)]">
                {p.body}
              </dd>
            </div>
          ))}
        </dl>
      </Section>

      <Section title="Referent">
        <p className="text-sm leading-relaxed text-[color:var(--muted)]">
          Who the “God” of a backward-direction claim actually is. Several
          load-bearing “God was once a man” texts ground themselves in
          Christ&apos;s mortality — a being who was mortal, is now God, and has
          a Father above him fits the Son perfectly and requires no theogony for
          the Father.
        </p>
        <dl className="mt-4 space-y-3">
          {REFERENTS.map((r) => (
            <div key={r} className="flex gap-3">
              <dt>
                <span
                  className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider ring-1 ${REFERENT_META[r].chip}`}
                >
                  {REFERENT_META[r].short}
                </span>
              </dt>
              <dd className="flex-1 text-sm leading-relaxed text-[color:var(--muted)]">
                {REFERENT_META[r].definition}
              </dd>
            </div>
          ))}
        </dl>
      </Section>

      <Section title="Original vs. citation">
        <dl className="space-y-3">
          {SOURCE_TYPES.map((t) => (
            <div key={t} className="flex gap-3">
              <dt>
                <span
                  className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider ring-1 ${SOURCE_TYPE_META[t].chip}`}
                >
                  {SOURCE_TYPE_META[t].label}
                </span>
              </dt>
              <dd className="flex-1 text-sm leading-relaxed text-[color:var(--muted)]">
                {SOURCE_TYPE_META[t].definition}
              </dd>
            </div>
          ))}
        </dl>
      </Section>

      <Section title="Hearsay & reliability scale">
        <p className="text-sm leading-relaxed text-[color:var(--muted)]">
          How directly the text traces to the speaker. This is a sourcing axis
          only — a low grade does not mean a teaching is unimportant, and a high
          grade does not mean it is currently taught. Where a source&apos;s
          quotes do not share a provenance, individual excerpts carry their own
          grade.
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
            <li
              key={item}
              className="border-l-2 border-[color:var(--border)] pl-3"
            >
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
