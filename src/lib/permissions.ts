import "server-only";

import { redirect } from "next/navigation";
import { getCurrentUser, type AuthContext } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

export type Capability = "download_channel_csv" | "compare_channels";

type CapabilityPolicy = "signed_in" | "premium";

const CAPABILITY_POLICIES: Record<Capability, CapabilityPolicy> = {
  download_channel_csv: "signed_in",
  compare_channels: "signed_in",
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
      redirect("/");
    }
  }

  return auth;
}

export async function isPremiumUser(auth: AuthContext): Promise<boolean> {
  const email = auth.profile?.email ?? auth.user.email ?? null;
  if (!email) return false;

  const { data, error } = await createSupabaseServiceClient()
    .from("premium_users")
    .select("id")
    .eq("email", email.trim().toLowerCase())
    .maybeSingle();
  if (error) throw error;
  return Boolean(data);
}
