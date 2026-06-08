import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CompareView } from "@/components/compare-view";
import { alignSections } from "@/lib/align-sections";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import type {
  ChangelogDocument,
  ChangelogSection,
  ChangelogVersion,
} from "@/lib/types";

type RouteParams = { slug: string };
type SearchParams = { a?: string; b?: string };

export async function generateMetadata({
  params,
  searchParams,
}: {
  params: Promise<RouteParams>;
  searchParams: Promise<SearchParams>;
}): Promise<Metadata> {
  const { slug } = await params;
  const { a, b } = await searchParams;
  const supabase = await createSupabaseServerClient();
  const { data: doc } = await supabase
    .from("changelog_documents")
    .select("title")
    .eq("slug", slug)
    .maybeSingle();
  if (!doc || !a || !b) return { title: "Compare" };
  const [{ data: va }, { data: vb }] = await Promise.all([
    supabase
      .from("changelog_versions")
      .select("label")
      .eq("id", a)
      .maybeSingle(),
    supabase
      .from("changelog_versions")
      .select("label")
      .eq("id", b)
      .maybeSingle(),
  ]);
  return {
    title: `${doc.title}: ${va?.label ?? "?"} vs ${vb?.label ?? "?"}`,
  };
}

export default async function ComparePage({
  params,
  searchParams,
}: {
  params: Promise<RouteParams>;
  searchParams: Promise<SearchParams>;
}) {
  const { slug } = await params;
  const { a, b } = await searchParams;

  if (!a || !b) {
    return (
      <div className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
        <Link
          href={`/versions/${slug}`}
          className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
        >
          ← Back
        </Link>
        <p className="mt-8 text-[color:var(--muted)]">
          Select two editions to compare from the document page.
        </p>
      </div>
    );
  }

  const supabase = await createSupabaseServerClient();

  const [
    { data: docData, error: docError },
    { data: vaData, error: vaError },
    { data: vbData, error: vbError },
  ] = await Promise.all([
    supabase
      .from("changelog_documents")
      .select("*")
      .eq("slug", slug)
      .maybeSingle(),
    supabase.from("changelog_versions").select("*").eq("id", a).maybeSingle(),
    supabase.from("changelog_versions").select("*").eq("id", b).maybeSingle(),
  ]);

  if (docError) throw docError;
  if (vaError) throw vaError;
  if (vbError) throw vbError;
  if (!docData || !vaData || !vbData) notFound();

  const doc = docData as ChangelogDocument;
  const va = vaData as ChangelogVersion;
  const vb = vbData as ChangelogVersion;

  if (va.document_id !== doc.id || vb.document_id !== doc.id) notFound();

  const [{ data: sectionsA, error: errA }, { data: sectionsB, error: errB }] =
    await Promise.all([
      supabase
        .from("changelog_sections")
        .select("*")
        .eq("version_id", va.id)
        .order("ordinal", { ascending: true }),
      supabase
        .from("changelog_sections")
        .select("*")
        .eq("version_id", vb.id)
        .order("ordinal", { ascending: true }),
    ]);
  if (errA) throw errA;
  if (errB) throw errB;

  const pairs = alignSections(
    (sectionsA ?? []) as ChangelogSection[],
    (sectionsB ?? []) as ChangelogSection[],
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 sm:py-14">
      <Link
        href={`/versions/${slug}`}
        className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
      >
        ← {doc.title}
      </Link>
      <h1 className="serif mt-4 text-2xl font-semibold tracking-tight sm:text-3xl">
        {doc.title}
      </h1>
      <CompareView va={va} vb={vb} pairs={pairs} />
    </div>
  );
}
