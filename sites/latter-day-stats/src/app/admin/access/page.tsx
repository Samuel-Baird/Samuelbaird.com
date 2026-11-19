import { setUserRole, upsertUserAccess, type UserRole } from "@/app/admin/actions";
import { CopyEmails } from "@/components/copy-emails";
import { SubmitButton } from "@/components/submit-button";
import { requireAdmin } from "@/lib/auth";
import { fmtDate } from "@/lib/format";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

type RoleRow = { email: string; name: string | null; created_at: string };
type ProfileAdminRow = { email: string | null; full_name: string | null };

type Person = {
  email: string;
  name: string | null;
  premium: boolean;
  admin: boolean;
  addedAt: string | null;
};

const ROLES: { key: UserRole; label: string }[] = [
  { key: "premium", label: "Premium" },
  { key: "admin", label: "Admin" },
];

export default async function AdminAccessPage() {
  // Gate here, not just in admin/layout.tsx — a layout-only check isn't
  // enough to keep this page's real data out of the response.
  await requireAdmin();

  const supabase = createSupabaseServiceClient();

  const [
    { data: premiumRows, error: premiumError },
    { data: adminRows, error: adminError },
    { data: adminProfileRows, error: profileError },
    { data: digestRows, error: digestError },
  ] = await Promise.all([
    supabase.from("premium_users").select("email, name, created_at"),
    supabase.from("admins").select("email, name, created_at"),
    supabase.from("profiles").select("email, full_name").eq("is_admin", true),
    supabase.from("premium_users").select("email").eq("notify_weekly", true),
  ]);
  if (premiumError) throw premiumError;
  if (adminError) throw adminError;
  if (profileError) throw profileError;
  if (digestError) throw digestError;

  const people = new Map<string, Person>();
  function upsert(email: string | null, name: string | null, addedAt: string | null, role?: UserRole) {
    if (!email) return;
    const existing = people.get(email);
    const person: Person = existing ?? {
      email,
      name: null,
      premium: false,
      admin: false,
      addedAt: null,
    };
    person.name = person.name ?? name;
    person.addedAt = person.addedAt ?? addedAt;
    if (role) person[role] = true;
    people.set(email, person);
  }

  for (const r of (premiumRows ?? []) as RoleRow[]) upsert(r.email, r.name, r.created_at, "premium");
  for (const r of (adminRows ?? []) as RoleRow[]) upsert(r.email, r.name, r.created_at, "admin");
  // Admins granted before this table existed (the hardcoded owner bootstrap)
  // still need to show up and be manageable here.
  for (const r of (adminProfileRows ?? []) as ProfileAdminRow[]) {
    upsert(r.email, r.full_name, null, "admin");
  }

  const roster = [...people.values()].sort((a, b) => a.email.localeCompare(b.email));

  const digestEmails = ((digestRows ?? []) as { email: string }[])
    .map((r) => r.email)
    .sort();

  return (
    <div>
      <h1 className="serif text-4xl font-semibold tracking-tight">
        Access &amp; roles
      </h1>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
        Grant premium and admin access from one place — before or after
        someone signs in. Check a role to add it, uncheck to remove it;
        changes apply immediately.
      </p>

      <form
        action={upsertUserAccess}
        className="mt-8 grid gap-4 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 sm:grid-cols-[1fr_1fr_auto_auto_auto]"
      >
        <label className="block">
          <span className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
            Email
          </span>
          <input
            name="email"
            type="email"
            required
            className="mt-1.5 h-11 w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-sm"
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
            className="mt-1.5 h-11 w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-sm"
            placeholder="Optional display name"
          />
        </label>
        {ROLES.map((role) => (
          <label
            key={role.key}
            className="flex items-end gap-1.5 pb-2.5 text-sm"
          >
            <input type="checkbox" name={role.key} className="h-4 w-4" />
            {role.label}
          </label>
        ))}
        <div className="flex items-end">
          <SubmitButton pendingLabel="Saving...">Add / update</SubmitButton>
        </div>
      </form>

      <div className="mt-8 overflow-x-auto rounded-[var(--radius)] border border-[color:var(--border)] bg-white">
        {roster.length > 0 ? (
          <table className="w-full min-w-[640px] text-sm">
            <thead className="bg-[color:var(--muted-soft)] text-left text-xs uppercase tracking-wider text-[color:var(--muted)]">
              <tr>
                <th className="px-5 py-3 font-medium">Name</th>
                <th className="px-5 py-3 font-medium">Email</th>
                {ROLES.map((role) => (
                  <th key={role.key} className="px-5 py-3 font-medium">
                    {role.label}
                  </th>
                ))}
                <th className="px-5 py-3 font-medium">Added</th>
              </tr>
            </thead>
            <tbody>
              {roster.map((person) => (
                <tr
                  key={person.email}
                  className="border-t border-[color:var(--border)]"
                >
                  <td className="px-5 py-3 font-medium">
                    {person.name || "No name"}
                  </td>
                  <td className="px-5 py-3 text-[color:var(--muted)]">
                    {person.email}
                  </td>
                  {ROLES.map((role) => {
                    const active = person[role.key];
                    return (
                      <td key={role.key} className="px-5 py-3">
                        <form
                          action={setUserRole.bind(
                            null,
                            person.email,
                            role.key,
                            !active,
                          )}
                        >
                          <button
                            type="submit"
                            className={
                              "rounded-[var(--radius)] border px-2.5 py-1 text-xs font-medium transition-colors " +
                              (active
                                ? "border-[color:var(--accent)] bg-[color:var(--accent-soft)] text-[color:var(--accent)]"
                                : "border-[color:var(--border)] text-[color:var(--muted)] hover:text-[color:var(--foreground)]")
                            }
                          >
                            {active ? "✓" : "—"}
                          </button>
                        </form>
                      </td>
                    );
                  })}
                  <td className="px-5 py-3 text-[color:var(--muted)]">
                    {person.addedAt ? fmtDate(person.addedAt) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="p-8 text-center text-sm text-[color:var(--muted)]">
            Nobody has premium or admin access yet.
          </div>
        )}
      </div>

      <div className="mt-10 grid gap-6 sm:grid-cols-2">
        <section className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 sm:p-6">
          <h2 className="serif text-xl font-semibold tracking-tight">
            Weekly digest recipients
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-[color:var(--muted)]">
            Premium members opted into the weekly email digest.
          </p>
          <div className="mt-4 text-sm text-[color:var(--muted)]">
            {digestEmails.length} {digestEmails.length === 1 ? "recipient" : "recipients"}
          </div>
          <div className="mt-3">
            <CopyEmails value={digestEmails.join(", ")} />
          </div>
        </section>
      </div>
    </div>
  );
}
