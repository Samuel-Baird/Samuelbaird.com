import type { Metadata } from "next";
import Link from "next/link";
import { ChannelPicker } from "@/components/channel-picker";
import {
  ComparisonChart,
  type ComparisonSeries,
} from "@/components/comparison-chart";
import {
  getChannelBySlug,
  getChannelStatsHistory,
  getChannelsWithLatest,
} from "@/lib/data";
import { fmtCompact, fmtNumber } from "@/lib/format";

export const metadata: Metadata = {
  title: "Compare channels",
  description:
    "Overlay subscriber growth for up to four Latter-day Saint YouTube channels.",
};

export const revalidate = 600;

const PALETTE = ["#1f4f7a", "#b45309", "#047857", "#7c3aed"];
const MAX = 4;

type SearchParams = { slugs?: string };

function parseSlugs(value: string | undefined): string[] {
  if (!value) return [];
  return value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
    .slice(0, MAX);
}

export default async function ComparePage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const { slugs: slugsParam } = await searchParams;
  const slugs = parseSlugs(slugsParam);

  const allChannels = await getChannelsWithLatest();
  const options = allChannels
    .map((c) => ({ slug: c.slug, name: c.name }))
    .sort((a, b) => a.name.localeCompare(b.name));

  const resolved = await Promise.all(
    slugs.map(async (slug, i) => {
      const channel = await getChannelBySlug(slug);
      if (!channel) return null;
      const history = await getChannelStatsHistory(channel.id);
      return {
        channel,
        history,
        color: PALETTE[i % PALETTE.length],
      };
    }),
  );
  const valid = resolved.filter(
    (r): r is NonNullable<typeof r> => r !== null,
  );

  const series: ComparisonSeries[] = valid.map((r) => ({
    label: r.channel.name,
    color: r.color,
    data: r.history.map((p) => ({
      captured_at: p.captured_at,
      subscribers: p.subscribers,
    })),
  }));

  return (
    <div className="mx-auto max-w-5xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Compare
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        Channel comparison
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        Pick up to {MAX} channels and overlay their subscriber growth. Toggle
        between absolute counts and an indexed view that rebases each channel
        to 100 at its earliest snapshot, so channels of different sizes can be
        compared directly.
      </p>

      <div className="mt-8">
        <ChannelPicker
          allChannels={options}
          selectedSlugs={valid.map((r) => r.channel.slug)}
          max={MAX}
        />
      </div>

      <div className="mt-6">
        {series.length >= 2 ? (
          <ComparisonChart series={series} />
        ) : (
          <div className="rounded-2xl border border-dashed border-[color:var(--border)] bg-white p-10 text-center text-sm text-[color:var(--muted)]">
            {series.length === 1
              ? "Add at least one more channel to start the comparison."
              : "Add channels above to get started."}
          </div>
        )}
      </div>

      {valid.length > 0 && (
        <div className="mt-8 overflow-hidden rounded-2xl border border-[color:var(--border)] bg-white">
          <table className="w-full text-sm">
            <thead className="bg-[color:var(--muted-soft)] text-left text-xs uppercase tracking-wider text-[color:var(--muted)]">
              <tr>
                <th className="px-5 py-3 font-medium">Channel</th>
                <th className="px-3 py-3 text-right font-medium">Subscribers</th>
                <th className="px-3 py-3 text-right font-medium">Total views</th>
                <th className="px-3 py-3 text-right font-medium">Videos</th>
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
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="mt-10 text-xs text-[color:var(--muted)]">
        Share this comparison by copying the URL — your selected channels are
        encoded in the page address.
      </p>
    </div>
  );
}
