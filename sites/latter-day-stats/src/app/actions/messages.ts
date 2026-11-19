"use server";

import { revalidatePath } from "next/cache";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { uuidSchema } from "@/lib/validation";

// The contact form (and its submitMessage action) is gone: people email
// CONTACT_EMAIL instead. This only lets admins resolve the messages already
// in the inbox at /admin/messages.
export async function markMessageResolved(id: string, resolved: boolean) {
  if (!uuidSchema.safeParse(id).success) {
    throw new Error("Invalid message id.");
  }
  const supabase = await createSupabaseServerClient();
  const { error } = await supabase
    .from("messages")
    .update({
      resolved,
      resolved_at: resolved ? new Date().toISOString() : null,
    })
    .eq("id", id);
  if (error) throw error;
  revalidatePath("/admin/messages");
}
