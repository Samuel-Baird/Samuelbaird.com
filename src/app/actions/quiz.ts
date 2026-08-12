"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { ALL_QUESTIONS, isValidAnswer } from "@/lib/quiz";
import { createSupabaseServerClient } from "@/lib/supabase/server";

const TIMELINE_BY_QUESTION = new Map(ALL_QUESTIONS.map((q) => [q.id, q.timeline]));

type SaveAnswerInput = {
  questionId: string;
  optionId: string;
  currentPath?: string;
};

/**
 * Records one answer. Answers save as they are given rather than on a submit
 * button, so a half-finished quiz is still there tomorrow and an answer given
 * on a timeline page is already given on /quiz.
 */
export async function saveQuizAnswer(input: SaveAnswerInput) {
  const timeline = TIMELINE_BY_QUESTION.get(input.questionId);
  if (!timeline || !isValidAnswer(input.questionId, input.optionId)) {
    throw new Error("Unknown quiz question or option.");
  }

  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect(`/login?next=${encodeURIComponent(input.currentPath ?? "/quiz")}`);
  }

  const { error } = await supabase.from("quiz_answers").upsert(
    {
      user_id: user.id,
      question_id: input.questionId,
      option_id: input.optionId,
      timeline,
      updated_at: new Date().toISOString(),
    },
    { onConflict: "user_id,question_id" },
  );
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
  revalidatePath("/me/quiz");
  return { questionId: input.questionId, optionId: input.optionId };
}

type ClearInput = {
  /** Clear one timeline's answers, or all of them when omitted. */
  timeline?: string;
  currentPath?: string;
};

export async function clearQuizAnswers(input: ClearInput = {}) {
  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect(`/login?next=${encodeURIComponent(input.currentPath ?? "/quiz")}`);
  }

  let query = supabase.from("quiz_answers").delete().eq("user_id", user.id);
  if (input.timeline) query = query.eq("timeline", input.timeline);
  const { error } = await query;
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
  revalidatePath("/me/quiz");
  return { cleared: true };
}
