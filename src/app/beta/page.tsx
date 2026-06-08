import type { Metadata } from "next";
import Link from "next/link";
import { ChannelPicker } from "@/components/channel-picker";
import {
  ComparisonChart,
  type ComparisonSeries,
} from "@/components/comparison-chart";
import { FreshnessBadge } from "@/components/freshness-badge";
import { RisersFallers } from "@/components/risers-fallers";
import { WeeklyDigestToggle } from "@/components/weekly-digest-toggle";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";
import {
  getChannelBySlug,
  getChannelStatsHistory,
  getChannelsWithLatest,
  getRisersAndFallers,
} from "@/lib/data";
import { fmtCompact, fmtNumber } from "@/lib/format";
import { getPremiumStatus } from "@/lib/permissions";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

export const metadata: Metadata = {
  title: "Beta",
  description:
    "Beta features for Latter-day Stats — risers and fallers, channel comparison, CSV exports, critical creators, and the weekly digest.",
};

export const dynamic = "force-dynamic";

const PALETTE = ["#1f4f7a", "#b45309", "#047857", "#7c3aed"];
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

const BENEFITS = [
  {
    title: "Risers & fallers",
    desc: "See which channels are growing fastest — and which are losing ground — over the past 30 days.",
  },
  {
    title: "Compare channels",
    desc: "Overlay subscriber growth for up to four channels at once. Indexed or absolute view.",
  },
  {
    title: "CSV channel export",
    desc: "Download the full channel directory with stats — subscribers, views, videos, language, country.",
  },
  {
    title: "Critical content creators",
    desc: "Access channels in the Critical category — hidden from public listings.",
  },
  {
    title: "Weekly email digest",
    desc: "New studies, new channels, and trend research delivered weekly.",
  },
  {
    title: "Versions",
    desc: "Compare multiple accounts of the same event, or trace how official handbooks, manuals, and guides change across editions over time.",
  },
];

export default async function PremiumPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const { slugs: slugsParam } = await searchParams;
  const status = await getPremiumStatus();

  if (status.premium) {
    return (
      <div className="mx-auto max-w-5xl px-5 py-14 sm:px-8 sm:py-20">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-amber-500">
          Beta
        </p>
        <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
          Thank you for supporting Latter-day Stats
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
          You have full access to all beta features. Enjoy.
        </p>

        <PremiumContent slugsParam={slugsParam} email={status.email} />

        <BenefitsList heading="Your beta benefits" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-amber-500">
        Beta
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        Beta features
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        A handful of bonus features for beta testers of Latter-day Stats. Want
        access? Email{" "}
        <a
          href={mailto("Beta access")}
          className="text-amber-600 underline underline-offset-2 hover:no-underline"
        >
          {CONTACT_EMAIL}
        </a>
        .
      </p>

      <BenefitsList />

      <LockedNotice signedIn={status.signedIn} />
    </div>
  );
}

function BenefitsList({ heading }: { heading?: string } = {}) {
  return (
    <section className="mt-12">
      {heading ? (
        <h2 className="serif text-2xl font-semibold tracking-tight sm:text-3xl">
          {heading}
        </h2>
      ) : null}
      <div className={`${heading ? "mt-6" : ""} grid gap-4 sm:grid-cols-2`}>
        {BENEFITS.map((b) => (
          <div
            key={b.title}
            className="rounded-2xl border border-amber-300/60 bg-amber-50/40 p-5 dark:border-amber-700/40 dark:bg-amber-950/20"
          >
            <h3 className="serif text-lg font-semibold tracking-tight text-amber-700 dark:text-amber-400">
              {b.title}
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-[color:var(--muted)] dark:text-[color:var(--foreground)]">
              {b.desc}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

function LockedNotice({ signedIn }: { signedIn: boolean }) {
  return (
    <section className="mt-12 rounded-2xl border border-amber-400/60 bg-amber-50/60 p-6 sm:p-8 dark:border-amber-700/40 dark:bg-amber-950/25">
      <p className="serif text-xl font-semibold tracking-tight text-amber-700 dark:text-amber-300">
        These features are for beta testers.
      </p>
      <p className="mt-3 text-sm leading-relaxed text-[color:var(--foreground)]">
        Please contact Sam if you would like to become a beta tester.
      </p>
      <div className="mt-5 flex flex-wrap gap-3">
        <a
          href={mailto("Beta access")}
          className="inline-flex h-11 items-center rounded-full bg-amber-500 px-5 text-sm font-medium text-white hover:bg-amber-400"
        >
          Email Sam ({CONTACT_EMAIL})
        </a>
        {!signedIn ? (
          <Link
            href="/login?next=/beta"
            className="inline-flex h-11 items-center rounded-full border border-amber-600/60 bg-amber-100 px-5 text-sm font-medium text-black hover:bg-amber-200 dark:bg-amber-900/40 dark:text-white dark:border-amber-600/60 dark:hover:bg-amber-900/60"
          >
            Sign in
          </Link>
        ) : null}
      </div>
    </section>
  );
}

async function PremiumContent({
  slugsParam,
  email,
}: {
  slugsParam: string | undefined;
  email: string | null;
}) {
  const slugs = parseSlugs(slugsParam);

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
    <>
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
            basePath="/beta"
          />
        </div>

        <div className="mt-6 space-y-6">
          {series.length >= 2 ? (
            <>
              <ComparisonChart series={series} metricLabel="Subscribers" />
              <ComparisonChart series={viewsSeries} metricLabel="Views" />
            </>
          ) : (
            <div className="rounded-2xl border border-dashed border-[color:var(--border)] bg-[color:var(--muted-soft)] p-10 text-center text-sm text-[color:var(--muted)]">
              {series.length === 1
                ? "Add at least one more channel to start the comparison."
                : "Add channels above to get started."}
            </div>
          )}
        </div>

        {valid.length > 0 && (
          <div className="mt-8 overflow-hidden rounded-2xl border border-[color:var(--border)]">
            <table className="w-full text-sm">
              <thead className="bg-[color:var(--muted-soft)] text-left text-xs uppercase tracking-wider text-[color:var(--muted)]">
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

      <section className="mt-20 rounded-2xl border border-[color:var(--border)] bg-[color:var(--muted-soft)] p-6 sm:p-8">
        <h2 className="serif text-2xl font-semibold tracking-tight">
          Weekly digest
        </h2>
        <p className="mt-2 text-sm text-[color:var(--muted)]">
          Opt in to receive the weekly email roundup. Sent manually by Sam.
        </p>
        <div className="mt-5">
          <WeeklyDigestToggle initial={notifyWeekly} />
        </div>
      </section>
    </>
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
