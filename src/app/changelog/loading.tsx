export default function ChangelogLoading() {
  return (
    <div className="mx-auto max-w-4xl px-5 py-14 sm:px-8 sm:py-20">
      <div className="h-3 w-24 animate-pulse rounded-full bg-[color:var(--muted-soft)]" />
      <div className="mt-4 h-12 w-3/4 animate-pulse rounded-lg bg-[color:var(--muted-soft)] sm:h-14" />
      <div className="mt-5 h-4 w-3/4 max-w-xl animate-pulse rounded bg-[color:var(--muted-soft)]" />

      <div className="mt-10 grid gap-3 sm:grid-cols-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="h-40 animate-pulse rounded-2xl bg-[color:var(--muted-soft)]"
          />
        ))}
      </div>
    </div>
  );
}
