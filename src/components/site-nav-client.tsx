"use client";

import { Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { AuthAvatar, type AuthMenuUser } from "@/components/auth-menu";

export type SiteNavLink = {
  href: string;
  label: string;
};

type SiteNavClientProps = {
  links: SiteNavLink[];
  user: AuthMenuUser | null;
  signOut: () => Promise<void>;
};

function isActive(pathname: string, href: string) {
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}

export function SiteNavClient({ links, user, signOut }: SiteNavClientProps) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <>
      <nav className="hidden gap-7 text-sm md:flex">
        {links.map((link) => {
          const active = isActive(pathname, link.href);
          return (
            <Link
              key={link.href}
              href={link.href}
              className={
                active
                  ? "text-[color:var(--foreground)]"
                  : "text-[color:var(--muted)] transition-colors hover:text-[color:var(--foreground)]"
              }
            >
              {link.label}
            </Link>
          );
        })}
      </nav>

      <button
        type="button"
        aria-label={open ? "Close menu" : "Open menu"}
        aria-expanded={open}
        className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-[color:var(--border)] md:hidden"
        onClick={() => setOpen((value) => !value)}
      >
        {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {open ? (
        <div className="absolute inset-x-0 top-full border-t border-[color:var(--border)] bg-[color:var(--background)] md:hidden">
          <nav className="mx-auto flex max-w-6xl flex-col px-5 py-3 sm:px-8">
            {links.map((link) => {
              const active = isActive(pathname, link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className={
                    "rounded-md px-2 py-3 text-base " +
                    (active
                      ? "bg-[color:var(--muted-soft)] text-[color:var(--foreground)]"
                      : "text-[color:var(--muted)] hover:text-[color:var(--foreground)]")
                  }
                >
                  {link.label}
                </Link>
              );
            })}

            <div className="mt-3 border-t border-[color:var(--border)] pt-3">
              {user ? (
                <>
                  <div className="flex items-center gap-3 px-2 py-2">
                    <AuthAvatar user={user} />
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-[color:var(--foreground)]">
                        {user.full_name || "Signed in"}
                      </p>
                      <p className="truncate text-xs text-[color:var(--muted)]">
                        {user.email}
                      </p>
                    </div>
                  </div>
                  <Link
                    href="/me/bookmarks"
                    onClick={() => setOpen(false)}
                    className="block rounded-md px-2 py-3 text-base text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
                  >
                    My bookmarks
                  </Link>
                  {user.is_admin ? (
                    <Link
                      href="/admin"
                      onClick={() => setOpen(false)}
                      className="block rounded-md px-2 py-3 text-base text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
                    >
                      Admin
                    </Link>
                  ) : null}
                  <form action={signOut}>
                    <button
                      type="submit"
                      className="block w-full rounded-md px-2 py-3 text-left text-base text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
                    >
                      Sign out
                    </button>
                  </form>
                </>
              ) : (
                <Link
                  href={`/login?next=${encodeURIComponent(pathname || "/")}`}
                  onClick={() => setOpen(false)}
                  className="block rounded-md px-2 py-3 text-base font-medium text-[color:var(--foreground)]"
                >
                  Sign in
                </Link>
              )}
            </div>
          </nav>
        </div>
      ) : null}
    </>
  );
}
