"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { BookmarkButton } from "@/components/bookmark-button";
import { colorsForType } from "@/lib/channel-types";
import type { ChannelWithStats } from "@/lib/types";
import {
  fmtCompact,
  fmtNumber,
  fmtYearsSince,
  fmtAvgViews,
} from "@/lib/format";

type SortKey =
  | "name"
  | "type"
  | "subscribers"
  | "total_views"
  | "video_count"
  | "avg_views"
  | "age";

type SortDirection = "asc" | "desc";

type Props = {
  channels: ChannelWithStats[];
  bookmarkedSet?: Set<string>;
  signedIn?: boolean;
  initialSort?: SortKey;
};

const sortLabels: Record<SortKey, string> = {
  name: "Name",
  type: "Type",
  subscribers: "Subscribers",
  total_views: "Total views",
  video_count: "Videos",
  avg_views: "Avg views/video",
  age: "Channel age",
};

const defaultDirection: Record<SortKey, SortDirection> = {
  name: "asc",
  type: "asc",
  subscribers: "desc",
  total_views: "desc",
  video_count: "desc",
  avg_views: "desc",
  age: "desc",
};

function TypePill({ type }: { type: string | null }) {
  if (!type) return <span className="text-[color:var(--muted)]">-</span>;
  const { bg, text } = colorsForType(type);
  return (
    <span
      className={`inline-flex rounded-full ${bg} ${text} px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider`}
    >
      {type}
    </span>
  );
}

function InactivePill() {
  return (
    <span
      title="This channel has been flagged as inactive for not posting for a long period of time."
      className="inline-flex cursor-help rounded-full bg-[color:var(--muted-soft)] px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider text-[color:var(--muted)] ring-1 ring-[color:var(--border)]"
    >
      Inactive
    </span>
  );
}

function SortHeader({
  label,
  sortKey,
  activeSort,
  direction,
  onSort,
  align = "left",
  className = "px-3",
}: {
  label: string;
  sortKey: SortKey;
  activeSort: SortKey;
  direction: SortDirection;
  onSort: (sortKey: SortKey) => void;
  align?: "left" | "right";
  className?: string;
}) {
  const active = activeSort === sortKey;
  return (
    <th
      className={`${className} py-3 font-medium ${
        align === "right" ? "text-right" : ""
      }`}
    >
      <button
        type="button"
        onClick={() => onSort(sortKey)}
        className={`inline-flex items-center gap-1 rounded-full px-2 py-1 transition-colors hover:bg-white/70 hover:text-[color:var(--foreground)] ${
          align === "right" ? "justify-end" : ""
        }`}
      >
        <span>{label}</span>
        <span aria-hidden="true" className="w-2 text-[10px]">
          {active ? (direction === "desc" ? "\u2193" : "\u2191") : ""}
        </span>
      </button>
    </th>
  );
}

