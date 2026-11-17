export default function StudiesLoading() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <div className="h-3 w-20 animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]" />
      <div className="mt-4 h-12 w-1/2 animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)] sm:h-14" />
      <div className="mt-5 h-4 w-3/4 max-w-xl animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]" />

      <div className="mt-10 grid gap-5 sm:grid-cols-2">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="h-48 animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]"
          />
        ))}
      </div>
    </div>
  );
}
