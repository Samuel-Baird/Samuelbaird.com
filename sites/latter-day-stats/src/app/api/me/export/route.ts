import { NextResponse } from "next/server";
import { getCurrentUser } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

// Self-serve data export (GDPR/CCPA). Returns the raw rows this account
// owns — not a curated report — across every user-scoped table.
export async function GET() {
  const auth = await getCurrentUser();
  if (!auth) {
    return NextResponse.json({ error: "Not signed in" }, { status: 401 });
  }

  const supabase = createSupabaseServiceClient();
  const userId = auth.user.id;

  const [bookmarks, upvotes, studyProgress, messages] =
    await Promise.all([
      supabase
        .from("bookmarks")
        .select("target_type, target_id, created_at")
        .eq("user_id", userId),
      supabase
        .from("upvotes")
        .select("target_type, target_id, created_at")
        .eq("user_id", userId),
      supabase
        .from("study_progress")
        .select("study_id, status, notes, updated_at")
        .eq("user_id", userId),
      supabase
        .from("messages")
        .select("category, body, page_ref, created_at")
        .eq("user_id", userId),
    ]);

  const exportData = {
    exported_at: new Date().toISOString(),
    profile: {
      id: userId,
      email: auth.profile?.email ?? auth.user.email ?? null,
      full_name: auth.profile?.full_name ?? null,
      account_created_at: auth.profile?.created_at ?? null,
    },
    bookmarks: bookmarks.data ?? [],
    upvotes: upvotes.data ?? [],
    study_progress: studyProgress.data ?? [],
    messages_sent: messages.data ?? [],
  };

  return new NextResponse(JSON.stringify(exportData, null, 2), {
    headers: {
      "Content-Type": "application/json",
      "Content-Disposition": 'attachment; filename="latter-day-stats-data.json"',
    },
  });
}
