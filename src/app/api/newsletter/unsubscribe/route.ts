import { NextRequest, NextResponse } from "next/server";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { unsubscribeByToken } from "@/lib/newsletter";

// RFC 8058 one-click unsubscribe target, advertised via the List-Unsubscribe
// / List-Unsubscribe-Post headers on the monthly newsletter. POST-only and no
// GET export on purpose: mail clients and link-scanners routinely prefetch
// GET links, which would silently unsubscribe people who never clicked
// anything. The human-facing link in the email body goes to /unsubscribe
// (a confirm page) instead.
export async function POST(req: NextRequest) {
  const token = req.nextUrl.searchParams.get("token")?.trim() ?? "";
  if (token) {
    await unsubscribeByToken(createSupabaseServiceClient(), token);
  }
  // Always 200 regardless of whether a row matched, so this endpoint can't
  // be used to probe which tokens are valid.
  return NextResponse.json({ ok: true });
}
