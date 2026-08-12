import type { Metadata } from "next";
import Link from "next/link";
import { BeehiveMark } from "@/components/beehive-mark";
import { CollapsibleSection } from "@/components/collapsible-section";
import { DeseretTitle } from "@/components/deseret-title";
import { Quiz } from "@/components/quiz/quiz-section";
import { PortraitHall } from "./portraits/portrait-hall";
import { parseSources } from "./schema";
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
  {
    title: "Corpus-level coverage",
    body: "Every General Conference talk containing an exaltation word-form — 1,980 talks, 1850s to the 2020s — has been classified, and the at-risk classes were then re-read in full in a second, adversarial pass, together with 349 further talks that carry related vocabulary without ever saying “exaltation.” Of 2,329 talks screened, 222 make substantive claims on these axes. Conference sources here are drawn from that class; claims about absence rest on the screen rather than on a failure to recall an example. The full classification ledger, including which pass classified each talk, is published in the project repository.",
  },
  {
    title: "One scale per question",
    body: "Being tagged with a claim says nothing about which way a source leans on it, so each excerpt also answers the questions its tags raise — and every question keeps its own scale, because they do not all have two sides. How many Gods stand above the Father has four answers, and an unquantified chain is an indefinite claim rather than an infinite one. Questions are kept apart even where the sources run them together: whether the Father was always God is not the same question as whether he lived a mortal life, since this tradition already holds that Christ was God throughout his. A passage that turns out not to speak to a question it raised is recorded as answering exactly that. All of it is a reading of the excerpt rather than an official characterisation, and the readings still unconfirmed are marked.",
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
  // Citation counts for the portrait hall come from the live dataset, so the
  // "cited N times" captions stay honest as sources are added.
  const citedCounts: Record<string, number> = {};
  for (const entry of entries) {
    citedCounts[entry.speaker] = (citedCounts[entry.speaker] ?? 0) + 1;
  }

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Source timeline · v2
      </p>
      <h1 className="serif mt-4 max-w-3xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="Eternal regress & eternal increase." />
      </h1>
      <p className="mt-5 max-w-3xl text-base leading-relaxed text-[color:var(--muted)]">
        A chronological gathering of primary and official sources on four
        related questions: whether God the Father had a Father, whether exalted
        humans become parents of spirits, how spirit birth was described, and
        how those teachings were reframed in correlated materials.
      </p>

      <p className="mt-6 max-w-3xl rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)]/60 p-4 text-sm leading-relaxed text-[color:var(--muted)]">
        Working research document. Categorizations are the author&apos;s
        analysis, not official characterizations.
      </p>

      <details className="group mt-8">
        <summary className="inline-flex cursor-pointer list-none items-center gap-1.5 text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)] [&::-webkit-details-marker]:hidden">
          Method
          <span className="normal-case tracking-normal text-[color:var(--muted)] group-open:hidden">
            — four rules the dataset follows
          </span>
        </summary>
        <dl className="mt-4 max-w-3xl space-y-4">
          {PRINCIPLES.map((p) => (
            <div key={p.title}>
              <dt className="text-sm font-semibold">{p.title}</dt>
              <dd className="mt-1 text-sm leading-relaxed text-[color:var(--muted)]">
                {p.body}
              </dd>
            </div>
          ))}
        </dl>
      </details>

      <CollapsibleSection
        title="Which of them are you?"
        blurb={
          <>
            The six questions the portrait hall reads each speaker against, put to you
            instead. Answer them and see whose positions yours line up with — and where you
            part company. You can also{" "}
            <Link
              href="/quiz"
              className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
            >
              answer every timeline&apos;s questions at once
            </Link>
            .
          </>
        }
        meta="6 questions · answers saved to your account"
        closedLabel="Take the quiz"
        openLabel="Hide the quiz"
      >
        <Quiz
          timeline="/eternal-increase-timeline"
          signInReason="Sign in to take the quiz."
        />
      </CollapsibleSection>

      <CollapsibleSection
        title="The portrait hall"
        blurb="The ten voices heard most often in this timeline's sources, hung as framed cameos. Select one for a summary of what its sitter believed, then the detailed profile."
        meta="10 speakers"
        closedLabel="See the profiles"
        openLabel="Hide the profiles"
      >
        <PortraitHall citedCounts={citedCounts} />
      </CollapsibleSection>

      <div className="dinkus" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>

      <TimelineExplorer entries={entries} />

      <div className="dinkus" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>

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
