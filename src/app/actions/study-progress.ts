"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";

type ToggleInput = {
  studyId: string;
  currentPath?: string;
};

export async function toggleStudyRead(input: ToggleInput) {
  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) {
    redirect(`/login?next=${encodeURIComponent(input.currentPath ?? "/")}`);
  }

  const { data: existing, error: lookupError } = await supabase
    .from("study_progress")
    .select("status")
    .eq("user_id", user.id)
    .eq("study_id", input.studyId)
    .maybeSingle();
  if (lookupError) throw lookupError;

  const nextStatus = existing?.status === "read" ? "unread" : "read";

  const { error } = await supabase
    .from("study_progress")
    .upsert(
      {
        user_id: user.id,
        study_id: input.studyId,
        status: nextStatus,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "user_id,study_id" },
    );
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
  return { status: nextStatus as "read" | "unread" };
}

type SaveNoteInput = {
  studyId: string;
  notes: string;
  currentPath?: string;
};

export async function saveStudyNote(input: SaveNoteInput) {
  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) {
    redirect(`/login?next=${encodeURIComponent(input.currentPath ?? "/")}`);
  }

  const trimmed = input.notes.slice(0, 5000);

  const { error } = await supabase
    .from("study_progress")
    .upsert(
      {
        user_id: user.id,
        study_id: input.studyId,
        notes: trimmed,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "user_id,study_id" },
    );
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
  return { notes: trimmed };
}
