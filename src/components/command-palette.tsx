"use client";

import { Command } from "cmdk";
import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { SearchItem } from "@/lib/data";

type Props = {
  items: SearchItem[];
};

const KIND_LABEL: Record<SearchItem["kind"], string> = {
  channel: "Channels",
  study: "Studies",
  tag: "Tags",
};

function hrefFor(item: SearchItem): string {
  if (item.kind === "channel") return `/channels/${item.slug}`;
  if (item.kind === "study") return `/studies/${item.slug}`;
  return `/studies?tag=${encodeURIComponent(item.slug)}`;
}

export function CommandPalette({ items }: Props) {
  const router = useRouter();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const isToggle =
        (e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey);
      const isSlash =
        e.key === "/" &&
        !(e.target instanceof HTMLInputElement) &&
        !(e.target instanceof HTMLTextAreaElement) &&
        !(e.target instanceof HTMLSelectElement);
      if (isToggle || isSlash) {
        e.preventDefault();
        setOpen((v) => !v);
      }
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  function go(item: SearchItem) {
    setOpen(false);
    router.push(hrefFor(item));
  }

  const grouped: Record<SearchItem["kind"], SearchItem[]> = {
    channel: [],
    study: [],
    tag: [],
  };
  for (const item of items) grouped[item.kind].push(item);

  return (
    <>
      <button
        type="button"
        aria-label="Open search (⌘K)"
        onClick={() => setOpen(true)}
        className="inline-flex h-10 w-10 items-center justify-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)] md:w-auto md:justify-start md:gap-2 md:px-3"
      >
        <Search size={16} aria-hidden="true" />
        <span className="hidden md:inline">Search…</span>
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center px-4 pt-[10vh]"
          role="dialog"
          aria-modal="true"
        >
          <button
            type="button"
            aria-label="Close search"
            onClick={() => setOpen(false)}
            className="absolute inset-0 bg-black/40"
          />
          <Command
            label="Site search"
            className="relative w-full max-w-xl overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)] bg-white shadow-lg"
          >
            <div className="flex items-center gap-3 border-b border-[color:var(--border)] px-4">
              <Search
                size={18}
                aria-hidden="true"
                className="text-[color:var(--muted)]"
              />
              <Command.Input
                autoFocus
                placeholder="Search channels, studies, tags…"
                className="h-12 w-full bg-transparent text-sm outline-none placeholder:text-[color:var(--muted)]"
              />
              <kbd className="hidden rounded border border-[color:var(--border)] bg-[color:var(--muted-soft)] px-1.5 py-0.5 text-[10px] font-medium text-[color:var(--muted)] sm:inline-block">
                Esc
              </kbd>
            </div>
            <Command.List className="max-h-[60vh] overflow-y-auto p-2">
              <Command.Empty className="px-3 py-6 text-center text-sm text-[color:var(--muted)]">
                No results.
              </Command.Empty>
              {(Object.keys(grouped) as SearchItem["kind"][]).map((kind) => {
                const list = grouped[kind];
                if (list.length === 0) return null;
                return (
                  <Command.Group
                    key={kind}
                    heading={KIND_LABEL[kind]}
                    className="px-1 py-1 text-xs uppercase tracking-wider text-[color:var(--muted)]"
                  >
                    {list.map((item) => (
                      <Command.Item
                        key={`${item.kind}:${item.slug}`}
                        value={`${item.name} ${item.sub ?? ""} ${item.kind}`}
                        onSelect={() => go(item)}
                        className="flex cursor-pointer items-center justify-between gap-3 rounded-[var(--radius)] px-3 py-2 text-sm text-[color:var(--foreground)] aria-selected:bg-[color:var(--muted-soft)]"
                      >
                        <span className="truncate font-medium">
                          {item.name}
                        </span>
                        {item.sub && (
                          <span className="shrink-0 text-xs text-[color:var(--muted)]">
                            {item.sub}
                          </span>
                        )}
                      </Command.Item>
                    ))}
                  </Command.Group>
                );
              })}
            </Command.List>
          </Command>
        </div>
      )}
    </>
  );
}
