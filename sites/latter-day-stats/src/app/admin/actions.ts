"use server";

import { revalidatePath, revalidateTag } from "next/cache";
import { redirect } from "next/navigation";
import { requireAdmin } from "@/lib/auth";
import { logEvent } from "@/lib/log";
import { runStatsRefresh } from "@/lib/refresh-stats";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import {
  emailSchema,
  linkSchema,
  uuidSchema,
  yearSchema,
} from "@/lib/validation";
import {
  fetchYouTubeSnapshots,
  parseHandleInput,
  resolveHandleToChannelId,
  slugifyName,
} from "@/lib/youtube";

function assertUuid(id: string) {
  if (!uuidSchema.safeParse(id).success) throw new Error("Invalid id.");
}

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
  assertUuid(id);
  const { error } = await createSupabaseServiceClient()
    .from("channels")
    .update({ featured: value })
    .eq("id", id);
  if (error) throw error;
  revalidateTag("channels", { expire: 0 });
  revalidatePath("/admin/channels");
  revalidatePath("/channels");
  revalidatePath("/");
}

function normalizeEmail(value: FormDataEntryValue | null) {
  return String(value ?? "").trim().toLowerCase();
}

// ============================================================================
// Unified access management — /admin/access grants premium and admin status
// from one email-keyed form instead of separate screens. Each role still
// lives in its own allowlist table (premium_users / admins) so
// isPremiumUser()/requireAdmin() and their RLS/cache posture are unchanged;
// this is only a UI + one table (admins) consolidating how they're edited.
// ============================================================================

export type UserRole = "premium" | "admin";

const ROLE_TABLE: Record<UserRole, "premium_users" | "admins"> = {
  premium: "premium_users",
  admin: "admins",
};

const ROLE_TAG: Record<UserRole, string> = {
  premium: "premium-users",
  admin: "admins",
};

function assertRole(role: string): asserts role is UserRole {
  if (role !== "premium" && role !== "admin") {
    throw new Error("Invalid role.");
  }
}

// Adds a person with an initial set of roles, or updates their name/roles if
// they're already on one of the lists (upsert semantics per role).
export async function upsertUserAccess(formData: FormData) {
  const auth = await requireAdmin();
  const email = normalizeEmail(formData.get("email"));
  const name = String(formData.get("name") ?? "").trim() || null;
  if (!emailSchema.safeParse(email).success) {
    throw new Error("Enter a valid email address.");
  }

  const roles: UserRole[] = (["premium", "admin"] as const).filter(
    (r) => formData.get(r) === "on",
  );

  const supabase = createSupabaseServiceClient();
  for (const role of roles) {
    const { error } = await supabase
      .from(ROLE_TABLE[role])
      .upsert({ email, name, created_by: auth.user.id }, { onConflict: "email" });
    if (error) throw error;
    revalidateTag(ROLE_TAG[role], { expire: 0 });
  }
  if (roles.includes("admin")) {
    const { error } = await supabase
      .from("profiles")
      .update({ is_admin: true })
      .eq("email", email);
    if (error) throw error;
  }

  revalidatePath("/admin/access");
}

// Per-row checkbox toggle, mirroring setChannelFeatured/setChannelActive.
export async function setUserRole(email: string, role: string, value: boolean) {
  assertRole(role);
  const auth = await requireAdmin();
  if (!emailSchema.safeParse(email).success) {
    throw new Error("Invalid email.");
  }

  const supabase = createSupabaseServiceClient();
  if (value) {
    const { error } = await supabase
      .from(ROLE_TABLE[role])
      .upsert({ email, created_by: auth.user.id }, { onConflict: "email" });
    if (error) throw error;
  } else {
    const { error } = await supabase.from(ROLE_TABLE[role]).delete().eq("email", email);
    if (error) throw error;
  }
  revalidateTag(ROLE_TAG[role], { expire: 0 });

  if (role === "admin") {
    // Takes effect immediately for anyone who already has a profile; the
    // admins-table row above is what a not-yet-signed-in grant relies on
    // (synced into profiles.is_admin by the sign-up trigger).
    const { error } = await supabase
      .from("profiles")
      .update({ is_admin: value })
      .eq("email", email);
    if (error) throw error;
  }

  revalidatePath("/admin/access");
}

export async function setChannelActive(id: string, value: boolean) {
  await requireAdmin();
  assertUuid(id);
  const { error } = await createSupabaseServiceClient()
    .from("channels")
    .update({ is_active: value })
    .eq("id", id);
  if (error) throw error;
  revalidateTag("channels", { expire: 0 });
  revalidatePath("/admin/channels");
  revalidatePath("/channels");
  revalidatePath("/");
}

