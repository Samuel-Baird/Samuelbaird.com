"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import {
  deleteChannel,
  setChannelActive,
  setChannelFeatured,
} from "@/app/admin/actions";
import { Tag } from "@/components/tag";
import { inkForType } from "@/lib/channel-types";
import { fmtCompact } from "@/lib/format";
import type { Channel, ChannelStats } from "@/lib/types";

type Props = {
  channels: Channel[];
  stats: ChannelStats[];
  types: string[];
};

function channelTagsOf(c: Channel): string[] {
  return c.channel_types?.length ? c.channel_types : c.channel_type ? [c.channel_type] : [];
}

export function AdminChannelsTable({ channels, stats, types }: Props) {
  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const byId = useMemo(
    () => new Map(stats.map((stat) => [stat.channel_id, stat])),
    [stats],
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return channels.filter((c) => {
      if (typeFilter && !channelTagsOf(c).includes(typeFilter)) return false;
      if (!q) return true;
      return (
        c.name.toLowerCase().includes(q) ||
        (c.handle ?? "").toLowerCase().includes(q) ||
        channelTagsOf(c).some((t) => t.toLowerCase().includes(q)) ||
        (c.country ?? "").toLowerCase().includes(q) ||
        (c.country_manual ?? "").toLowerCase().includes(q) ||
        (c.owned_by ?? "").toLowerCase().includes(q) ||
        c.youtube_channel_id.toLowerCase().includes(q)
      );
    });
  }, [channels, query, typeFilter]);

  return (
    <div>
      <div className="mt-6 flex flex-wrap items-center gap-3">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by name, handle, type, country…"
          className="h-10 flex-1 min-w-[260px] rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none"
        />
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="h-10 rounded-[var(--radius)] border border-[color:var(--border)] px-3 text-sm"
        >
          <option value="">All types</option>
          {types.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <span className="text-xs text-[color:var(--muted)]">
          {filtered.length} / {channels.length}
        </span>
      </div>

      <div className="mt-4 overflow-x-auto rounded-[var(--radius)] border border-[color:var(--border)] bg-white">
        <table className="w-full min-w-[900px] text-sm">
          <thead className="bg-[color:var(--muted-soft)]/60 text-left text-xs uppercase tracking-wider text-[color:var(--muted)]">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3 text-right">Subs</th>
              <th className="px-4 py-3">Featured</th>
              <th className="px-4 py-3">Active</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {filtered.map((channel) => {
              const latest = byId.get(channel.id);
              return (
                <tr
                  key={channel.id}
                  className="border-t border-[color:var(--border)]"
                >
                  <td className="px-4 py-3 font-medium">
                    <div>{channel.name}</div>
                    {channel.handle && (
                      <div className="text-xs text-[color:var(--muted)]">
                        {channel.handle}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {channelTagsOf(channel).length === 0 ? (
                      <span className="text-xs text-[color:var(--muted)]">—</span>
                    ) : (
                      <div className="flex max-w-[220px] flex-wrap gap-1">
                        {channelTagsOf(channel).map((t) => (
                          <Tag key={t} ink={inkForType(t)}>
                            {t}
                          </Tag>
                        ))}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {fmtCompact(latest?.subscribers)}
                  </td>
                  <td className="px-4 py-3">
                    <form
                      action={setChannelFeatured.bind(
                        null,
                        channel.id,
                        !channel.featured,
                      )}
                    >
                      <button className="rounded-[var(--radius)] border border-[color:var(--border)] px-3 py-1 text-xs hover:bg-[color:var(--muted-soft)]">
                        {channel.featured ? "Featured" : "Not featured"}
                      </button>
                    </form>
                  </td>
                  <td className="px-4 py-3">
                    <form
                      action={setChannelActive.bind(
                        null,
                        channel.id,
                        !channel.is_active,
                      )}
                    >
                      <button className="rounded-[var(--radius)] border border-[color:var(--border)] px-3 py-1 text-xs hover:bg-[color:var(--muted-soft)]">
                        {channel.is_active ? "Active" : "Inactive"}
                      </button>
                    </form>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-3">
                      <Link
                        href={`/channels/${channel.slug}`}
                        className="text-xs text-[color:var(--accent)] hover:underline"
                      >
                        View
                      </Link>
                      <Link
                        href={`/admin/channels/${channel.slug}/edit`}
                        className="text-xs text-[color:var(--accent)] hover:underline"
                      >
                        Edit
                      </Link>
                      <form action={deleteChannel.bind(null, channel.id)}>
                        <button className="text-xs text-red-700 hover:underline">
                          Delete
                        </button>
                      </form>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
