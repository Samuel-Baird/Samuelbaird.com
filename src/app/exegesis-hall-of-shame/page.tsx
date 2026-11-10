import type { Metadata } from "next";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { SHAME_ENTRIES } from "@/lib/hall-of-shame";

export const metadata: Metadata = {
  title: "Exegesis Hall of Shame",
  description:
    "Funny examples of poor exegesis I have come across.",
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
          Just some funny examples of poor exegesis I have come across.
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
              </div>

              <blockquote className="mt-5 border-l-2 border-[color:var(--honey)] pl-4 text-sm italic leading-relaxed text-[color:var(--muted)] sm:text-base">
                {e.text}
              </blockquote>

              <p className="small-caps mt-6 text-[11px] font-medium text-[color:var(--oxblood)]">
                The exegesis
              </p>
              <p className="serif mt-1 text-lg leading-snug sm:text-xl">
                {e.heard}
              </p>
              <p className="mt-2 text-xs text-[color:var(--muted)]">
                {e.source}
              </p>

              <p className="mt-5 text-sm">
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
