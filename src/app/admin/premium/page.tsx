import { deletePremiumUser, upsertPremiumUser } from "@/app/admin/actions";
import { CopyEmails } from "@/components/copy-emails";
import { SubmitButton } from "@/components/submit-button";
import { fmtDate } from "@/lib/format";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

type PremiumUser = {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
  notify_weekly: boolean;
};

export default async function AdminPremiumUsersPage() {
  const { data, error } = await createSupabaseServiceClient()
    .from("premium_users")
    .select("id, email, name, created_at, notify_weekly")
    .order("created_at", { ascending: false });
  if (error) throw error;

  const premiumUsers = (data ?? []) as PremiumUser[];
  const digestEmails = premiumUsers
    .filter((u) => u.notify_weekly)
    .map((u) => u.email)
    .sort();
  const digestCsv = digestEmails.join(", ");

  return (
    <div>
      <h1 className="serif text-4xl font-semibold tracking-tight">
        Premium members
      </h1>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
        Add people here once they&apos;ve donated $5 or more and sent their
        receipt — before or after they sign in. Premium access grants CSV
        exports, channel comparison, risers &amp; fallers, critical creators,
        and the weekly digest opt-in.
      </p>

      <form
        action={upsertPremiumUser}
        className="mt-8 grid gap-4 rounded-2xl border border-[color:var(--border)] bg-white p-5 sm:grid-cols-[1fr_1fr_auto]"
      >
        <label className="block">
          <span className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
            Email
          </span>
          <input
            name="email"
            type="email"
            required
            className="mt-1.5 h-11 w-full rounded-xl border border-[color:var(--border)] bg-white px-3 text-sm"
            placeholder="person@example.com"
          />
        </label>
        <label className="block">
          <span className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
            Name
          </span>
          <input
            name="name"
            type="text"
            className="mt-1.5 h-11 w-full rounded-xl border border-[color:var(--border)] bg-white px-3 text-sm"
            placeholder="Optional display name"
          />
        </label>
        <div className="flex items-end">
          <SubmitButton
            pendingLabel="Saving..."
            className="inline-flex h-11 w-full items-center justify-center rounded-full bg-[color:var(--accent)] px-5 text-sm font-medium text-white hover:opacity-90 sm:w-auto"
          >
            Add / update
          </SubmitButton>
        </div>
      </form>

      <section className="mt-10 rounded-2xl border border-[color:var(--border)] bg-white p-5 sm:p-6">
        <h2 className="serif text-xl font-semibold tracking-tight">
          Weekly digest recipients
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
          Premium members who opted in to the weekly email digest. Copy the
          comma-separated list below and paste into your email client to send
          the digest manually.
        </p>
        <div className="mt-4 text-sm text-[color:var(--muted)]">
          {digestEmails.length}{" "}
          {digestEmails.length === 1 ? "recipient" : "recipients"}
        </div>
        <div className="mt-3">
          <CopyEmails value={digestCsv} />
        </div>
      </section>

      <div className="mt-8 overflow-hidden rounded-2xl border border-[color:var(--border)] bg-white">
        {premiumUsers.length > 0 ? (
          <table className="w-full text-sm">
            <thead className="bg-[color:var(--muted-soft)] text-left text-xs uppercase tracking-wider text-[color:var(--muted)]">
              <tr>
                <th className="px-5 py-3 font-medium">Name</th>
                <th className="px-5 py-3 font-medium">Email</th>
                <th className="px-5 py-3 font-medium">Added</th>
                <th className="px-5 py-3 font-medium">Weekly digest</th>
                <th className="px-5 py-3 text-right font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {premiumUsers.map((user) => (
                <tr
                  key={user.id}
                  className="border-t border-[color:var(--border)]"
                >
                  <td className="px-5 py-3 font-medium">
                    {user.name || "No name"}
                  </td>
                  <td className="px-5 py-3 text-[color:var(--muted)]">
                    {user.email}
                  </td>
                  <td className="px-5 py-3 text-[color:var(--muted)]">
                    {fmtDate(user.created_at)}
                  </td>
                  <td className="px-5 py-3 text-[color:var(--muted)]">
                    {user.notify_weekly ? (
                      <span className="text-emerald-700">Opted in</span>
                    ) : (
                      <span>—</span>
                    )}
                  </td>
                  <td className="px-5 py-3 text-right">
                    <form action={deletePremiumUser.bind(null, user.id)}>
                      <button
                        type="submit"
                        className="text-xs font-medium text-red-700 hover:underline"
                      >
                        Remove
                      </button>
                    </form>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="p-8 text-center text-sm text-[color:var(--muted)]">
            No premium members yet.
          </div>
        )}
      </div>
    </div>
  );
}
