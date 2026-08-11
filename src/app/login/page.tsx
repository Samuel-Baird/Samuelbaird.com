"use client";

import { Loader2 } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { createSupabaseBrowserClient } from "@/lib/supabase/browser";

export default function LoginPage() {
  return (
    <Suspense fallback={<LoginCardSkeleton />}>
      <LoginContent />
    </Suspense>
  );
}

function LoginContent() {
  const searchParams = useSearchParams();
  const nextParam = searchParams.get("next") ?? "/";
  const error = searchParams.get("error");
  const [pending, setPending] = useState(false);

  async function continueWithGoogle() {
    setPending(true);
    const supabase = createSupabaseBrowserClient();
    const redirectTo = `${window.location.origin}/auth/callback?next=${encodeURIComponent(nextParam)}`;
    const { error: oauthError } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo },
    });

    if (oauthError) {
      setPending(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-6xl items-center justify-center px-5 py-16 sm:px-8">
      <section className="w-full max-w-md rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--background)] p-8">
        <div className="text-center">
          <h1 className="serif text-3xl font-semibold tracking-tight text-[color:var(--foreground)]">
            Latter-day Stats
          </h1>
          <p className="mt-3 text-sm text-[color:var(--muted)]">
            Sign in to bookmark channels and studies.
          </p>
        </div>

        {error ? (
          <p className="mt-6 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)] px-4 py-3 text-sm text-[color:var(--foreground)]">
            Sign-in failed. Please try again.
          </p>
        ) : null}

        <button
          type="button"
          disabled={pending}
          onClick={continueWithGoogle}
          className="mt-8 inline-flex h-12 w-full items-center justify-center gap-2 rounded-[var(--radius)] bg-[color:var(--accent)] px-5 text-sm font-medium text-white transition-colors hover:bg-[color:var(--foreground)] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          Continue with Google
        </button>
      </section>
    </div>
  );
}

function LoginCardSkeleton() {
  return (
    <div className="mx-auto flex min-h-[70vh] max-w-6xl items-center justify-center px-5 py-16 sm:px-8">
      <div className="h-56 w-full max-w-md animate-pulse rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)]" />
    </div>
  );
}
