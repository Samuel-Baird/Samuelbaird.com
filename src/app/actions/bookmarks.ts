"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { toggleTargetSchema } from "@/lib/validation";

type ToggleBookmarkInput = {
  targetType: "channel" | "study";
  targetId: string;
  currentPath?: string;
};

export async function toggleBookmark(input: ToggleBookmarkInput) {
  const parsed = toggleTargetSchema.safeParse(input);
  if (!parsed.success) throw new Error("Invalid bookmark target.");
  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect(`/login?next=${encodeURIComponent(input.currentPath ?? "/")}`);
  }

  const { data: existing, error: lookupError } = await supabase
    .from("bookmarks")
    .select("id")
    .eq("user_id", user.id)
    .eq("target_type", input.targetType)
    .eq("target_id", input.targetId)
    .maybeSingle();
  if (lookupError) throw lookupError;

  let bookmarked = true;
  if (existing) {
    const { error } = await supabase
      .from("bookmarks")
      .delete()
      .eq("id", existing.id);
    if (error) throw error;
    bookmarked = false;
  } else {
    const { error } = await supabase.from("bookmarks").insert({
      user_id: user.id,
      target_type: input.targetType,
      target_id: input.targetId,
    });
    if (error) throw error;
  }

  if (input.currentPath) revalidatePath(input.currentPath);
  revalidatePath("/me/bookmarks");
  return { bookmarked };
}
