"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Tag } from "@/components/tag";
import { inkForType } from "@/lib/channel-types";
import { fmtCompact } from "@/lib/format";
import type { ChannelWithStats } from "@/lib/types";

const PAGE_SIZE = 6;
const ROTATE_MS = 6000;

function channelTagsOf(c: ChannelWithStats): string[] {
  return c.channel_types?.length
    ? c.channel_types
    : c.channel_type
      ? [c.channel_type]
      : [];
}

export function ChannelsCarousel({ channels }: { channels: ChannelWithStats[] }) {
  const pageCount = Math.max(1, Math.ceil(channels.length / PAGE_SIZE));
  const [page, setPage] = useState(0);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (paused || pageCount <= 1) return;
    const id = setInterval(() => {
      setPage((p) => (p + 1) % pageCount);
    }, ROTATE_MS);
    return () => clearInterval(id);
  }, [paused, pageCount]);

  if (channels.length === 0) return null;

  const start = page * PAGE_SIZE;
  const visible = channels.slice(start, start + PAGE_SIZE);

  return (
    <section
      className="mt-20"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <div className="flex items-end justify-between gap-3">
        <h2 className="serif text-2xl font-semibold tracking-tight sm:text-3xl">
          Featured channels
        </h2>
        <Link
          href="/channels"
          className="text-sm text-[color:var(--accent)] hover:underline"
        >
          View all →
        </Link>
      </div>
      <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {visible.map((c, i) => {
          const tags = channelTagsOf(c);
          return (
            <li key={`${c.id}-${start + i}`}>
              <Link
                href={`/channels/${c.slug}`}
                className="group flex h-full items-center gap-4 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-4 transition-colors hover:border-[color:var(--accent)]"
              >
                {c.thumbnail_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={c.thumbnail_url}
                    alt=""
                    className="h-14 w-14 shrink-0 rounded-full object-cover"
                  />
                ) : (
                  <div className="h-14 w-14 shrink-0 rounded-full bg-[color:var(--muted-soft)]" />
                )}
                <div className="min-w-0 flex-1">
                  <h3 className="truncate text-sm font-semibold group-hover:text-[color:var(--accent)]">
                    {c.name}
                  </h3>
                  <div className="mt-1 flex flex-wrap items-center gap-1.5 text-xs text-[color:var(--muted)]">
                    {tags.map((tag) => (
                      <Tag key={tag} ink={inkForType(tag)}>
                        {tag}
                      </Tag>
                    ))}
                    <span className="tabular-nums">
                      {fmtCompact(c.latest?.subscribers)} subs
                    </span>
                  </div>
                </div>
              </Link>
            </li>
          );
        })}
      </ul>
      {pageCount > 1 && (
        <div className="mt-5 flex items-center justify-center gap-2">
          {Array.from({ length: pageCount }).map((_, i) => (
            <button
              key={i}
              type="button"
              aria-label={`Show channels page ${i + 1}`}
              onClick={() => setPage(i)}
              className={
                "h-1.5 rounded-full transition-all " +
                (i === page
                  ? "w-6 bg-[color:var(--accent)]"
                  : "w-1.5 bg-[color:var(--border)] hover:bg-[color:var(--muted)]")
              }
            />
          ))}
        </div>
      )}
    </section>
  );
}
