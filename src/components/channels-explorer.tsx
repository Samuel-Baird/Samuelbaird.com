"use client";

import { SlidersHorizontal, X } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { ChannelsFilterSidebar, type FilterGroup } from "@/components/channels-filter-sidebar";
import { ChannelsTable } from "@/components/channels-table";
import { ExportCsvButton } from "@/components/export-csv-button";
import { fmtAvgViews } from "@/lib/format";
import type { ChannelWithStats } from "@/lib/types";

type Props = {
  channels: ChannelWithStats[];
  bookmarkedSet: Set<string>;
  upvotedSet: Set<string>;
  upvoteCounts: Record<string, number>;
  signedIn: boolean;
};

type FilterKey = FilterGroup["key"];

const UNKNOWN = "Unknown";

const groupLabels: Record<FilterKey, string> = {
  type: "Type",
  country: "Country",
  language: "Language",
};

function normalizeFilterValue(value: string | null) {
  const normalized = value?.trim();
  return normalized ? normalized : UNKNOWN;
}

function getChannelFilterValue(channel: ChannelWithStats, key: FilterKey) {
  if (key === "type") return normalizeFilterValue(channel.channel_type);
  if (key === "country")
    return normalizeFilterValue(channel.country_manual ?? channel.country);
  return normalizeFilterValue(channel.language_manual ?? channel.language);
}

function matchesSelections(
  channel: ChannelWithStats,
  selections: Record<FilterKey, Set<string>>,
  keys: FilterKey[] = ["type", "country", "language"],
) {
  return keys.every((key) => {
    const selected = selections[key];
    return selected.size === 0 || selected.has(getChannelFilterValue(channel, key));
  });
}

function nextSelectionSet(current: Set<string>, value: string) {
  const next = new Set(current);
  if (next.has(value)) {
    next.delete(value);
  } else {
    next.add(value);
  }
  return next;
}

