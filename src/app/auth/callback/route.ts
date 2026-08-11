import { NextResponse, after, type NextRequest } from "next/server";
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

  // COPPA: /login only reaches here after the age-confirmation checkbox is
  // checked, so record it — but only stamp it once, and never let this block
  // sign-in. Swallowed rather than awaited-and-thrown: a stats/schema hiccup
  // here must not lock a real user out of their account.
  if (
    request.nextUrl.searchParams.get("age_confirmed") === "1" &&
    data.user
  ) {
    const userId = data.user.id;
    after(async () => {
      const { error: updateError } = await supabase
        .from("profiles")
        .update({ age_confirmed_at: new Date().toISOString() })
        .eq("id", userId)
        .is("age_confirmed_at", null);
      if (updateError) {
        console.error("age_confirmed_at stamp failed:", updateError);
      }
    });
  }

  return NextResponse.redirect(new URL(next, request.nextUrl.origin));
}
