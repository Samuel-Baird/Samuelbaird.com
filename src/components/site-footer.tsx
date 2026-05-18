import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-[color:var(--border)] bg-[color:var(--muted-soft)]/40">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-5 py-10 text-sm text-[color:var(--muted)] sm:px-8 md:flex-row md:items-center md:justify-between">
        <div className="space-y-2">
          <div className="serif text-base font-medium text-[color:var(--foreground)]">
            Latter-day Stats
          </div>
          <p className="max-w-md leading-relaxed">
            Statistics, research, and creator data on the Latter-day Saint
            community. Not affiliated with The Church of Jesus Christ of
            Latter-day Saints.
          </p>
        </div>
        <nav className="flex flex-wrap gap-x-6 gap-y-2">
          <Link href="/channels" className="hover:text-[color:var(--foreground)] transition-colors">Channels</Link>
          <Link href="/studies" className="hover:text-[color:var(--foreground)] transition-colors">Studies</Link>
          <Link href="/about" className="hover:text-[color:var(--foreground)] transition-colors">About</Link>
          <Link href="/contact" className="hover:text-[color:var(--foreground)] transition-colors">Contact</Link>
        </nav>
      </div>
    </footer>
  );
}
