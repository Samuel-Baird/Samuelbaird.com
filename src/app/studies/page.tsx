import type { Metadata } from "next";
import { StudiesExplorer } from "@/components/studies-explorer";
import { getCurrentUser } from "@/lib/auth";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";
import {
  getAllStudyTags,
  getBookmarkSetForUser,
  getStudies,
  getUpvoteCountMap,
  getUpvoteSetForUser,
  type StudySort,
} from "@/lib/data";

export const metadata: Metadata = {
  title: "Studies",
  description:
    "Academic studies and research relating to the Latter-day Saint community.",
};

type SearchParams = {
  q?: string;
  tag?: string | string[];
  sort?: string;
};

function parseSort(value: string | undefined): StudySort {
  if (value === "year" || value === "upvotes") return value;
  return "categories";
}

function parseTags(value: SearchParams["tag"]): string[] {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

export default async function StudiesPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  const q = (params.q ?? "").trim();
  const tags = parseTags(params.tag);
  const sort = parseSort(params.sort);

  const [studies, allTags, auth] = await Promise.all([
    getStudies({ query: q || undefined, tags: tags.length ? tags : undefined, sort }),
    getAllStudyTags(),
    getCurrentUser(),
  ]);

  const [bookmarks, upvotes, upvoteCounts] = await Promise.all([
    auth
      ? getBookmarkSetForUser(auth.user.id)
      : Promise.resolve({ channels: new Set<string>(), studies: new Set<string>() }),
    auth
      ? getUpvoteSetForUser(auth.user.id)
      : Promise.resolve({ channels: new Set<string>(), studies: new Set<string>() }),
    getUpvoteCountMap(
      "study",
      studies.map((s) => s.id),
    ),
  ]);

  const upvoteCountsObj: Record<string, number> = {};
  for (const [k, v] of upvoteCounts.entries()) upvoteCountsObj[k] = v;

  return (
    <div className="w-full px-5 py-14 sm:px-8 sm:py-20">
      <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
        Studies
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        Research library
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        Curated academic studies relating to the Latter-day Saint community.
        Search by keyword, filter by topic, and upvote the ones worth sharing.
      </p>

      <div className="mt-10">
        <StudiesExplorer
          studies={studies}
          tags={allTags}
          bookmarkedSet={bookmarks.studies}
          upvotedSet={upvotes.studies}
          upvoteCounts={upvoteCountsObj}
          signedIn={Boolean(auth)}
          initial={{ q, tags, sort }}
        />
      </div>

      <aside className="mt-12 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--accent-soft)]/40 p-6 text-sm text-[color:var(--foreground)] sm:p-8">
        <p className="serif text-lg font-semibold tracking-tight">
          Know a study we should add?
        </p>
        <p className="mt-2 leading-relaxed text-[color:var(--muted)]">
          Email{" "}
          <a
            href={mailto("Add a study")}
            className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
          >
            {CONTACT_EMAIL}
          </a>{" "}
          with a link or PDF — peer-reviewed work and reputable independent
          research are both welcome.
        </p>
      </aside>
    </div>
  );
}
