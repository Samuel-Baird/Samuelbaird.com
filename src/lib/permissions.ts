import "server-only";

import { cache } from "react";
import { unstable_cache } from "next/cache";
import { redirect } from "next/navigation";
import { getCurrentUser, type AuthContext } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

export type Capability =
  | "download_channel_csv"
  | "compare_channels"
  | "download_evangelical_quiz_data";

type CapabilityPolicy = "signed_in" | "premium";

const CAPABILITY_POLICIES: Record<Capability, CapabilityPolicy> = {
  download_channel_csv: "premium",
  compare_channels: "premium",
  download_evangelical_quiz_data: "premium",
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
