"use server";

import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import {
  createSupabaseServerClient,
  createSupabaseServiceClient,
} from "@/lib/supabase/server";

const VALID_CATEGORIES = [
  "general",
  "correction",
  "channel_suggestion",
  "study_suggestion",
  "bug",
] as const;
type Category = (typeof VALID_CATEGORIES)[number];

function isCategory(value: string): value is Category {
  return (VALID_CATEGORIES as readonly string[]).includes(value);
}

export async function submitMessage(formData: FormData) {
  const categoryRaw = String(formData.get("category") ?? "").trim();
  const category: Category = isCategory(categoryRaw) ? categoryRaw : "general";
  const website = String(formData.get("website") ?? "").trim();
  const name = String(formData.get("name") ?? "").trim().slice(0, 120) || null;
  const email = String(formData.get("email") ?? "").trim().slice(0, 200) || null;
  const pageRef =
    String(formData.get("page_ref") ?? "").trim().slice(0, 300) || null;
  const body = String(formData.get("body") ?? "").trim();
  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect(
      `/login?next=${encodeURIComponent(buildRedirect("/contact", { category, pageRef }))}`,
    );
  }

  if (website) {
    redirect("/contact?sent=1");
  }

  if (!body) {
    redirect(buildRedirect("/contact", { error: "empty", category, pageRef }));
  }
  if (body.length > 5000) {
    redirect(buildRedirect("/contact", { error: "too_long", category, pageRef }));
  }
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    redirect(buildRedirect("/contact", { error: "bad_email", category, pageRef }));
  }

  const limited = await isRateLimited(user.id);
  if (limited) {
    redirect(buildRedirect("/contact", { error: "rate_limited", category, pageRef }));
  }

  const { error } = await supabase.from("messages").insert({
    category,
    name,
    email,
    page_ref: pageRef,
    body,
    user_id: user.id,
  });
  if (error) throw error;

  revalidatePath("/admin/messages");
  redirect("/contact?sent=1");
}

async function isRateLimited(userId: string) {
  const supabase = createSupabaseServiceClient();
  const tenMinutesAgo = new Date(Date.now() - 10 * 60 * 1000).toISOString();
  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

  const [
    { count: recentCount, error: recentError },
    { count: dayCount, error: dayError },
  ] = await Promise.all([
    supabase
      .from("messages")
      .select("id", { count: "exact", head: true })
      .eq("user_id", userId)
      .gte("created_at", tenMinutesAgo),
    supabase
      .from("messages")
      .select("id", { count: "exact", head: true })
      .eq("user_id", userId)
      .gte("created_at", oneDayAgo),
  ]);

  if (recentError || dayError) {
    throw recentError ?? dayError;
  }

  return (recentCount ?? 0) >= 2 || (dayCount ?? 0) >= 8;
}

function buildRedirect(
  base: string,
  params: { error?: string; category?: string; pageRef?: string | null },
) {
  const q = new URLSearchParams();
  if (params.error) q.set("error", params.error);
  if (params.category) q.set("category", params.category);
  if (params.pageRef) q.set("ref", params.pageRef);
  const qs = q.toString();
  return qs ? `${base}?${qs}` : base;
}

export async function markMessageResolved(id: string, resolved: boolean) {
  const supabase = await createSupabaseServerClient();
  const { error } = await supabase
    .from("messages")
    .update({
      resolved,
      resolved_at: resolved ? new Date().toISOString() : null,
    })
    .eq("id", id);
  if (error) throw error;
  revalidatePath("/admin/messages");
}
