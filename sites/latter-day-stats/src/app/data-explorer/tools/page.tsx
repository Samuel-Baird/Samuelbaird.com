import type { Metadata } from "next";
import Link from "next/link";
import { DataExplorerTabs } from "@/components/data-explorer-tabs";
import { DeseretTitle } from "@/components/deseret-title";

export const metadata: Metadata = {
  title: "Data Explorer Tools",
  description: "Interactive calculators built on Data Explorer datasets.",
  alternates: { canonical: "/data-explorer/tools" },
};

export default function ToolsPage() {
  return (
    <div className="mx-auto w-full max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <h1 className="serif text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="Data Explorer" />
      </h1>
      <div className="mt-8">
        <DataExplorerTabs />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
      <Link
        href="/data-explorer/tools/activity-estimator"
        className="block rounded-[var(--radius)] border border-[color:var(--border)] p-6 hover:border-[color:var(--accent)]"
      >
        <p className="small-caps text-[11px] font-medium text-[color:var(--muted)]">Calculator</p>
        <h2 className="serif mt-2 text-xl font-semibold">Activity estimator</h2>
        <p className="mt-2 text-sm text-[color:var(--muted)]">
          Set how many people attend a typical ward or branch and see the activity rate that the
          country&apos;s unit counts imply.
        </p>
      </Link>
      <Link
        href="/data-explorer/tools/map-explorer"
        className="block rounded-[var(--radius)] border border-[color:var(--border)] p-6 hover:border-[color:var(--accent)]"
      >
        <p className="small-caps text-[11px] font-medium text-[color:var(--muted)]">Map</p>
        <h2 className="serif mt-2 text-xl font-semibold">Map explorer</h2>
        <p className="mt-2 text-sm text-[color:var(--muted)]">
          Members, wards, stakes, missions, temples and more, by country. Hover for the full
          record.
        </p>
      </Link>
      </div>
    </div>
  );
}
