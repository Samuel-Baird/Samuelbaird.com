"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { ChannelWithStats } from "@/lib/types";
import {
  fmtCompact,
  fmtNumber,
  fmtYearsSince,
  fmtAvgViews,
} from "@/lib/format";

type SortKey =
  | "name"
  | "subscribers"
  | "total_views"
  | "video_count"
  | "avg_views"
  | "age";

type Props = { channels: ChannelWithStats[] };

const sortLabels: Record<SortKey, string> = {
  name: "Name (A→Z)",
  subscribers: "Subscribers",
  total_views: "Total views",
  video_count: "Videos",
  avg_views: "Avg views/video",
  age: "Channel age",
};

export function ChannelsTable({ channels }: Props) {
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<SortKey>("subscribers");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = q
      ? channels.filter((c) => c.name.toLowerCase().includes(q))
      : channels.slice();

    const get = {
      name: (c: ChannelWithStats) => c.name.toLowerCase(),
      subscribers: (c: ChannelWithStats) => -(c.latest?.subscribers ?? -1),
      total_views: (c: ChannelWithStats) => -(c.latest?.total_views ?? -1),
      video_count: (c: ChannelWithStats) => -(c.latest?.video_count ?? -1),
      avg_views: (c: ChannelWithStats) => {
        const v = c.latest?.total_views ?? 0;
        const n = c.latest?.video_count ?? 0;
        return -(n > 0 ? v / n : -1);
      },
      age: (c: ChannelWithStats) =>
        c.created_at_youtube
          ? new Date(c.created_at_youtube).getTime()
          : Infinity,
    }[sort];

    return list.sort((a, b) => {
      const av = get(a);
      const bv = get(b);
      if (typeof av === "string" && typeof bv === "string") {
        return av.localeCompare(bv);
      }
      return (av as number) - (bv as number);
    });
  }, [channels, query, sort]);

  return (
    <div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <input
          type="search"
          inputMode="search"
          placeholder="Search channels…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="h-11 w-full rounded-full border border-[color:var(--border)] bg-white px-5 text-sm placeholder:text-[color:var(--muted)] focus:border-[color:var(--accent)] focus:outline-none sm:max-w-xs"
        />
        <label className="flex items-center gap-2 text-sm text-[color:var(--muted)]">
          <span className="hidden sm:inline">Sort by</span>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value as SortKey)}
            className="h-11 rounded-full border border-[color:var(--border)] bg-white px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none"
          >
            {Object.entries(sortLabels).map(([k, label]) => (
              <option key={k} value={k}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <p className="mt-3 text-xs text-[color:var(--muted)]">
        Showing {filtered.length} of {channels.length} channels
      </p>

      {/* Desktop table */}
      <div className="mt-6 hidden overflow-hidden rounded-2xl border border-[color:var(--border)] bg-white md:block">
        <table className="w-full text-sm">
          <thead className="bg-[color:var(--muted-soft)]/60 text-left text-xs uppercase tracking-wider text-[color:var(--muted)]">
            <tr>
              <th className="px-5 py-3 font-medium">Channel</th>
              <th className="px-3 py-3 text-right font-medium">Subs</th>
              <th className="px-3 py-3 text-right font-medium">Total views</th>
              <th className="px-3 py-3 text-right font-medium">Videos</th>
              <th className="px-3 py-3 text-right font-medium">Avg/video</th>
              <th className="px-3 py-3 text-right font-medium">Age</th>
              <th className="px-5 py-3" />
            </tr>
          </thead>
          <tbody>
            {filtered.map((c) => (
              <tr
                key={c.id}
                className="border-t border-[color:var(--border)] hover:bg-[color:var(--muted-soft)]/40"
              >
                <td className="px-5 py-3.5">
                  <Link
                    href={`/channels/${c.slug}`}
                    className="font-medium text-[color:var(--foreground)] hover:text-[color:var(--accent)]"
                  >
                    {c.name}
                  </Link>
                </td>
                <td className="px-3 py-3.5 text-right tabular-nums">
                  {fmtCompact(c.latest?.subscribers)}
                </td>
                <td className="px-3 py-3.5 text-right tabular-nums text-[color:var(--muted)]">
                  {fmtCompact(c.latest?.total_views)}
                </td>
                <td className="px-3 py-3.5 text-right tabular-nums text-[color:var(--muted)]">
                  {fmtNumber(c.latest?.video_count)}
                </td>
                <td className="px-3 py-3.5 text-right tabular-nums text-[color:var(--muted)]">
                  {fmtAvgViews(c.latest?.total_views, c.latest?.video_count)}
                </td>
                <td className="px-3 py-3.5 text-right tabular-nums text-[color:var(--muted)]">
                  {fmtYearsSince(c.created_at_youtube)}
                </td>
                <td className="px-5 py-3.5 text-right">
                  <Link
                    href={`/channels/${c.slug}`}
                    className="text-xs text-[color:var(--accent)] hover:underline"
                  >
                    View →
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <ul className="mt-6 space-y-3 md:hidden">
        {filtered.map((c) => (
          <li
            key={c.id}
            className="rounded-2xl border border-[color:var(--border)] bg-white p-4"
          >
            <Link
              href={`/channels/${c.slug}`}
              className="block min-h-[44px]"
              aria-label={`View ${c.name}`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="font-medium leading-snug">{c.name}</div>
                <div className="serif text-lg tabular-nums">
                  {fmtCompact(c.latest?.subscribers)}
                </div>
              </div>
              <dl className="mt-3 grid grid-cols-3 gap-2 text-xs text-[color:var(--muted)]">
                <div>
                  <dt className="text-[10px] uppercase tracking-wider">Views</dt>
                  <dd className="tabular-nums text-[color:var(--foreground)]">
                    {fmtCompact(c.latest?.total_views)}
                  </dd>
                </div>
                <div>
                  <dt className="text-[10px] uppercase tracking-wider">Videos</dt>
                  <dd className="tabular-nums text-[color:var(--foreground)]">
                    {fmtNumber(c.latest?.video_count)}
                  </dd>
                </div>
                <div>
                  <dt className="text-[10px] uppercase tracking-wider">Age</dt>
                  <dd className="tabular-nums text-[color:var(--foreground)]">
                    {fmtYearsSince(c.created_at_youtube)}
                  </dd>
                </div>
              </dl>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
