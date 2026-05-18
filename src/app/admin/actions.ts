"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { requireAdmin } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import {
  fetchYouTubeSnapshots,
  parseHandleInput,
  resolveHandleToChannelId,
  slugifyName,
} from "@/lib/youtube";

function parseCsv(value: FormDataEntryValue | null): string[] {
  return String(value ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function sanitizeFilename(name: string) {
  return name
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9_.-]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-+|-+$/g, "")
    .toLowerCase();
}

async function uniqueSlug(baseName: string, table: "channels" | "studies") {
  const supabase = createSupabaseServiceClient();
  const base = slugifyName(baseName) || table.slice(0, -1);
  let slug = base;
  let n = 2;

  while (true) {
    const { data, error } = await supabase
      .from(table)
      .select("id")
      .eq("slug", slug)
      .maybeSingle();
    if (error) throw error;
    if (!data) return slug;
    const suffix = `-${n++}`;
    slug = `${base.slice(0, 80 - suffix.length).replace(/-+$/g, "")}${suffix}`;
  }
}

async function refreshLatestView() {
  const supabase = createSupabaseServiceClient();
  const { error } = await supabase.rpc("refresh_channel_stats_latest");
  if (error) throw error;
}

export async function setChannelFeatured(id: string, value: boolean) {
  await requireAdmin();
  const { error } = await createSupabaseServiceClient()
    .from("channels")
    .update({ featured: value })
    .eq("id", id);
  if (error) throw error;
  revalidatePath("/admin/channels");
  revalidatePath("/channels");
  revalidatePath("/");
}

export async function setChannelActive(id: string, value: boolean) {
  await requireAdmin();
  const { error } = await createSupabaseServiceClient()
    .from("channels")
    .update({ is_active: value })
    .eq("id", id);
  if (error) throw error;
  revalidatePath("/admin/channels");
  revalidatePath("/channels");
  revalidatePath("/");
}

export async function deleteChannel(id: string) {
  await requireAdmin();
  const { error } = await createSupabaseServiceClient()
    .from("channels")
    .delete()
    .eq("id", id);
  if (error) throw error;
  revalidatePath("/admin/channels");
  revalidatePath("/channels");
  revalidatePath("/");
}

export async function addChannelByInput(rawInput: string) {
  await requireAdmin();
  const parsed = parseHandleInput(rawInput);
  if (!parsed) throw new Error("Enter a YouTube handle, URL, or channel ID.");

  const youtubeId =
    parsed.kind === "id"
      ? parsed.id
      : await resolveHandleToChannelId(parsed.handleSlug);
  if (!youtubeId) throw new Error("Could not resolve that YouTube handle.");

  const supabase = createSupabaseServiceClient();
  const { data: existing, error: existingError } = await supabase
    .from("channels")
    .select("slug, name")
    .eq("youtube_channel_id", youtubeId)
    .maybeSingle();
  if (existingError) throw existingError;
  if (existing) {
    redirect(`/admin/channels?duplicate=${existing.slug}`);
  }

  const [snapshot] = await fetchYouTubeSnapshots([youtubeId]);
  if (!snapshot) throw new Error("YouTube did not return that channel.");

  const slug = await uniqueSlug(snapshot.name, "channels");
  const handle = parsed.kind === "handle" ? parsed.handle : null;

  const { data: channel, error } = await supabase
    .from("channels")
    .insert({
      youtube_channel_id: snapshot.id,
      name: snapshot.name,
      slug,
      channel_type: null,
      description: snapshot.description,
      country: snapshot.country,
      language: snapshot.defaultLanguage,
      thumbnail_url: snapshot.thumbnailUrl,
      created_at_youtube: snapshot.publishedAt,
      handle,
    })
    .select("id, slug")
    .single();
  if (error) throw error;

  const { error: statsError } = await supabase.from("channel_stats").insert({
    channel_id: channel.id,
    subscribers: snapshot.subscribers,
    total_views: snapshot.totalViews,
    video_count: snapshot.videoCount,
  });
  if (statsError) throw statsError;

  await refreshLatestView();
  revalidatePath("/admin/channels");
  revalidatePath("/channels");
  revalidatePath("/");
  redirect(`/admin/channels?added=${channel.slug}`);
}

