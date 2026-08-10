export default function ChannelDetailLoading() {
  return (
    <div className="mx-auto max-w-4xl px-5 py-14 sm:px-8 sm:py-20">
      <div className="h-3 w-24 animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]" />
      <div className="mt-6 flex items-center gap-5">
        <div className="h-20 w-20 shrink-0 animate-pulse rounded-full bg-[color:var(--muted-soft)] sm:h-24 sm:w-24" />
        <div className="h-10 flex-1 animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)] sm:h-12" />
      </div>

      <div className="mt-10 grid grid-cols-2 gap-3 sm:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="h-24 animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]"
          />
        ))}
      </div>

      <div className="mt-10 h-64 animate-pulse rounded-[var(--radius)] bg-[color:var(--muted-soft)]" />
    </div>
  );
}
