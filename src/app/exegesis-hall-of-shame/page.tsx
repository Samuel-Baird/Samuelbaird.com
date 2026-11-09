import type { Metadata } from "next";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { Tag } from "@/components/tag";
import { mailto } from "@/lib/contact";
import { SHAME_ENTRIES } from "@/lib/hall-of-shame";

export const metadata: Metadata = {
  title: "Exegesis Hall of Shame",
  description:
    "Readings of scripture so confidently wrong they are funny, each one followed by what the passage plainly says.",
  alternates: { canonical: "/exegesis-hall-of-shame" },
};

export default function ExegesisHallOfShamePage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <header className="border-b border-[color:var(--border)] pb-10">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Hall of Shame
        </p>
        <h1 className="serif mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          <DeseretTitle text="The Exegesis Hall of Shame." />
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
          Readings of scripture so bad they are funny. Each entry gives the
          claim as it was reported, then what the passage says when you read
          the sentence around it.
        </p>
      </header>

      <div className="mt-10 lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-14">
        <ol className="max-w-2xl space-y-10">
          {SHAME_ENTRIES.map((e, i) => (
            <li
              key={e.id}
              id={e.id}
              className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 sm:p-7"
            >
              <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
                <span className="serif-onum text-sm tabular-nums text-[color:var(--muted)]">
                  No. {SHAME_ENTRIES.length - i}
                </span>
                <h2 className="serif text-2xl font-semibold tracking-tight">
                  {e.reference}
                </h2>
                <Tag ink={e.faultInk}>{e.fault}</Tag>
              </div>

              <blockquote className="mt-5 border-l-2 border-[color:var(--honey)] pl-4 text-sm italic leading-relaxed text-[color:var(--muted)] sm:text-base">
                {e.text}
              </blockquote>

              <p className="small-caps mt-6 text-[11px] font-medium text-[color:var(--oxblood)]">
                The claim
              </p>
              <p className="serif mt-1 text-lg leading-snug sm:text-xl">
                {e.heard}
              </p>
              <p className="mt-2 text-xs text-[color:var(--muted)]">
                {e.source}
              </p>

              <p className="small-caps mt-6 text-[11px] font-medium text-[color:var(--muted)]">
                The plain reading
              </p>
              <p className="mt-1 text-base leading-relaxed">{e.plain}</p>
              <p className="mt-4 text-sm">
                <a
                  href={e.readUrl}
                  className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                >
                  Read the passage
                </a>
              </p>
            </li>
          ))}
        </ol>

        <aside className="mt-14 space-y-8 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-10">
          <section>
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Nominate an entry
            </h2>
            <p className="mt-3 text-sm leading-relaxed">
              Heard a reading that made you put your pen down? Send the verse,
              the claim as close to word for word as you can, and where you
              heard it.
            </p>
            <a
              href={mailto("Exegesis Hall of Shame nomination")}
              className="small-caps mt-4 inline-flex h-10 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-[13px] transition-colors hover:bg-[color:var(--muted-soft)]"
            >
              Send a nomination
            </a>
          </section>

          <section>
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              House rules
            </h2>
            <ul className="mt-3 space-y-2 text-sm leading-relaxed">
              <li>The reading is the target. The scripture is not.</li>
              <li>Speakers stay anonymous unless they said it in public.</li>
              <li>Reports are unverified, and the page says so.</li>
              <li>
                A reading that is merely different from yours does not qualify.
                It has to ignore the sentence it sits in.
              </li>
            </ul>
          </section>

          <p className="text-xs leading-relaxed text-[color:var(--muted)]">
            Independent and{" "}
            <Link
              href="/about"
              className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
            >
              not affiliated with the Church
            </Link>
            .
          </p>
        </aside>
      </div>
    </div>
  );
}
