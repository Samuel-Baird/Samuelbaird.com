"use client";

import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { X } from "lucide-react";

type ChannelOption = { slug: string; name: string };

type Props = {
  allChannels: ChannelOption[];
  selectedSlugs: string[];
  max?: number;
  basePath?: string;
};

export function ChannelPicker({
  allChannels,
  selectedSlugs,
  max = 4,
  basePath = "/compare",
}: Props) {
  const router = useRouter();
  const [query, setQuery] = useState("");

  const bySlug = useMemo(
    () => new Map(allChannels.map((c) => [c.slug, c])),
    [allChannels],
  );
  const selected = selectedSlugs
    .map((s) => bySlug.get(s))
    .filter((c): c is ChannelOption => Boolean(c));

  const matches = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return allChannels
      .filter(
        (c) =>
          !selectedSlugs.includes(c.slug) &&
          c.name.toLowerCase().includes(q),
      )
      .slice(0, 8);
  }, [allChannels, query, selectedSlugs]);

  function navigate(next: string[]) {
    const params = new URLSearchParams();
    if (next.length > 0) params.set("slugs", next.join(","));
    router.replace(`${basePath}${params.toString() ? `?${params}` : ""}`);
  }

  function add(slug: string) {
    if (selectedSlugs.includes(slug)) return;
    if (selectedSlugs.length >= max) return;
    setQuery("");
    navigate([...selectedSlugs, slug]);
  }

  function remove(slug: string) {
    navigate(selectedSlugs.filter((s) => s !== slug));
  }

  const atMax = selectedSlugs.length >= max;

  return (
    <div className="rounded-2xl border border-[color:var(--border)] bg-white p-4 sm:p-5">
      <div className="flex flex-wrap items-center gap-2">
        {selected.map((c) => (
          <button
            key={c.slug}
            type="button"
            onClick={() => remove(c.slug)}
            aria-label={`Remove ${c.name}`}
            className="inline-flex min-h-9 items-center gap-1.5 rounded-full bg-[color:var(--accent-soft)] px-3 text-xs text-[color:var(--accent)] hover:opacity-80"
          >
            <span className="font-medium">{c.name}</span>
            <X aria-hidden="true" size={14} />
          </button>
        ))}
        {selected.length === 0 && (
          <p className="text-sm text-[color:var(--muted)]">
            Add up to {max} channels to compare.
          </p>
        )}
      </div>

      {!atMax && (
        <div className="relative mt-3">
          <input
            type="search"
            inputMode="search"
            placeholder="Add a channel by name..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="h-11 w-full rounded-full border border-[color:var(--border)] bg-white px-5 text-sm placeholder:text-[color:var(--muted)] focus:border-[color:var(--accent)] focus:outline-none"
          />
          {matches.length > 0 && (
            <ul className="absolute left-0 right-0 z-20 mt-2 max-h-72 overflow-y-auto rounded-2xl border border-[color:var(--border)] bg-white shadow-lg">
              {matches.map((c) => (
                <li key={c.slug}>
                  <button
                    type="button"
                    onClick={() => add(c.slug)}
                    className="block w-full px-4 py-2.5 text-left text-sm hover:bg-[color:var(--muted-soft)]"
                  >
                    {c.name}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      {atMax && (
        <p className="mt-3 text-xs text-[color:var(--muted)]">
          Remove a channel to add another (max {max}).
        </p>
      )}
    </div>
  );
}
