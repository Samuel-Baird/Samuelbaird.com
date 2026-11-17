"use client";

import { Loader2, X } from "lucide-react";
import { usePathname, useSearchParams } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { createSupabaseBrowserClient } from "@/lib/supabase/browser";
import { BASE_PATH } from "@/lib/site";

type AuthPromptContextValue = {
  requestLogin: (reason?: string) => void;
};

const AuthPromptContext = createContext<AuthPromptContextValue | null>(null);

export function useAuthPrompt(): AuthPromptContextValue {
  const ctx = useContext(AuthPromptContext);
  if (!ctx) {
    return { requestLogin: () => {} };
  }
  return ctx;
}

export function AuthPromptProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState<string | undefined>();
  const [pending, setPending] = useState(false);
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const currentPath = useMemo(() => {
    const qs = searchParams?.toString();
    return `${pathname || "/"}${qs ? `?${qs}` : ""}`;
  }, [pathname, searchParams]);

  const requestLogin = useCallback((nextReason?: string) => {
    setReason(nextReason);
    setOpen(true);
  }, []);

  const close = useCallback(() => {
    setOpen(false);
    setPending(false);
  }, []);

  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [open, close]);

  async function continueWithGoogle() {
    setPending(true);
    const supabase = createSupabaseBrowserClient();
    const redirectTo = `${window.location.origin}${BASE_PATH}/auth/callback?next=${encodeURIComponent(currentPath)}`;
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo },
    });
    if (error) setPending(false);
  }

  return (
    <AuthPromptContext.Provider value={{ requestLogin }}>
      {children}
      {open && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center px-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="auth-prompt-title"
        >
          <button
            type="button"
            aria-label="Close sign-in"
            onClick={close}
            className="absolute inset-0 bg-black/40"
          />
          <section className="relative w-full max-w-md rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--background)] p-7 shadow-lg">
            <button
              type="button"
              onClick={close}
              aria-label="Close"
              className="absolute right-3 top-3 inline-flex h-9 w-9 items-center justify-center rounded-full text-[color:var(--muted)] hover:bg-[color:var(--muted-soft)] hover:text-[color:var(--foreground)]"
            >
              <X size={18} aria-hidden="true" />
            </button>
            <h2
              id="auth-prompt-title"
              className="serif text-2xl font-semibold tracking-tight"
            >
              Sign in to continue
            </h2>
            <p className="mt-2 text-sm text-[color:var(--muted)]">
              {reason ?? "Sign in to upvote and bookmark channels and studies."}
            </p>
            <button
              type="button"
              disabled={pending}
              onClick={continueWithGoogle}
              className="mt-6 inline-flex h-12 w-full items-center justify-center gap-2 rounded-[var(--radius)] bg-[color:var(--accent)] px-5 text-sm font-medium text-white transition-colors hover:bg-[color:var(--foreground)] disabled:cursor-not-allowed disabled:opacity-70"
            >
              {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Continue with Google
            </button>
          </section>
        </div>
      )}
    </AuthPromptContext.Provider>
  );
}
