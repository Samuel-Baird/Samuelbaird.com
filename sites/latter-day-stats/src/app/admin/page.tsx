import { requireAdmin } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { fmtDate, fmtNumber } from "@/lib/format";

export default async function AdminDashboardPage() {
  await requireAdmin();

  const supabase = createSupabaseServiceClient();
  const [
    activeChannels,
    inactiveChannels,
    studies,
    profiles,
    lastStats,
    recentProfiles,
  ] = await Promise.all([
    supabase.from("channels").select("id", { count: "exact", head: true }).eq("is_active", true),
    supabase.from("channels").select("id", { count: "exact", head: true }).eq("is_active", false),
    supabase.from("studies").select("id", { count: "exact", head: true }),
    supabase.from("profiles").select("id", { count: "exact", head: true }),
    supabase
      .from("channel_stats")
      .select("captured_at")
      .order("captured_at", { ascending: false })
      .limit(1)
      .maybeSingle(),
    supabase
      .from("profiles")
      .select("email, full_name, created_at")
      .order("created_at", { ascending: false })
      .limit(5),
  ]);

  return (
    <div>
      <h1 className="serif text-4xl font-semibold tracking-tight">Admin</h1>
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Tile
          label="Channels"
          value={fmtNumber((activeChannels.count ?? 0) + (inactiveChannels.count ?? 0))}
          detail={`${activeChannels.count ?? 0} active / ${inactiveChannels.count ?? 0} inactive`}
        />
        <Tile
          label="Studies"
          value={fmtNumber(studies.count)}
          detail="catalogued"
        />
        <Tile label="Users" value={fmtNumber(profiles.count)} detail="registered profiles" />
        <Tile
          label="Last stats refresh"
          value={fmtDate(lastStats.data?.captured_at)}
          detail="channel_stats max captured_at"
        />
      </div>

      <section className="mt-10">
        <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
          Recent sign-ups
        </h2>
        <ul className="mt-4 overflow-hidden rounded-2xl border border-[color:var(--border)] bg-white">
          {(recentProfiles.data ?? []).map((profile) => (
            <li
              key={`${profile.email}-${profile.created_at}`}
              className="flex flex-wrap items-center justify-between gap-3 border-t border-[color:var(--border)] px-5 py-3 first:border-t-0"
            >
              <div>
                <p className="text-sm font-medium">{profile.full_name || "No name"}</p>
                <p className="text-xs text-[color:var(--muted)]">{profile.email}</p>
              </div>
              <p className="text-xs text-[color:var(--muted)]">
                {fmtDate(profile.created_at)}
              </p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function Tile({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-2xl border border-[color:var(--border)] bg-white p-5">
      <div className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
        {label}
      </div>
      <div className="serif mt-2 text-3xl font-semibold tabular-nums">{value}</div>
      <p className="mt-2 text-xs text-[color:var(--muted)]">{detail}</p>
    </div>
  );
}
