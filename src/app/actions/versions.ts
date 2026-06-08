"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { requireAdmin } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { slugifyName } from "@/lib/youtube";

function str(value: FormDataEntryValue | null): string {
  return String(value ?? "").trim();
}

function strOrNull(value: FormDataEntryValue | null): string | null {
  return str(value) || null;
}

function intOrNull(value: FormDataEntryValue | null): number | null {
  const raw = str(value);
  if (!raw) return null;
  const n = Number(raw);
  return Number.isFinite(n) ? Math.trunc(n) : null;
}

async function uniqueDocumentSlug(baseName: string, exceptId?: string) {
  const supabase = createSupabaseServiceClient();
  const base = slugifyName(baseName) || "document";
  let slug = base;
  let n = 2;
  while (true) {
    const { data, error } = await supabase
      .from("changelog_documents")
      .select("id")
      .eq("slug", slug)
      .maybeSingle();
    if (error) throw error;
    if (!data || data.id === exceptId) return slug;
    const suffix = `-${n++}`;
    slug = `${base.slice(0, 80 - suffix.length).replace(/-+$/g, "")}${suffix}`;
  }
}

function revalidateDocument(slug: string) {
  revalidatePath("/versions");
  revalidatePath(`/versions/${slug}`);
  revalidatePath("/admin/versions");
  revalidatePath(`/admin/versions/${slug}/edit`);
}

// ---------------------------------------------------------------------------
// Documents
// ---------------------------------------------------------------------------
export async function createChangelogDocument(formData: FormData) {
  await requireAdmin();
  const title = str(formData.get("title"));
  if (!title) throw new Error("Title is required.");

  const supabase = createSupabaseServiceClient();
  const providedSlug = str(formData.get("slug"));
  const slug = await uniqueDocumentSlug(providedSlug || title);

  const { error } = await supabase.from("changelog_documents").insert({
    slug,
    title,
    summary: strOrNull(formData.get("summary")),
    category: strOrNull(formData.get("category")),
  });
  if (error) throw error;

  revalidateDocument(slug);
  redirect(`/admin/versions/${slug}/edit`);
}

export async function updateChangelogDocument(id: string, formData: FormData) {
  await requireAdmin();
  const title = str(formData.get("title"));
  if (!title) throw new Error("Title is required.");

  const supabase = createSupabaseServiceClient();
  const slug = await uniqueDocumentSlug(str(formData.get("slug")) || title, id);

  const { error } = await supabase
    .from("changelog_documents")
    .update({
      title,
      slug,
      summary: strOrNull(formData.get("summary")),
      category: strOrNull(formData.get("category")),
    })
    .eq("id", id);
  if (error) throw error;

  revalidateDocument(slug);
  redirect(`/admin/versions/${slug}/edit`);
}

export async function deleteChangelogDocument(id: string) {
  await requireAdmin();
  const { error } = await createSupabaseServiceClient()
    .from("changelog_documents")
    .delete()
    .eq("id", id);
  if (error) throw error;
  revalidatePath("/versions");
  revalidatePath("/admin/versions");
  redirect("/admin/versions");
}

// ---------------------------------------------------------------------------
// Versions
// ---------------------------------------------------------------------------
export async function createChangelogVersion(
  documentId: string,
  docSlug: string,
  formData: FormData,
) {
  await requireAdmin();
  const label = str(formData.get("label"));
  if (!label) throw new Error("Version label is required.");

  const supabase = createSupabaseServiceClient();
  const { count, error: countError } = await supabase
    .from("changelog_versions")
    .select("id", { count: "exact", head: true })
    .eq("document_id", documentId);
  if (countError) throw countError;

  const { error } = await supabase.from("changelog_versions").insert({
    document_id: documentId,
    label,
    published_on: strOrNull(formData.get("published_on")),
    ordinal: intOrNull(formData.get("ordinal")) ?? count ?? 0,
    source_type: str(formData.get("source_type")) || "markdown",
    source_url: strOrNull(formData.get("source_url")),
    confidence: strOrNull(formData.get("confidence")),
  });
  if (error) throw error;
  revalidateDocument(docSlug);
}

export async function updateChangelogVersion(
  id: string,
  docSlug: string,
  formData: FormData,
) {
  await requireAdmin();
  const label = str(formData.get("label"));
  if (!label) throw new Error("Version label is required.");

  const { error } = await createSupabaseServiceClient()
    .from("changelog_versions")
    .update({
      label,
      published_on: strOrNull(formData.get("published_on")),
      ordinal: intOrNull(formData.get("ordinal")) ?? 0,
      source_type: str(formData.get("source_type")) || "markdown",
      source_url: strOrNull(formData.get("source_url")),
      confidence: strOrNull(formData.get("confidence")),
    })
    .eq("id", id);
  if (error) throw error;
  revalidateDocument(docSlug);
}

export async function deleteChangelogVersion(id: string, docSlug: string) {
  await requireAdmin();
  const { error } = await createSupabaseServiceClient()
    .from("changelog_versions")
    .delete()
    .eq("id", id);
  if (error) throw error;
  revalidateDocument(docSlug);
}

// ---------------------------------------------------------------------------
// Sections
// ---------------------------------------------------------------------------
export async function createChangelogSection(
  versionId: string,
  docSlug: string,
  formData: FormData,
) {
  await requireAdmin();
  const supabase = createSupabaseServiceClient();
  const { count, error: countError } = await supabase
    .from("changelog_sections")
    .select("id", { count: "exact", head: true })
    .eq("version_id", versionId);
  if (countError) throw countError;

  const { error } = await supabase.from("changelog_sections").insert({
    version_id: versionId,
    heading: strOrNull(formData.get("heading")),
    body_markdown: strOrNull(formData.get("body_markdown")),
    ordinal: intOrNull(formData.get("ordinal")) ?? count ?? 0,
  });
  if (error) throw error;
  revalidateDocument(docSlug);
}

export async function updateChangelogSection(
  id: string,
  docSlug: string,
  formData: FormData,
) {
  await requireAdmin();
  const { error } = await createSupabaseServiceClient()
    .from("changelog_sections")
    .update({
      heading: strOrNull(formData.get("heading")),
      body_markdown: strOrNull(formData.get("body_markdown")),
      ordinal: intOrNull(formData.get("ordinal")) ?? 0,
    })
    .eq("id", id);
  if (error) throw error;
  revalidateDocument(docSlug);
}

export async function deleteChangelogSection(id: string, docSlug: string) {
  await requireAdmin();
  const { error } = await createSupabaseServiceClient()
    .from("changelog_sections")
    .delete()
    .eq("id", id);
  if (error) throw error;
  revalidateDocument(docSlug);
}
