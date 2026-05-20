import { redirect } from "next/navigation";

type SearchParams = { slugs?: string };

export default async function ComparePage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const { slugs } = await searchParams;
  const qs = slugs ? `?slugs=${encodeURIComponent(slugs)}` : "";
  redirect(`/premium${qs}`);
}
