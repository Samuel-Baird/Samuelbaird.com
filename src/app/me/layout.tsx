import Link from "next/link";
import { requireUser } from "@/lib/auth";

export default async function MeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  await requireUser();

  return (
    <div className="mx-auto max-w-6xl px-5 py-10 sm:px-8">
      <nav className="mb-8 flex gap-6 border-b border-[color:var(--border)] text-sm">
        <Link
          href="/me/bookmarks"
          className="border-b-2 border-[color:var(--accent)] px-1 pb-3 font-medium text-[color:var(--foreground)]"
        >
          Bookmarks
        </Link>
      </nav>
      {children}
    </div>
  );
}
