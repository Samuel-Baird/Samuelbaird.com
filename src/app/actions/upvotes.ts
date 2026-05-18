"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";

type ToggleUpvoteInput = {
  targetType: "channel" | "study";
  targetId: string;
  currentPath?: string;
};

export async function toggleUpvote(input: ToggleUpvoteInput) {
  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect(`/login?next=${encodeURIComponent(input.currentPath ?? "/")}`);
  }

  const { data: existing, error: lookupError } = await supabase
    .from("upvotes")
    .select("target_id")
    .eq("user_id", user.id)
    .eq("target_type", input.targetType)
    .eq("target_id", input.targetId)
    .maybeSingle();
  if (lookupError) throw lookupError;

  let upvoted = true;
  if (existing) {
    const { error } = await supabase
      .from("upvotes")
      .delete()
      .eq("user_id", user.id)
      .eq("target_type", input.targetType)
      .eq("target_id", input.targetId);
    if (error) throw error;
    upvoted = false;
  } else {
    const { error } = await supabase.from("upvotes").insert({
      user_id: user.id,
      target_type: input.targetType,
      target_id: input.targetId,
    });
    if (error) throw error;
  }

  if (input.currentPath) revalidatePath(input.currentPath);
  return { upvoted };
}
