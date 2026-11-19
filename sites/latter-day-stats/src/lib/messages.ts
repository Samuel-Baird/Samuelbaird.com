// Labels for the categories on rows in the `messages` table. New messages no
// longer arrive (the contact form was replaced by a plain email address), but
// /admin/messages still lists and resolves the ones already received.
export const CATEGORY_LABELS: Record<string, string> = {
  general: "General",
  correction: "Correction",
  channel_suggestion: "Channel",
  study_suggestion: "Study",
  bug: "Bug",
};

export function categoryLabel(category: string) {
  return CATEGORY_LABELS[category] ?? category;
}
