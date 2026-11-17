"use server";

import { revalidatePath, revalidateTag } from "next/cache";
import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { toggleTargetSchema } from "@/lib/validation";

type ToggleUpvoteInput = {
  targetType: "channel" | "study";
  targetId: string;
  currentPath?: string;
};

export async function toggleUpvote(input: ToggleUpvoteInput) {
  const parsed = toggleTargetSchema.safeParse(input);
  if (!parsed.success) throw new Error("Invalid upvote target.");
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

  revalidateTag("upvotes", { expire: 0 });
  if (input.currentPath) revalidatePath(input.currentPath);
  return { upvoted };
}
