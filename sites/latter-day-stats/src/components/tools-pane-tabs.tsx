"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const PANES = [
  { href: "/data-explorer/tools/activity-estimator", label: "Activity estimator" },
  { href: "/data-explorer/tools/map-explorer", label: "Map explorer" },
];

/** Switches between the tools; each is its own route so it's linkable. */
export function ToolsPaneTabs() {
  const pathname = usePathname();
  return (
    <nav className="mb-8 flex flex-wrap gap-2" aria-label="Tools">
      {PANES.map((p) => {
        const on = pathname.startsWith(p.href);
        return (
          <Link
            key={p.href}
            href={p.href}
            aria-current={on ? "page" : undefined}
            className={
              "rounded-[var(--radius)] border px-3 py-1.5 text-sm " +
              (on
                ? "border-[color:var(--accent)] bg-[color:var(--accent-soft)] text-[color:var(--accent)]"
                : "border-[color:var(--border)] text-[color:var(--muted)] hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]")
            }
          >
            {p.label}
          </Link>
        );
      })}
    </nav>
  );
}
