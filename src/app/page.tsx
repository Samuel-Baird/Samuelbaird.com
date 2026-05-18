import Link from "next/link";

export default function Home() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <section className="max-w-3xl">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
          Latter-day Stats
        </p>
        <h1 className="serif mt-4 text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl md:text-6xl">
          Statistics, research, and creator data on the Latter-day Saint community.
        </h1>
        <p className="mt-6 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
          A public hub tracking LDS YouTube creators, academic studies, and
          community trends — sourced from public data and updated regularly.
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/channels"
            className="inline-flex h-11 items-center rounded-full bg-[color:var(--accent)] px-5 text-sm font-medium text-white transition-colors hover:opacity-90"
          >
            Browse channels
          </Link>
          <Link
            href="/studies"
            className="inline-flex h-11 items-center rounded-full border border-[color:var(--border)] bg-white px-5 text-sm font-medium text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
          >
            Read studies
          </Link>
        </div>
      </section>

      <section className="mt-20 rounded-2xl border border-dashed border-[color:var(--border)] bg-white p-8 text-sm text-[color:var(--muted)]">
        <div className="serif text-lg text-[color:var(--foreground)]">
          Coming soon
        </div>
        <p className="mt-2 max-w-xl">
          Core metrics, top-10 channel strip, and featured studies will appear
          here once the database is connected. For now you can preview the{" "}
          <Link href="/channels" className="underline underline-offset-2">
            channels
          </Link>{" "}
          and{" "}
          <Link href="/studies" className="underline underline-offset-2">
            studies
          </Link>{" "}
          sections.
        </p>
      </section>
    </div>
  );
}
