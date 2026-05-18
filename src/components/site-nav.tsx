import Link from "next/link";
import { AuthMenu, type AuthMenuUser } from "@/components/auth-menu";
import { SiteNavClient, type SiteNavLink } from "@/components/site-nav-client";
import { getCurrentUser, signOutAction } from "@/lib/auth";

const links: SiteNavLink[] = [
  { href: "/channels", label: "Channels" },
  { href: "/studies", label: "Studies" },
  { href: "/about", label: "About" },
];

export async function SiteNav() {
  const auth = await getCurrentUser();
  const user: AuthMenuUser | null = auth
    ? {
        id: auth.user.id,
        email: auth.profile?.email ?? auth.user.email ?? null,
        full_name:
          auth.profile?.full_name ??
          (auth.user.user_metadata.full_name as string | undefined) ??
          null,
        avatar_url:
          auth.profile?.avatar_url ??
          (auth.user.user_metadata.avatar_url as string | undefined) ??
          null,
        is_admin: auth.profile?.is_admin === true,
      }
    : null;

  return (
    <header className="sticky top-0 z-40 border-b border-[color:var(--border)] bg-[color:var(--background)]/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-4 sm:px-8">
        <Link
          href="/"
          className="serif text-xl font-semibold tracking-tight text-[color:var(--foreground)] sm:text-2xl"
        >
          Latter-day Stats
        </Link>

        <div className="flex items-center gap-3">
          <SiteNavClient links={links} user={user} signOut={signOutAction} />
          <AuthMenu user={user} signOut={signOutAction} />
        </div>
      </div>
    </header>
  );
}
