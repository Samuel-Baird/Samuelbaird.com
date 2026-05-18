import Link from "next/link";
import {
  deleteChannel,
  setChannelActive,
  setChannelFeatured,
} from "@/app/admin/actions";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { fmtCompact, fmtNumber } from "@/lib/format";
import type { Channel, ChannelStats } from "@/lib/types";

type SearchParams = { page?: string; added?: string };

export default async function AdminChannelsPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  const page = Math.max(1, Number(params.page ?? 1) || 1);
  const pageSize = 50;
  const from = (page - 1) * pageSize;
  const to = from + pageSize - 1;
  const supabase = createSupabaseServiceClient();
  const [{ data: channels, count, error }, { data: stats, error: statsError }] =
    await Promise.all([
      supabase
        .from("channels")
        .select("*", { count: "exact" })
        .order("name", { ascending: true })
        .range(from, to),
      supabase.from("channel_stats_latest").select("*"),
    ]);
  if (error) throw error;
  if (statsError) throw statsError;

  const byId = new Map(
    ((stats ?? []) as ChannelStats[]).map((stat) => [stat.channel_id, stat]),
  );
  const totalPages = Math.max(1, Math.ceil((count ?? 0) / pageSize));

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="serif text-4xl font-semibold tracking-tight">
            Channels
          </h1>
          {params.added && (
            <p className="mt-2 text-sm text-[color:var(--accent)]">
              Added {params.added}
            </p>
          )}
        </div>
        <Link
          href="/admin/channels/new"
          className="inline-flex h-10 items-center rounded-full bg-[color:var(--accent)] px-4 text-sm font-medium text-white hover:opacity-90"
        >
          New channel
        </Link>
      </div>

      <div className="mt-6 overflow-x-auto rounded-2xl border border-[color:var(--border)] bg-white">
        <table className="w-full min-w-[900px] text-sm">
          <thead className="bg-[color:var(--muted-soft)]/60 text-left text-xs uppercase tracking-wider text-[color:var(--muted)]">
            <tr>
              <th className="px-4 py-3">Thumbnail</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3 text-right">Subs</th>
              <th className="px-4 py-3">Featured</th>
              <th className="px-4 py-3">Active</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {((channels ?? []) as Channel[]).map((channel) => {
              const latest = byId.get(channel.id);
              return (
                <tr key={channel.id} className="border-t border-[color:var(--border)]">
                  <td className="px-4 py-3">
                    {channel.thumbnail_url ? (
                      <img
                        src={channel.thumbnail_url}
                        alt=""
                        className="h-10 w-10 rounded-full object-cover"
                      />
                    ) : (
                      <div className="h-10 w-10 rounded-full bg-[color:var(--muted-soft)]" />
                    )}
                  </td>
                  <td className="px-4 py-3 font-medium">{channel.name}</td>
                  <td className="px-4 py-3 text-[color:var(--muted)]">
                    {channel.channel_type ?? "-"}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {fmtCompact(latest?.subscribers)}
                  </td>
                  <td className="px-4 py-3">
                    <form action={setChannelFeatured.bind(null, channel.id, !channel.featured)}>
                      <button className="rounded-full border border-[color:var(--border)] px-3 py-1 text-xs hover:bg-[color:var(--muted-soft)]">
                        {channel.featured ? "Featured" : "Not featured"}
                      </button>
                    </form>
                  </td>
                  <td className="px-4 py-3">
                    <form action={setChannelActive.bind(null, channel.id, !channel.is_active)}>
                      <button className="rounded-full border border-[color:var(--border)] px-3 py-1 text-xs hover:bg-[color:var(--muted-soft)]">
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

      <div className="mt-5 flex items-center justify-between text-sm text-[color:var(--muted)]">
        <span>
          Page {fmtNumber(page)} of {fmtNumber(totalPages)}
        </span>
        <div className="flex gap-2">
          {page > 1 && <PageLink page={page - 1}>Previous</PageLink>}
          {page < totalPages && <PageLink page={page + 1}>Next</PageLink>}
        </div>
      </div>
    </div>
  );
}

function PageLink({
  page,
  children,
}: {
  page: number;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={`/admin/channels?page=${page}`}
      className="rounded-full border border-[color:var(--border)] px-3 py-1 hover:bg-[color:var(--muted-soft)]"
    >
      {children}
    </Link>
  );
}
