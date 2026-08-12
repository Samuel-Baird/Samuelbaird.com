import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { Tag } from "@/components/tag";
import { ALL_QUESTIONS } from "@/lib/quiz";
import { TIMELINES } from "./registry";

export const metadata: Metadata = {
  title: "Timelines",
  description:
    "Chronological collections of primary and official sources, showing how particular teachings have been stated over time.",
  alternates: { canonical: "/timelines" },
};

export default function TimelinesPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <header className="border-b border-[color:var(--border)] pb-10">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Timelines
        </p>
        <div className="mt-4 lg:grid lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:gap-14">
          <h1 className="serif text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
            <DeseretTitle text="Sources over time." />
          </h1>
          <p className="mt-5 text-base leading-relaxed text-[color:var(--muted)] lg:mt-2">
            A timeline gathers the primary and official sources on a single
            question and lays them out in order, so you can see for yourself how
            a teaching has been stated, restated, and sometimes reframed. Each
            entry links to the original, is graded for how directly it traces to
            the speaker, and records whether the Church currently publishes it.
          </p>
        </div>
      </header>

      <section className="mt-10">
        <div className="rounded-[var(--radius)] border border-[color:var(--honey)]/40 bg-[color:var(--honey-soft)]/40 p-5 sm:p-6 lg:flex lg:items-center lg:gap-10">
          <div className="min-w-0 lg:flex-1">
            <h2 className="serif text-xl font-semibold tracking-tight sm:text-2xl">
              Answer every timeline&apos;s questions at once
            </h2>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
              Each timeline reads its sources against a handful of questions. The quiz puts
              the same{" "}
              <span className="tabular-nums">{ALL_QUESTIONS.length}</span> questions to you
              and tells you which figure on each timeline you come out closest to. Do them
              all here, or answer a timeline&apos;s own set on its page — it is one set of
              answers, saved to your account.
            </p>
          </div>
          <Link
            href="/quiz"
            className="mt-5 inline-flex min-h-11 shrink-0 items-center gap-2 rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white lg:mt-0"
          >
            Take the quiz
            <ArrowRight aria-hidden="true" size={14} />
          </Link>
        </div>
      </section>

      <section className="mt-12">
        <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
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
                className="group block p-5 transition-colors hover:bg-[color:var(--muted-soft)]/50 sm:p-6 lg:grid lg:grid-cols-[minmax(0,1fr)_14rem] lg:items-start lg:gap-10"
              >
                <div className="min-w-0">
                  <h3 className="serif text-xl font-semibold leading-snug tracking-tight group-hover:text-[color:var(--accent)] sm:text-2xl">
                    {t.title}
                  </h3>
                  <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
                    {t.question}
                  </p>
                  <p className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)]">
                    {t.planned ? "See the scope and take its quiz" : "Open timeline"}
                    <ArrowRight aria-hidden="true" size={13} />
                  </p>
                </div>
                <dl className="mt-5 flex flex-wrap items-center gap-x-6 gap-y-2 lg:mt-0 lg:block lg:space-y-3 lg:border-l lg:border-[color:var(--border)] lg:pl-6">
                  {t.span && (
                    <div>
                      <dt className="small-caps text-[11px] text-[color:var(--muted)]">
                        Span
                      </dt>
                      <dd className="serif-onum text-base tabular-nums">
                        {t.span}
                      </dd>
                    </div>
                  )}
                  {t.sourceCount !== undefined && (
                    <div>
                      <dt className="small-caps text-[11px] text-[color:var(--muted)]">
                        Sources
                      </dt>
                      <dd className="serif-onum text-base tabular-nums">
                        {t.sourceCount}
                      </dd>
                    </div>
                  )}
                  {t.status && (
                    <div>
                      <dt className="sr-only">Status</dt>
                      <dd>
                        <Tag ink={t.planned ? "muted" : "honey"}>{t.status}</Tag>
                      </dd>
                    </div>
                  )}
                </dl>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <div className="mt-14 grid gap-10 border-t border-[color:var(--border)] pt-10 md:grid-cols-2 md:gap-14">
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
            published under the speaker&apos;s direction down to attributions
            with no traceable original. That grade is about sourcing only: a low
            grade does not mean a teaching was unimportant, and a high grade does
            not mean it is currently taught.
          </p>
        </Section>
      </div>
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
    <section>
      <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
        {title}
      </h2>
      <div className="mt-4 text-base leading-relaxed text-[color:var(--foreground)]">
        {children}
      </div>
    </section>
  );
}
