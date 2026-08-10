import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { Tag } from "@/components/tag";
import { TIMELINES } from "./registry";

export const metadata: Metadata = {
  title: "Timelines",
  description:
    "Chronological collections of primary and official sources, showing how particular teachings have been stated over time.",
};

export default function TimelinesPage() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Timelines
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        Sources over time.
      </h1>
      <p className="mt-5 text-base leading-relaxed text-[color:var(--muted)]">
        A timeline gathers the primary and official sources on a single
        question and lays them out in order, so you can see for yourself how a
        teaching has been stated, restated, and sometimes reframed. Each entry
        links to the original, is graded for how directly it traces to the
        speaker, and records whether the Church currently publishes it.
      </p>

      <Section title="What these are for">
        <p>
          The aim is to show evidence rather than argue a conclusion. Sources
          are tagged for what they actually state — not for what later
          frameworks read back into them — and a later source that quotes an
          earlier one is marked as a citation rather than counted as
          independent evidence. That distinction makes it possible to ask what
          has genuinely been taught, by whom, and when.
        </p>
        <p className="mt-3">
          Categorizations are the author&apos;s analysis, not official
          characterizations, and several entries are still being verified
          against their originals. Read them as a working research document.
        </p>
      </Section>

      <section className="mt-12">
        <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
          Available timelines
        </h2>
        <ul className="mt-4 rounded-[var(--radius)] border border-[color:var(--border)]">
          {TIMELINES.map((t, i) => (
            <li key={t.href}>
              {i > 0 && (
                <div className="dinkus" aria-hidden="true" style={{ marginBlock: 0 }}>
                  <BeehiveMark className="h-3.5 w-3.5" />
                </div>
              )}
              <Link
                href={t.href}
                className="group block p-5 transition-colors hover:bg-[color:var(--muted-soft)]/50 sm:p-6"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="serif-onum rounded-[var(--radius)] bg-[color:var(--muted-soft)] px-2.5 py-1 text-xs tabular-nums">
                    {t.span}
                  </span>
                  <span className="text-xs text-[color:var(--muted)]">
                    {t.sourceCount} sources
                  </span>
                  {t.status && <Tag ink="honey">{t.status}</Tag>}
                </div>
                <h3 className="serif mt-3 text-xl font-semibold leading-snug tracking-tight group-hover:text-[color:var(--accent)]">
                  {t.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-[color:var(--muted)]">
                  {t.question}
                </p>
                <p className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)]">
                  Open timeline
                  <ArrowRight aria-hidden="true" size={13} />
                </p>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <Section title="How sources are handled">
        <p>
          Every source is cited to its original wherever one survives — a
          manuscript or first printing in preference to a later reprint. Where
          a sermon exists in several independent scribal accounts, each is
          listed, because amalgamated texts quietly smooth over real
          disagreements between the reporters.
        </p>
        <p className="mt-3">
          Sources are graded A to E for provenance, from first-person text
          published under the speaker&apos;s direction down to attributions with
          no traceable original. That grade is about sourcing only: a low grade
          does not mean a teaching was unimportant, and a high grade does not
          mean it is currently taught.
        </p>
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
