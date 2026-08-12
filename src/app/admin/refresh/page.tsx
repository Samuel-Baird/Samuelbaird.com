import { refreshStatsNow } from "@/app/admin/actions";
import { SubmitButton } from "@/components/submit-button";
import { requireAdmin } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { fmtDateTime } from "@/lib/format";

type SearchParams = { confirm?: string; refreshed?: string };

export default async function AdminRefreshPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  await requireAdmin();

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
        Last refresh: {fmtDateTime(data?.captured_at)}
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
            <div className="mt-5">
              <SubmitButton pendingLabel="Refreshing…">
                Refresh stats now
              </SubmitButton>
            </div>
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
