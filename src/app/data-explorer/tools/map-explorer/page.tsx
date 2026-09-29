import type { Metadata } from "next";
import { DataExplorerTabs } from "@/components/data-explorer-tabs";
import { DeseretTitle } from "@/components/deseret-title";
import { MapExplorer } from "@/components/map-explorer/map-explorer";
import { ToolsPaneTabs } from "@/components/tools-pane-tabs";
import { buildUsStateMap, buildWorldMap } from "@/lib/world-map";
import stats from "../../../../../docs/datasets/lds-units-by-country/country-stats.json";
import stateStats from "../../../../../docs/datasets/lds-states/state-stats.json";

export const metadata: Metadata = {
  title: "Map Explorer",
  description:
    "A world map of Latter-day Saint membership, congregations, wards, branches, stakes, missions, temples and family history centers by country.",
  alternates: { canonical: "/data-explorer/tools/map-explorer" },
};

export default function MapExplorerPage() {
  const map = buildWorldMap(Object.keys(stats.countries));
  const usMap = buildUsStateMap();
  return (
    <div className="mx-auto w-full max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <h1 className="serif text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="Map Explorer" />
      </h1>
      <div className="mt-8">
        <DataExplorerTabs />
      </div>
      <ToolsPaneTabs />
      <p className="mb-8 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        Pick a statistic, then hover or tap a country for its full record. Click a country to zoom in; the United States opens a state-by-state map. Figures come from the
        Church&apos;s own facts-and-statistics page for each country.
      </p>
      <MapExplorer
        map={map}
        usMap={usMap}
        countries={stats.countries}
        states={stateStats.countries}
        asOf={stats.as_of}
      />
    </div>
  );
}
