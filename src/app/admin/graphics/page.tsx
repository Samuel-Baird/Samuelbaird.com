import Image from "next/image";
import Link from "next/link";
import { GraphicPostControls } from "@/components/admin/graphic-post-controls";
import { DATASETS, graphicId } from "@/lib/data-explorer";
import { requireAdmin } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import type { GraphicPost } from "@/lib/types";

type Filter = "all" | "posted" | "unposted";

export default async function AdminGraphicsPage({
  searchParams,
}: {
  searchParams: Promise<{ filter?: string }>;
}) {
  await requireAdmin();

  const { filter: rawFilter } = await searchParams;
  const filter: Filter =
    rawFilter === "posted" || rawFilter === "unposted" ? rawFilter : "all";

  const { data, error } = await createSupabaseServiceClient()
    .from("graphic_posts")
    .select("dataset_slug, graphic_id, posted, posted_dates");
  if (error) throw error;

  const statusByKey = new Map<string, GraphicPost>(
    ((data ?? []) as GraphicPost[]).map((row) => [
      `${row.dataset_slug}/${row.graphic_id}`,
      row,
    ]),
  );

  const totalGraphics = DATASETS.reduce((n, d) => n + d.graphics.length, 0);
  const totalPosted = [...statusByKey.values()].filter((s) => s.posted).length;

  const filterHref = (f: Filter) => (f === "all" ? "/admin/graphics" : `/admin/graphics?filter=${f}`);

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="serif text-4xl font-semibold tracking-tight">Graphics</h1>
          <p className="mt-2 text-sm text-[color:var(--muted)]">
            {totalPosted} of {totalGraphics} posted
          </p>
        </div>
        <nav className="flex gap-2">
          {(["all", "unposted", "posted"] as const).map((f) => (
            <Link
              key={f}
              href={filterHref(f)}
              className={
                "rounded-[var(--radius)] border px-3 py-1.5 text-xs font-medium capitalize " +
                (filter === f
                  ? "border-[color:var(--accent)] bg-[color:var(--accent-soft)] text-[color:var(--accent)]"
                  : "border-[color:var(--border)] text-[color:var(--muted)] hover:text-[color:var(--foreground)]")
              }
            >
              {f}
            </Link>
          ))}
        </nav>
      </div>

      <div className="mt-8 space-y-10">
        {DATASETS.filter((d) => d.graphics.length > 0).map((dataset) => {
          const rows = dataset.graphics
            .map((g) => {
              const id = graphicId(g);
              const status = statusByKey.get(`${dataset.slug}/${id}`);
              return { graphic: g, id, posted: status?.posted ?? false, postedDates: status?.posted_dates ?? "" };
            })
            .filter((r) => {
              if (filter === "posted") return r.posted;
              if (filter === "unposted") return !r.posted;
              return true;
            });

          if (rows.length === 0) return null;

          return (
            <section key={dataset.slug}>
              <h2 className="serif text-lg font-semibold tracking-tight">
                <Link
                  href={`/data-explorer/${dataset.slug}/graphics`}
                  className="hover:underline"
                >
                  {dataset.name}
                </Link>
              </h2>
              <div className="mt-3 divide-y divide-[color:var(--border)] rounded-[var(--radius)] border border-[color:var(--border)] bg-white">
                {rows.map(({ graphic, id, posted, postedDates }) => (
                  <div
                    key={id}
                    className="flex flex-wrap items-center gap-4 p-4"
                  >
                    <Link
                      href={`/data-explorer/${dataset.slug}/graphics/${id}`}
                      className="block w-24 shrink-0 overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]"
                    >
                      <Image
                        src={graphic.imageSrc}
                        alt={graphic.alt}
                        width={graphic.width}
                        height={graphic.height}
                        className="h-auto w-full"
                      />
                    </Link>
                    <div className="min-w-[160px] flex-1">
                      <Link
                        href={`/data-explorer/${dataset.slug}/graphics/${id}`}
                        className="text-sm font-medium hover:underline"
                      >
                        {graphic.title}
                      </Link>
                    </div>
                    <div className="w-full sm:w-auto sm:min-w-[320px]">
                      <GraphicPostControls
                        datasetSlug={dataset.slug}
                        graphicId={id}
                        posted={posted}
                        postedDates={postedDates}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}