export function ChannelsExplorer({
  channels,
  bookmarkedSet,
  upvotedSet,
  upvoteCounts,
  signedIn,
}: Props) {
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(new Set());
  const [selectedCountries, setSelectedCountries] = useState<Set<string>>(new Set());
  const [selectedLanguages, setSelectedLanguages] = useState<Set<string>>(new Set());
  const [drawerOpen, setDrawerOpen] = useState(false);
  const drawerRef = useRef<HTMLDivElement>(null);

  const selections = useMemo<Record<FilterKey, Set<string>>>(
    () => ({
      type: selectedTypes,
      country: selectedCountries,
      language: selectedLanguages,
    }),
    [selectedCountries, selectedLanguages, selectedTypes],
  );

  const availableOptions = useMemo<Record<FilterKey, string[]>>(() => {
    const values: Record<FilterKey, Set<string>> = {
      type: new Set(),
      country: new Set(),
      language: new Set(),
    };

    for (const channel of channels) {
      values.type.add(getChannelFilterValue(channel, "type"));
      values.country.add(getChannelFilterValue(channel, "country"));
      values.language.add(getChannelFilterValue(channel, "language"));
    }

    return {
      type: [...values.type].sort((a, b) => a.localeCompare(b)),
      country: [...values.country].sort((a, b) => a.localeCompare(b)),
      language: [...values.language].sort((a, b) => a.localeCompare(b)),
    };
  }, [channels]);

  const filteredChannels = useMemo(
    () => channels.filter((channel) => matchesSelections(channel, selections)),
    [channels, selections],
  );

  const groups = useMemo<FilterGroup[]>(() => {
    const keys: FilterKey[] = ["type", "country", "language"];

    return keys.map((key) => {
      const otherKeys = keys.filter((candidate) => candidate !== key);
      const countBase = channels.filter((channel) =>
        matchesSelections(channel, selections, otherKeys),
      );

      return {
        key,
        label: groupLabels[key],
        options: availableOptions[key].map((value) => ({
          value,
          label: value,
          count: countBase.filter(
            (channel) => getChannelFilterValue(channel, key) === value,
          ).length,
        })),
      };
    });
  }, [availableOptions, channels, selections]);

  const activeFilters = useMemo(
    () =>
      (Object.keys(groupLabels) as FilterKey[]).flatMap((key) =>
        [...selections[key]]
          .sort((a, b) => a.localeCompare(b))
          .map((value) => ({ key, label: groupLabels[key], value })),
      ),
    [selections],
  );

  const activeFilterCount = activeFilters.length;

  function setGroupSelection(key: FilterKey, next: Set<string>) {
    if (key === "type") setSelectedTypes(next);
    if (key === "country") setSelectedCountries(next);
    if (key === "language") setSelectedLanguages(next);
  }

  function handleToggle(key: FilterKey, value: string) {
    setGroupSelection(key, nextSelectionSet(selections[key], value));
  }

  function handleSelectAll(key: FilterKey) {
    setGroupSelection(key, new Set(availableOptions[key]));
  }

  function handleSelectNone(key: FilterKey) {
    setGroupSelection(key, new Set());
  }

  function clearAll() {
    setSelectedTypes(new Set());
    setSelectedCountries(new Set());
    setSelectedLanguages(new Set());
  }

  useEffect(() => {
    if (!drawerOpen) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const focusableSelector =
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), details, [tabindex]:not([tabindex="-1"])';

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setDrawerOpen(false);
        return;
      }

      if (event.key !== "Tab" || !drawerRef.current) return;

      const focusable = Array.from(
        drawerRef.current.querySelectorAll<HTMLElement>(focusableSelector),
      ).filter((element) => element.offsetParent !== null);

      if (focusable.length === 0) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    window.setTimeout(() => {
      drawerRef.current
        ?.querySelector<HTMLElement>(focusableSelector)
        ?.focus();
    }, 0);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [drawerOpen]);

  return (
    <div>
      <div className="mb-5 flex items-center justify-between gap-3 md:hidden">
        <button
          type="button"
          aria-label="Open filters"
          onClick={() => setDrawerOpen(true)}
          className="inline-flex min-h-10 items-center gap-2 rounded-full border border-[color:var(--border)] bg-white px-4 text-sm font-medium shadow-sm"
        >
          <SlidersHorizontal aria-hidden="true" size={16} />
          Filters
          {activeFilterCount > 0 && (
            <span className="rounded-full bg-[color:var(--accent-soft)] px-2 py-0.5 text-xs text-[color:var(--accent)]">
              {activeFilterCount}
            </span>
          )}
        </button>
        <span className="text-xs text-[color:var(--muted)]">
          {filteredChannels.length} of {channels.length}
        </span>
      </div>

      <div className="grid gap-8 md:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="hidden md:block">
          <div className="sticky top-20 max-h-[calc(100vh-6rem)] overflow-y-auto pr-1">
            <ChannelsFilterSidebar
              groups={groups}
              selections={selections}
              onToggle={handleToggle}
              onSelectAll={handleSelectAll}
              onSelectNone={handleSelectNone}
              onClearAll={clearAll}
            />
          </div>
        </aside>

        <div className="min-w-0">
          {activeFilterCount > 0 && (
            <div className="mb-5 rounded-2xl border border-[color:var(--border)] bg-white p-3">
              <div className="flex flex-wrap items-center gap-2">
                {activeFilters.map((filter) => (
                  <button
                    key={`${filter.key}:${filter.value}`}
                    type="button"
                    onClick={() => handleToggle(filter.key, filter.value)}
                    aria-label={`Remove filter ${filter.label}: ${filter.value}`}
                    className="inline-flex min-h-10 items-center gap-1.5 rounded-full bg-[color:var(--muted-soft)] px-3 text-xs text-[color:var(--foreground)] hover:bg-[color:var(--accent-soft)]"
                  >
                    <span>
                      {filter.label}: {filter.value}
                    </span>
                    <X aria-hidden="true" size={14} />
                  </button>
                ))}
                <button
                  type="button"
                  onClick={clearAll}
                  className="min-h-10 px-2 text-sm text-[color:var(--accent)] hover:underline"
                >
                  Clear filters
                </button>
              </div>
              <p className="mt-2 text-xs text-[color:var(--muted)]">
                Showing {filteredChannels.length} of {channels.length} channels
                before search
              </p>
            </div>
          )}

          <div className="mb-4 flex justify-end">
            <ExportCsvButton
              rows={filteredChannels}
              filename="latter-day-stats-channels.csv"
              columns={[
                { header: "Name", value: (c) => c.name },
                { header: "Type", value: (c) => c.channel_type ?? "" },
                {
                  header: "Country",
                  value: (c) => c.country_manual ?? c.country ?? "",
                },
                {
                  header: "Language",
                  value: (c) => c.language_manual ?? c.language ?? "",
                },
                {
                  header: "Subscribers",
                  value: (c) => c.latest?.subscribers ?? "",
                },
                {
                  header: "Total views",
                  value: (c) => c.latest?.total_views ?? "",
                },
                { header: "Videos", value: (c) => c.latest?.video_count ?? "" },
                {
                  header: "Avg views/video",
                  value: (c) =>
                    fmtAvgViews(c.latest?.total_views, c.latest?.video_count),
                },
                {
                  header: "Channel created",
                  value: (c) => c.created_at_youtube ?? "",
                },
                {
                  header: "Upvotes",
                  value: (c) => upvoteCounts[c.id] ?? 0,
                },
                {
                  header: "YouTube URL",
                  value: (c) =>
                    c.handle
                      ? `https://www.youtube.com/${c.handle.startsWith("@") ? c.handle : `@${c.handle}`}`
                      : `https://www.youtube.com/channel/${c.youtube_channel_id}`,
                },
              ]}
            />
          </div>

          <ChannelsTable
            channels={filteredChannels}
            bookmarkedSet={bookmarkedSet}
            upvotedSet={upvotedSet}
            upvoteCounts={upvoteCounts}
            signedIn={signedIn}
          />
        </div>
      </div>

      {drawerOpen && (
        <div className="fixed inset-0 z-50 md:hidden" role="dialog" aria-modal="true">
          <button
            type="button"
            aria-label="Close filters"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/35"
          />
          <div
            ref={drawerRef}
            className="absolute right-0 top-0 flex h-full w-[88vw] max-w-sm translate-x-0 flex-col bg-[color:var(--background)] shadow-xl transition-transform duration-200"
          >
            <div className="flex-1 overflow-y-auto">
              <ChannelsFilterSidebar
                groups={groups}
                selections={selections}
                onToggle={handleToggle}
                onSelectAll={handleSelectAll}
                onSelectNone={handleSelectNone}
                onClearAll={clearAll}
                variant="drawer"
              />
            </div>
            <div className="sticky bottom-0 border-t border-[color:var(--border)] bg-[color:var(--background)] p-4">
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                className="min-h-11 w-full rounded-full bg-[color:var(--accent)] px-5 text-sm font-medium text-white"
              >
                Show {filteredChannels.length} channels
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
