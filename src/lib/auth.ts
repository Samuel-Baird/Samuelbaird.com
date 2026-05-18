import "server-only";

import { notFound, redirect } from "next/navigation";
import type { User } from "@supabase/supabase-js";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export type Profile = {
  id: string;
  email: string | null;
  full_name: string | null;
  avatar_url: string | null;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
};

export type AuthContext = {
  user: User;
  profile: Profile | null;
};

export async function getCurrentUser(): Promise<AuthContext | null> {
  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return null;
  }

  const { data: profile, error } = await supabase
    .from("profiles")
    .select("*")
    .eq("id", user.id)
    .maybeSingle();

  if (error) {
    throw error;
  }

  return {
    user,
    profile: (profile as Profile | null) ?? null,
  };
}

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
