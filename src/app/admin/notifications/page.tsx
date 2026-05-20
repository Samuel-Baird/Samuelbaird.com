import { CopyEmails } from "@/components/copy-emails";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

type Row = { email: string; name: string | null };

export default async function AdminNotificationsPage() {
  const { data, error } = await createSupabaseServiceClient()
    .from("premium_users")
    .select("email, name")
    .eq("notify_weekly", true)
    .order("email", { ascending: true });
  if (error) throw error;

  const rows = (data ?? []) as Row[];
  const csv = rows.map((r) => r.email).join(", ");

  return (
    <div>
      <h1 className="serif text-4xl font-semibold tracking-tight">
        Weekly digest recipients
      </h1>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
        Premium users who have opted in to the weekly email digest. Copy the
        comma-separated list below into your email client to send the digest
        manually.
      </p>

      <div className="mt-6 text-sm text-[color:var(--muted)]">
        {rows.length} {rows.length === 1 ? "recipient" : "recipients"}
      </div>

      <div className="mt-4">
        <CopyEmails value={csv} />
      </div>

      {rows.length > 0 ? (
        <div className="mt-8 overflow-hidden rounded-2xl border border-[color:var(--border)] bg-white">
          <table className="w-full text-sm">
            <thead className="bg-[color:var(--muted-soft)] text-left text-xs uppercase tracking-wider text-[color:var(--muted)]">
              <tr>
                <th className="px-5 py-3 font-medium">Name</th>
                <th className="px-5 py-3 font-medium">Email</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr
                  key={r.email}
                  className="border-t border-[color:var(--border)]"
                >
                  <td className="px-5 py-3 font-medium">
                    {r.name || "—"}
                  </td>
                  <td className="px-5 py-3 text-[color:var(--muted)]">
                    {r.email}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}
