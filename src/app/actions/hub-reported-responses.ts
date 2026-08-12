"use server";

import { revalidatePath } from "next/cache";
import { requireApologist } from "@/lib/permissions";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { linkSchema, uuidSchema } from "@/lib/validation";

// Reads/writes go through the service client (RLS on hub_reported_responses
// is deny-all — see supabase/migrations/0043_hub_reported_responses.sql).
// The gate is requireApologist(); added_by always comes from the
// authenticated context below, never from the form.

type AddReportedResponseInput = {
  videoId: string;
  url: string;
  currentPath?: string;
};

export async function addReportedResponse(input: AddReportedResponseInput) {
  const auth = await requireApologist();

  if (!uuidSchema.safeParse(input.videoId).success) {
    throw new Error("Invalid video id.");
  }

  const trimmed = input.url.trim();
  const parsed = linkSchema.safeParse(trimmed);
  if (!parsed.success || !parsed.data) {
    throw new Error("Enter a valid link.");
  }
  const url = /^https?:\/\//.test(parsed.data) ? parsed.data : `https://${parsed.data}`;

  const { error } = await createSupabaseServiceClient()
    .from("hub_reported_responses")
    .insert({
      video_id: input.videoId,
      url,
      added_by: auth.user.id,
    });
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
}

type RemoveReportedResponseInput = {
  id: string;
  currentPath?: string;
};

export async function removeReportedResponse(input: RemoveReportedResponseInput) {
  const auth = await requireApologist();

  if (!uuidSchema.safeParse(input.id).success) {
    throw new Error("Invalid id.");
  }

  const supabase = createSupabaseServiceClient();

  // Only the apologist who logged a link (or an admin) can remove it.
  let query = supabase.from("hub_reported_responses").delete().eq("id", input.id);
  if (auth.profile?.is_admin !== true) {
    query = query.eq("added_by", auth.user.id);
  }
  const { error } = await query;
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
}
