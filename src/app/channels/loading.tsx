export default function ChannelsLoading() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <div className="h-3 w-24 animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]" />
      <div className="mt-4 h-12 w-2/3 animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)] sm:h-14" />
      <div className="mt-5 h-4 w-3/4 max-w-xl animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]" />
      <div className="mt-2 h-4 w-1/2 max-w-md animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]" />

      <div className="mt-10 grid gap-8 md:grid-cols-[260px_minmax(0,1fr)]">
        <div className="hidden md:block">
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className="h-32 animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]"
              />
            ))}
          </div>
        </div>
        <div className="space-y-3">
          <div className="h-11 w-full max-w-xs animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]" />
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={i}
              className="h-16 animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]"
            />
          ))}
        </div>
      </div>
    </div>
  );
}
