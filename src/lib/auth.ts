import "server-only";

import { cache } from "react";
import { notFound, redirect } from "next/navigation";
import type { User } from "@supabase/supabase-js";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export type Profile = {
  id: string;
  email: string | null;
  full_name: string | null;
  avatar_url: string | null;
  is_admin: boolean;
  age_confirmed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type AuthContext = {
  user: User;
  profile: Profile | null;
};

// cache() dedupes the auth + profile round trips within a single render pass
// (layout navbar, page, and permission checks all call this).
export const getCurrentUser = cache(async (): Promise<AuthContext | null> => {
  const supabase = await createSupabaseServerClient();
  let user: User | null = null;
  try {
    const result = await supabase.auth.getUser();
    user = result.data.user;
  } catch (error) {
    console.error("auth.getUser failed:", error);
    return null;
  }

  if (!user) {
    return null;
  }

  const { data: profile, error } = await supabase
    .from("profiles")
    .select("*")
    .eq("id", user.id)
    .maybeSingle();

  if (error) {
    // Don't 500 the whole layout on a profile-fetch hiccup; degrade to
    // "signed-in user, profile unknown" so the navbar still renders.
    console.error("profile fetch failed:", error);
    return { user, profile: null };
  }

  return {
    user,
    profile: (profile as Profile | null) ?? null,
  };
});

export async function requireUser(): Promise<AuthContext> {
  const auth = await getCurrentUser();

  if (!auth) {
    notFound();
  }

  return auth;
}

export async function requireAdmin(): Promise<AuthContext> {
  const auth = await requireUser();

  if (auth.profile?.is_admin !== true) {
    notFound();
  }

  return auth;
}

export async function signOutAction() {
  "use server";

  const supabase = await createSupabaseServerClient();
  await supabase.auth.signOut();
  redirect("/");
}
