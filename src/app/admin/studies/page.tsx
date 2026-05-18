import Link from "next/link";
import { deleteStudy, setStudyFeatured } from "@/app/admin/actions";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import type { Study } from "@/lib/types";

type SearchParams = { added?: string };

export default async function AdminStudiesPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  const { data, error } = await createSupabaseServiceClient()
    .from("studies")
    .select("*")
    .order("created_at", { ascending: false });
  if (error) throw error;

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="serif text-4xl font-semibold tracking-tight">
            Studies
          </h1>
          {params.added && (
            <p className="mt-2 text-sm text-[color:var(--accent)]">
              Added {params.added}
            </p>
          )}
        </div>
        <Link
          href="/admin/studies/new"
          className="inline-flex h-10 items-center rounded-full bg-[color:var(--accent)] px-4 text-sm font-medium text-white hover:opacity-90"
        >
          + New study
        </Link>
      </div>

      <div className="mt-6 overflow-x-auto rounded-2xl border border-[color:var(--border)] bg-white">
        <table className="w-full min-w-[700px] text-sm">
          <thead className="bg-[color:var(--muted-soft)]/60 text-left text-xs uppercase tracking-wider text-[color:var(--muted)]">
            <tr>
              <th className="px-4 py-3">Title</th>
              <th className="px-4 py-3">Year</th>
              <th className="px-4 py-3">Featured</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {((data ?? []) as Study[]).map((study) => (
              <tr key={study.id} className="border-t border-[color:var(--border)]">
                <td className="px-4 py-3 font-medium">{study.title}</td>
                <td className="px-4 py-3 tabular-nums text-[color:var(--muted)]">
                  {study.year ?? "-"}
                </td>
                <td className="px-4 py-3">
                  <form action={setStudyFeatured.bind(null, study.id, !study.featured)}>
                    <button className="rounded-full border border-[color:var(--border)] px-3 py-1 text-xs hover:bg-[color:var(--muted-soft)]">
                      {study.featured ? "Featured" : "Not featured"}
                    </button>
                  </form>
                </td>
                <td className="px-4 py-3">
                  <div className="flex justify-end gap-3">
                    <Link
                      href={`/studies/${study.slug}`}
                      className="text-xs text-[color:var(--accent)] hover:underline"
                    >
                      View
                    </Link>
                    <form action={deleteStudy.bind(null, study.id)}>
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
    </div>
  );
}
