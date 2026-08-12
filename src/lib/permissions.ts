import "server-only";

import { cache } from "react";
import { unstable_cache } from "next/cache";
import { notFound, redirect } from "next/navigation";
import { getCurrentUser, type AuthContext } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

export type Capability = "download_channel_csv" | "compare_channels";

type CapabilityPolicy = "signed_in" | "premium";

const CAPABILITY_POLICIES: Record<Capability, CapabilityPolicy> = {
  download_channel_csv: "premium",
  compare_channels: "premium",
};

function loginPath(nextPath: string) {
  const safeNext =
    nextPath.startsWith("/") && !nextPath.startsWith("//") ? nextPath : "/";
  return `/login?next=${encodeURIComponent(safeNext)}`;
}

export async function requireCapability(
  capability: Capability,
  nextPath: string,
): Promise<AuthContext> {
  const auth = await getCurrentUser();
  if (!auth) {
    redirect(loginPath(nextPath));
  }

  const policy = CAPABILITY_POLICIES[capability];
  if (policy === "premium") {
    const premium = await isPremiumUser(auth);
    if (!premium) {
      redirect("/premium");
    }
  }

  return auth;
}

// Cached across requests (keyed by email); admin premium-user edits call
// revalidateTag("premium-users") so grants/revocations apply immediately.
const isPremiumEmail = unstable_cache(
  async (email: string): Promise<boolean> => {
    const { data, error } = await createSupabaseServiceClient()
      .from("premium_users")
      .select("id")
      .eq("email", email)
      .maybeSingle();
    if (error) throw error;
    return Boolean(data);
  },
  ["premium-email"],
  { tags: ["premium-users"], revalidate: 300 },
);

export async function isPremiumUser(auth: AuthContext): Promise<boolean> {
  const email = auth.profile?.email ?? auth.user.email ?? null;
  if (!email) return false;
  return isPremiumEmail(email.trim().toLowerCase());
}

export type PremiumStatus = {
  signedIn: boolean;
  premium: boolean;
  email: string | null;
};

export const getPremiumStatus = cache(async (): Promise<PremiumStatus> => {
  const auth = await getCurrentUser();
  if (!auth) return { signedIn: false, premium: false, email: null };
  const email = auth.profile?.email ?? auth.user.email ?? null;
  const premium = await isPremiumUser(auth);
  return { signedIn: true, premium, email };
});

// ============================================================================
// Apologetics Hub access — mirrors the premium allowlist exactly (email-keyed
// table, cached lookup, tag-based invalidation on admin grant/revoke), but
// gates with notFound() rather than a redirect: the hub does not exist
// unless you're allowed in, matching requireAdmin()'s hidden-404 semantics.
// ============================================================================

// Cached across requests (keyed by email); admin apologist-user edits call
// revalidateTag("apologists") so grants/revocations apply immediately.
const isApologistEmail = unstable_cache(
  async (email: string): Promise<boolean> => {
    const { data, error } = await createSupabaseServiceClient()
      .from("apologists")
      .select("id")
      .eq("email", email)
      .maybeSingle();
    if (error) throw error;
    return Boolean(data);
  },
  ["apologist-email"],
  { tags: ["apologists"], revalidate: 300 },
);

export async function isApologistUser(auth: AuthContext): Promise<boolean> {
  // Admins always have hub access, regardless of allowlist membership.
  if (auth.profile?.is_admin === true) return true;
  const email = auth.profile?.email ?? auth.user.email ?? null;
  if (!email) return false;
  return isApologistEmail(email.trim().toLowerCase());
}

export async function requireApologist(): Promise<AuthContext> {
  const auth = await getCurrentUser();
  if (!auth) {
    notFound();
  }

  if (!(await isApologistUser(auth))) {
    notFound();
  }

  return auth;
}
