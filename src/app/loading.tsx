const BONE = "animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]";

export default function HomeLoading() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      {/* Hero */}
      <section className="max-w-3xl">
        <div className={`h-3 w-24 ${BONE}`} />
        <div className={`mt-4 h-14 w-full sm:h-16 md:h-[72px] ${BONE}`} />
        <div className={`mt-2 h-10 w-3/4 md:h-[72px] ${BONE}`} />
        <div className={`mt-6 h-5 w-3/4 max-w-2xl ${BONE}`} />
        <div className={`mt-2 h-5 w-2/3 max-w-xl ${BONE}`} />
        <div className="mt-8 flex flex-wrap gap-3">
          <div className={`h-11 w-36 ${BONE}`} />
          <div className={`h-11 w-32 ${BONE}`} />
          <div className={`h-11 w-32 ${BONE}`} />
        </div>
      </section>

      {/* Site-wide metric tiles */}
      <section className="mt-16 grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className={`h-24 ${BONE}`} />
        ))}
      </section>

      {/* Feature grid */}
      <section className="mt-16">
        <div className={`h-8 w-40 ${BONE}`} />
        <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <li key={i}>
              <div className={`h-44 ${BONE}`} />
            </li>
          ))}
        </ul>
      </section>

      {/* TopStatsCarousel */}
      <div className={`mt-16 h-52 ${BONE}`} />

      {/* Graphics strip */}
      <section className="mt-20">
        <div className={`h-8 w-64 ${BONE}`} />
        <ul className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <li key={i}>
              <div className={`h-52 ${BONE}`} />
            </li>
          ))}
        </ul>
      </section>

      {/* Movers + new this month */}
      <div className="mt-16 grid gap-12 lg:grid-cols-2">
        {Array.from({ length: 2 }).map((_, col) => (
          <section key={col}>
            <div className={`h-8 w-48 ${BONE}`} />
            <div className="mt-6 space-y-3">
              {Array.from({ length: 3 }).map((_, row) => (
                <div key={row} className={`h-16 ${BONE}`} />
              ))}
            </div>
          </section>
        ))}
      </div>

      {/* Featured studies */}
      <section className="mt-20">
        <div className="flex items-end justify-between gap-3">
          <div className={`h-8 w-44 ${BONE}`} />
          <div className="h-4 w-16 animate-pulse rounded bg-[color:var(--muted-soft)]" />
        </div>
        <ul className="mt-6 grid gap-5 sm:grid-cols-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <li key={i}>
              <div className={`h-40 ${BONE}`} />
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
