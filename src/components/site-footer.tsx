import Link from "next/link";
import { BeehiveMark } from "@/components/beehive-mark";

export function SiteFooter() {
  return (
    <footer className="border-t border-[color:var(--border)] bg-[color:var(--muted-soft)]/40">
      <div className="mx-auto max-w-6xl px-5 py-10 sm:px-8">
        <div className="flex flex-col gap-6 text-sm text-[color:var(--muted)] md:flex-row md:items-center md:justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-2 serif text-base font-medium text-[color:var(--foreground)]">
              <BeehiveMark className="h-4 w-4 text-[color:var(--honey)]" />
              Latter-day Stats
            </div>
            <p className="max-w-md leading-relaxed">
              Statistics, research, and creator data on the Latter-day Saint
              community. Not affiliated with The Church of Jesus Christ of
              Latter-day Saints.
            </p>
          </div>
          <nav className="small-caps flex flex-wrap gap-x-6 gap-y-2 text-[13px]">
            <Link href="/channels" className="hover:text-[color:var(--foreground)] transition-colors">Channels</Link>
            <Link href="/studies" className="hover:text-[color:var(--foreground)] transition-colors">Studies</Link>
            <Link href="/data-explorer" className="hover:text-[color:var(--foreground)] transition-colors">Data Explorer</Link>
            <Link href="/compare" className="hover:text-[color:var(--foreground)] transition-colors">Compare</Link>
            <Link href="/connect" className="hover:text-[color:var(--foreground)] transition-colors">Use with AI</Link>
            <Link href="/about" className="hover:text-[color:var(--foreground)] transition-colors">About</Link>
            <Link href="/faq" className="hover:text-[color:var(--foreground)] transition-colors">FAQ</Link>
            <Link href="/contact" className="hover:text-[color:var(--foreground)] transition-colors">Contact</Link>
            <Link href="/donate" className="hover:text-[color:var(--foreground)] transition-colors">Donate</Link>
          </nav>
        </div>
        <div className="dinkus mt-8 mb-0 text-xs">
          <BeehiveMark className="h-3.5 w-3.5" />
        </div>

        <nav className="small-caps flex flex-wrap justify-center gap-x-5 gap-y-2 text-[11px] text-[color:var(--muted)]">
          <Link href="/terms" className="hover:text-[color:var(--foreground)] transition-colors">Terms</Link>
          <Link href="/privacy" className="hover:text-[color:var(--foreground)] transition-colors">Privacy</Link>
          <Link href="/dmca" className="hover:text-[color:var(--foreground)] transition-colors">Copyright</Link>
          <Link href="/accessibility" className="hover:text-[color:var(--foreground)] transition-colors">Accessibility</Link>
        </nav>
      </div>
    </footer>
  );
}
