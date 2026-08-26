"use server";

import { revalidatePath } from "next/cache";
import { QUIZ_DATA } from "@/lib/evangelical-quiz";
import { createSupabaseServerClient } from "@/lib/supabase/server";

const ITEM_SCALE_LENGTH = new Map(QUIZ_DATA.items.map((i) => [i.id, i.scale.length]));

type SaveAnswerInput = {
  itemId: string;
  responseIndex: number;
  currentPath?: string;
};

/**
 * Records one answer for a signed-in reader. This quiz is playable with no
 * account (see scripts/evangelical-quiz/README.md) - unlike the timeline
 * quiz's saveQuizAnswer, this never redirects an anonymous caller to
 * /login. The client only calls this once it already knows the reader is
 * signed in; a signed-out call is just a no-op, not an error, since a
 * client-side auth state could theoretically be stale by a request.
 */
export async function saveEvangelicalQuizAnswer(input: SaveAnswerInput) {
  const scaleLength = ITEM_SCALE_LENGTH.get(input.itemId);
  if (scaleLength === undefined || input.responseIndex < 0 || input.responseIndex >= scaleLength) {
    throw new Error("Unknown evangelical quiz item or response.");
  }

  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { saved: false as const };

  const { error } = await supabase.from("evangelical_quiz_answers").upsert(
    {
      user_id: user.id,
      item_id: input.itemId,
      response_index: input.responseIndex,
      data_version: QUIZ_DATA.data_version,
      updated_at: new Date().toISOString(),
    },
    { onConflict: "user_id,item_id" },
  );
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
  return { saved: true as const };
}

type ClearInput = {
  currentPath?: string;
};

/** Deletes a signed-in reader's saved answers, e.g. to retake the quiz. */
export async function clearEvangelicalQuizAnswers(input: ClearInput = {}) {
  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { cleared: false as const };

  const { error } = await supabase
    .from("evangelical_quiz_answers")
    .delete()
    .eq("user_id", user.id);
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
  return { cleared: true as const };
}
