import { NextRequest, NextResponse } from "next/server";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { sendDailyDigestEmail, type NotifiableMessage } from "@/lib/messages";
import { logEvent } from "@/lib/log";
import { monthlyWindow, runMonthlyNewsletter } from "@/lib/newsletter";

// Vercel Hobby caps a project at 2 cron jobs; both are already spent (this
// route + refresh-stats), so the monthly newsletter rides along here instead
// of getting its own schedule — see the day-of-month guard below.
export const maxDuration = 300;

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

  // The monthly newsletter runs on the 1st of the month (UTC), reporting the
  // month that just closed. `?newsletter=force` (still behind CRON_SECRET,
  // checked above) lets it be triggered on any day for testing; the
  // month_key unique constraint in runMonthlyNewsletter still prevents a
  // real double-send. Kept in its own try/catch so a newsletter failure
  // can't take down the daily digest response, and vice versa.
  const isFirstOfMonth = new Date().getUTCDate() === 1;
  const forceNewsletter = req.nextUrl.searchParams.get("newsletter") === "force";
  let newsletter: unknown = null;
  if (isFirstOfMonth || forceNewsletter) {
    try {
      newsletter = await runMonthlyNewsletter(supabase, monthlyWindow());
    } catch (err) {
      logEvent(
        "newsletter.failed",
        { error: err instanceof Error ? err.message : String(err) },
        "error",
      );
      newsletter = { status: "failed" };
    }
  }

  return NextResponse.json({
    ok: true,
    sent,
    since,
    newCount: recent.length,
    openCount,
    newsletter,
  });
}
