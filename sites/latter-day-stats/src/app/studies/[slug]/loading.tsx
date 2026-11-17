export default function StudyDetailLoading() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
      <div className="h-3 w-20 animate-pulse rounded-full bg-[color:var(--muted-soft)]" />
      <div className="mt-4 h-10 w-full max-w-2xl animate-pulse rounded-lg bg-[color:var(--muted-soft)] sm:h-12" />
      <div className="mt-3 h-4 w-1/3 animate-pulse rounded bg-[color:var(--muted-soft)]" />

      <div className="mt-10 space-y-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="h-4 w-full animate-pulse rounded bg-[color:var(--muted-soft)]"
          />
        ))}
        <div className="h-4 w-2/3 animate-pulse rounded bg-[color:var(--muted-soft)]" />
      </div>
    </div>
  );
}
