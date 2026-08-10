"use server";

import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { after } from "next/server";
import {
  createSupabaseServerClient,
  createSupabaseServiceClient,
} from "@/lib/supabase/server";
import { getCurrentUser } from "@/lib/auth";
import { uuidSchema } from "@/lib/validation";
import { sendNewMessageEmail } from "@/lib/messages";

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
  const pageRef =
    String(formData.get("page_ref") ?? "").trim().slice(0, 300) || null;
  const body = String(formData.get("body") ?? "").trim();

  const auth = await getCurrentUser();
  if (!auth) {
    redirect(
      `/login?next=${encodeURIComponent(buildRedirect("/contact", { category, pageRef }))}`,
    );
  }
  const { user } = auth;

  if (website) {
    redirect("/contact?sent=1");
  }

  if (!body) {
    redirect(buildRedirect("/contact", { error: "empty", category, pageRef }));
  }
  if (body.length > 5000) {
    redirect(buildRedirect("/contact", { error: "too_long", category, pageRef }));
  }

  const limited = await isRateLimited(user.id);
  if (limited) {
    redirect(buildRedirect("/contact", { error: "rate_limited", category, pageRef }));
  }

  // Identity comes from the signed-in account, not free-text form fields —
  // keeps a visitor from submitting a message under someone else's name.
  const name =
    auth.profile?.full_name?.trim() ||
    (typeof user.user_metadata?.full_name === "string"
      ? user.user_metadata.full_name.trim()
      : "") ||
    null;
  const email = auth.profile?.email ?? user.email ?? null;

  const supabase = await createSupabaseServerClient();

  // Generated here rather than read back from the insert: RLS grants select on
  // messages to admins only, so a returning-insert would fail for visitors.
  const id = crypto.randomUUID();
  const { error } = await supabase.from("messages").insert({
    id,
    category,
    name,
    email,
    page_ref: pageRef,
    body,
    user_id: user.id,
  });
  if (error) throw error;

  // Notify after the response is sent — sendNewMessageEmail never throws, so a
  // mail outage can't cost the visitor their submission. `after` still runs
  // despite the redirect() below.
  after(() =>
    sendNewMessageEmail({
      id,
      category,
      name,
      email,
      page_ref: pageRef,
      body,
      created_at: new Date().toISOString(),
    }),
  );

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
  if (!uuidSchema.safeParse(id).success) {
    throw new Error("Invalid message id.");
  }
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
