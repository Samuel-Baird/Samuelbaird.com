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
    .select("slug")
    .eq("youtube_channel_id", youtubeId)
    .maybeSingle();
  if (existingError) throw existingError;
  if (existing) {
    redirect(`/admin/channels?duplicate=${existing.slug}`);
  }

  const [snapshot] = await fetchYouTubeSnapshots([youtubeId]);
  if (!snapshot) throw new Error("YouTube did not return that channel.");

  const handle = parsed.kind === "handle" ? parsed.handle : null;

  // Slug == youtube_channel_id (stable across renames). The before-insert trigger
  // fills it from youtube_channel_id when omitted, but set it explicitly here too.
  const { data: channel, error } = await supabase
    .from("channels")
    .insert({
      youtube_channel_id: snapshot.id,
      slug: snapshot.id,
      handle,
    })
    .select("id, slug")
    .single();
  if (error) throw error;

  const { error: ytError } = await supabase.from("channel_youtube").upsert(
    {
      channel_id: channel.id,
      name: snapshot.name,
      description: snapshot.description,
      country: snapshot.country,
      default_language: snapshot.defaultLanguage,
      thumbnail_url: snapshot.thumbnailUrl,
      created_at_youtube: snapshot.publishedAt,
      last_synced_at: new Date().toISOString(),
      last_sync_status: "ok",
      last_sync_error: null,
    },
    { onConflict: "channel_id" },
  );
  if (ytError) throw ytError;

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

export type SaveResult =
  | { ok: true; warnings: string[] }
  | { ok: false; error: string };

