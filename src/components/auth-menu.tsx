"use client";

import { ChevronDown, LogOut, Shield, UserRound } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

export type AuthMenuUser = {
  id: string;
  email: string | null;
  full_name: string | null;
  avatar_url: string | null;
  is_admin: boolean;
};

type AuthMenuProps = {
  user: AuthMenuUser | null;
  signOut: () => Promise<void>;
};

function userInitial(user: AuthMenuUser) {
  return (user.full_name?.trim() || user.email || "?").charAt(0).toUpperCase();
}

export function AuthAvatar({ user }: { user: AuthMenuUser }) {
  if (user.avatar_url) {
    return (
      <img
        src={user.avatar_url}
        alt=""
        referrerPolicy="no-referrer"
        className="h-8 w-8 rounded-full object-cover"
      />
    );
  }

  return (
    <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-[color:var(--accent-soft)] text-sm font-semibold text-[color:var(--accent)]">
      {userInitial(user)}
    </span>
  );
}

export function AuthMenu({ user, signOut }: AuthMenuProps) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) {
      return;
    }

    function onMouseDown(event: MouseEvent) {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    }

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", onMouseDown);
    document.addEventListener("keydown", onKeyDown);

    return () => {
      document.removeEventListener("mousedown", onMouseDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  if (!user) {
    const next = encodeURIComponent(pathname || "/");

    return (
      <Link
        href={`/login?next=${next}`}
        className="inline-flex h-10 items-center justify-center rounded-full border border-[color:var(--border)] px-4 text-sm font-medium text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
      >
        Sign in
      </Link>
    );
  }

  return (
    <div ref={menuRef} className="relative">
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
        className="inline-flex h-10 items-center gap-2 rounded-full border border-[color:var(--border)] bg-[color:var(--background)] px-1.5 pr-3 text-sm text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
      >
        <AuthAvatar user={user} />
        <ChevronDown className="h-4 w-4 text-[color:var(--muted)]" />
      </button>

      {open ? (
        <div
          role="menu"
          className="absolute right-0 top-12 z-50 w-64 rounded-lg border border-[color:var(--border)] bg-[color:var(--background)] p-2 shadow-lg"
        >
          <div className="border-b border-[color:var(--border)] px-3 py-3">
            <p className="truncate text-sm font-medium text-[color:var(--foreground)]">
              {user.full_name || "Signed in"}
            </p>
            <p className="mt-0.5 truncate text-xs text-[color:var(--muted)]">
              {user.email}
            </p>
          </div>

          <Link
            href="/me/bookmarks"
            role="menuitem"
            onClick={() => setOpen(false)}
            className="mt-2 flex items-center gap-2 rounded-md px-3 py-2 text-sm text-[color:var(--foreground)] hover:bg-[color:var(--muted-soft)]"
          >
            <UserRound className="h-4 w-4 text-[color:var(--muted)]" />
            My bookmarks
          </Link>

          {user.is_admin ? (
            <Link
              href="/admin"
              role="menuitem"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-[color:var(--foreground)] hover:bg-[color:var(--muted-soft)]"
            >
              <Shield className="h-4 w-4 text-[color:var(--muted)]" />
              Admin
            </Link>
          ) : null}

          <form action={signOut}>
            <button
              type="submit"
              role="menuitem"
              className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm text-[color:var(--foreground)] hover:bg-[color:var(--muted-soft)]"
            >
              <LogOut className="h-4 w-4 text-[color:var(--muted)]" />
              Sign out
            </button>
          </form>
        </div>
      ) : null}
    </div>
  );
}
