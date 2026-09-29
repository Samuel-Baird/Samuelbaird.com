import type { Metadata } from "next";
import { ActivityEstimator } from "@/components/activity-estimator/activity-estimator";
import { DataExplorerTabs } from "@/components/data-explorer-tabs";
import { DeseretTitle } from "@/components/deseret-title";
import units from "../../../../../docs/datasets/lds-units-by-country/units-by-country.json";
import baselines from "../../../../../docs/datasets/lds-units-by-country/activity-baselines.json";
import handbook from "../../../../../docs/datasets/lds-units-by-country/handbook-thresholds.json";

export const metadata: Metadata = {
  title: "Activity Estimator",
  description:
    "Estimate how many Latter-day Saints attend, from each country's ward and branch counts and an attendance-per-unit assumption you choose.",
  alternates: { canonical: "/data-explorer/tools/activity-estimator" },
};

export default function ActivityEstimatorPage() {
  return (
    <div className="mx-auto w-full max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <h1 className="serif text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="Activity Estimator" />
      </h1>
      <div className="mt-8">
        <DataExplorerTabs />
      </div>
      <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-14">
        <div>
          <p className="mb-8 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
            Membership counts everyone on the rolls. Wards and branches are counted separately, so
            a guess at how many people attend each one gives an independent estimate of
            attendance. Pick low, mid and high guesses below. The result is attendance implied by
            unit counts, not a measured activity rate.
          </p>
          <ActivityEstimator
            asOf={units.as_of}
            worldwideMembers={units.worldwide_members}
            countries={units.countries}
            order={units.country_order}
            baselines={baselines.baselines}
          />
        </div>
        <aside className="space-y-6 text-sm leading-relaxed text-[color:var(--muted)] lg:border-l lg:border-[color:var(--border)] lg:pl-10">
          <div>
            <p className="small-caps text-[11px] font-medium">General Handbook minimums</p>
            <ul className="mt-2 space-y-1">
              <li>
                Ward: {handbook.ward.members} members, {handbook.ward.participating_adults}{" "}
                participating adults, {handbook.ward.mp_holders} active Melchizedek Priesthood
                holders.
              </li>
              <li>
                Branch in a stake: {handbook.branch_in_stake.members} members,{" "}
                {handbook.branch_in_stake.mp_holders} such holders.
              </li>
              <li>Branch in a mission: no member minimum.</li>
            </ul>
            <p className="mt-2">
              These are minimums to create a unit, not averages.{" "}
              <a className="text-[color:var(--accent)] hover:underline" href={handbook.source_url}>
                Handbook 36
              </a>
            </p>
          </div>
          <div>
            <p className="small-caps text-[11px] font-medium">Caveats</p>
            <ul className="mt-2 list-disc space-y-1 pl-4">
              <li>Not everyone in a unit is active.</li>
              <li>Some large units choose not to split.</li>
              <li>Fast-growing countries split early, so units run smaller.</li>
              <li>
                A survey baseline compares self-identification with rolls in one year. It is not
                the same measure.
              </li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
}