export async function updateChannelDetails(
  id: string,
  _prevState: SaveResult | null,
  formData: FormData,
): Promise<SaveResult> {
  try {
    await requireAdmin();
  } catch {
    return { ok: false, error: "Not authorized." };
  }
  const warnings: string[] = [];
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
  const coreDetails = {
    ...base,
    country_manual: get("country_manual"),
    language_manual: get("language_manual"),
    lds_affiliation_source: get("lds_affiliation_source"),
  };
  const detailsWithoutAffiliationSource = {
    ...base,
    country_manual: get("country_manual"),
    language_manual: get("language_manual"),
  };
  const socialProfiles = {
    facebook_url: get("facebook_url"),
    instagram_url: get("instagram_url"),
    tiktok_url: get("tiktok_url"),
    x_url: get("x_url"),
  };

  let { data, error } = await supabase
    .from("channels")
    .update(coreDetails)
    .eq("id", id)
    .select("slug")
    .single();

  if (error && /lds_affiliation_source/.test(error.message)) {
    warnings.push("LDS affiliation source did not save — migration 0007 not applied.");
    ({ data, error } = await supabase
      .from("channels")
      .update(detailsWithoutAffiliationSource)
      .eq("id", id)
      .select("slug")
      .single());
  }

  if (error && /country_manual|language_manual/.test(error.message)) {
    warnings.push("Country/language overrides did not save — migration 0006 not applied.");
    ({ data, error } = await supabase
      .from("channels")
      .update(base)
      .eq("id", id)
      .select("slug")
      .single());
  }
  if (error) return { ok: false, error: error.message };
  if (!data) return { ok: false, error: "Channel not found." };

  const hasSocialInput = Object.values(socialProfiles).some((v) => v !== null);
  const { error: socialError } = await supabase
    .from("channels")
    .update(socialProfiles)
    .eq("id", id);
  if (
    socialError &&
    /facebook_url|instagram_url|tiktok_url|x_url/.test(socialError.message)
  ) {
    if (hasSocialInput) {
      warnings.push("Social profile URLs did not save — migration 0008 not applied.");
    }
  } else if (socialError) {
    return { ok: false, error: socialError.message };
  }

  revalidatePath("/admin/channels");
  revalidatePath(`/admin/channels/${data.slug}/edit`);
  revalidatePath(`/channels/${data.slug}`);
  revalidatePath("/channels");
  revalidatePath("/");
  return { ok: true, warnings };
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

  const externalUrl = String(formData.get("external_url") ?? "").trim() || null;
  const file = formData.get("pdf");
  const hasPdf = file instanceof File && file.size > 0;

  if (!hasPdf && !externalUrl) {
    throw new Error("Either a PDF file or an External URL is required.");
  }
  if (hasPdf && (file as File).type !== "application/pdf") {
    throw new Error("Upload a PDF file no larger than 25MB.");
  }
  if (hasPdf && (file as File).size > 25 * 1024 * 1024) {
    throw new Error("Upload a PDF file no larger than 25MB.");
  }

  const supabase = createSupabaseServiceClient();
  const slug = await uniqueSlug(title, "studies");

  let pdfPath: string | null = null;
  if (hasPdf) {
    const filename = sanitizeFilename((file as File).name) || "study.pdf";
    pdfPath = `${slug}/${filename}`;
    const { error: uploadError } = await supabase.storage
      .from("studies")
      .upload(pdfPath, file as File, { contentType: "application/pdf", upsert: false });
    if (uploadError) throw uploadError;
  }

  const previewFile = formData.get("preview_image");
  const hasPreview = previewFile instanceof File && previewFile.size > 0;
  let previewImagePath: string | null = null;
  if (hasPreview) {
    const ext = ((previewFile as File).name.split(".").pop() ?? "png").toLowerCase();
    previewImagePath = `${slug}/preview.${ext}`;
    const { error: previewError } = await supabase.storage
      .from("studies")
      .upload(previewImagePath, previewFile as File, {
        contentType: (previewFile as File).type || "image/png",
        upsert: true,
      });
    if (previewError) throw previewError;
  }
  const previewIsAi = formData.get("preview_image_is_ai") === "on";
  const previewCaption = String(formData.get("preview_image_caption") ?? "").trim() || null;

  const yearValue = String(formData.get("year") ?? "").trim();
  const sourceTypeRaw = String(formData.get("source_type") ?? "").trim() || null;
  const base = {
    slug,
    title,
    authors: parseCsv(formData.get("authors")),
    year: yearValue ? Number(yearValue) : null,
    source: String(formData.get("source") ?? "").trim() || null,
    abstract: String(formData.get("abstract") ?? "").trim() || null,
    tags: parseCsv(formData.get("tags")),
    featured: formData.get("featured") === "on",
    external_url: externalUrl,
    secondary_url: String(formData.get("secondary_url") ?? "").trim() || null,
    source_type: sourceTypeRaw,
    category: String(formData.get("category") ?? "").trim() || null,
    pdf_path: pdfPath,
    preview_image_path: previewImagePath,
    preview_image_source: previewImagePath ? "manual" : null,
    preview_image_caption: previewCaption,
    preview_image_is_ai: previewIsAi,
  };
  const extras = {
    findings: parseLines(formData.get("findings")),
    limitations: String(formData.get("limitations") ?? "").trim() || null,
    flagged_problematic: formData.get("flagged_problematic") === "on",
    flag_reason: String(formData.get("flag_reason") ?? "").trim() || null,
    context_note: String(formData.get("context_note") ?? "").trim() || null,
  };
  let { error } = await supabase.from("studies").insert({ ...base, ...extras });
  if (error && /findings|limitations|flagged_problematic|flag_reason|context_note|preview_image/.test(error.message)) {
    const { preview_image_path, preview_image_source, preview_image_caption, preview_image_is_ai, ...baseNoPreview } = base;
    void preview_image_path; void preview_image_source; void preview_image_caption; void preview_image_is_ai;
    ({ error } = await supabase.from("studies").insert(baseNoPreview));
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

export async function updateStudy(
  id: string,
  _prevState: SaveResult | null,
  formData: FormData,
): Promise<SaveResult> {
  try {
    await requireAdmin();
  } catch {
    return { ok: false, error: "Not authorized." };
  }
  const warnings: string[] = [];
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
    warnings.push("Findings/limitations/flag/context fields did not save — migration 0005 not applied.");
    ({ data, error } = await supabase
      .from("studies")
      .update(base)
      .eq("id", id)
      .select("slug")
      .single());
  }
  if (error) return { ok: false, error: error.message };
  if (!data) return { ok: false, error: "Study not found." };
  revalidatePath("/admin/studies");
  revalidatePath(`/admin/studies/${data.slug}/edit`);
  revalidatePath(`/studies/${data.slug}`);
  revalidatePath("/studies");
  revalidatePath("/");
  return { ok: true, warnings };
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

  const now = new Date().toISOString();
  for (const snapshot of snapshots) {
    const channelId = byYtId.get(snapshot.id);
    if (!channelId) continue;

    const { error: ytError } = await supabase
      .from("channel_youtube")
      .upsert(
        {
          channel_id: channelId,
          name: snapshot.name,
          description: snapshot.description,
          country: snapshot.country,
          default_language: snapshot.defaultLanguage,
          thumbnail_url: snapshot.thumbnailUrl,
          created_at_youtube: snapshot.publishedAt,
          last_synced_at: now,
          last_sync_status: "ok",
          last_sync_error: null,
        },
        { onConflict: "channel_id" },
      );
    if (ytError) throw ytError;

    const { error: statsError } = await supabase.from("channel_stats").insert({
      channel_id: channelId,
      subscribers: snapshot.subscribers,
      total_views: snapshot.totalViews,
      video_count: snapshot.videoCount,
    });
    if (statsError) throw statsError;
  }

  await refreshLatestView();
  revalidatePath("/admin");
  revalidatePath("/admin/channels");
  revalidatePath("/admin/refresh");
  revalidatePath("/channels");
  revalidatePath("/");
  redirect("/admin/refresh?refreshed=1");
}
