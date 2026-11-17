"use server";

import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import {
  createSupabaseServerClient,
  createSupabaseServiceClient,
} from "@/lib/supabase/server";

// COPPA: stamps the current user's one-time age confirmation, shown by the
// site-wide AgeGateModal on first login (see /auth/callback). Guarded with
// `.is("age_confirmed_at", null)` so a double-submit (or a stale modal still
// open in another tab) can't overwrite an existing timestamp.
export async function confirmAge() {
  const auth = await getCurrentUser();
  if (!auth) throw new Error("Not signed in");

  const supabase = await createSupabaseServerClient();
  const { error } = await supabase
    .from("profiles")
    .update({ age_confirmed_at: new Date().toISOString() })
    .eq("id", auth.user.id)
    .is("age_confirmed_at", null);

  if (error) throw error;
}

// Bookmarks, upvotes, study_progress, and newsletter_subscribers all
// cascade-delete from auth.users via FK constraints (see the migrations that
// define them), so deleting the auth user is sufficient — nothing else to
// clean up by hand. `messages` intentionally keeps its rows with user_id set
// to null (ON DELETE SET NULL) rather than cascading, since a submitted
// correction/bug report shouldn't vanish along with the account that sent
// it. premium_users is matched by email, independent of the account.
export async function deleteMyAccount() {
  const auth = await getCurrentUser();
  if (!auth) throw new Error("Not signed in");

  const service = createSupabaseServiceClient();
  const { error } = await service.auth.admin.deleteUser(auth.user.id);
  if (error) throw error;

  const supabase = await createSupabaseServerClient();
  await supabase.auth.signOut();

  redirect("/");
}
