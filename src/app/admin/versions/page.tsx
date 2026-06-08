import Link from "next/link";
import { deleteChangelogDocument } from "@/app/actions/versions";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import type { ChangelogDocument } from "@/lib/types";

export const dynamic = "force-dynamic";

type DocumentRow = ChangelogDocument & {
  changelog_versions: { count: number }[];
};

export default async function AdminVersionsPage() {
  const { data, error } = await createSupabaseServiceClient()
    .from("changelog_documents")
    .select("*, changelog_versions(count)")
    .order("title", { ascending: true });
  if (error) throw error;
  const documents = (data ?? []) as DocumentRow[];

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="serif text-4xl font-semibold tracking-tight">
          Versions
        </h1>
        <Link
          href="/admin/versions/new"
          className="inline-flex h-10 items-center rounded-full bg-[color:var(--accent)] px-4 text-sm font-medium text-white hover:opacity-90"
        >
          + New document
        </Link>
      </div>

      {documents.length === 0 ? (
        <p className="mt-6 rounded-2xl border border-[color:var(--border)] bg-white p-6 text-sm text-[color:var(--muted)]">
          No documents yet. Create one to start tracking its editions.
        </p>
      ) : (
        <div className="mt-6 overflow-x-auto rounded-2xl border border-[color:var(--border)] bg-white">
          <table className="w-full min-w-[640px] text-sm">
            <thead className="bg-[color:var(--muted-soft)]/60 text-left text-xs uppercase tracking-wider text-[color:var(--muted)]">
              <tr>
                <th className="px-4 py-3">Title</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Editions</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id} className="border-t border-[color:var(--border)]">
                  <td className="px-4 py-3 font-medium">{doc.title}</td>
                  <td className="px-4 py-3 text-[color:var(--muted)]">
                    {doc.category ?? "-"}
                  </td>
                  <td className="px-4 py-3 tabular-nums text-[color:var(--muted)]">
                    {doc.changelog_versions?.[0]?.count ?? 0}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-3">
                      <Link
                        href={`/versions/${doc.slug}`}
                        className="text-xs text-[color:var(--accent)] hover:underline"
                      >
                        View
                      </Link>
                      <Link
                        href={`/admin/versions/${doc.slug}/edit`}
                        className="text-xs text-[color:var(--accent)] hover:underline"
                      >
                        Edit
                      </Link>
                      <form action={deleteChangelogDocument.bind(null, doc.id)}>
                        <button className="text-xs text-red-700 hover:underline">
                          Delete
                        </button>
                      </form>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
