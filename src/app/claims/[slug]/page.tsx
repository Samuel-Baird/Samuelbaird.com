import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/breadcrumbs";
import { Tag } from "@/components/tag";
import { getClaimBySlug, getClaimReachMap, getPublishedClaims } from "@/lib/data";
import type { Claim } from "@/lib/types";

type RouteParams = { slug: string };

export async function generateMetadata({
  params,
}: {
  params: Promise<RouteParams>;
}): Promise<Metadata> {
  const { slug } = await params;
  const claim = await getClaimBySlug(slug);
  if (!claim) return { title: "Claim not found" };
  return {
    title: claim.title,
    description: claim.claim_text.slice(0, 200),
    alternates: { canonical: `/claims/${slug}` },
  };
}

export default async function ClaimDetailPage({
  params,
}: {
  params: Promise<RouteParams>;
}) {
  const { slug } = await params;
  const claim = await getClaimBySlug(slug);
  if (!claim) notFound();

  const [reachMap, allClaims] = await Promise.all([
    getClaimReachMap([claim.id]),
    getPublishedClaims(),
  ]);
  const reach = reachMap[claim.id] ?? null;
  const related = relatedClaims(claim, allClaims);

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <Breadcrumbs
        items={[{ label: "Claims", href: "/claims" }, { label: claim.title }]}
      />

      <div className="mt-6 flex flex-wrap items-center gap-2">
        {claim.topic_tags.map((t) => (
          <Tag key={t} ink="accent">
            {t}
          </Tag>
        ))}
      </div>

      <h1 className="serif mt-4 max-w-3xl text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">
        {claim.title}
      </h1>

      <div className="mt-10 lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-14">
        <div className="min-w-0">
          <section>
            <h2 className="small-caps text-xs font-medium text-[color:var(--oxblood)]">
              The claim
            </h2>
            <blockquote className="mt-3 max-w-2xl border-l-2 border-[color:var(--oxblood)]/40 pl-5 text-base leading-relaxed text-[color:var(--foreground)] sm:text-lg">
              {claim.claim_text}
            </blockquote>
            <p className="mt-3 max-w-2xl text-xs leading-relaxed text-[color:var(--muted)]">
              Stated as strongly as it can fairly be put, in the terms critics
              use — not a softened version chosen to be easy to answer.
            </p>
          </section>

          <section className="mt-12">
            <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
              The response
            </h2>
            <div className="mt-3 max-w-2xl space-y-4 text-base leading-relaxed text-[color:var(--foreground)] sm:text-lg">
              {claim.response
                .split(/\n{2,}/)
                .map((para) => para.trim())
                .filter(Boolean)
                .map((para, i) => (
                  <p key={i} className="whitespace-pre-line">
                    {para}
                  </p>
                ))}
            </div>
          </section>

          {claim.response_video_url && (
            <section className="mt-12 max-w-2xl">
              <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
                Video response
              </h2>
              <a
                href={claim.response_video_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 inline-flex h-11 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-5 text-sm font-medium hover:bg-[color:var(--muted-soft)]"
              >
                Watch the response ↗
              </a>
            </section>
          )}

          <p className="mt-12 text-xs text-[color:var(--muted)]">
            <Link
              href={`/contact?category=correction&ref=${encodeURIComponent(
                `claim:${claim.slug}`,
              )}`}
              className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
            >
              Report an error
            </Link>{" "}
            on this response.
          </p>
        </div>

        <aside className="mt-12 space-y-8 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-10">
          <section>
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Sources
            </h2>
            <ul className="mt-3 space-y-3">
              {claim.sources.map((source, i) => (
                <li key={i} className="text-sm leading-relaxed">
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                  >
                    {source.title}
                  </a>
                  {source.note && (
                    <span className="block text-[color:var(--muted)]">
                      {source.note}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </section>

          {reach && reach.videoCount > 0 && (
            <section>
              <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
                Where this comes up
              </h2>
              {/* Counts only, never the videos themselves — linking them would
                  send traffic to the channels making the claim. */}
              <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
                Documented in{" "}
                <span className="tabular-nums text-[color:var(--foreground)]">
                  {reach.videoCount}
                </span>{" "}
                {reach.videoCount === 1 ? "video" : "videos"} across{" "}
                <span className="tabular-nums text-[color:var(--foreground)]">
                  {reach.channelCount}
                </span>{" "}
                {reach.channelCount === 1 ? "channel" : "channels"} tracked by
                Latter-day Stats
                {reach.firstSeenYear != null && (
                  <>
                    , earliest in{" "}
                    <span className="serif-onum text-[color:var(--foreground)]">
                      {reach.firstSeenYear}
                    </span>
                  </>
                )}
                .
              </p>
            </section>
          )}

          {related.length > 0 && (
            <section>
              <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
                Related claims
              </h2>
              <ul className="mt-3 space-y-3">
                {related.map((r) => (
                  <li key={r.id}>
                    <Link
                      href={`/claims/${r.slug}`}
                      className="serif text-sm font-semibold leading-snug tracking-tight text-[color:var(--foreground)] hover:text-[color:var(--accent)]"
                    >
                      {r.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </aside>
      </div>
    </div>
  );
}

// Overlap on topic tags, most shared tags first. Small-N by design: the
// library is curated, so a full similarity model would be overkill.
function relatedClaims(claim: Claim, all: Claim[]): Claim[] {
  const own = new Set(claim.topic_tags);
  if (own.size === 0) return [];
  return all
    .filter((c) => c.id !== claim.id)
    .map((c) => ({
      claim: c,
      shared: c.topic_tags.filter((t) => own.has(t)).length,
    }))
    .filter((x) => x.shared > 0)
    .sort((a, b) => b.shared - a.shared)
    .slice(0, 5)
    .map((x) => x.claim);
}
