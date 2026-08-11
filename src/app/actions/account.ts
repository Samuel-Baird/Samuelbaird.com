"use server";

import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import {
  createSupabaseServerClient,
  createSupabaseServiceClient,
} from "@/lib/supabase/server";

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
