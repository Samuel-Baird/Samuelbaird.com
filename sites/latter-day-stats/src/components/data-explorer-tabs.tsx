"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  {
    href: "/data-explorer",
    label: "Datasets",
    match: (p: string) => !p.startsWith("/data-explorer/tools"),
  },
  {
    href: "/data-explorer/tools",
    label: "Tools",
    match: (p: string) => p.startsWith("/data-explorer/tools"),
  },
];

export function DataExplorerTabs() {
  const pathname = usePathname();
  return (
    <nav
      className="mb-8 flex gap-6 border-b border-[color:var(--border)] text-sm"
      aria-label="Data Explorer sections"
    >
      {TABS.map((tab) => (
        <Link
          key={tab.href}
          href={tab.href}
          className={
            "border-b-2 px-1 pb-3 " +
            (tab.match(pathname)
              ? "border-[color:var(--accent)] font-medium text-[color:var(--foreground)]"
              : "border-transparent text-[color:var(--muted)] hover:text-[color:var(--foreground)]")
          }
        >
          {tab.label}
        </Link>
      ))}
    </nav>
  );
}
