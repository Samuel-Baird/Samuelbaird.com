import { deleteApologist, upsertApologist } from "@/app/admin/actions";
import { SubmitButton } from "@/components/submit-button";
import { Tag } from "@/components/tag";
import { requireAdmin } from "@/lib/auth";
import { fmtDate } from "@/lib/format";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

type Apologist = {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
};

export default async function AdminApologistsPage() {
  // Gate here too, not just in admin/layout.tsx: Next streams a layout's
  // not-found boundary independently of a sibling page segment's own data
  // fetching, so a layout-only check can still leak this query's real rows
  // into the raw response even though the rendered page correctly shows
  // 404. Every gated page must call its own require*() before fetching.
  await requireAdmin();

  const { data, error } = await createSupabaseServiceClient()
    .from("apologists")
    .select("id, email, name, created_at")
    .order("created_at", { ascending: false });
  if (error) throw error;

  const apologists = (data ?? []) as Apologist[];

  return (
    <div>
      <h1 className="serif text-4xl font-semibold tracking-tight">
        Apologists
      </h1>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
        Add trusted apologist content creators here — before or after they
        sign in. Apologist access unlocks the Apologetics Hub: claim-level
        rebuttals and sources for critical-channel videos. Everyone else gets
        a 404 on hub pages.
      </p>

      <form
        action={upsertApologist}
        className="mt-8 grid gap-4 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 sm:grid-cols-[1fr_1fr_auto]"
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
        <div className="flex items-end">
          <SubmitButton pendingLabel="Saving...">Add / update</SubmitButton>
        </div>
      </form>

      <div className="mt-8 overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)] bg-white">
        {apologists.length > 0 ? (
          <table className="w-full text-sm">
            <thead className="bg-[color:var(--muted-soft)] text-left text-xs uppercase tracking-wider text-[color:var(--muted)]">
              <tr>
                <th className="px-5 py-3 font-medium">Name</th>
                <th className="px-5 py-3 font-medium">Email</th>
                <th className="px-5 py-3 font-medium">Added</th>
                <th className="px-5 py-3 text-right font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {apologists.map((apologist) => (
                <tr
                  key={apologist.id}
                  className="border-t border-[color:var(--border)]"
                >
                  <td className="px-5 py-3 font-medium">
                    {apologist.name || "No name"}
                  </td>
                  <td className="px-5 py-3 text-[color:var(--muted)]">
                    {apologist.email}
                  </td>
                  <td className="px-5 py-3 text-[color:var(--muted)]">
                    {fmtDate(apologist.created_at)}
                  </td>
                  <td className="px-5 py-3 text-right">
                    <form action={deleteApologist.bind(null, apologist.id)}>
                      <button
                        type="submit"
                        className="text-xs font-medium text-[color:var(--oxblood)] hover:underline"
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
            No apologists yet.{" "}
            <Tag ink="accent">Admins always have hub access</Tag>
          </div>
        )}
      </div>
    </div>
  );
}
