export default function HomeLoading() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      {/* Hero */}
      <section className="max-w-3xl">
        <div className="h-3 w-24 animate-pulse rounded-full bg-[color:var(--muted-soft)]" />
        <div className="mt-4 h-14 w-full animate-pulse rounded-lg bg-[color:var(--muted-soft)] sm:h-16 md:h-[72px]" />
        <div className="mt-2 h-10 w-3/4 animate-pulse rounded-lg bg-[color:var(--muted-soft)] md:h-[72px]" />
        <div className="mt-6 h-5 w-3/4 max-w-2xl animate-pulse rounded bg-[color:var(--muted-soft)]" />
        <div className="mt-2 h-5 w-2/3 max-w-xl animate-pulse rounded bg-[color:var(--muted-soft)]" />
        <div className="mt-8 flex gap-3">
          <div className="h-11 w-36 animate-pulse rounded-full bg-[color:var(--muted-soft)]" />
          <div className="h-11 w-32 animate-pulse rounded-full bg-[color:var(--muted-soft)]" />
        </div>
      </section>

      {/* Metric tiles — channels */}
      <section className="mt-16 grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="h-24 animate-pulse rounded-2xl bg-[color:var(--muted-soft)]"
          />
        ))}
      </section>

      {/* Metric tiles — research library */}
      <section className="mt-5">
        <div className="mb-3 h-3 w-36 animate-pulse rounded-full bg-[color:var(--muted-soft)]" />
        <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="h-24 animate-pulse rounded-2xl bg-[color:var(--muted-soft)]"
            />
          ))}
        </div>
      </section>

      {/* TopStatsCarousel */}
      <div className="mt-12 h-52 animate-pulse rounded-2xl bg-[color:var(--muted-soft)]" />

      {/* Featured channels */}
      <section className="mt-20">
        <div className="flex items-end justify-between gap-3">
          <div className="h-8 w-48 animate-pulse rounded-lg bg-[color:var(--muted-soft)]" />
          <div className="h-4 w-16 animate-pulse rounded bg-[color:var(--muted-soft)]" />
        </div>
        <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <li key={i}>
              <div className="h-24 animate-pulse rounded-2xl bg-[color:var(--muted-soft)]" />
            </li>
          ))}
        </ul>
      </section>

      {/* RisersFallers */}
      <div className="mt-20">
        <div className="h-8 w-40 animate-pulse rounded-lg bg-[color:var(--muted-soft)]" />
        <div className="mt-6 grid gap-6 sm:grid-cols-2">
          {Array.from({ length: 2 }).map((_, col) => (
            <div key={col} className="space-y-3">
              <div className="h-4 w-24 animate-pulse rounded bg-[color:var(--muted-soft)]" />
              {Array.from({ length: 4 }).map((_, row) => (
                <div
                  key={row}
                  className="h-10 animate-pulse rounded-xl bg-[color:var(--muted-soft)]"
                />
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Featured studies */}
      <section className="mt-20">
        <div className="flex items-end justify-between gap-3">
          <div className="h-8 w-44 animate-pulse rounded-lg bg-[color:var(--muted-soft)]" />
          <div className="h-4 w-16 animate-pulse rounded bg-[color:var(--muted-soft)]" />
        </div>
        <ul className="mt-6 grid gap-5 sm:grid-cols-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <li key={i}>
              <div className="h-40 animate-pulse rounded-2xl bg-[color:var(--muted-soft)]" />
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
