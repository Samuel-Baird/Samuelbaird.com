import type { Metadata } from "next";
import { DataExplorerTabs } from "@/components/data-explorer-tabs";
import { DeseretTitle } from "@/components/deseret-title";
import { ToolsPaneTabs } from "@/components/tools-pane-tabs";
import { MiscComparisonMap } from "@/components/misc-map/misc-comparison-map";
import { buildWorldMap } from "@/lib/world-map";
import comparisonData from "../../../../../docs/datasets/misc/misc-comparisons/comparison.json";

export const metadata: Metadata = {
  title: "LDS Stats vs. The World",
  description:
    "A world map comparing Latter-day Saint statistics against bananas, hospital beds, military personnel, and volcanoes.",
  alternates: { canonical: "/data-explorer/tools/misc-comparisons" },
};

export default function MiscComparisonsPage() {
  const countries = comparisonData.countries as Record<
    string,
    {
      lds_members: number;
      lds_congregations: number;
      lds_wards: number;
      lds_branches: number;
      lds_stakes: number;
      lds_districts: number;
      lds_missions: number;
      lds_temples: number;
      lds_family_history_centers: number;
      banana_tonnes?: number;
      hospital_beds_per_1000?: number;
      armed_forces?: number;
      volcanoes?: number;
    }
  >;

  const map = buildWorldMap(Object.keys(countries));

  const items = Object.entries(countries).map(([name, data]) => ({
    name,
    lds_members: data.lds_members,
    lds_congregations: data.lds_congregations,
    lds_wards: data.lds_wards,
    lds_branches: data.lds_branches,
    lds_stakes: data.lds_stakes,
    lds_districts: data.lds_districts,
    lds_missions: data.lds_missions,
    lds_temples: data.lds_temples,
    lds_family_history_centers: data.lds_family_history_centers,
    banana_tonnes: data.banana_tonnes ?? null,
    hospital_beds_per_1000: data.hospital_beds_per_1000 ?? null,
    armed_forces: data.armed_forces ?? null,
    volcanoes: data.volcanoes ?? null,
  }));

  const ldsYear = comparisonData.lds_year.split(" ")[0]; // "2025 (per-country...)" -> "2025"

  const TRUCKLOAD_TONNES = comparisonData.truckload_tonnes;

  return (
    <div className="mx-auto w-full max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <h1 className="serif text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="LDS Stats vs. The World" />
      </h1>
      <div className="mt-8">
        <DataExplorerTabs />
      </div>
      <ToolsPaneTabs />
      <p className="mb-8 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        For every country: does it have more Latter-day Saint members, or more hospital beds per 1,000 people? Or volcanoes? Dark blue means the LDS stat is higher; bright yellow means the comparison stat wins.
      </p>
      <section className="rounded-[var(--radius)] border border-[color:var(--border)] p-4 sm:p-7">
        <MiscComparisonMap
          map={map}
          items={items}
          title="LDS Stats vs. The World"
          source="Church facts and statistics; FAOSTAT; World Bank; Smithsonian GVP"
          filename="lds-stats-vs-the-world"
          truckloadTonnes={TRUCKLOAD_TONNES}
        />
      </section>
    </div>
  );
}