export function ChannelsTable({
  channels,
  bookmarkedSet = new Set<string>(),
  signedIn = false,
  initialSort = "subscribers",
}: Props) {
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<SortKey>(initialSort);
  const [direction, setDirection] = useState<SortDirection>(
    defaultDirection[initialSort],
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = q
      ? channels.filter((c) =>
          [c.name, c.channel_type].some((v) => v?.toLowerCase().includes(q)),
        )
      : channels.slice();

    const get = {
      name: (c: ChannelWithStats) => c.name.toLowerCase(),
      type: (c: ChannelWithStats) => c.channel_type?.toLowerCase() ?? "",
      subscribers: (c: ChannelWithStats) => c.latest?.subscribers ?? -1,
      total_views: (c: ChannelWithStats) => c.latest?.total_views ?? -1,
      video_count: (c: ChannelWithStats) => c.latest?.video_count ?? -1,
      avg_views: (c: ChannelWithStats) => {
        const v = c.latest?.total_views ?? 0;
        const n = c.latest?.video_count ?? 0;
        return n > 0 ? v / n : -1;
      },
      age: (c: ChannelWithStats) =>
        c.created_at_youtube
          ? new Date(c.created_at_youtube).getTime()
          : -1,
    }[sort];

    return list.sort((a, b) => {
      const av = get(a);
      const bv = get(b);
      const result =
        typeof av === "string" && typeof bv === "string"
          ? av.localeCompare(bv)
          : (av as number) - (bv as number);
      return direction === "asc" ? result : -result;
    });
  }, [channels, direction, query, sort]);

  function setSortKey(nextSort: SortKey) {
    if (nextSort === sort) {
      setDirection((current) => (current === "desc" ? "asc" : "desc"));
      return;
    }
    setSort(nextSort);
    setDirection(defaultDirection[nextSort]);
  }

  return (
    <div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <input
          type="search"
          inputMode="search"
          placeholder="Search channels..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="h-11 w-full rounded-full border border-[color:var(--border)] bg-white px-5 text-sm placeholder:text-[color:var(--muted)] focus:border-[color:var(--accent)] focus:outline-none sm:max-w-xs"
        />
        <label className="flex items-center gap-2 text-sm text-[color:var(--muted)]">
          <span className="hidden sm:inline">Sort by</span>
          <select
            value={sort}
            onChange={(e) => {
              const nextSort = e.target.value as SortKey;
              setSort(nextSort);
              setDirection(defaultDirection[nextSort]);
            }}
            className="h-11 rounded-full border border-[color:var(--border)] bg-white px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none"
          >
            {Object.entries(sortLabels).map(([k, label]) => {
              const key = k as SortKey;
              return (
                <option key={key} value={key}>
                  {label} ({defaultDirection[key] === "desc" ? "high-low" : "A-Z"})
                </option>
              );
            })}
          </select>
        </label>
      </div>

      <p className="mt-3 text-xs text-[color:var(--muted)]">
        Showing {filtered.length} of {channels.length} channels
      </p>

      {/* Desktop table */}
      <div className="mt-6 hidden rounded-2xl border border-[color:var(--border)] bg-white md:block">
        <table className="w-full border-separate border-spacing-0 text-sm">
          <thead className="sticky top-16 z-10 bg-[color:var(--muted-soft)] text-left text-xs uppercase tracking-wider text-[color:var(--muted)] shadow-[0_1px_0_0_var(--border)]">
            <tr>
              <th className="w-12 px-3 py-3 text-right text-[color:var(--muted)]">#</th>
              <SortHeader
                label="Channel"
                sortKey="name"
                activeSort={sort}
                direction={direction}
                onSort={setSortKey}
                className="px-5"
              />
              <SortHeader
                label="Type"
                sortKey="type"
                activeSort={sort}
                direction={direction}
                onSort={setSortKey}
              />
              <SortHeader
                label="Subs"
                sortKey="subscribers"
                activeSort={sort}
                direction={direction}
                onSort={setSortKey}
                align="right"
              />
              <SortHeader
                label="Total views"
                sortKey="total_views"
                activeSort={sort}
                direction={direction}
                onSort={setSortKey}
                align="right"
              />
              <SortHeader
                label="Videos"
                sortKey="video_count"
                activeSort={sort}
                direction={direction}
                onSort={setSortKey}
                align="right"
              />
              <SortHeader
                label="Avg/video"
                sortKey="avg_views"
                activeSort={sort}
                direction={direction}
                onSort={setSortKey}
                align="right"
              />
              <SortHeader
                label="Age"
                sortKey="age"
                activeSort={sort}
                direction={direction}
                onSort={setSortKey}
                align="right"
              />
              <th className="px-5 py-3" />
            </tr>
          </thead>
          <tbody>
            {filtered.map((c, index) => (
              <tr
                key={c.id}
                className="border-t border-[color:var(--border)] hover:bg-[color:var(--muted-soft)]/40"
              >
                <td className="px-3 py-3.5 text-right tabular-nums text-[color:var(--muted)]">
                  {index + 1}
                </td>
                <td className="px-5 py-3.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <Link
                      href={`/channels/${c.slug}`}
                      className="font-medium text-[color:var(--foreground)] hover:text-[color:var(--accent)]"
                    >
                      {c.name}
                    </Link>
                    {!c.is_active && <InactivePill />}
                  </div>
                </td>
                <td className="px-3 py-3.5">
                  <TypePill type={c.channel_type} />
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
                  <div className="inline-flex items-center gap-3">
                    <Link
                      href={`/channels/${c.slug}`}
                      className="text-xs text-[color:var(--accent)] hover:underline"
                    >
                      View →
                    </Link>
                    <BookmarkButton
                      targetType="channel"
                      targetId={c.id}
                      initial={bookmarkedSet.has(c.id)}
                      signedIn={signedIn}
                      size="sm"
                    />
                  </div>
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
            className="relative rounded-2xl border border-[color:var(--border)] bg-white p-4 pr-14"
          >
            <div className="absolute right-3 top-3 z-10">
              <BookmarkButton
                targetType="channel"
                targetId={c.id}
                initial={bookmarkedSet.has(c.id)}
                signedIn={signedIn}
                size="sm"
              />
            </div>
            <Link
              href={`/channels/${c.slug}`}
              className="block min-h-[44px]"
              aria-label={`View ${c.name}`}
            >
              {(c.channel_type || !c.is_active) && (
                <div className="mb-2 flex flex-wrap gap-2">
                  {c.channel_type && <TypePill type={c.channel_type} />}
                  {!c.is_active && <InactivePill />}
                </div>
              )}
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