export async function setChannelType(id: string, value: string) {
  await requireAdmin();
  const { error } = await createSupabaseServiceClient()
    .from("channels")
    .update({ channel_type: value || null })
    .eq("id", id);
  if (error) throw error;
  revalidatePath("/admin/channels");
  revalidatePath("/channels");
  revalidatePath("/");
}

export async function updateChannelDetails(id: string, formData: FormData) {
  await requireAdmin();
  const get = (key: string) => {
    const value = String(formData.get(key) ?? "").trim();
    return value || null;
  };
  const supabase = createSupabaseServiceClient();
  const base = {
    channel_type: get("channel_type"),
    state: get("state"),
    city: get("city"),
    owned_by: get("owned_by"),
    handle: get("handle"),
    featured: formData.get("featured") === "on",
    is_active: formData.get("is_active") === "on",
  };
  const withOverrides = {
    ...base,
    country_manual: get("country_manual"),
    language_manual: get("language_manual"),
  };

  let { data, error } = await supabase
    .from("channels")
    .update(withOverrides)
    .eq("id", id)
    .select("slug")
    .single();

  // Fallback: migration 0006 (country_manual/language_manual) hasn't been
  // applied yet. Retry without the override columns so saves still work.
  if (error && /country_manual|language_manual/.test(error.message)) {
    ({ data, error } = await supabase
      .from("channels")
      .update(base)
      .eq("id", id)
      .select("slug")
      .single());
  }
  if (error) throw error;
  if (!data) throw new Error("Channel not found.");
  revalidatePath("/admin/channels");
  revalidatePath(`/admin/channels/${data.slug}/edit`);
  revalidatePath(`/channels/${data.slug}`);
  revalidatePath("/channels");
  revalidatePath("/");
  redirect(`/admin/channels?updated=${data.slug}`);
}

export async function setStudyFeatured(id: string, value: boolean) {
  await requireAdmin();
  const { error } = await createSupabaseServiceClient()
    .from("studies")
    .update({ featured: value })
    .eq("id", id);
  if (error) throw error;
  revalidatePath("/admin/studies");
  revalidatePath("/studies");
  revalidatePath("/");
}

export async function deleteStudy(id: string) {
  await requireAdmin();
  const { error } = await createSupabaseServiceClient()
    .from("studies")
    .delete()
    .eq("id", id);
  if (error) throw error;
  revalidatePath("/admin/studies");
  revalidatePath("/studies");
  revalidatePath("/");
}

export async function createStudy(formData: FormData) {
  await requireAdmin();
  const title = String(formData.get("title") ?? "").trim();
  if (!title) throw new Error("Title is required.");

  const file = formData.get("pdf");
  if (!(file instanceof File) || file.size === 0) {
    throw new Error("PDF file is required.");
  }
  if (file.type !== "application/pdf" || file.size > 25 * 1024 * 1024) {
    throw new Error("Upload a PDF file no larger than 25MB.");
  }

  const supabase = createSupabaseServiceClient();
  const slug = await uniqueSlug(title, "studies");
  const filename = sanitizeFilename(file.name) || "study.pdf";
  const pdfPath = `${slug}/${filename}`;
  const { error: uploadError } = await supabase.storage
    .from("studies")
    .upload(pdfPath, file, { contentType: "application/pdf", upsert: false });
  if (uploadError) throw uploadError;

  const yearValue = String(formData.get("year") ?? "").trim();
  const base = {
    slug,
    title,
    authors: parseCsv(formData.get("authors")),
    year: yearValue ? Number(yearValue) : null,
    source: String(formData.get("source") ?? "").trim() || null,
    abstract: String(formData.get("abstract") ?? "").trim() || null,
    tags: parseCsv(formData.get("tags")),
    featured: formData.get("featured") === "on",
    pdf_path: pdfPath,
  };
  const extras = {
    findings: parseLines(formData.get("findings")),
    limitations: String(formData.get("limitations") ?? "").trim() || null,
    flagged_problematic: formData.get("flagged_problematic") === "on",
    flag_reason: String(formData.get("flag_reason") ?? "").trim() || null,
    context_note: String(formData.get("context_note") ?? "").trim() || null,
  };
  let { error } = await supabase.from("studies").insert({ ...base, ...extras });
  if (error && /findings|limitations|flagged_problematic|flag_reason|context_note/.test(error.message)) {
    ({ error } = await supabase.from("studies").insert(base));
  }
  if (error) throw error;

  revalidatePath("/admin/studies");
  revalidatePath("/studies");
  revalidatePath("/");
  redirect(`/admin/studies?added=${slug}`);
}

