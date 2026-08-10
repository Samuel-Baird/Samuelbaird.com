"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/me/bookmarks", label: "Bookmarks" },
  { href: "/me/settings", label: "Settings" },
];

export function MeTabs() {
  const pathname = usePathname();

  return (
    <nav className="mb-8 flex gap-6 border-b border-[color:var(--border)] text-sm">
      {TABS.map((tab) => {
        const active = pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={
              "border-b-2 px-1 pb-3 " +
              (active
                ? "border-[color:var(--accent)] font-medium text-[color:var(--foreground)]"
                : "border-transparent text-[color:var(--muted)] hover:text-[color:var(--foreground)]")
            }
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
