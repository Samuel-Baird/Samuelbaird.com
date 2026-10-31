import type { Metadata } from "next";
import Link from "next/link";
import { ChannelPicker } from "@/components/channel-picker";
import { SERIES_PAINT } from "@/components/charts/palette";
import {
  ComparisonChart,
  type ComparisonSeries,
} from "@/components/comparison-chart";
import { DeseretTitle } from "@/components/deseret-title";
import { FreshnessBadge } from "@/components/freshness-badge";
import { RisersFallers } from "@/components/risers-fallers";
import { WeeklyDigestToggle } from "@/components/weekly-digest-toggle";
import { getCurrentUser } from "@/lib/auth";
import {
  getChannelBySlug,
  getChannelStatsHistory,
  getChannelsWithLatest,
  getRisersAndFallers,
} from "@/lib/data";
import { fmtCompact, fmtNumber } from "@/lib/format";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

export const metadata: Metadata = {
  title: "Compare channels",
  description:
    "Risers and fallers over the past 30 days, and side-by-side subscriber and view growth for up to four Latter-day Saint YouTube channels. Free for everyone.",
  alternates: { canonical: "/compare" },
};

export const dynamic = "force-dynamic";

// Series colours are the canonical chart-kit palette (src/components/charts/
// palette.ts), so this chart reads as part of the site. var() resolves in the
// SVG paint attributes that comparison-chart sets, as well as in the legend
// swatch backgrounds.
const PALETTE = SERIES_PAINT;
const MAX_COMPARE = 4;

type SearchParams = { slugs?: string };

function parseSlugs(value: string | undefined): string[] {
  if (!value) return [];
  return value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
    .slice(0, MAX_COMPARE);
}

export default async function ComparePage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const { slugs: slugsParam } = await searchParams;
  const slugs = parseSlugs(slugsParam);
  const auth = await getCurrentUser();
  const email = auth?.profile?.email ?? auth?.user.email ?? null;

  const [movers, allChannels, notifyWeekly] = await Promise.all([
    getRisersAndFallers(30, 5),
    getChannelsWithLatest({ includeInactive: true }),
    getNotifyWeekly(email),
  ]);

  const options = allChannels
    .map((c) => ({ slug: c.slug, name: c.name }))
    .sort((a, b) => a.name.localeCompare(b.name));

  const resolved = await Promise.all(
    slugs.map(async (slug, i) => {
      const channel = await getChannelBySlug(slug);
      if (!channel) return null;
      const history = await getChannelStatsHistory(channel.id);
      return { channel, history, color: PALETTE[i % PALETTE.length] };
    }),
  );
  const valid = resolved.filter((r): r is NonNullable<typeof r> => r !== null);

  const series: ComparisonSeries[] = valid.map((r) => ({
    label: r.channel.name,
    color: r.color,
    data: r.history.map((p) => ({
      captured_at: p.captured_at,
      subscribers: p.subscribers,
    })),
  }));
  const viewsSeries: ComparisonSeries[] = valid.map((r) => ({
    label: r.channel.name,
    color: r.color,
    data: r.history.map((p) => ({
      captured_at: p.captured_at,
      value: p.total_views,
    })),
  }));

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="small-caps text-xs font-medium text-[color:var(--honey)]">
        Compare
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        <DeseretTitle text="Compare channels" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        Which channels are growing fastest, and how they stack up against each
        other. Free for everyone.
      </p>

      <section className="mt-12">
        <RisersFallers risers={movers.risers} fallers={movers.fallers} />
      </section>

      <section className="mt-20">
        <h2 className="serif text-2xl font-semibold tracking-tight sm:text-3xl">
          Compare channels
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
          Pick up to {MAX_COMPARE} channels and overlay subscriber growth.
          Toggle between absolute counts and an indexed view.
        </p>

        <div className="mt-6">
          <ChannelPicker
            allChannels={options}
            selectedSlugs={valid.map((r) => r.channel.slug)}
            max={MAX_COMPARE}
            basePath="/compare"
          />
        </div>

        <div className="mt-6 space-y-6">
          {series.length >= 2 ? (
            <>
              <ComparisonChart series={series} metricLabel="Subscribers" />
              <ComparisonChart series={viewsSeries} metricLabel="Views" />
            </>
          ) : (
            <div className="rounded-[var(--radius)] border border-dashed border-[color:var(--border)] bg-[color:var(--muted-soft)] p-10 text-center text-sm text-[color:var(--muted)]">
              {series.length === 1
                ? "Add at least one more channel to start the comparison."
                : "Add channels above to get started."}
            </div>
          )}
        </div>

        {valid.length > 0 && (
          <div className="mt-8 overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]">
            <table className="w-full text-sm">
              <thead className="small-caps bg-[color:var(--muted-soft)] text-left text-xs text-[color:var(--muted)]">
                <tr>
                  <th className="px-5 py-3 font-medium">Channel</th>
                  <th className="px-3 py-3 text-right font-medium">
                    Subscribers
                  </th>
                  <th className="px-3 py-3 text-right font-medium">
                    Total views
                  </th>
                  <th className="px-3 py-3 text-right font-medium">Videos</th>
                  <th className="px-3 py-3 text-right font-medium">Updated</th>
                </tr>
              </thead>
              <tbody>
                {valid.map((r) => (
                  <tr
                    key={r.channel.slug}
                    className="border-t border-[color:var(--border)]"
                  >
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        <span
                          className="inline-block h-2.5 w-2.5 shrink-0 rounded-full"
                          style={{ backgroundColor: r.color }}
                          aria-hidden="true"
                        />
                        <Link
                          href={`/channels/${r.channel.slug}`}
                          className="font-medium hover:text-[color:var(--accent)]"
                        >
                          {r.channel.name}
                        </Link>
                      </div>
                    </td>
                    <td className="px-3 py-3 text-right tabular-nums">
                      {fmtCompact(r.channel.latest?.subscribers)}
                    </td>
                    <td className="px-3 py-3 text-right tabular-nums text-[color:var(--muted)]">
                      {fmtCompact(r.channel.latest?.total_views)}
                    </td>
                    <td className="px-3 py-3 text-right tabular-nums text-[color:var(--muted)]">
                      {fmtNumber(r.channel.latest?.video_count)}
                    </td>
                    <td className="px-3 py-3 text-right">
                      <FreshnessBadge iso={r.channel.latest?.captured_at} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="mt-20 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)] p-6 sm:p-8">
        <h2 className="serif text-2xl font-semibold tracking-tight">
          Weekly digest
        </h2>
        <p className="mt-2 text-sm text-[color:var(--muted)]">
          Opt in to receive the weekly email roundup: new studies, new
          channels, and trend research. Sent manually by Sam.
        </p>
        <div className="mt-5">
          {email ? (
            <WeeklyDigestToggle initial={notifyWeekly} />
          ) : (
            <p className="text-sm text-[color:var(--muted)]">
              <Link
                href="/login?next=/compare"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                Sign in
              </Link>{" "}
              to subscribe.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}

async function getNotifyWeekly(email: string | null): Promise<boolean> {
  if (!email) return false;
  const { data, error } = await createSupabaseServiceClient()
    .from("premium_users")
    .select("notify_weekly")
    .eq("email", email.trim().toLowerCase())
    .maybeSingle();
  if (error) throw error;
  return Boolean(data?.notify_weekly);
}
