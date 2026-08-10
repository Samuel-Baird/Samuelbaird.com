"use server";

import { revalidatePath } from "next/cache";
import { getCurrentUser } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

export async function setNewsletterSubscription(formData: FormData) {
  const auth = await getCurrentUser();
  if (!auth) throw new Error("Not signed in");

  const enabled = formData.get("enabled") === "true";
  const supabase = createSupabaseServiceClient();

  if (enabled) {
    const email = (auth.profile?.email ?? auth.user.email ?? "")
      .trim()
      .toLowerCase();
    if (!email) throw new Error("No email on account");

    const { error } = await supabase.from("newsletter_subscribers").upsert(
      { user_id: auth.user.id, email, unsubscribed_at: null },
      { onConflict: "user_id" },
    );
    if (error) throw error;
  } else {
    const { error } = await supabase
      .from("newsletter_subscribers")
      .update({ unsubscribed_at: new Date().toISOString() })
      .eq("user_id", auth.user.id);
    if (error) throw error;
  }

  revalidatePath("/me/settings");
}
