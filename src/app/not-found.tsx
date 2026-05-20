import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-24 sm:px-8 sm:py-32">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        404
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        Page not found.
      </h1>
      <p className="mt-5 max-w-md text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        The page you&rsquo;re looking for doesn&rsquo;t exist or may have moved.
      </p>
      <div className="mt-8 flex flex-wrap gap-3">
        <Link
          href="/"
          className="inline-flex h-11 items-center rounded-full bg-[color:var(--accent)] px-5 text-sm font-medium text-white transition-colors hover:opacity-90"
        >
          Go home
        </Link>
        <Link
          href="/channels"
          className="inline-flex h-11 items-center rounded-full border border-[color:var(--border)] bg-white px-5 text-sm font-medium text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
        >
          Browse channels
        </Link>
        <Link
          href="/studies"
          className="inline-flex h-11 items-center rounded-full border border-[color:var(--border)] bg-white px-5 text-sm font-medium text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
        >
          Browse studies
        </Link>
      </div>
    </div>
  );
}
