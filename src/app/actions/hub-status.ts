"use server";

import { revalidatePath } from "next/cache";
import { requireApologist } from "@/lib/permissions";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { linkSchema, uuidSchema } from "@/lib/validation";
import type { HubVideoStatusValue } from "@/lib/types";

// Reads/writes go through the service client (RLS on hub_video_statuses is
// deny-all — see supabase/migrations/0039_apologetics_hub.sql). The gate is
// requireApologist(), and user_id always comes from the authenticated
// context below, never from the form, so a caller cannot set another
// creator's status.

type SetStatusInput = {
  videoId: string;
  status: HubVideoStatusValue;
  responseUrl?: string;
  currentPath?: string;
};

export async function setHubVideoStatus(input: SetStatusInput) {
  const auth = await requireApologist();

  if (!uuidSchema.safeParse(input.videoId).success) {
    throw new Error("Invalid video id.");
  }
  if (input.status !== "working_on_it" && input.status !== "responded") {
    throw new Error("Invalid status.");
  }

  let responseUrl: string | null = null;
  if (input.responseUrl && input.responseUrl.trim()) {
    const parsed = linkSchema.safeParse(input.responseUrl.trim());
    if (!parsed.success) {
      throw new Error("Enter a valid response link.");
    }
    responseUrl = parsed.data || null;
  }

  const { error } = await createSupabaseServiceClient()
    .from("hub_video_statuses")
    .upsert(
      {
        user_id: auth.user.id,
        video_id: input.videoId,
        status: input.status,
        response_url: responseUrl,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "user_id,video_id" },
    );
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
  return { status: input.status, response_url: responseUrl };
}

type ClearStatusInput = {
  videoId: string;
  currentPath?: string;
};

export async function clearHubVideoStatus(input: ClearStatusInput) {
  const auth = await requireApologist();

  if (!uuidSchema.safeParse(input.videoId).success) {
    throw new Error("Invalid video id.");
  }

  const { error } = await createSupabaseServiceClient()
    .from("hub_video_statuses")
    .delete()
    .eq("user_id", auth.user.id)
    .eq("video_id", input.videoId);
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
}
