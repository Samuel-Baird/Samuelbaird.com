import { NextRequest, NextResponse } from "next/server";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { sendDailyDigestEmail, type NotifiableMessage } from "@/lib/messages";

export const maxDuration = 60;

const WINDOW_MS = 24 * 60 * 60 * 1000;

export async function GET(req: NextRequest) {
  const authHeader = req.headers.get("authorization");
  const cronSecret = process.env.CRON_SECRET;
  // Fail closed: a missing CRON_SECRET must lock the route, not open it.
  if (!cronSecret || authHeader !== `Bearer ${cronSecret}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const since = new Date(Date.now() - WINDOW_MS).toISOString();
  const supabase = createSupabaseServiceClient();

  const [recentRes, openRes] = await Promise.all([
    supabase
      .from("messages")
      .select("id, category, name, email, page_ref, body, created_at")
      .gte("created_at", since)
      .order("created_at", { ascending: false }),
    supabase
      .from("messages")
      .select("id", { count: "exact", head: true })
      .eq("resolved", false),
  ]);

  if (recentRes.error || openRes.error) {
    throw recentRes.error ?? openRes.error;
  }

  const recent = (recentRes.data ?? []) as NotifiableMessage[];
  const openCount = openRes.count ?? 0;

  const sent = await sendDailyDigestEmail({ since, recent, openCount });

  return NextResponse.json({
    ok: true,
    sent,
    since,
    newCount: recent.length,
    openCount,
  });
}
