"use server";

import { revalidatePath } from "next/cache";
import { getCurrentUser } from "@/lib/auth";
import { isPremiumUser } from "@/lib/permissions";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

export async function setWeeklyNotification(formData: FormData) {
  const auth = await getCurrentUser();
  if (!auth) throw new Error("Not signed in");
  const premium = await isPremiumUser(auth);
  if (!premium) throw new Error("Not a beta tester");
  const email = (auth.profile?.email ?? auth.user.email ?? "")
    .trim()
    .toLowerCase();
  if (!email) throw new Error("No email on account");

  const enabled = formData.get("enabled") === "true";

  const { error } = await createSupabaseServiceClient()
    .from("premium_users")
    .update({ notify_weekly: enabled })
    .eq("email", email);
  if (error) throw error;

  revalidatePath("/beta");
  revalidatePath("/admin/premium");
}