export async function deleteChannel(id: string) {
  await requireAdmin();
  assertUuid(id);
  const { error } = await createSupabaseServiceClient()
    .from("channels")
    .delete()
    .eq("id", id);
  if (error) throw error;
  revalidateTag("channels", { expire: 0 });
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
  revalidateTag("channels", { expire: 0 });
  revalidatePath("/admin/channels");
  revalidatePath("/channels");
  revalidatePath("/");
  redirect(`/admin/channels?added=${channel.slug}`);
}

export async function setChannelType(id: string, value: string) {
  await requireAdmin();
  assertUuid(id);
  const types = value ? [value] : [];
  const { error } = await createSupabaseServiceClient()
    .from("channels")
    .update({ channel_types: types, channel_type: value || null })
    .eq("id", id);
  if (error) throw error;
  revalidateTag("channels", { expire: 0 });
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
  if (!uuidSchema.safeParse(id).success) {
    return { ok: false, error: "Invalid channel id." };
  }
  const warnings: string[] = [];
  const get = (key: string) => {
    const value = String(formData.get(key) ?? "").trim();
    return value || null;
  };
  const supabase = createSupabaseServiceClient();
  const channelTypes = formData
    .getAll("channel_types")
    .map((v) => String(v).trim())
    .filter(Boolean);
  // Deduplicate while preserving order.
  const channelTypesDeduped = [...new Set(channelTypes)];
  const base = {
    channel_types: channelTypesDeduped,
    channel_type: channelTypesDeduped[0] ?? null,
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
  for (const [field, value] of Object.entries(socialProfiles)) {
    if (value !== null && !linkSchema.safeParse(value).success) {
      return {
        ok: false,
        error: `${field.replace("_url", "")} link doesn't look valid.`,
      };
    }
  }

  let { data, error } = await supabase
    .from("channels")
    .update(coreDetails)
    .eq("id", id)
    .select("slug")
    .single();

  if (error && /channel_types/.test(error.message)) {
    logEvent("channel_update_fallback", { id, message: error.message }, "error");
    warnings.push("Multiple tags did not save — migration 0026 not applied.");
    const { channel_types: _drop, ...withoutArray } = coreDetails;
    void _drop;
    ({ data, error } = await supabase
      .from("channels")
      .update(withoutArray)
      .eq("id", id)
      .select("slug")
      .single());
  }

  if (error && /lds_affiliation_source/.test(error.message)) {
    logEvent("channel_update_fallback", { id, message: error.message }, "error");
    warnings.push("LDS affiliation source did not save — migration 0007 not applied.");
    ({ data, error } = await supabase
      .from("channels")
      .update(detailsWithoutAffiliationSource)
      .eq("id", id)
      .select("slug")
      .single());
  }

  if (error && /country_manual|language_manual/.test(error.message)) {
    logEvent("channel_update_fallback", { id, message: error.message }, "error");
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

  revalidateTag("channels", { expire: 0 });
  revalidatePath("/admin/channels");
  revalidatePath(`/admin/channels/${data.slug}/edit`);
  revalidatePath(`/channels/${data.slug}`);
  revalidatePath("/channels");
  revalidatePath("/");
  return { ok: true, warnings };
}

export async function deleteStudy(id: string) {
  await requireAdmin();
  assertUuid(id);
  const { error } = await createSupabaseServiceClient()
    .from("studies")
    .delete()
    .eq("id", id);
  if (error) throw error;
  revalidateTag("studies", { expire: 0 });
  revalidatePath("/admin/studies");
  revalidatePath("/studies");
  revalidatePath("/");
}

export async function createStudy(formData: FormData) {
  await requireAdmin();
  const title = String(formData.get("title") ?? "").trim();
  if (!title) throw new Error("Title is required.");
  if (title.length > 300) throw new Error("Title is too long (300 max).");
  const yearRaw = String(formData.get("year") ?? "").trim();
  if (yearRaw && !yearSchema.safeParse(yearRaw).success) {
    throw new Error("Year must be a 4-digit year.");
  }

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

  revalidateTag("studies", { expire: 0 });
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
  if (!uuidSchema.safeParse(id).success) {
    return { ok: false, error: "Invalid study id." };
  }
  const warnings: string[] = [];
  const yearValue = String(formData.get("year") ?? "").trim();
  if (yearValue && !yearSchema.safeParse(yearValue).success) {
    return { ok: false, error: "Year must be a 4-digit year." };
  }
  const supabase = createSupabaseServiceClient();
  const base = {
    title: String(formData.get("title") ?? "").trim(),
    authors: parseCsv(formData.get("authors")),
    year: yearValue ? Number(yearValue) : null,
    source: String(formData.get("source") ?? "").trim() || null,
    abstract: String(formData.get("abstract") ?? "").trim() || null,
    tags: parseCsv(formData.get("tags")),
  };

  // Preview image handling: a new file replaces, "clear" wipes, otherwise
  // only the caption/AI flag are updated.
  const previewFile = formData.get("preview_image");
  const hasPreview = previewFile instanceof File && previewFile.size > 0;
  const clearPreview = formData.get("preview_image_clear") === "on";
  const previewIsAi = formData.get("preview_image_is_ai") === "on";
  const previewCaption =
    String(formData.get("preview_image_caption") ?? "").trim() || null;
  const previewUpdate: Record<string, unknown> = {
    preview_image_caption: previewCaption,
    preview_image_is_ai: previewIsAi,
  };
  if (clearPreview) {
    previewUpdate.preview_image_path = null;
    previewUpdate.preview_image_source = null;
    previewUpdate.preview_image_is_ai = false;
    previewUpdate.preview_image_caption = null;
  } else if (hasPreview) {
    const { data: existing } = await supabase
      .from("studies")
      .select("slug")
      .eq("id", id)
      .single();
    const slug = existing?.slug;
    if (slug) {
      const ext = ((previewFile as File).name.split(".").pop() ?? "png").toLowerCase();
      const path = `${slug}/preview.${ext}`;
      const { error: upErr } = await supabase.storage
        .from("studies")
        .upload(path, previewFile as File, {
          contentType: (previewFile as File).type || "image/png",
          upsert: true,
        });
      if (upErr) return { ok: false, error: upErr.message };
      previewUpdate.preview_image_path = path;
      previewUpdate.preview_image_source = "manual";
    }
  }
  const extras = {
    findings: parseLines(formData.get("findings")),
    limitations: String(formData.get("limitations") ?? "").trim() || null,
    flagged_problematic: formData.get("flagged_problematic") === "on",
    flag_reason: String(formData.get("flag_reason") ?? "").trim() || null,
    context_note: String(formData.get("context_note") ?? "").trim() || null,
  };
  let { data, error } = await supabase
    .from("studies")
    .update({ ...base, ...extras, ...previewUpdate })
    .eq("id", id)
    .select("slug")
    .single();
  if (error && /findings|limitations|flagged_problematic|flag_reason|context_note|preview_image/.test(error.message)) {
    logEvent("study_update_fallback", { id, message: error.message }, "error");
    warnings.push("Some optional fields did not save — newer migration not applied.");
    ({ data, error } = await supabase
      .from("studies")
      .update(base)
      .eq("id", id)
      .select("slug")
      .single());
  }
  if (error) return { ok: false, error: error.message };
  if (!data) return { ok: false, error: "Study not found." };
  revalidateTag("studies", { expire: 0 });
  revalidatePath("/admin/studies");
  revalidatePath(`/admin/studies/${data.slug}/edit`);
  revalidatePath(`/studies/${data.slug}`);
  revalidatePath("/studies");
  revalidatePath("/");
  return { ok: true, warnings };
}

export async function regenerateStudyPreview(id: string) {
  await requireAdmin();
  assertUuid(id);
  // Relies on scripts/ and child_process, which aren't available on Vercel
  // functions or Cloudflare Workers — this is local-only admin tooling.
  const onWorkers =
    typeof navigator !== "undefined" && navigator.userAgent === "Cloudflare-Workers";
  if (process.env.VERCEL || onWorkers) {
    throw new Error(
      "Preview regeneration only works when running the admin locally.",
    );
  }
  const supabase = createSupabaseServiceClient();
  const { data: study, error } = await supabase
    .from("studies")
    .select("slug")
    .eq("id", id)
    .single();
  if (error || !study) throw error ?? new Error("Study not found.");

  const { spawn } = await import("node:child_process");
  const path = await import("node:path");
  const cwd = process.cwd();
  await new Promise<void>((resolve, reject) => {
    const child = spawn(
      process.execPath,
      [path.join(cwd, "scripts", "generate-study-preview.mjs"), study.slug],
      { cwd, stdio: "inherit", timeout: 120_000 },
    );
    child.on("error", reject);
    child.on("exit", (code, signal) => {
      if (code === 0) resolve();
      else if (signal)
        reject(new Error(`generate-study-preview timed out (${signal})`));
      else reject(new Error(`generate-study-preview exited with ${code}`));
    });
  });

  revalidateTag("studies", { expire: 0 });
  revalidatePath(`/admin/studies/${study.slug}/edit`);
  revalidatePath(`/studies/${study.slug}`);
  revalidatePath("/studies");
}

export async function refreshStatsNow() {
  await requireAdmin();
  const supabase = createSupabaseServiceClient();
  // Manual refresh covers inactive channels too, unlike the daily cron.
  await runStatsRefresh(supabase, { activeOnly: false });
  revalidatePath("/admin");
  revalidatePath("/admin/channels");
  revalidatePath("/admin/refresh");
  redirect("/admin/refresh?refreshed=1");
}
