import type { Metadata } from "next";
import { DataExplorerTabs } from "@/components/data-explorer-tabs";
import { DeseretTitle } from "@/components/deseret-title";
import { ToolsPaneTabs } from "@/components/tools-pane-tabs";
import { BananaComparisonMap } from "@/components/banana-map/banana-comparison-map";
import { buildWorldMap } from "@/lib/world-map";
import comparisonData from "../../../../../docs/datasets/misc/bananas-vs-lds/comparison.json";

export const metadata: Metadata = {
  title: "LDS Members vs. Banana Truckloads",
  description:
    "A world map comparing Latter-day Saint membership against banana production converted to semi-truck loads, by country.",
  alternates: { canonical: "/data-explorer/tools/bananas-vs-lds" },
};

const TRUCKLOAD_TONNES = comparisonData.truckload_tonnes;

export default function BananasVsLdsPage() {
  const countries = comparisonData.countries as Record<
    string,
    { lds_members: number; banana_tonnes?: number; banana_truckloads?: number }
  >;

  const map = buildWorldMap(Object.keys(countries));

  const items = Object.entries(countries).map(([name, data]) => ({
    name,
    lds_members: data.lds_members,
    banana_tonnes: data.banana_tonnes ?? null,
  }));

  const ldsYear = comparisonData.lds_year.split(" ")[0]; // "2025 (per-country...)" -> "2025"
  const bananaYear = String(comparisonData.banana_year);

  return (
    <div className="mx-auto w-full max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <h1 className="serif text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="LDS Members vs. Banana Truckloads" />
      </h1>
      <div className="mt-8">
        <DataExplorerTabs />
      </div>
      <ToolsPaneTabs />
      <p className="mb-8 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        For every country: does it have more Latter-day Saint members, or more semi-truck loads of
        bananas? One truckload = {TRUCKLOAD_TONNES} metric tonnes. Dark blue means LDS wins; bright
        yellow means bananas win. LDS data from the Church&apos;s own facts-and-statistics pages
        ({ldsYear}); banana production from FAOSTAT via Our World in Data ({bananaYear}).
      </p>
      <section className="rounded-[var(--radius)] border border-[color:var(--border)] p-4 sm:p-7">
        <BananaComparisonMap
          map={map}
          items={items}
          title="LDS Members vs. Semi-Truck Loads of Bananas"
          subtitle={`Dark blue: country has more LDS members than banana truckloads (1 truck = ${TRUCKLOAD_TONNES} t). Bright yellow: banana truckloads outnumber LDS members. LDS: Church-reported ${ldsYear}; bananas: FAOSTAT ${bananaYear}.`}
          source={`Church facts and statistics ${ldsYear}; FAOSTAT ${bananaYear}`}
          filename="lds-members-vs-banana-truckloads"
          truckloadTonnes={TRUCKLOAD_TONNES}
        />
      </section>
    </div>
  );
}
