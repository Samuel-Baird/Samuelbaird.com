import { NextResponse, type NextRequest } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const nextParam = request.nextUrl.searchParams.get("next") || "/";
  const next =
    nextParam.startsWith("/") && !nextParam.startsWith("//") ? nextParam : "/";

  if (!code) {
    return NextResponse.redirect(new URL("/login?error=oauth", request.url));
  }

  const supabase = await createSupabaseServerClient();
  const { data, error } = await supabase.auth.exchangeCodeForSession(code);

  if (error) {
    return NextResponse.redirect(new URL("/login?error=oauth", request.url));
  }

  // COPPA: every sign-in path (the /login page and the AuthPromptProvider
  // modal) lands here, so this is the one place that reliably knows whether
  // a user has ever confirmed their age. A never-confirmed profile means
  // this is (in effect) a first login — send them on to `next` with
  // `age_gate=1` so the site-wide AgeGateModal can collect confirmation
  // post sign-in, without blocking the OAuth flow itself. A lookup failure
  // must never block sign-in, so it's treated the same as "already
  // confirmed" rather than retried.
  let needsAgeGate = false;
  if (data.user) {
    const { data: profile, error: profileError } = await supabase
      .from("profiles")
      .select("age_confirmed_at")
      .eq("id", data.user.id)
      .maybeSingle();
    if (profileError) {
      console.error("age_confirmed_at lookup failed:", profileError);
    } else {
      needsAgeGate = !profile?.age_confirmed_at;
    }
  }

  const redirectUrl = new URL(next, request.nextUrl.origin);
  if (needsAgeGate) {
    redirectUrl.searchParams.set("age_gate", "1");
  }

  return NextResponse.redirect(redirectUrl);
}
