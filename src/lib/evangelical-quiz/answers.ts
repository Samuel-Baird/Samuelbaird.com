import "server-only";

import { createSupabaseServerClient } from "@/lib/supabase/server";
import { QUIZ_DATA } from "./index";
import type { AnswerMap } from "./types";

/**
 * A signed-in reader's saved answers, keyed by item id. Uses the
 * cookie-bound client and must not be wrapped in unstable_cache - see the
 * note at the top of src/lib/data.ts.
 *
 * Rows for items no longer in the current data.json are dropped rather than
 * surfaced - the workbook only grows, but this keeps the map always valid
 * against QUIZ_DATA even if an item is ever retired.
 */
export async function getEvangelicalQuizAnswersForUser(userId: string): Promise<AnswerMap> {
  const supabase = await createSupabaseServerClient();
  const { data, error } = await supabase
    .from("evangelical_quiz_answers")
    .select("item_id, response_index")
    .eq("user_id", userId);

  if (error || !data) return {};

  const validIds = new Set(QUIZ_DATA.items.map((i) => i.id));
  const answers: AnswerMap = {};
  for (const row of data) {
    if (validIds.has(row.item_id)) answers[row.item_id] = row.response_index;
  }
  return answers;
}
