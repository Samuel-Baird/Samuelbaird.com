import "server-only";

import { createSupabaseServerClient } from "@/lib/supabase/server";
import type { AnswerMap } from "./index";

/**
 * A reader's saved answers. Per-user, so this uses the cookie-bound client and
 * must not be wrapped in unstable_cache — see the note at the top of
 * src/lib/data.ts.
 */
export async function getQuizAnswersForUser(userId: string): Promise<AnswerMap> {
  const supabase = await createSupabaseServerClient();
  const { data, error } = await supabase
    .from("quiz_answers")
    .select("question_id, option_id")
    .eq("user_id", userId);

  if (error || !data) return {};
  const answers: AnswerMap = {};
  for (const row of data) answers[row.question_id] = row.option_id;
  return answers;
}
