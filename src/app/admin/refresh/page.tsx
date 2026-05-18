import { refreshStatsNow } from "@/app/admin/actions";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { fmtDate } from "@/lib/format";

type SearchParams = { confirm?: string; refreshed?: string };

export default async function AdminRefreshPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  const { data } = await createSupabaseServiceClient()
    .from("channel_stats")
    .select("captured_at")
    .order("captured_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  return (
    <div className="max-w-xl">
      <h1 className="serif text-4xl font-semibold tracking-tight">
        Refresh stats
      </h1>
      <p className="mt-3 text-sm text-[color:var(--muted)]">
        Last refresh: {fmtDate(data?.captured_at)}
      </p>
      {params.refreshed && (
        <p className="mt-3 text-sm text-[color:var(--accent)]">
          Stats refresh completed.
        </p>
      )}

      <div className="mt-8 rounded-2xl border border-[color:var(--border)] bg-white p-6">
        {params.confirm === "1" ? (
          <form action={refreshStatsNow}>
            <p className="text-sm text-[color:var(--muted)]">
              This will call the YouTube API for every tracked channel and append
              a new stats snapshot.
            </p>
            <button className="mt-5 inline-flex h-10 items-center rounded-full bg-[color:var(--accent)] px-4 text-sm font-medium text-white hover:opacity-90">
              Refresh stats now
            </button>
          </form>
        ) : (
          <a
            href="/admin/refresh?confirm=1"
            className="inline-flex h-10 items-center rounded-full bg-[color:var(--accent)] px-4 text-sm font-medium text-white hover:opacity-90"
          >
            Continue to confirmation
          </a>
        )}
      </div>
    </div>
  );
}
