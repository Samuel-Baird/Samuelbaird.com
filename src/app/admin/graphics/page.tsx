import Image from "next/image";
import Link from "next/link";
import { GraphicPostControls } from "@/components/admin/graphic-post-controls";
import { LocalTime } from "@/components/admin/local-time";
import { requireAdmin } from "@/lib/auth";
import { DATASETS, graphicId, type Graphic } from "@/lib/data-explorer";
import { getStudiesBySlugs } from "@/lib/data";
import { publishState, type PublishState } from "@/lib/graphic-publish";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { getStudyFolderSlugs, STUDY_GRAPHICS } from "@/lib/study-graphics";
import type { GraphicPost } from "@/lib/types";

type Filter = "all" | "posted" | "unposted" | "hidden" | "scheduled";

const FILTERS: Filter[] = ["all", "hidden", "scheduled", "unposted", "posted"];

type Section = {
  key: string;
  title: string;
  basePath: string;
  graphics: Graphic[];
};

export default async function AdminGraphicsPage({
  searchParams,
}: {
  searchParams: Promise<{ filter?: string }>;
}) {
  await requireAdmin();

  const { filter: rawFilter } = await searchParams;
  // "unpublished" is the pre-0054 name for "hidden"; keep old links working.
  const filter: Filter =
    rawFilter === "unpublished"
      ? "hidden"
      : (FILTERS as string[]).includes(rawFilter ?? "")
        ? (rawFilter as Filter)
        : "all";

  const [{ data, error }, studies] = await Promise.all([
    createSupabaseServiceClient()
      .from("graphic_posts")
      .select("dataset_slug, graphic_id, posted, posted_dates, published, publish_at"),
    getStudiesBySlugs(getStudyFolderSlugs()),
  ]);
  if (error) throw error;

  const statusByKey = new Map<string, GraphicPost>(
    ((data ?? []) as GraphicPost[]).map((row) => [
      `${row.dataset_slug}/${row.graphic_id}`,
      row,
    ]),
  );

  const studiesBySlug = new Map(studies.map((s) => [s.slug, s]));

  const datasetSections: Section[] = DATASETS.filter((d) => d.graphics.length > 0).map((d) => ({
    key: d.slug,
    title: d.name,
    basePath: `/data-explorer/${d.slug}/graphics`,
    graphics: d.graphics,
  }));

  const studySections: Section[] = STUDY_GRAPHICS.filter((e) => e.graphics.length > 0)
    .map((e) => {
      const study = studiesBySlug.get(e.studySlug);
      if (!study) return null;
      return {
        key: e.studySlug,
        title: study.title,
        basePath: `/studies/${e.studySlug}/graphics`,
        graphics: e.graphics,
      };
    })
    .filter((s): s is Section => s !== null);

  const sections = [...datasetSections, ...studySections];

  // One pass over every registry graphic, so the counts and the scheduled
  // queue reflect graphics with no row yet (hidden) as well as stored rows.
  const stateCounts: Record<PublishState, number> = { hidden: 0, scheduled: 0, published: 0 };
  const scheduled: { section: Section; graphic: Graphic; id: string; publishAt: string }[] = [];
  for (const section of sections) {
    for (const g of section.graphics) {
      const id = graphicId(g);
      const status = statusByKey.get(`${section.key}/${id}`);
      const state = publishState(status);
      stateCounts[state] += 1;
      if (state === "scheduled" && status?.publish_at) {
        scheduled.push({ section, graphic: g, id, publishAt: status.publish_at });
      }
    }
  }
  scheduled.sort((a, b) => Date.parse(a.publishAt) - Date.parse(b.publishAt));

  const totalGraphics = sections.reduce((n, s) => n + s.graphics.length, 0);
  const totalPosted = [...statusByKey.values()].filter((s) => s.posted).length;

  const filterHref = (f: Filter) => (f === "all" ? "/admin/graphics" : `/admin/graphics?filter=${f}`);

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="serif text-4xl font-semibold tracking-tight">Graphics</h1>
          <p className="mt-2 text-sm text-[color:var(--muted)]">
            {stateCounts.published} of {totalGraphics} published · {stateCounts.scheduled} scheduled ·{" "}
            {stateCounts.hidden} hidden · {totalPosted} of {totalGraphics} posted
          </p>
        </div>
        <nav className="flex gap-2">
          {FILTERS.map((f) => (
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

      {scheduled.length > 0 && filter === "all" && (
        <section className="mt-8 rounded-[var(--radius)] border border-[color:var(--accent)]/40 bg-[color:var(--accent-soft)]/40 p-4">
          <h2 className="serif text-lg font-semibold tracking-tight">Upcoming</h2>
          <p className="mt-1 text-xs text-[color:var(--muted)]">
            Goes live on the site at these times (your local zone). Line up social posts to match.
          </p>
          <ol className="mt-3 divide-y divide-[color:var(--border)]">
            {scheduled.map(({ section, graphic, id, publishAt }) => (
              <li key={`${section.key}/${id}`} className="flex flex-wrap items-baseline gap-x-4 gap-y-1 py-2 text-sm">
                <LocalTime iso={publishAt} className="w-40 shrink-0 font-medium tabular-nums" />
                <Link href={`${section.basePath}/${id}`} className="min-w-0 flex-1 hover:underline">
                  {graphic.title}
                </Link>
                <span className="text-xs text-[color:var(--muted)]">{section.title}</span>
              </li>
            ))}
          </ol>
        </section>
      )}

      <div className="mt-8 space-y-10">
        {sections.map((section) => {
          const rows = section.graphics
            .map((g) => {
              const id = graphicId(g);
              const status = statusByKey.get(`${section.key}/${id}`);
              return {
                graphic: g,
                id,
                posted: status?.posted ?? false,
                postedDates: status?.posted_dates ?? "",
                published: status?.published ?? false,
                publishAt: status?.publish_at ?? null,
                state: publishState(status),
              };
            })
            .filter((r) => {
              if (filter === "posted") return r.posted;
              if (filter === "unposted") return !r.posted;
              if (filter === "hidden" || filter === "scheduled") return r.state === filter;
              return true;
            });

          if (rows.length === 0) return null;

          return (
            <section key={section.key}>
              <h2 className="serif text-lg font-semibold tracking-tight">
                <Link href={section.basePath} className="hover:underline">
                  {section.title}
                </Link>
              </h2>
              <div className="mt-3 divide-y divide-[color:var(--border)] rounded-[var(--radius)] border border-[color:var(--border)] bg-white">
                {rows.map(({ graphic, id, posted, postedDates, published, publishAt }) => (
                  <div key={id} className="flex flex-wrap items-center gap-4 p-4">
                    <Link
                      href={`${section.basePath}/${id}`}
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
                      <Link href={`${section.basePath}/${id}`} className="text-sm font-medium hover:underline">
                        {graphic.title}
                      </Link>
                    </div>
                    <div className="w-full sm:w-auto sm:min-w-[380px]">
                      <GraphicPostControls
                        datasetSlug={section.key}
                        graphicId={id}
                        posted={posted}
                        postedDates={postedDates}
                        published={published}
                        publishAt={publishAt}
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
