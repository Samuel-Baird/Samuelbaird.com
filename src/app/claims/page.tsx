import type { Metadata } from "next";
import Link from "next/link";
import { ClaimsExplorer, type ClaimSortValue } from "@/components/claims-explorer";
import { DeseretTitle } from "@/components/deseret-title";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";
import {
  getAllClaimTopicTags,
  getClaimReachMap,
  getPublishedClaims,
} from "@/lib/data";

export const metadata: Metadata = {
  title: "Claim library",
  description:
    "Common criticisms of the Church of Jesus Christ of Latter-day Saints, each stated at its strongest and answered with cited sources.",
  alternates: { canonical: "/claims" },
};

type SearchParams = {
  q?: string;
  tag?: string | string[];
  sort?: string;
};

function parseSort(value: string | undefined): ClaimSortValue {
  if (value === "reach" || value === "title") return value;
  return "recent";
}

function parseTags(value: SearchParams["tag"]): string[] {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

export default async function ClaimsPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  const q = (params.q ?? "").trim();
  const tags = parseTags(params.tag);
  const sort = parseSort(params.sort);

  const [claimsResult, allTags] = await Promise.all([
    getPublishedClaims({ query: q || undefined, tags: tags.length ? tags : undefined, sort }),
    getAllClaimTopicTags(),
  ]);

  const reach = await getClaimReachMap(claimsResult.map((c) => c.id));

  // "Most repeated" needs the occurrence counts, which the data layer fetches
  // separately, so it is applied here rather than in getPublishedClaims.
  const claims =
    sort === "reach"
      ? claimsResult
          .slice()
          .sort(
            (a, b) =>
              (reach[b.id]?.videoCount ?? 0) - (reach[a.id]?.videoCount ?? 0),
          )
      : claimsResult;

  return (
    <div className="w-full px-5 py-14 sm:px-8 sm:py-20">
      <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
        Claims
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        <DeseretTitle text="Claim library" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        Criticisms that come up again and again, each stated as strongly as it
        can fairly be put, then answered from primary sources. Every citation is
        checked against the original before a claim is published here.
      </p>

      <div className="mt-10">
        <ClaimsExplorer
          claims={claims}
          tags={allTags}
          reach={reach}
          initial={{ q, tags, sort }}
        />
      </div>

      <aside className="mt-12 grid gap-6 lg:grid-cols-2">
        <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--accent-soft)]/40 p-6 text-sm sm:p-8">
          <p className="serif text-lg font-semibold tracking-tight">
            How these are written
          </p>
          <p className="mt-2 leading-relaxed text-[color:var(--muted)]">
            A claim is only published with at least one source, and the response
            quotes the record rather than paraphrasing it. Where the honest
            answer is &ldquo;the sources disagree&rdquo; or &ldquo;this is
            unresolved,&rdquo; it says so. Read the{" "}
            <Link
              href="/methodology"
              className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
            >
              methodology
            </Link>{" "}
            for how sourcing is graded across the site.
          </p>
        </div>
        <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 text-sm sm:p-8">
          <p className="serif text-lg font-semibold tracking-tight">
            Think a response is wrong?
          </p>
          <p className="mt-2 leading-relaxed text-[color:var(--muted)]">
            Corrections are welcome and get read. Email{" "}
            <a
              href={mailto("Claim correction")}
              className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
            >
              {CONTACT_EMAIL}
            </a>{" "}
            with the claim and what the sources actually say.
          </p>
        </div>
      </aside>
    </div>
  );
}
