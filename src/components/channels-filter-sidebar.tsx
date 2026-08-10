"use client";

import { ChevronDown } from "lucide-react";
import { useMemo, useState } from "react";

export type FilterGroup = {
  key: "type" | "country" | "language";
  label: string;
  options: { value: string; label: string; count: number }[];
};

type Props = {
  groups: FilterGroup[];
  selections: Record<string, Set<string>>;
  onToggle: (groupKey: FilterGroup["key"], value: string) => void;
  onSelectAll: (groupKey: FilterGroup["key"]) => void;
  onSelectNone: (groupKey: FilterGroup["key"]) => void;
  onClearAll: () => void;
  variant?: "desktop" | "drawer";
};

const defaultOpen: Record<FilterGroup["key"], boolean> = {
  type: true,
  country: false,
  language: false,
};

export function ChannelsFilterSidebar({
  groups,
  selections,
  onToggle,
  onSelectAll,
  onSelectNone,
  onClearAll,
  variant = "desktop",
}: Props) {
  const [openGroups, setOpenGroups] =
    useState<Record<FilterGroup["key"], boolean>>(defaultOpen);

  const activeCount = useMemo(
    () =>
      groups.reduce((total, group) => total + (selections[group.key]?.size ?? 0), 0),
    [groups, selections],
  );

  return (
    <div
      className={
        variant === "desktop"
          ? "rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5"
          : "bg-[color:var(--background)] p-5"
      }
    >
      <div className="flex min-h-10 items-center justify-between gap-4">
        <h2 className="serif text-xl font-semibold tracking-tight">Filters</h2>
        {activeCount > 0 && (
          <button
            type="button"
            onClick={onClearAll}
            className="min-h-10 rounded-[var(--radius)] px-2 text-sm text-[color:var(--accent)] hover:underline"
          >
            Clear all
          </button>
        )}
      </div>

      <div className="mt-4 divide-y divide-[color:var(--border)]">
        {groups.map((group) => {
          const selected = selections[group.key] ?? new Set<string>();
          const isOpen = openGroups[group.key];

          return (
            <details
              key={group.key}
              open={isOpen}
              onToggle={(event) => {
                setOpenGroups((current) => ({
                  ...current,
                  [group.key]: event.currentTarget.open,
                }));
              }}
              className="group py-3"
            >
              <summary className="flex min-h-10 cursor-pointer list-none items-center justify-between gap-3 text-sm font-medium [&::-webkit-details-marker]:hidden">
                <span className="flex items-center gap-2">
                  <span>{group.label}</span>
                  {selected.size > 0 && (
                    <span className="rounded-[var(--radius)] bg-[color:var(--accent-soft)] px-2 py-0.5 text-xs text-[color:var(--accent)]">
                      {selected.size}
                    </span>
                  )}
                </span>
                <ChevronDown
                  aria-hidden="true"
                  size={16}
                  className={`shrink-0 text-[color:var(--muted)] transition-transform ${
                    isOpen ? "rotate-180" : ""
                  }`}
                />
              </summary>

              <div className="pb-1 pt-2">
                <div className="flex min-h-10 items-center gap-3 text-xs">
                  <button
                    type="button"
                    onClick={() => onSelectAll(group.key)}
                    className="min-h-10 rounded-[var(--radius)] pr-2 text-[color:var(--accent)] hover:underline"
                  >
                    Select all
                  </button>
                  <button
                    type="button"
                    onClick={() => onSelectNone(group.key)}
                    className="min-h-10 rounded-[var(--radius)] px-2 text-[color:var(--muted)] hover:text-[color:var(--foreground)] hover:underline"
                  >
                    Select none
                  </button>
                </div>

                <div className="pr-1">
                  {group.options.map((option) => (
                    <label
                      key={option.value}
                      className="flex min-h-10 cursor-pointer items-center gap-3 rounded-[var(--radius)] py-2.5 text-sm hover:bg-[color:var(--muted-soft)]/60"
                    >
                      <input
                        type="checkbox"
                        checked={selected.has(option.value)}
                        onChange={() => onToggle(group.key, option.value)}
                        className="ml-1 h-4 w-4 rounded border-[color:var(--border)] accent-[color:var(--accent)]"
                      />
                      <span className="min-w-0 flex-1 truncate pl-1">
                        {option.label}
                      </span>
                      <span className="pr-2 text-xs text-[color:var(--muted)]">
                        ({option.count})
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </details>
          );
        })}
      </div>
    </div>
  );
}
