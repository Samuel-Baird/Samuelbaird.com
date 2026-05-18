import Link from "next/link";
import { AdminChannelsTable } from "@/components/admin-channels-table";
import { TYPE_COLORS } from "@/lib/channel-types";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import type { Channel, ChannelStats } from "@/lib/types";

type SearchParams = { added?: string; updated?: string; duplicate?: string };

export default async function AdminChannelsPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  const supabase = createSupabaseServiceClient();
  const [{ data: channels, error }, { data: stats, error: statsError }] =
    await Promise.all([
      supabase.from("channels").select("*").order("name", { ascending: true }),
      supabase.from("channel_stats_latest").select("*"),
    ]);
  if (error) throw error;
  if (statsError) throw statsError;

  const types = Object.keys(TYPE_COLORS).sort();

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
          {params.updated && (
            <p className="mt-2 text-sm text-[color:var(--accent)]">
              Updated {params.updated}
            </p>
          )}
          {params.duplicate && (
            <p className="mt-2 text-sm text-red-700">
              Already in the database: {params.duplicate}
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

      <AdminChannelsTable
        channels={(channels ?? []) as Channel[]}
        stats={(stats ?? []) as ChannelStats[]}
        types={types}
      />
    </div>
  );
}
