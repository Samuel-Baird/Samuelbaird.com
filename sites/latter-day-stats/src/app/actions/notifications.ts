"use server";

import { revalidatePath } from "next/cache";
import { getCurrentUser } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

// The weekly digest is open to every signed-in reader. The subscriber list
// still lives in premium_users (email + notify_weekly), which /admin/access
// reads when the digest is sent, so opting in upserts a row there.
export async function setWeeklyNotification(formData: FormData) {
  const auth = await getCurrentUser();
  if (!auth) throw new Error("Not signed in");
  const email = (auth.profile?.email ?? auth.user.email ?? "")
    .trim()
    .toLowerCase();
  if (!email) throw new Error("No email on account");

  const enabled = formData.get("enabled") === "true";

  const { error } = await createSupabaseServiceClient()
    .from("premium_users")
    .upsert({ email, notify_weekly: enabled }, { onConflict: "email" });
  if (error) throw error;

  revalidatePath("/admin/access");
}