function parseLines(value: FormDataEntryValue | null): string[] {
  return String(value ?? "")
    .split(/\r?\n/)
    .map((line) => line.replace(/^[-*\s]+/, "").trim())
    .filter(Boolean);
}

export async function updateStudy(id: string, formData: FormData) {
  await requireAdmin();
  const yearValue = String(formData.get("year") ?? "").trim();
  const supabase = createSupabaseServiceClient();
  const base = {
    title: String(formData.get("title") ?? "").trim(),
    authors: parseCsv(formData.get("authors")),
    year: yearValue ? Number(yearValue) : null,
    source: String(formData.get("source") ?? "").trim() || null,
    abstract: String(formData.get("abstract") ?? "").trim() || null,
    tags: parseCsv(formData.get("tags")),
    featured: formData.get("featured") === "on",
  };
  const extras = {
    findings: parseLines(formData.get("findings")),
    limitations: String(formData.get("limitations") ?? "").trim() || null,
    flagged_problematic: formData.get("flagged_problematic") === "on",
    flag_reason: String(formData.get("flag_reason") ?? "").trim() || null,
    context_note: String(formData.get("context_note") ?? "").trim() || null,
  };
  let { data, error } = await supabase
    .from("studies")
    .update({ ...base, ...extras })
    .eq("id", id)
    .select("slug")
    .single();
  if (error && /findings|limitations|flagged_problematic|flag_reason|context_note/.test(error.message)) {
    ({ data, error } = await supabase
      .from("studies")
      .update(base)
      .eq("id", id)
      .select("slug")
      .single());
  }
  if (error) throw error;
  if (!data) throw new Error("Study not found.");
  revalidatePath("/admin/studies");
  revalidatePath(`/admin/studies/${data.slug}/edit`);
  revalidatePath(`/studies/${data.slug}`);
  revalidatePath("/studies");
  revalidatePath("/");
  redirect(`/admin/studies?updated=${data.slug}`);
}

export async function refreshStatsNow() {
  await requireAdmin();
  const supabase = createSupabaseServiceClient();
  const { data: channels, error } = await supabase
    .from("channels")
    .select("id, youtube_channel_id")
    .not("youtube_channel_id", "is", null);
  if (error) throw error;

  const snapshots = await fetchYouTubeSnapshots(
    (channels ?? []).map((channel) => channel.youtube_channel_id),
  );
  const byYtId = new Map((channels ?? []).map((c) => [c.youtube_channel_id, c.id]));

  for (const snapshot of snapshots) {
    const channelId = byYtId.get(snapshot.id);
    if (!channelId) continue;

    const { error: statsError } = await supabase.from("channel_stats").insert({
      channel_id: channelId,
      subscribers: snapshot.subscribers,
      total_views: snapshot.totalViews,
      video_count: snapshot.videoCount,
    });
    if (statsError) throw statsError;

    const update: Record<string, string> = {};
    if (snapshot.description) update.description = snapshot.description;
    if (snapshot.country) update.country = snapshot.country;
    if (snapshot.defaultLanguage) update.language = snapshot.defaultLanguage;
    if (snapshot.thumbnailUrl) update.thumbnail_url = snapshot.thumbnailUrl;
    if (Object.keys(update).length > 0) {
      const { error: updateError } = await supabase
        .from("channels")
        .update(update)
        .eq("id", channelId);
      if (updateError) throw updateError;
    }
  }

  await refreshLatestView();
  revalidatePath("/admin");
  revalidatePath("/admin/channels");
  revalidatePath("/admin/refresh");
  revalidatePath("/channels");
  revalidatePath("/");
  redirect("/admin/refresh?refreshed=1");
}
