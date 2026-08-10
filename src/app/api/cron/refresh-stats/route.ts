import { NextRequest, NextResponse } from "next/server";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { runStatsRefresh } from "@/lib/refresh-stats";

export const maxDuration = 300;

export async function GET(req: NextRequest) {
  const authHeader = req.headers.get("authorization");
  const cronSecret = process.env.CRON_SECRET;
  // Fail closed: a missing CRON_SECRET must lock the route, not open it.
  if (!cronSecret || authHeader !== `Bearer ${cronSecret}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const supabase = createSupabaseServiceClient();
  const summary = await runStatsRefresh(supabase, { activeOnly: true });

  // Non-200 on write failures so Vercel cron monitoring flags the run.
  // "missing" channels are a data condition (deleted/renamed on YouTube),
  // not a failure of the refresh itself.
  const ok = summary.failed === 0 && (summary.synced > 0 || summary.total === 0);
  return NextResponse.json({ ok, ...summary }, { status: ok ? 200 : 500 });
}
