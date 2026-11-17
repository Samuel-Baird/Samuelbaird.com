import { requireAdmin } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { fmtDate } from "@/lib/format";
import { markMessageResolved } from "@/app/actions/messages";
import { categoryLabel } from "@/lib/messages";

type Message = {
  id: string;
  category: string;
  name: string | null;
  email: string | null;
  page_ref: string | null;
  body: string;
  user_id: string | null;
  resolved: boolean;
  resolved_at: string | null;
  created_at: string;
};

type SearchParams = { filter?: string };

async function toggleResolved(formData: FormData) {
  "use server";
  const id = String(formData.get("id"));
  const resolved = formData.get("resolved") === "true";
  await markMessageResolved(id, resolved);
}

export default async function AdminMessagesPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  await requireAdmin();

  const params = await searchParams;
  const showResolved = params.filter === "resolved";
  const showAll = params.filter === "all";

  const supabase = createSupabaseServiceClient();
  let q = supabase
    .from("messages")
    .select("*")
    .order("created_at", { ascending: false });
  if (!showAll) {
    q = q.eq("resolved", showResolved);
  }
  const { data, error } = await q;
  if (error) throw error;
  const messages = (data ?? []) as Message[];

  const tabs = [
    { key: "open", label: "Open", href: "/admin/messages" },
    { key: "resolved", label: "Resolved", href: "/admin/messages?filter=resolved" },
    { key: "all", label: "All", href: "/admin/messages?filter=all" },
  ];
  const activeKey = showAll ? "all" : showResolved ? "resolved" : "open";

  return (
    <div>
      <h1 className="serif text-4xl font-semibold tracking-tight">Messages</h1>
      <p className="mt-2 text-sm text-[color:var(--muted)]">
        Submissions from the public contact form.
      </p>

      <nav className="mt-6 flex gap-2 border-b border-[color:var(--border)] pb-3">
        {tabs.map((t) => (
          <a
            key={t.key}
            href={t.href}
            className={
              "rounded-md px-3 py-1.5 text-sm " +
              (activeKey === t.key
                ? "bg-[color:var(--muted-soft)] text-[color:var(--foreground)]"
                : "text-[color:var(--muted)] hover:bg-[color:var(--muted-soft)]")
            }
          >
            {t.label}
          </a>
        ))}
      </nav>

      {messages.length === 0 ? (
        <p className="mt-10 text-sm text-[color:var(--muted)]">
          No messages in this view.
        </p>
      ) : (
        <ul className="mt-6 space-y-4">
          {messages.map((m) => (
            <li
              key={m.id}
              id={`message-${m.id}`}
              className="scroll-mt-28 rounded-2xl border border-[color:var(--border)] bg-white p-5 target:border-[color:var(--accent)] target:ring-2 target:ring-[color:var(--accent-soft)]"
            >
              <div className="flex flex-wrap items-center gap-2 text-xs text-[color:var(--muted)]">
                <span className="rounded-full bg-[color:var(--accent-soft)] px-2.5 py-1 text-[color:var(--accent)]">
                  {categoryLabel(m.category)}
                </span>
                <span>{fmtDate(m.created_at)}</span>
                {m.resolved && (
                  <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-emerald-800">
                    Resolved
                  </span>
                )}
                {m.page_ref && (
                  <span>
                    ref:{" "}
                    <code className="text-[color:var(--foreground)]">
                      {m.page_ref}
                    </code>
                  </span>
                )}
              </div>
              <div className="mt-3 text-sm">
                {(m.name || m.email) && (
                  <p className="text-[color:var(--muted)]">
                    From: {m.name ?? "(no name)"}
                    {m.email && (
                      <>
                        {" "}
                        ·{" "}
                        <a
                          href={`mailto:${m.email}`}
                          className="text-[color:var(--accent)] underline"
                        >
                          {m.email}
                        </a>
                      </>
                    )}
                  </p>
                )}
                <p className="mt-2 whitespace-pre-line leading-relaxed text-[color:var(--foreground)]">
                  {m.body}
                </p>
              </div>
              <form action={toggleResolved} className="mt-4">
                <input type="hidden" name="id" value={m.id} />
                <input
                  type="hidden"
                  name="resolved"
                  value={m.resolved ? "false" : "true"}
                />
                <button
                  type="submit"
                  className="inline-flex h-9 items-center rounded-full border border-[color:var(--border)] px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
                >
                  {m.resolved ? "Reopen" : "Mark resolved"}
                </button>
              </form>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
