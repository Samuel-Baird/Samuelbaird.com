import { redirect } from "next/navigation";

type SearchParams = { slugs?: string };

// Premium is gone: everything that lived here is free and now sits at /compare.
// Old links and bookmarks keep working.
export default async function PremiumPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const { slugs } = await searchParams;
  const qs = slugs ? `?slugs=${encodeURIComponent(slugs)}` : "";
  redirect(`/compare${qs}`);
}
